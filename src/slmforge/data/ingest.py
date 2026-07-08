import os
import json
import csv
import math
from typing import Iterator, Dict, Any

try:
    import magic
except ImportError:
    magic = None


def is_nan(val: Any) -> bool:
    """Check if a value is a float NaN."""
    try:
        return isinstance(val, float) and math.isnan(val)
    except Exception:
        return False


def normalize_record(raw_record: Dict[str, Any]) -> Dict[str, str]:
    """Normalize a raw record dictionary to a standardized shape:
    {
        "instruction": str,
        "input": str,
        "output": str
    }
    """
    normalized = {"instruction": "", "input": "", "output": ""}

    # Try to extract the canonical fields case-insensitively
    for key in ["instruction", "input", "output"]:
        found_val = None
        found = False
        for k, v in raw_record.items():
            if k.lower() == key:
                found_val = v
                found = True
                break

        if found:
            if found_val is None or is_nan(found_val):
                normalized[key] = ""
            else:
                normalized[key] = str(found_val)
        else:
            normalized[key] = ""

    # Fallback heuristics: If the record has no values for the canonical keys,
    # try to map fields like "text", "prompt", "content", etc., to "instruction".
    if not normalized["instruction"] and not normalized["input"] and not normalized["output"]:
        text_keys = ["text", "prompt", "content", "story", "document"]
        for tk in text_keys:
            found_val = None
            found = False
            for k, v in raw_record.items():
                if k.lower() == tk:
                    found_val = v
                    found = True
                    break
            if found:
                if found_val is not None and not is_nan(found_val):
                    normalized["instruction"] = str(found_val)
                break

        # If still empty, fall back to the first non-empty field
        if not normalized["instruction"] and raw_record:
            for k, v in raw_record.items():
                if v is not None and not is_nan(v):
                    normalized["instruction"] = str(v)
                    break

    return normalized


def detect_format(path: str) -> str:
    """Detect the format of the file or directory.
    Returns one of: 'jsonl', 'csv', 'parquet', 'txt-folder'.
    Raises FileNotFoundError if the path doesn't exist.
    Raises ValueError if the format cannot be determined.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path does not exist: {path}")

    if os.path.isdir(path):
        return "txt-folder"

    # Check Parquet file signature (first 4 bytes must be PAR1)
    try:
        with open(path, "rb") as f:
            header = f.read(4)
            if header == b"PAR1":
                return "parquet"
    except Exception:
        pass

    # Use python-magic to detect mime type
    mime = ""
    try:
        mime = magic.from_file(path, mime=True)
    except Exception:
        pass

    if mime:
        if "parquet" in mime:
            return "parquet"
        if mime == "text/csv":
            return "csv"
        if mime in ("application/json", "application/x-jsonlines", "application/jsonlines"):
            return "jsonl"

    # Read first non-empty line of the file to guess text format
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            first_line = ""
            for line in f:
                if line.strip():
                    first_line = line.strip()
                    break

            if first_line:
                # Try parsing as JSON (JSONL starts with a JSON object/list)
                try:
                    json.loads(first_line)
                    return "jsonl"
                except json.JSONDecodeError:
                    pass

                # Try parsing as CSV
                try:
                    reader = csv.reader([first_line])
                    row = next(reader)
                    if len(row) > 1:
                        return "csv"
                except Exception:
                    pass
    except Exception:
        pass

    # Fallback to extension check
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return "csv"
    elif ext in (".jsonl", ".json"):
        return "jsonl"
    elif ext == ".parquet":
        return "parquet"

    raise ValueError(f"Could not determine format for path: {path}")


def read_jsonl(path: str) -> Iterator[Dict[str, str]]:
    """Yield normalized records from a JSONL file."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                raw_record = json.loads(line)
                if isinstance(raw_record, dict):
                    yield normalize_record(raw_record)
            except Exception:
                pass


def read_csv(path: str) -> Iterator[Dict[str, str]]:
    """Yield normalized records from a CSV file."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        # Detect delimiter using sniffer
        sample = f.read(2048)
        f.seek(0)

        delimiter = ","
        if sample:
            try:
                dialect = csv.Sniffer().sniff(sample)
                delimiter = dialect.delimiter
            except Exception:
                pass

        reader = csv.DictReader(f, delimiter=delimiter)
        for row in reader:
            yield normalize_record(row)


def read_parquet(path: str) -> Iterator[Dict[str, str]]:
    """Yield normalized records from a Parquet file using pandas."""
    import pandas as pd

    df = pd.read_parquet(path)
    for _, row in df.iterrows():
        yield normalize_record(row.to_dict())


def read_txt_folder(path: str) -> Iterator[Dict[str, str]]:
    """Yield normalized records from a directory of .txt files."""
    if not os.path.isdir(path):
        raise ValueError(f"Not a directory: {path}")

    filenames = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".txt"):
                filenames.append(os.path.join(root, file))

    # Sort files for deterministic results
    filenames.sort()
    for filepath in filenames:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                yield {"instruction": content, "input": "", "output": ""}
        except Exception:
            pass


def ingest_path(path: str) -> Iterator[Dict[str, str]]:
    """Automatically detect the format of path and stream normalized records."""
    fmt = detect_format(path)
    if fmt == "jsonl":
        yield from read_jsonl(path)
    elif fmt == "csv":
        yield from read_csv(path)
    elif fmt == "parquet":
        yield from read_parquet(path)
    elif fmt == "txt-folder":
        yield from read_txt_folder(path)
    else:
        raise ValueError(f"Unsupported format: {fmt}")
