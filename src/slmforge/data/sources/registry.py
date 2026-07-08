from typing import Dict, Type
from slmforge.data.sources.base import Source
from slmforge.data.sources.synthetic import SyntheticSource
from slmforge.data.sources.public import PublicHFSource
from slmforge.data.sources.local import LocalSource
from slmforge.data.sources.internal import InternalSource

_REGISTRY: Dict[str, Type[Source]] = {
    "synthetic": SyntheticSource,
    "public": PublicHFSource,
    "local": LocalSource,
    "internal": InternalSource,
}


def get_source_class(source_type: str) -> Type[Source]:
    """Retrieve the concrete source adapter class for the given source type.

    Args:
        source_type: The type label (e.g., 'synthetic', 'public', 'local', 'internal').

    Returns:
        The matching Source class.

    Raises:
        ValueError: If the source type is not registered.
    """
    if source_type not in _REGISTRY:
        raise ValueError(
            f"Unknown source type: '{source_type}'. Registered types: {list(_REGISTRY.keys())}"
        )
    return _REGISTRY[source_type]


def register_source(source_type: str, source_class: Type[Source]) -> None:
    """Register a new source type mapping to a Source adapter class.

    Args:
        source_type: The source type string.
        source_class: The subclass of Source to register.
    """
    if not issubclass(source_class, Source):
        raise TypeError("Registered class must be a subclass of Source.")
    _REGISTRY[source_type] = source_class
