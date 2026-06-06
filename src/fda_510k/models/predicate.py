from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class PredicateCandidate(BaseModel):
    k_number: str
    device_name: str
    applicant: str
    product_code: str
    regulation_number: str | None = None
    device_class: str | None = None
    advisory_committee: str | None = None
    decision_date: date | None = None
    decision_code: str | None = None
    statement_or_summary: str | None = None
    rank_score: float = 0.0
    rank_rationale: str = ""
    risks: list[str] = Field(default_factory=list)
    similarity_signals: dict[str, float] = Field(default_factory=dict)


class SEComparisonRow(BaseModel):
    characteristic: str
    subject_device: str
    predicate_device: str
    comparison_notes: str = ""
    raises_different_questions: bool = False


class SEComparison(BaseModel):
    predicate_k_number: str
    predicate_device_name: str
    rows: list[SEComparisonRow] = Field(default_factory=list)
    narrative_draft: str = ""
    confidence_notes: list[str] = Field(default_factory=list)
