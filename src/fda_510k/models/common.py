from __future__ import annotations

from enum import Enum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class FieldProvenance(str, Enum):
    EXPLICIT = "explicit"
    INFERRED = "inferred"
    MISSING = "missing"


class SourceRef(BaseModel):
    doc_id: str
    doc_name: str
    page: int | None = None
    snippet: str | None = None


class ExtractedField(BaseModel, Generic[T]):
    value: T | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    provenance: FieldProvenance = FieldProvenance.MISSING
    source_refs: list[SourceRef] = Field(default_factory=list)
    notes: str | None = None

    @classmethod
    def missing(cls) -> "ExtractedField[T]":
        return cls(provenance=FieldProvenance.MISSING)

    @classmethod
    def from_value(
        cls,
        value: T,
        *,
        confidence: float,
        provenance: FieldProvenance,
        source_refs: list[SourceRef] | None = None,
        notes: str | None = None,
    ) -> "ExtractedField[T]":
        return cls(
            value=value,
            confidence=confidence,
            provenance=provenance,
            source_refs=source_refs or [],
            notes=notes,
        )
