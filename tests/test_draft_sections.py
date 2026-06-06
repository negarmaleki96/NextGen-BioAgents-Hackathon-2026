from fda_510k.models.profile import SubmissionProfile
from fda_510k.tools.draft_all_estar_sections import _template_draft
from fda_510k.tools.gap_analysis_estar import run_gap_analysis


def test_template_fallback_non_empty():
    profile = SubmissionProfile()
    gaps = run_gap_analysis(profile)
    text = _template_draft("principle_of_operation", "Principle of operation", profile, None, None)
    assert "DRAFT" in text
    assert "VERIFY" in text or "operation" in text.lower()
