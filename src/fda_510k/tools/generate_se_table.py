from __future__ import annotations

from fda_510k.models.predicate import PredicateCandidate, SEComparison, SEComparisonRow
from fda_510k.models.profile import SubmissionProfile


def _val(profile: SubmissionProfile, field: str, default: str = "Not provided") -> str:
    f = getattr(profile, field, None)
    if f and f.value is not None:
        if isinstance(f.value, list):
            return ", ".join(str(v) for v in f.value)
        return str(f.value)
    return default


def generate_se_comparison(
    profile: SubmissionProfile,
    predicate: PredicateCandidate,
) -> SEComparison:
    rows = [
        SEComparisonRow(
            characteristic="Indications for Use",
            subject_device=_val(profile, "indications_for_use"),
            predicate_device="See 510(k) Summary (not in openFDA metadata)",
            comparison_notes="Compare intended use statements carefully — must not expand indications.",
        ),
        SEComparisonRow(
            characteristic="Device Trade Name",
            subject_device=_val(profile, "device_trade_name"),
            predicate_device=predicate.device_name,
        ),
        SEComparisonRow(
            characteristic="Technology / Principle of Operation",
            subject_device=_val(profile, "principle_of_operation"),
            predicate_device="Refer to predicate 510(k) Summary for detailed comparison",
            comparison_notes="Document any technological differences and why they do not raise new SE questions.",
        ),
        SEComparisonRow(
            characteristic="Materials",
            subject_device=_val(profile, "materials"),
            predicate_device="Refer to predicate 510(k) Summary",
        ),
        SEComparisonRow(
            characteristic="Energy Source",
            subject_device=_val(profile, "energy_source"),
            predicate_device="Refer to predicate 510(k) Summary",
        ),
        SEComparisonRow(
            characteristic="Software",
            subject_device=_val(profile, "software_present"),
            predicate_device="Refer to predicate 510(k) Summary",
            comparison_notes="Software differences often raise different questions — document thoroughly.",
            raises_different_questions=bool(profile.software_present.value),
        ),
        SEComparisonRow(
            characteristic="Product Code",
            subject_device=_val(profile, "product_code"),
            predicate_device=predicate.product_code,
            comparison_notes="Same product code supports SE; different code requires justification.",
            raises_different_questions=(
                profile.product_code.value is not None
                and predicate.product_code != profile.product_code.value
            ),
        ),
    ]

    confidence_notes = []
    for field_name in ("indications_for_use", "principle_of_operation", "materials"):
        f = getattr(profile, field_name)
        if f.provenance.value == "missing":
            confidence_notes.append(f"{field_name}: missing — comparison is incomplete")
        elif f.provenance.value == "inferred":
            confidence_notes.append(f"{field_name}: inferred — verify before submission")

    subject = _val(profile, "device_trade_name", default="")
    indications = _val(profile, "indications_for_use", default="")
    narrative_parts = [
        "Substantial Equivalence Comparison",
        f"Subject Device: {subject}" if subject else "",
        f"Predicate Device: {predicate.device_name} ({predicate.k_number})",
        f"Predicate Applicant: {predicate.applicant}",
        f"Predicate Clearance Date: {predicate.decision_date}",
    ]
    if indications:
        narrative_parts.append(f"Subject Indications for Use: {indications}")
    narrative = "\n".join(part for part in narrative_parts if part)

    return SEComparison(
        predicate_k_number=predicate.k_number,
        predicate_device_name=predicate.device_name,
        rows=rows,
        narrative_draft=narrative,
        confidence_notes=confidence_notes,
    )
