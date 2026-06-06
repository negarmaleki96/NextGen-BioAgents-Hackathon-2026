from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from fda_510k.models.common import SourceRef


class GapSeverity(str, Enum):
    BLOCKER = "blocker"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


class GapItem(BaseModel):
    estar_section_id: str
    field_id: str
    label: str
    severity: GapSeverity
    status: Literal["missing", "weak", "present"]
    source_refs: list[SourceRef] = Field(default_factory=list)
    draft_available: bool = False
    notes: str | None = None
