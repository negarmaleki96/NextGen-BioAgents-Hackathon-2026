from fda_510k.models.common import ExtractedField, FieldProvenance
from fda_510k.models.profile import SubmissionProfile
from fda_510k.tools.gap_analysis_estar import get_blocker_gaps, run_gap_analysis


def test_gap_analysis_empty_profile():
    profile = SubmissionProfile()
    gaps = run_gap_analysis(profile)
    assert len(gaps) > 0
    blockers = get_blocker_gaps(gaps)
    assert any(g.field_id == "product_code" for g in blockers)
    assert any(g.field_id == "indications_for_use" for g in blockers)


def test_gap_analysis_partial_profile():
    profile = SubmissionProfile(
        product_code=ExtractedField.from_value(
            "DQA",
            confidence=0.9,
            provenance=FieldProvenance.EXPLICIT,
        ),
        indications_for_use=ExtractedField.from_value(
            "Measure SpO2 in adults",
            confidence=0.9,
            provenance=FieldProvenance.EXPLICIT,
        ),
        principle_of_operation=ExtractedField.from_value(
            "LED pulse oximetry",
            confidence=0.8,
            provenance=FieldProvenance.EXPLICIT,
        ),
    )
    gaps = run_gap_analysis(profile)
    product_gap = next(g for g in gaps if g.field_id == "product_code")
    assert product_gap.status == "present"
