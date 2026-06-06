from __future__ import annotations

from fda_510k.models.gap import GapItem, GapSeverity
from fda_510k.models.output import FDAQuestion
from fda_510k.models.predicate import SEComparison
from fda_510k.models.profile import SubmissionProfile


def generate_fda_questions(
    profile: SubmissionProfile,
    gaps: list[GapItem],
    se_comparison: SEComparison | None = None,
) -> list[FDAQuestion]:
    questions: list[FDAQuestion] = []

    blockers = [g for g in gaps if g.severity == GapSeverity.BLOCKER and g.status != "present"]
    if blockers:
        questions.append(
            FDAQuestion(
                category="RTA / Technical Screening",
                question=(
                    "FDA may issue a Refuse to Accept (RTA) hold because required submission "
                    f"elements are missing: {', '.join(g.label for g in blockers[:5])}."
                ),
                risk_level="high",
                mitigation="Complete all blocker fields before submission to avoid RTA delay.",
                triggered_by=[g.field_id for g in blockers],
            )
        )

    if not profile.product_code.value:
        questions.append(
            FDAQuestion(
                category="Classification",
                question="What is the appropriate FDA product code and device classification for this device?",
                risk_level="high",
                mitigation="Confirm product code via FDA Product Classification Database.",
                triggered_by=["product_code"],
            )
        )

    if profile.software_present.value:
        questions.append(
            FDAQuestion(
                category="Software / AI",
                question=(
                    "FDA will likely request software documentation per FDA Software Guidance "
                    "(IEC 62304 level, hazard analysis, SOUP, cybersecurity). "
                    "If AI/ML is involved, additional documentation may be required."
                ),
                risk_level="high",
                mitigation="Prepare Software Description, V&V summary, and cybersecurity risk assessment.",
                triggered_by=["software_present", "software_vv", "cybersecurity_features"],
            )
        )

    if profile.patient_contact.value and not profile.biocompatibility.value:
        questions.append(
            FDAQuestion(
                category="Biocompatibility",
                question=(
                    "FDA will likely request biocompatibility testing per ISO 10993 "
                    "for the identified patient-contacting materials."
                ),
                risk_level="high",
                mitigation="Conduct biocompatibility risk assessment and testing per ISO 10993-1.",
                triggered_by=["patient_contact", "biocompatibility"],
            )
        )

    if profile.electrical_powered.value and not profile.emc.value:
        questions.append(
            FDAQuestion(
                category="EMC / Electrical Safety",
                question="FDA may request EMC and electrical safety testing per IEC 60601-1 / IEC 60601-1-2.",
                risk_level="medium",
                mitigation="Perform EMC testing and document compliance with recognized standards.",
                triggered_by=["electrical_powered", "emc"],
            )
        )

    if se_comparison:
        diff_rows = [r for r in se_comparison.rows if r.raises_different_questions]
        if diff_rows:
            questions.append(
                FDAQuestion(
                    category="Substantial Equivalence",
                    question=(
                        "FDA may question whether technological differences "
                        f"({', '.join(r.characteristic for r in diff_rows)}) "
                        "raise different questions of safety and effectiveness."
                    ),
                    risk_level="high",
                    mitigation="Provide detailed discussion of differences with supporting performance data.",
                    triggered_by=[r.characteristic for r in diff_rows],
                )
            )

    if not profile.risk_analysis.value:
        questions.append(
            FDAQuestion(
                category="Risk Management",
                question="FDA may request risk management documentation (ISO 14971 hazard analysis).",
                risk_level="medium",
                mitigation="Complete design risk analysis and link hazards to mitigations and V&V.",
                triggered_by=["risk_analysis"],
            )
        )

    return questions
