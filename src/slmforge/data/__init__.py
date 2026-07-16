# Package initialization for slmforge.data
from slmforge.data.ingest import detect_format, ingest_path
from slmforge.data.preview import preview_source
from slmforge.data.builder import DatasetBuilder
from slmforge.data.card import generate_card
from slmforge.data.source_guard import validate
from slmforge.data.prefetch import prefetch

__all__ = [
    "detect_format",
    "ingest_path",
    "preview_source",
    "DatasetBuilder",
    "generate_card",
    "validate",
    "prefetch",
]
