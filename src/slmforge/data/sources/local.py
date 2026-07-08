import os
from typing import Iterator, Dict, Any
from slmforge.data.sources.base import Source
from slmforge.data.ingest import ingest_path


class LocalSource(Source):
    """Adapter for local data files or directories."""

    def __init__(self, path: str) -> None:
        self.path = path

    def iter_records(self) -> Iterator[Dict[str, Any]]:
        if os.path.exists(self.path):
            yield from ingest_path(self.path)
        else:
            # Dummy records for scaffolding/tests
            for i in range(3):
                yield {
                    "instruction": f"Local instruction {i} from {self.path}",
                    "input": f"Local input {i}",
                    "output": f"Local output {i}",
                }

    def metadata(self) -> Dict[str, Any]:
        return {
            "type": "local",
            "path": self.path,
        }
