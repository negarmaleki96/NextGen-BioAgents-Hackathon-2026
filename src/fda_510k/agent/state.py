from __future__ import annotations

from typing import Annotated, Optional, TypedDict

from fda_510k.ingestion.pipeline import ParsedDocument
from fda_510k.models.gap import GapItem
from fda_510k.models.output import (
    AgentOutput,
    ClarifyingQuestion,
    EstarDraft,
    FDAQuestion,
)
from fda_510k.models.predicate import PredicateCandidate, SEComparison
from fda_510k.models.profile import SubmissionProfile


def _merge_list(left: list, right: list) -> list:
    return left + right


class AgentState(TypedDict, total=False):
    user_text: str
    file_paths: list[str]
    clarifications: dict[str, str]
    parsed_docs: list[ParsedDocument]
    profile: SubmissionProfile
    gaps: list[GapItem]
    clarifying_questions: list[ClarifyingQuestion]
    predicate_candidates: list[PredicateCandidate]
    se_comparison: Optional[SEComparison]
    estar_drafts: list[EstarDraft]
    fda_questions: list[FDAQuestion]
    output: AgentOutput
    status_message: str
    errors: Annotated[list[str], _merge_list]
