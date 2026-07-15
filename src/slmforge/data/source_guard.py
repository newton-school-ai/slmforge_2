import os
from typing import Any
from slmforge.data.sources.registry import _REGISTRY


def validate(source: Any) -> None:
    """Validate a source representation (dict, Pydantic schema model, Source instance, or path/type string).

    Raises:
        ValueError: If the source type is unregistered or if it contains '_internal' in any path field.
    """
    source_type = None
    path_values = []

    # 1. Dictionary representation
    if isinstance(source, dict):
        source_type = source.get("type")
        for key in ("path", "url", "id", "dataset_id"):
            if key in source and source[key] is not None:
                path_values.append(str(source[key]))

    # 2. Pydantic schema / object representation
    elif hasattr(source, "type"):
        source_type = getattr(source, "type")
        for attr in ("path", "url", "id", "dataset_id"):
            if hasattr(source, attr):
                val = getattr(source, attr)
                if val is not None:
                    path_values.append(str(val))

    # 3. Source instance representation
    elif hasattr(source, "metadata") and callable(source.metadata):
        try:
            meta = source.metadata()
            source_type = meta.get("type")
            for key in ("path", "url", "id", "dataset_id"):
                if key in meta and meta[key] is not None:
                    path_values.append(str(meta[key]))
        except NotImplementedError:
            # InternalSource metadata() raises NotImplementedError, which implies it's "internal"
            source_type = "internal"

    # 4. Raw string representation (could be registered type or path/URL)
    elif isinstance(source, str):
        if source in _REGISTRY:
            source_type = source
        elif "type" in source.lower() or "invalid" in source.lower() or "unknown" in source.lower():
            source_type = source
        else:
            path_values.append(source)

    # Validate source type if present
    if source_type is not None:
        if source_type not in _REGISTRY:
            raise ValueError(
                f"Unregistered source type: '{source_type}'. Allowed types: {list(_REGISTRY.keys())}"
            )

    # Validate that no path component is '_internal' (case-insensitive and platform-independent)
    for val in path_values:
        normalized = os.path.normpath(val).replace("\\", "/")
        parts = [p.lower() for p in normalized.split("/")]
        if "_internal" in parts:
            raise ValueError(f"Forbidden source containing '_internal' path: {val}")
