from typing import Iterator, Dict, Any, Optional
from slmforge.data.sources.base import Source


class SyntheticSource(Source):
    """Adapter for generating synthetic dataset records."""

    def __init__(self, generator: str, size: int, seed: Optional[int] = None) -> None:
        self.generator = generator
        self.size = size
        self.seed = seed

    def iter_records(self) -> Iterator[Dict[str, Any]]:
        for i in range(self.size):
            yield {
                "instruction": f"Synthetic instruction {i} from {self.generator}",
                "input": f"Synthetic input {i} (seed={self.seed})",
                "output": f"Synthetic output {i}",
            }

    def metadata(self) -> Dict[str, Any]:
        return {
            "type": "synthetic",
            "generator": self.generator,
            "size": self.size,
            "seed": self.seed,
        }
