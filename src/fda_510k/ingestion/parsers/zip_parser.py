import tempfile
import zipfile
from pathlib import Path

from fda_510k.ingestion.parsers.base import BaseParser, ParserResult


class ZipParser(BaseParser):
    extensions = (".zip",)

    def parse(self, path: Path) -> ParserResult:
        from fda_510k.ingestion.parsers.registry import get_default_registry

        registry = get_default_registry()
        combined_pages = []
        metadata: dict = {"nested_files": []}

        with zipfile.ZipFile(path, "r") as zf:
            with tempfile.TemporaryDirectory() as tmpdir:
                for name in zf.namelist():
                    if name.endswith("/"):
                        continue
                    extracted = Path(tmpdir) / Path(name).name
                    with zf.open(name) as src, extracted.open("wb") as dst:
                        dst.write(src.read())
                    parser = registry.get_parser(extracted)
                    if parser:
                        result = parser.parse(extracted)
                        for page in result.pages:
                            page.text = f"[{name}]\n{page.text}"
                            combined_pages.append(page)
                        metadata["nested_files"].append(name)

        return ParserResult(pages=combined_pages, metadata=metadata)
