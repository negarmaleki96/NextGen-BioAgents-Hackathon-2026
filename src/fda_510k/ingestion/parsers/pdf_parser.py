from pathlib import Path

import fitz

from fda_510k.ingestion.parsers.base import BaseParser, ParsedPage, ParserResult


class PdfParser(BaseParser):
    extensions = (".pdf",)

    def parse(self, path: Path) -> ParserResult:
        pages: list[ParsedPage] = []
        with fitz.open(path) as doc:
            for i, page in enumerate(doc):
                text = page.get_text("text")
                pages.append(ParsedPage(page_number=i + 1, text=text))
        return ParserResult(pages=pages, metadata={"page_count": len(pages)})
