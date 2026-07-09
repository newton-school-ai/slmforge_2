# Package initialization for slmforge.data
from slmforge.data.ingest import detect_format, ingest_path
from slmforge.data.preview import preview_source

__all__ = [
    "detect_format",
    "ingest_path",
    "preview_source",
]
