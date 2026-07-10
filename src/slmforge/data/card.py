from typing import List, Dict, Any
import datasets
from slmforge.data.sources.base import Source


def get_source_license(source: Source) -> str:
    """Determine the licence of a data source from attributes, metadata, or defaults."""
    for attr in ("licence", "license"):
        if hasattr(source, attr):
            val = getattr(source, attr)
            if val:
                return str(val)

    try:
        meta = source.metadata()
    except NotImplementedError:
        return "Proprietary"

    for key in ("licence", "license"):
        if key in meta and meta[key]:
            return str(meta[key])

    stype = meta.get("type", "unknown")
    if stype == "synthetic":
        return "Pod-authored"
    elif stype == "public":
        return "Apache-2.0"
    elif stype == "local":
        return "Proprietary"
    elif stype == "internal":
        return "Proprietary"

    return "Unspecified"


def format_size(size: int, metadata: Dict[str, Any]) -> str:
    """Format size cleanly (e.g. 20k or 20k (seed=42))."""
    if size >= 1000 and size % 1000 == 0:
        size_str = f"{size // 1000}k"
    else:
        size_str = str(size)

    if metadata.get("type") == "synthetic" and metadata.get("seed") is not None:
        return f"{size_str} (seed={metadata['seed']})"
    return size_str


def generate_card(
    build_id: str,
    sources: List[Source],
    dataset_dict: datasets.DatasetDict,
    seed: int = 42,
) -> str:
    """Generate the markdown content of the dataset card for a build."""
    table_rows = []
    for source in sources:
        try:
            meta = source.metadata()
            stype = meta.get("type", "unknown")
        except NotImplementedError:
            meta = {"type": "internal"}
            stype = "internal"

        # Identify target identifier field
        if stype == "local":
            identifier = meta.get("path", "unknown")
        elif stype == "public":
            identifier = meta.get("dataset_id", "unknown")
        elif stype == "synthetic":
            identifier = meta.get("generator", "unknown")
        else:
            identifier = "internal"

        # Count records
        try:
            if stype == "internal":
                size_val = 0
            else:
                size_val = len(list(source.iter_records()))
        except (NotImplementedError, Exception):
            size_val = 0

        licence = get_source_license(source)
        size_formatted = format_size(size_val, meta)

        table_rows.append(f"| {stype} | {identifier} | {size_formatted} | {licence} |")

    sources_table = "\n".join(table_rows)

    card_content = f"""# Dataset Card -- {build_id}

## Sources
| Type | Identifier | Size | Licence |
|------|-----------|------|---------|
{sources_table}

## Splits
- Train: 80%
- Val: 10%
- Held-out eval: 10% (seeded, frozen)

## Schema
```json
{{"instruction": "...", "input": "...", "output": "..."}}
```

## dePII
- Method:
- Manual spot-check sample size:
- Leaks found:

## Known limitations

## Citations
"""
    return card_content
