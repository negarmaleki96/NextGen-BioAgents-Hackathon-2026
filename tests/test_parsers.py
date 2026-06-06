from pathlib import Path

from fda_510k.ingestion.pipeline import IngestionPipeline

FIXTURES = Path(__file__).parent / "fixtures"
SAMPLES = Path(__file__).parent.parent / "data" / "samples"


def test_ingest_text():
    pipeline = IngestionPipeline()
    doc = pipeline.ingest_text("Test device for glucose monitoring.", doc_name="notes.txt")
    assert doc.chunks
    assert "glucose" in doc.raw_text.lower()


def test_ingest_txt_file():
    pipeline = IngestionPipeline()
    path = FIXTURES / "sample_notes.txt"
    doc = pipeline.ingest_file(path)
    assert doc.doc_name == "sample_notes.txt"
    assert "SpO2" in doc.raw_text


def test_ingest_sample_notes():
    pipeline = IngestionPipeline()
    path = SAMPLES / "glucose_monitor_notes.txt"
    doc = pipeline.ingest_file(path)
    assert "GlucoTrack" in doc.raw_text
    assert len(doc.chunks) >= 1
