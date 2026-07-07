from typing import Iterator, Dict, Any
from slmforge.data.sources.base import Source


class InternalSource(Source):
    """Stub adapter for future internal/NST data sources."""

    def __init__(self) -> None:
        pass

    def iter_records(self) -> Iterator[Dict[str, Any]]:
        raise NotImplementedError("Internal sources are not yet implemented in SLMForge.")

    def metadata(self) -> Dict[str, Any]:
        raise NotImplementedError("Internal sources are not yet implemented in SLMForge.")
