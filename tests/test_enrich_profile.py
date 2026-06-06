from fda_510k.models.common import ExtractedField, FieldProvenance
from fda_510k.models.predicate import PredicateCandidate
from fda_510k.models.profile import SubmissionProfile
from fda_510k.tools.enrich_profile import (
    apply_clarifications,
    apply_submission_defaults,
    backfill_from_predicate,
    enrich_profile,
)
from datetime import date


def test_apply_clarifications():
    profile = SubmissionProfile()
    profile = apply_clarifications(profile, {"product_code": "DQY", "applicant_name": "Acme Inc"})
    assert profile.product_code.value == "DQY"
    assert profile.product_code.provenance == FieldProvenance.EXPLICIT
    assert profile.applicant_name.value == "Acme Inc"


def test_backfill_from_predicate():
    profile = SubmissionProfile()
    pred = PredicateCandidate(
        k_number="K123456",
        device_name="Test Device",
        applicant="Corp",
        product_code="DQA",
        regulation_number="870.2700",
        device_class="2",
        decision_date=date(2020, 1, 1),
    )
    profile = backfill_from_predicate(profile, pred)
    assert profile.product_code.value == "DQA"
    assert profile.product_code.provenance == FieldProvenance.INFERRED
    assert profile.user_predicate_mentions.value is not None


def test_apply_submission_defaults():
    profile = SubmissionProfile()
    profile = apply_submission_defaults(profile)
    assert profile.submission_type.value == "Traditional"


def test_enrich_profile_combined():
    profile = SubmissionProfile()
    pred = PredicateCandidate(
        k_number="K999999",
        device_name="Oximeter",
        applicant="Test",
        product_code="DQA",
    )
    result = enrich_profile(profile, clarifications={"indications_for_use": "Measure SpO2"}, top_predicate=pred)
    assert result.indications_for_use.value == "Measure SpO2"
    assert result.product_code.value == "DQA"
    assert result.submission_type.value == "Traditional"
