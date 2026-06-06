from __future__ import annotations

from fda_510k.knowledge.checklist import evaluate_device_conditions, load_estar_checklist
from fda_510k.models.common import ExtractedField, FieldProvenance
from fda_510k.models.gap import GapItem, GapSeverity
from fda_510k.models.profile import SubmissionProfile


def _field_status(field: ExtractedField) -> str:
    if field.provenance == FieldProvenance.MISSING or field.value is None:
        return "missing"
    if field.provenance == FieldProvenance.INFERRED and field.confidence < 0.5:
        return "weak"
    if field.provenance == FieldProvenance.INFERRED:
        return "weak"
    return "present"


def run_gap_analysis(profile: SubmissionProfile) -> list[GapItem]:
    conditions = evaluate_device_conditions(profile)
    checklist = load_estar_checklist()
    gaps: list[GapItem] = []

    for item in checklist:
        if item.condition and not conditions.get(item.condition, False):
            continue

        field: ExtractedField = getattr(profile, item.profile_field, ExtractedField.missing())
        status = _field_status(field)

        # Special case: predicate can be satisfied by search results later
        if item.profile_field == "user_predicate_mentions" and status == "missing":
            status = "missing"

        gaps.append(
            GapItem(
                estar_section_id=item.section_id,
                field_id=item.id,
                label=item.label,
                severity=item.severity,
                status=status,  # type: ignore[arg-type]
                source_refs=field.source_refs,
                draft_available=status in ("missing", "weak"),
                notes=item.notes,
            )
        )

    return gaps


def get_blocker_gaps(gaps: list[GapItem]) -> list[GapItem]:
    return [g for g in gaps if g.severity == GapSeverity.BLOCKER and g.status != "present"]


def generate_clarifying_questions(
    profile: SubmissionProfile,
    gaps: list[GapItem],
    max_questions: int = 5,
) -> list[dict]:
    questions: list[dict] = []
    blockers = get_blocker_gaps(gaps)

    question_templates = {
        "product_code": (
            "What is the FDA product code for your device? "
            "(Check FDA Product Classification Database if unsure.)"
        ),
        "indications_for_use": (
            "What are the specific indications for use? "
            "Include patient population and clinical setting."
        ),
        "principle_of_operation": (
            "How does the device work? Describe the principle of operation."
        ),
        "user_predicate_mentions": (
            "Do you have a predicate device in mind? Provide a K-number or marketed device name."
        ),
        "device_trade_name": "What is the proposed trade name for your device?",
        "biocompatibility": (
            "Does the device have patient contact? "
            "If so, what biocompatibility testing has been performed per ISO 10993?"
        ),
        "software_vv": (
            "Describe your software verification and validation activities "
            "(IEC 62304 compliance level, testing performed)."
        ),
    }

    for gap in blockers:
        if len(questions) >= max_questions:
            break
        template = question_templates.get(gap.field_id)
        if template:
            questions.append(
                {
                    "question": template,
                    "field_id": gap.field_id,
                    "severity": gap.severity.value,
                    "rationale": f"Required for eSTAR section: {gap.estar_section_id}",
                }
            )

    return questions
