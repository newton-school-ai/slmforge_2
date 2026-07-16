import os
import json
from typing import Iterator, Dict, Any
import datasets
from slmforge.data.sources.base import Source
from slmforge.data.ingest import normalize_record


class PublicHFSource(Source):
    """Adapter for public Hugging Face datasets."""

    def __init__(self, dataset_id: str) -> None:
        self.dataset_id = dataset_id

    def iter_records(self) -> Iterator[Dict[str, Any]]:
        cache_dir = os.path.join("data", "cache", self.dataset_id)
        if os.path.exists(cache_dir):
            try:
                ds = datasets.load_dataset(self.dataset_id, cache_dir=cache_dir)
                if isinstance(ds, dict):
                    split = None
                    if "train" in ds:
                        split = "train"
                    elif len(ds) > 0:
                        split = list(ds.keys())[0]
                    if split is not None:
                        for raw_record in ds[split]:
                            yield normalize_record(raw_record)
                        return
                else:
                    for raw_record in ds:
                        yield normalize_record(raw_record)
                    return
            except Exception:
                pass

        # Fallback dummy records for scaffolding
        for i in range(3):
            yield {
                "instruction": f"Public HF instruction {i} from {self.dataset_id}",
                "input": f"Public HF input {i}",
                "output": f"Public HF output {i}",
            }

    def metadata(self) -> Dict[str, Any]:
        meta = {
            "type": "public",
            "dataset_id": self.dataset_id,
        }
        meta_path = os.path.join("data", "cache", self.dataset_id, "metadata.json")
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    cached_meta = json.load(f)
                    if "license" in cached_meta and cached_meta["license"]:
                        meta["license"] = cached_meta["license"]
            except Exception:
                pass
        return meta
