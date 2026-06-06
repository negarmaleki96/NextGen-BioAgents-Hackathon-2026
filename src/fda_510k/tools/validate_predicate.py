from __future__ import annotations

import re

from fda_510k.knowledge.db_510k import Device510kRepository
from fda_510k.models.predicate import PredicateCandidate


def _normalize_k_number(value: str) -> str:
    value = value.strip().upper()
    if re.match(r"^K\d+$", value):
        return value
    if re.match(r"^\d+$", value):
        return f"K{value}"
    return value


def validate_predicate(
    mention: str,
    repo: Device510kRepository | None = None,
) -> PredicateCandidate | None:
    repo = repo or Device510kRepository()
    mention = mention.strip()

    k_match = re.search(r"K\d{5,7}", mention.upper())
    if k_match:
        rec = repo.get_by_k_number(k_match.group())
        if rec:
            return PredicateCandidate(
                k_number=rec.k_number,
                device_name=rec.device_name,
                applicant=rec.applicant,
                product_code=rec.product_code,
                regulation_number=rec.regulation_number,
                device_class=rec.device_class,
                advisory_committee=rec.advisory_committee,
                decision_date=rec.decision_date,
                decision_code=rec.decision_code,
                statement_or_summary=rec.statement_or_summary,
                rank_score=1.0,
                rank_rationale="User-specified K-number validated in openFDA database",
                risks=["Verify SE relevance to subject device"],
            )
        return None

    results = repo.search_by_name_fuzzy(mention, limit=1)
    if results:
        rec, score = results[0]
        return PredicateCandidate(
            k_number=rec.k_number,
            device_name=rec.device_name,
            applicant=rec.applicant,
            product_code=rec.product_code,
            regulation_number=rec.regulation_number,
            device_class=rec.device_class,
            advisory_committee=rec.advisory_committee,
            decision_date=rec.decision_date,
            decision_code=rec.decision_code,
            statement_or_summary=rec.statement_or_summary,
            rank_score=score,
            rank_rationale=f"Matched user mention '{mention}' by device name",
            risks=["Confirm this is the intended predicate device"],
        )
    return None
