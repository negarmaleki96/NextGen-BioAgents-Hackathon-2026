from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from fda_510k.config import settings
from fda_510k.models.gap import GapSeverity
from fda_510k.models.profile import SubmissionProfile


@dataclass
class ChecklistField:
    id: str
    label: str
    profile_field: str
    severity: GapSeverity
    section_id: str
    section_label: str
    condition: str | None = None
    notes: str | None = None


def load_estar_checklist(path: Path | None = None) -> list[ChecklistField]:
    checklist_path = path or settings.data_dir / "estar_checklist_nivd.yaml"
    with checklist_path.open() as f:
        data = yaml.safe_load(f)

    fields: list[ChecklistField] = []
    for section in data.get("sections", []):
        for field in section.get("fields", []):
            fields.append(
                ChecklistField(
                    id=field["id"],
                    label=field["label"],
                    profile_field=field["profile_field"],
                    severity=GapSeverity(field["severity"]),
                    section_id=section["id"],
                    section_label=section["label"],
                    condition=field.get("condition"),
                    notes=field.get("notes"),
                )
            )
    return fields


def evaluate_device_conditions(profile: SubmissionProfile) -> dict[str, bool]:
    software = bool(profile.software_present.value)
    patient_contact = bool(profile.patient_contact.value)
    electrical = bool(profile.electrical_powered.value) or bool(
        profile.energy_source.value and "battery" in str(profile.energy_source.value).lower()
    )
    sterilization_needed = bool(
        profile.sterilization.value
        or (
            profile.materials.value
            and any("implant" in m.lower() for m in profile.materials.value)
        )
    )

    return {
        "requires_software_section": software,
        "requires_biocompat": patient_contact,
        "requires_emc": electrical,
        "requires_sterilization": sterilization_needed,
    }
