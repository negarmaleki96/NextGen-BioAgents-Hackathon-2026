from __future__ import annotations

from fda_510k.config import settings
from fda_510k.extraction.prompts.draft_sections import SECTION_DRAFT_SYSTEM, SECTION_DRAFT_USER
from fda_510k.knowledge.checklist import evaluate_device_conditions, load_estar_checklist
from fda_510k.knowledge.estar_transcript import get_estar_guidance
from fda_510k.llm.nebius_client import NebiusClient
from fda_510k.models.common import ExtractedField, FieldProvenance
from fda_510k.models.gap import GapItem
from fda_510k.models.output import EstarDraft
from fda_510k.models.predicate import PredicateCandidate, SEComparison
from fda_510k.models.profile import SubmissionProfile


def _field_content(field: ExtractedField | None) -> str:
    if field is None or field.value is None:
        return ""
    if isinstance(field.value, list):
        return ", ".join(str(v) for v in field.value)
    return str(field.value).strip()


def _strip_watermark(text: str) -> str:
    watermark = settings.draft_watermark
    cleaned = text.strip()
    if cleaned.startswith(watermark):
        cleaned = cleaned[len(watermark) :].strip()
    return cleaned


def _llm_draft_field(
    llm: NebiusClient,
    field_id: str,
    field_label: str,
    section_label: str,
    profile: SubmissionProfile,
    predicate: PredicateCandidate | None,
    known_value: str,
) -> str:
    estar_instructions = get_estar_guidance(field_id=field_id, section_label=section_label)
    if not estar_instructions:
        estar_instructions = "No specific eSTAR transcript excerpt available for this field."

    prompt = SECTION_DRAFT_USER.format(
        field_label=field_label,
        section_label=section_label,
        trade_name=_field_content(profile.device_trade_name) or "Unknown",
        common_name=_field_content(profile.device_common_name) or "Unknown",
        indications=_field_content(profile.indications_for_use) or "Not specified",
        principle=_field_content(profile.principle_of_operation) or "Not specified",
        product_code=_field_content(profile.product_code) or "Not specified",
        predicate=f"{predicate.device_name} ({predicate.k_number})" if predicate else "Not specified",
        known_value=known_value or "None",
        eSTAR_instructions=estar_instructions,
    )
    try:
        text = _strip_watermark(llm.generate(prompt, system=SECTION_DRAFT_SYSTEM, temperature=0.2))
        if text.lower() in {"", "unknown", "n/a", "not specified", "none"}:
            return ""
        return text
    except Exception:
        return ""


def draft_all_estar_sections(
    profile: SubmissionProfile,
    gaps: list[GapItem],
    *,
    predicate: PredicateCandidate | None = None,
    se: SEComparison | None = None,
    llm: NebiusClient | None = None,
) -> list[EstarDraft]:
    llm = llm or NebiusClient()
    use_llm = llm.is_available()
    conditions = evaluate_device_conditions(profile)
    gap_by_field = {g.field_id: g for g in gaps}
    drafts: list[EstarDraft] = []

    for item in load_estar_checklist():
        if item.condition and not conditions.get(item.condition, False):
            continue

        field: ExtractedField = getattr(profile, item.profile_field, ExtractedField.missing())
        known = _field_content(field)
        gap = gap_by_field.get(item.id)
        status = gap.status if gap else ("present" if known else "missing")

        if known:
            content = known
        elif use_llm:
            content = _llm_draft_field(
                llm, item.id, item.label, item.section_label, profile, predicate, known
            )
        else:
            content = ""

        drafts.append(
            EstarDraft(
                estar_section_id=item.section_id,
                section_label=item.section_label,
                field_id=item.id,
                content=content,
                is_draft=status != "present" or field.provenance != FieldProvenance.EXPLICIT,
            )
        )

    return drafts
