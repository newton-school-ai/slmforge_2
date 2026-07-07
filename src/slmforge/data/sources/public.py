from typing import Iterator, Dict, Any
from slmforge.data.sources.base import Source


class PublicHFSource(Source):
    """Adapter for public Hugging Face datasets."""

    def __init__(self, dataset_id: str) -> None:
        self.dataset_id = dataset_id

    def iter_records(self) -> Iterator[Dict[str, Any]]:
        # Dummy records for scaffolding
        for i in range(3):
            yield {
                "instruction": f"Public HF instruction {i} from {self.dataset_id}",
                "input": f"Public HF input {i}",
                "output": f"Public HF output {i}",
            }

    def metadata(self) -> Dict[str, Any]:
        return {
            "type": "public",
            "dataset_id": self.dataset_id,
        }
