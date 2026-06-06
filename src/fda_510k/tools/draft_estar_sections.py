from __future__ import annotations

from fda_510k.knowledge.checklist import load_estar_checklist
from fda_510k.models.gap import GapItem
from fda_510k.models.output import EstarDraft
from fda_510k.models.profile import SubmissionProfile


def draft_missing_sections(
    profile: SubmissionProfile,
    gaps: list[GapItem],
) -> list[EstarDraft]:
    checklist = {f.id: f for f in load_estar_checklist()}
    drafts: list[EstarDraft] = []

    for gap in gaps:
        if gap.status == "present" or not gap.draft_available:
            continue

        section = checklist.get(gap.field_id)
        profile_field = section.profile_field if section else gap.field_id
        field = getattr(profile, profile_field, None)
        section_label = section.section_label if section else gap.estar_section_id

        if field and field.value is not None:
            if isinstance(field.value, list):
                content = ", ".join(str(v) for v in field.value)
            else:
                content = str(field.value).strip()
        else:
            content = ""

        drafts.append(
            EstarDraft(
                estar_section_id=gap.estar_section_id,
                section_label=section_label,
                field_id=gap.field_id,
                content=content,
            )
        )

    return drafts
