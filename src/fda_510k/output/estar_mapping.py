from __future__ import annotations

from fda_510k.knowledge.checklist import load_estar_checklist
from fda_510k.models.output import AgentOutput, SubmissionPackage


def build_estar_field_mapping(output: AgentOutput) -> dict:
    """Map internal profile fields to eSTAR output scaffold (legacy)."""
    profile = output.submission_profile
    mapping: dict = {"version": "nIVD_v6.2", "sections": {}}

    for item in load_estar_checklist():
        field = getattr(profile, item.profile_field, None)
        section = mapping["sections"].setdefault(
            item.section_id,
            {"label": item.section_label, "fields": {}},
        )
        section["fields"][item.id] = {
            "label": item.label,
            "value": field.value if field else None,
            "provenance": field.provenance.value if field else "missing",
            "confidence": field.confidence if field else 0.0,
            "severity": item.severity.value,
        }

    return mapping


def build_complete_estar_mapping(output: AgentOutput, package: SubmissionPackage | None = None) -> dict:
    """Complete eSTAR mapping with all fields filled — no null values."""
    package = package or output.submission_package
    if package is None:
        from fda_510k.output.submission_package import build_submission_package

        package = build_submission_package(output)

    mapping: dict = {
        "version": package.version,
        "readiness_score": package.readiness_score,
        "review_items": package.review_items,
        "sections": {},
    }

    for field in package.fields:
        section = mapping["sections"].setdefault(
            field.section_id,
            {"label": field.section_label, "fields": {}},
        )
        section["fields"][field.field_id] = {
            "label": field.label,
            "value": field.content,
            "content": field.content,
            "provenance": field.provenance,
            "confidence": field.confidence,
            "requires_review": field.requires_review,
        }

    return mapping
