# Package initialization for slmforge.data
from slmforge.data.ingest import detect_format, ingest_path
from slmforge.data.preview import preview_source
from slmforge.data.builder import DatasetBuilder
from slmforge.data.card import generate_card

__all__ = [
    "detect_format",
    "ingest_path",
    "preview_source",
    "DatasetBuilder",
    "generate_card",
]
