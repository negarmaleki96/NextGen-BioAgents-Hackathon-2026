from __future__ import annotations

from fda_510k.knowledge.checklist import load_estar_checklist
from fda_510k.models.common import ExtractedField, FieldProvenance
from fda_510k.models.predicate import PredicateCandidate
from fda_510k.models.profile import SubmissionProfile

FIELD_ID_TO_PROFILE = {f.id: f.profile_field for f in load_estar_checklist()}


def _is_missing(field: ExtractedField) -> bool:
    return field.provenance == FieldProvenance.MISSING or field.value is None


def apply_clarifications(
    profile: SubmissionProfile,
    clarifications: dict[str, str] | None,
) -> SubmissionProfile:
    if not clarifications:
        return profile
    for field_id, answer in clarifications.items():
        if not answer or not answer.strip():
            continue
        profile_field = FIELD_ID_TO_PROFILE.get(field_id, field_id)
        if not hasattr(profile, profile_field):
            continue
        setattr(
            profile,
            profile_field,
            ExtractedField.from_value(
                answer.strip(),
                confidence=0.85,
                provenance=FieldProvenance.EXPLICIT,
                notes="User clarification",
            ),
        )
    profile.recompute_summary()
    return profile


def backfill_from_predicate(
    profile: SubmissionProfile,
    predicate: PredicateCandidate | None,
) -> SubmissionProfile:
    if predicate is None:
        return profile

    backfills = [
        ("product_code", predicate.product_code, f"Inferred from predicate {predicate.k_number}"),
        ("regulation_number", predicate.regulation_number, f"Inferred from predicate {predicate.k_number}"),
        ("device_class", predicate.device_class, f"Inferred from predicate {predicate.k_number}"),
        ("advisory_committee", predicate.advisory_committee, f"Inferred from predicate {predicate.k_number}"),
    ]
    for field_name, value, note in backfills:
        if value is None:
            continue
        current = getattr(profile, field_name)
        if _is_missing(current):
            setattr(
                profile,
                field_name,
                ExtractedField.from_value(
                    value,
                    confidence=0.45,
                    provenance=FieldProvenance.INFERRED,
                    notes=note,
                ),
            )

    pred_mentions = profile.user_predicate_mentions
    if _is_missing(pred_mentions):
        profile.user_predicate_mentions = ExtractedField.from_value(
            [f"{predicate.device_name} ({predicate.k_number})"],
            confidence=0.5,
            provenance=FieldProvenance.INFERRED,
            notes=f"Suggested predicate from openFDA search: {predicate.k_number}",
        )

    profile.recompute_summary()
    return profile


def apply_submission_defaults(profile: SubmissionProfile) -> SubmissionProfile:
    if _is_missing(profile.submission_type):
        profile.submission_type = ExtractedField.from_value(
            "Traditional",
            confidence=0.4,
            provenance=FieldProvenance.INFERRED,
            notes="Default assumption — verify submission pathway",
        )

    if _is_missing(profile.device_trade_name) and not _is_missing(profile.device_common_name):
        profile.device_trade_name = ExtractedField.from_value(
            profile.device_common_name.value,
            confidence=0.35,
            provenance=FieldProvenance.INFERRED,
            notes="Copied from common name — provide official trade name",
        )

    profile.recompute_summary()
    return profile


def enrich_profile(
    profile: SubmissionProfile,
    *,
    clarifications: dict[str, str] | None = None,
    top_predicate: PredicateCandidate | None = None,
) -> SubmissionProfile:
    profile = apply_clarifications(profile, clarifications)
    profile = backfill_from_predicate(profile, top_predicate)
    profile = apply_submission_defaults(profile)
    return profile
