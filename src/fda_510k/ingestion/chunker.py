from __future__ import annotations

from dataclasses import dataclass

from fda_510k.models.common import SourceRef


@dataclass
class DocumentChunk:
    text: str
    source_ref: SourceRef
    chunk_index: int


def chunk_text(
    text: str,
    *,
    doc_id: str,
    doc_name: str,
    page: int | None = None,
    chunk_size: int = 1500,
    overlap: int = 200,
) -> list[DocumentChunk]:
    text = text.strip()
    if not text:
        return []

    chunks: list[DocumentChunk] = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        snippet = text[start:end]
        chunks.append(
            DocumentChunk(
                text=snippet,
                source_ref=SourceRef(
                    doc_id=doc_id,
                    doc_name=doc_name,
                    page=page,
                    snippet=snippet[:200],
                ),
                chunk_index=idx,
            )
        )
        if end >= len(text):
            break
        start = end - overlap
        idx += 1
    return chunks
