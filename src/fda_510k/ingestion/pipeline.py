from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

from fda_510k.config import settings
from fda_510k.ingestion.chunker import DocumentChunk, chunk_text
from fda_510k.ingestion.parsers.registry import get_default_registry
from fda_510k.models.profile import InputManifestItem


@dataclass
class ParsedDocument:
    doc_id: str
    doc_name: str
    content_type: str
    size_bytes: int
    chunks: list[DocumentChunk] = field(default_factory=list)
    raw_text: str = ""


class IngestionPipeline:
    def __init__(self, upload_dir: Path | None = None) -> None:
        self.upload_dir = upload_dir or settings.upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.registry = get_default_registry()

    def ingest_text(self, text: str, *, doc_name: str = "user_text") -> ParsedDocument:
        doc_id = str(uuid4())
        chunks = chunk_text(text, doc_id=doc_id, doc_name=doc_name)
        return ParsedDocument(
            doc_id=doc_id,
            doc_name=doc_name,
            content_type="text/plain",
            size_bytes=len(text.encode("utf-8")),
            chunks=chunks,
            raw_text=text,
        )

    def ingest_file(self, source_path: Path) -> ParsedDocument:
        doc_id = str(uuid4())
        dest = self.upload_dir / f"{doc_id}_{source_path.name}"
        shutil.copy2(source_path, dest)

        parser = self.registry.get_parser(source_path)
        if parser is None:
            text = source_path.read_text(encoding="utf-8", errors="replace")
            chunks = chunk_text(text, doc_id=doc_id, doc_name=source_path.name)
            return ParsedDocument(
                doc_id=doc_id,
                doc_name=source_path.name,
                content_type="application/octet-stream",
                size_bytes=source_path.stat().st_size,
                chunks=chunks,
                raw_text=text,
            )

        result = parser.parse(source_path)
        chunks: list[DocumentChunk] = []
        for page in result.pages:
            chunks.extend(
                chunk_text(
                    page.text,
                    doc_id=doc_id,
                    doc_name=source_path.name,
                    page=page.page_number,
                )
            )

        return ParsedDocument(
            doc_id=doc_id,
            doc_name=source_path.name,
            content_type=source_path.suffix,
            size_bytes=source_path.stat().st_size,
            chunks=chunks,
            raw_text=result.full_text,
        )

    def ingest_files(self, paths: list[Path], user_text: str | None = None) -> list[ParsedDocument]:
        docs: list[ParsedDocument] = []
        if user_text and user_text.strip():
            docs.append(self.ingest_text(user_text.strip()))
        for path in paths:
            docs.append(self.ingest_file(path))
        return docs

    @staticmethod
    def to_manifest(docs: list[ParsedDocument]) -> list[InputManifestItem]:
        return [
            InputManifestItem(
                doc_id=d.doc_id,
                doc_name=d.doc_name,
                content_type=d.content_type,
                size_bytes=d.size_bytes,
            )
            for d in docs
        ]
