import pytest
from pathlib import Path

from fda_510k.config import settings
from fda_510k.knowledge.db_510k import Device510kRepository
from fda_510k.models.common import ExtractedField, FieldProvenance
from fda_510k.models.profile import SubmissionProfile
from fda_510k.tools.search_510k_db import search_predicates
from fda_510k.tools.validate_predicate import validate_predicate

pytestmark = pytest.mark.skipif(
    not settings.fda_510k_db_path.exists(),
    reason="510(k) database not imported — run scripts/import_510k_db.py",
)


@pytest.fixture
def repo():
    r = Device510kRepository()
    yield r
    r.close()


def test_get_by_k_number(repo):
    # K912880 is from sample data in openFDA JSON
    rec = repo.get_by_k_number("K912880")
    assert rec is not None
    assert rec.k_number == "K912880"


def test_search_by_product_code(repo):
    results = repo.search(product_code="DQA", limit=5)
    assert len(results) > 0
    assert all(r.product_code == "DQA" for r in results)


def test_search_predicates(repo):
    profile = SubmissionProfile(
        device_trade_name=ExtractedField.from_value(
            "Oximeter",
            confidence=0.8,
            provenance=FieldProvenance.EXPLICIT,
        ),
        product_code=ExtractedField.from_value(
            "DQA",
            confidence=0.9,
            provenance=FieldProvenance.EXPLICIT,
        ),
    )
    candidates = search_predicates(profile, repo=repo, top_k=3)
    assert len(candidates) <= 3
    assert candidates[0].rank_score > 0


def test_validate_predicate_k_number(repo):
    result = validate_predicate("K912880", repo=repo)
    assert result is not None
    assert result.k_number == "K912880"
