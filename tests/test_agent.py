import pytest
from pathlib import Path

from fda_510k.agent.graph import build_graph, run_agent
from fda_510k.config import settings
from fda_510k.extraction.profile_extractor import ProfileExtractor
from fda_510k.ingestion.pipeline import IngestionPipeline

SAMPLES = Path(__file__).parent.parent / "data" / "samples"

pytestmark = pytest.mark.skipif(
    not settings.fda_510k_db_path.exists(),
    reason="510(k) database not imported",
)


def test_build_graph():
    app = build_graph()
    assert app is not None


def test_run_agent_with_text():
    output = run_agent(
        user_text=Path(SAMPLES / "glucose_monitor_notes.txt").read_text(),
    )
    assert output.submission_profile is not None
    assert output.gap_analysis
    assert output.disclaimers
    assert output.submission_package is not None
    assert output.submission_package.readiness_score >= 0.5


def test_heuristic_extraction_without_llm():
    pipeline = IngestionPipeline()
    doc = pipeline.ingest_text(
        Path(SAMPLES / "glucose_monitor_notes.txt").read_text(),
        doc_name="notes.txt",
    )
    extractor = ProfileExtractor(llm=type("MockLLM", (), {"is_available": lambda self: False})())
    profile = extractor.extract([doc], use_llm=True)
    assert profile.extraction_summary.missing_count >= 0
