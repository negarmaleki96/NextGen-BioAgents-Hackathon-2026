from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from fda_510k.models.common import ExtractedField


class InputManifestItem(BaseModel):
    doc_id: str
    doc_name: str
    content_type: str
    size_bytes: int


class ExtractionSummary(BaseModel):
    explicit_count: int = 0
    inferred_count: int = 0
    missing_count: int = 0


class SubmissionProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    input_manifest: list[InputManifestItem] = Field(default_factory=list)
    extraction_summary: ExtractionSummary = Field(default_factory=ExtractionSummary)

    # Identity
    device_trade_name: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    device_common_name: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    model_numbers: ExtractedField[list[str]] = Field(default_factory=ExtractedField.missing)

    # Classification
    product_code: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    regulation_number: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    device_class: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    advisory_committee: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    submission_type: ExtractedField[str] = Field(default_factory=ExtractedField.missing)

    # Intended use
    indications_for_use: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    intended_use_population: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    intended_use_environment: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    contraindications: ExtractedField[str] = Field(default_factory=ExtractedField.missing)

    # Technology
    principle_of_operation: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    energy_source: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    materials: ExtractedField[list[str]] = Field(default_factory=ExtractedField.missing)
    software_present: ExtractedField[bool] = Field(default_factory=ExtractedField.missing)
    cybersecurity_features: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    sterilization: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    shelf_life: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    components_accessories: ExtractedField[str] = Field(default_factory=ExtractedField.missing)

    # Predicate hints
    user_predicate_mentions: ExtractedField[list[str]] = Field(default_factory=ExtractedField.missing)
    competitive_devices: ExtractedField[list[str]] = Field(default_factory=ExtractedField.missing)

    # Testing
    bench_testing: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    biocompatibility: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    emc: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    software_vv: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    clinical_data: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    risk_analysis: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    design_controls: ExtractedField[str] = Field(default_factory=ExtractedField.missing)

    # Labeling
    labeling_draft: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    ifu_draft: ExtractedField[str] = Field(default_factory=ExtractedField.missing)

    # Standards & administrative
    consensus_standards_cited: ExtractedField[list[str]] = Field(default_factory=ExtractedField.missing)
    applicant_name: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    contact: ExtractedField[str] = Field(default_factory=ExtractedField.missing)
    manufacturing_sites: ExtractedField[str] = Field(default_factory=ExtractedField.missing)

    # Device signals for conditional sections
    patient_contact: ExtractedField[bool] = Field(default_factory=ExtractedField.missing)
    electrical_powered: ExtractedField[bool] = Field(default_factory=ExtractedField.missing)

    def iter_fields(self) -> list[tuple[str, ExtractedField[Any]]]:
        return [
            (name, getattr(self, name))
            for name in SubmissionProfile.model_fields
            if name not in {"profile_id", "created_at", "input_manifest", "extraction_summary"}
        ]

    def recompute_summary(self) -> None:
        explicit = inferred = missing = 0
        for _, field in self.iter_fields():
            if field.provenance.value == "explicit":
                explicit += 1
            elif field.provenance.value == "inferred":
                inferred += 1
            else:
                missing += 1
        self.extraction_summary = ExtractionSummary(
            explicit_count=explicit,
            inferred_count=inferred,
            missing_count=missing,
        )
