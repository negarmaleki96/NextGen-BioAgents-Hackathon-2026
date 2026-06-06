from __future__ import annotations

from typing import Any

from fda_510k.config import settings
from fda_510k.extraction.prompts.extraction_passes import (
    PASS_1_IDENTITY,
    PASS_2_TECHNOLOGY,
    PASS_3_TESTING,
    PASS_4_PREDICATES,
)
from fda_510k.ingestion.pipeline import ParsedDocument
from fda_510k.llm.gemini_client import GeminiClient
from fda_510k.models.common import ExtractedField, FieldProvenance, SourceRef
from fda_510k.models.profile import SubmissionProfile


class ProfileExtractor:
    PASSES = [
        ("identity", PASS_1_IDENTITY),
        ("technology", PASS_2_TECHNOLOGY),
        ("testing", PASS_3_TESTING),
        ("predicates", PASS_4_PREDICATES),
    ]

    def __init__(self, llm: GeminiClient | None = None) -> None:
        self.llm = llm or GeminiClient()

    def _build_context(self, docs: list[ParsedDocument], max_chunks: int | None = None) -> str:
        max_chunks = max_chunks or settings.max_chunks_per_pass
        chunks = []
        for doc in docs:
            for chunk in doc.chunks[:max_chunks]:
                ref = chunk.source_ref
                header = f"[{ref.doc_name}"
                if ref.page:
                    header += f" p.{ref.page}"
                header += "]"
                chunks.append(f"{header}\n{chunk.text}")
        return "\n\n---\n\n".join(chunks[:max_chunks])

    def _field_from_raw(
        self,
        field_name: str,
        raw: dict[str, Any] | None,
        docs: list[ParsedDocument],
    ) -> ExtractedField:
        if not raw or raw.get("value") is None:
            return ExtractedField.missing()

        provenance = FieldProvenance(raw.get("provenance", "inferred"))
        confidence = float(raw.get("confidence", 0.5))
        if provenance == FieldProvenance.INFERRED:
            confidence = min(confidence, 0.6)
        elif provenance == FieldProvenance.EXPLICIT:
            confidence = max(confidence, 0.7)

        source_refs: list[SourceRef] = []
        snippet = raw.get("snippet")
        if snippet and docs:
            source_refs.append(
                SourceRef(
                    doc_id=docs[0].doc_id,
                    doc_name=docs[0].doc_name,
                    snippet=str(snippet)[:300],
                )
            )

        return ExtractedField(
            value=raw["value"],
            confidence=confidence,
            provenance=provenance,
            source_refs=source_refs,
            notes=raw.get("notes"),
        )

    def _run_pass(self, prompt: str, context: str) -> dict[str, Any]:
        full_prompt = f"SOURCE DOCUMENTS:\n{context}\n\nTASK:\n{prompt}"
        try:
            result = self.llm.generate_json(full_prompt, system="You are a regulatory document analyst.")
            if isinstance(result, dict):
                return result
        except (ValueError, Exception):
            pass
        return {}

    def extract(
        self,
        docs: list[ParsedDocument],
        *,
        use_llm: bool = True,
        clarifications: dict[str, str] | None = None,
    ) -> SubmissionProfile:
        profile = SubmissionProfile(input_manifest=[])
        context = self._build_context(docs)

        if clarifications:
            clar_text = "\n".join(f"{k}: {v}" for k, v in clarifications.items())
            context += f"\n\nUSER CLARIFICATIONS:\n{clar_text}"

        if use_llm and self.llm.is_available():
            for _, prompt in self.PASSES:
                raw_pass = self._run_pass(prompt, context)
                for field_name, raw_field in raw_pass.items():
                    if hasattr(profile, field_name):
                        setattr(
                            profile,
                            field_name,
                            self._field_from_raw(field_name, raw_field, docs),
                        )
        else:
            profile = self._heuristic_extract(docs)

        profile.recompute_summary()
        return profile

    def _heuristic_extract(self, docs: list[ParsedDocument]) -> SubmissionProfile:
        """Fallback when Gemini is unavailable — keyword-based extraction."""
        profile = SubmissionProfile()
        full_text = "\n".join(d.raw_text for d in docs).lower()

        def set_if_keyword(field: str, keywords: list[str], value: str) -> None:
            if any(kw in full_text for kw in keywords):
                setattr(
                    profile,
                    field,
                    ExtractedField.from_value(
                        value,
                        confidence=0.5,
                        provenance=FieldProvenance.INFERRED,
                        notes="Heuristic extraction (Gemini unavailable)",
                    ),
                )

        set_if_keyword("software_present", ["software", "firmware", "app", "bluetooth"], True)
        set_if_keyword("patient_contact", ["patient contact", "skin contact", "blood", "wound"], True)
        set_if_keyword("electrical_powered", ["battery", "rechargeable", "usb", "powered"], True)

        for doc in docs:
            text = doc.raw_text
            if "glucose" in text.lower():
                profile.device_common_name = ExtractedField.from_value(
                    "Continuous glucose monitor",
                    confidence=0.6,
                    provenance=FieldProvenance.INFERRED,
                    source_refs=[SourceRef(doc_id=doc.doc_id, doc_name=doc.doc_name, snippet=text[:200])],
                )
            if "K" in text:
                import re

                k_nums = re.findall(r"K\d{6}", text.upper())
                if k_nums:
                    profile.user_predicate_mentions = ExtractedField.from_value(
                        list(set(k_nums)),
                        confidence=0.8,
                        provenance=FieldProvenance.EXPLICIT,
                        source_refs=[SourceRef(doc_id=doc.doc_id, doc_name=doc.doc_name)],
                    )

        profile.recompute_summary()
        return profile
