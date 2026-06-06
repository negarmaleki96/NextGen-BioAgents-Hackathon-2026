from fda_510k.config import settings
from fda_510k.models.common import ExtractedField, FieldProvenance
from fda_510k.models.profile import SubmissionProfile
from fda_510k.tools.draft_all_estar_sections import draft_all_estar_sections
from fda_510k.tools.gap_analysis_estar import run_gap_analysis


def test_draft_uses_inferred_profile_value():
    profile = SubmissionProfile(
        applicant_name=ExtractedField.from_value(
            "Acme Medical Inc.",
            confidence=0.6,
            provenance=FieldProvenance.INFERRED,
        ),
    )
    gaps = run_gap_analysis(profile)
    drafts = draft_all_estar_sections(profile, gaps)
    applicant = next(d for d in drafts if d.field_id == "applicant_name")
    assert applicant.content == "Acme Medical Inc."
    assert settings.draft_watermark not in applicant.content


def test_draft_leaves_blank_without_profile_value():
    profile = SubmissionProfile()
    gaps = run_gap_analysis(profile)
    drafts = draft_all_estar_sections(profile, gaps, llm=type("OfflineLLM", (), {"is_available": lambda self: False})())
    applicant = next(d for d in drafts if d.field_id == "applicant_name")
    assert applicant.content == ""
