from typing import List, Dict, Any
from slmforge.data.ingest import ingest_path


def preview_source(path: str, n: int = 5) -> List[Dict[str, Any]]:
    """Return the first n records from the dataset at the given path.

    Each record in the returned list matches the normalized shape:
    {
        "instruction": str,
        "input": str,
        "output": str
    }
    """
    records = []
    try:
        stream = ingest_path(path)
        for i, record in enumerate(stream):
            if i >= n:
                break
            records.append(record)
    except Exception as e:
        raise e
    return records
