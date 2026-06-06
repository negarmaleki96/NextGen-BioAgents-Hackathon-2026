from pathlib import Path

from fda_510k.ingestion.parsers.base import BaseParser, ParsedPage, ParserResult


class TextParser(BaseParser):
    extensions = (".txt", ".md", ".markdown", ".csv", ".log")

    def parse(self, path: Path) -> ParserResult:
        text = path.read_text(encoding="utf-8", errors="replace")
        return ParserResult(pages=[ParsedPage(page_number=None, text=text)])
