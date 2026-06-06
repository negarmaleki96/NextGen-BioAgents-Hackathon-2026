import json
from pathlib import Path

from fda_510k.ingestion.parsers.base import BaseParser, ParsedPage, ParserResult


class JsonParser(BaseParser):
    extensions = (".json",)

    def parse(self, path: Path) -> ParserResult:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        text = json.dumps(data, indent=2)
        return ParserResult(pages=[ParsedPage(page_number=None, text=text)])
