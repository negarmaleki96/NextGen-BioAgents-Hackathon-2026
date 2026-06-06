from __future__ import annotations

from pathlib import Path

from fda_510k.ingestion.parsers.base import BaseParser
from fda_510k.ingestion.parsers.docx_parser import DocxParser
from fda_510k.ingestion.parsers.json_parser import JsonParser
from fda_510k.ingestion.parsers.pdf_parser import PdfParser
from fda_510k.ingestion.parsers.pptx_parser import PptxParser
from fda_510k.ingestion.parsers.text_parser import TextParser
from fda_510k.ingestion.parsers.xlsx_parser import XlsxParser
from fda_510k.ingestion.parsers.zip_parser import ZipParser


class ParserRegistry:
    def __init__(self, parsers: list[BaseParser] | None = None) -> None:
        self.parsers = parsers or [
            TextParser(),
            JsonParser(),
            PdfParser(),
            DocxParser(),
            PptxParser(),
            XlsxParser(),
            ZipParser(),
        ]

    def get_parser(self, path: Path) -> BaseParser | None:
        for parser in self.parsers:
            if parser.supports(path):
                return parser
        return None


_default_registry: ParserRegistry | None = None


def get_default_registry() -> ParserRegistry:
    global _default_registry
    if _default_registry is None:
        _default_registry = ParserRegistry()
    return _default_registry
