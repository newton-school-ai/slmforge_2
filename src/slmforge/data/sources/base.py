from abc import ABC, abstractmethod
from typing import Iterator, Dict, Any


class Source(ABC):
    """Abstract Base Class representing a data source for fine-tuning.

    All custom and built-in source adapters must inherit from this class and
    implement the required methods.
    """

    @abstractmethod
    def iter_records(self) -> Iterator[Dict[str, Any]]:
        """Yield records from the data source.

        Each record yielded must be a dictionary representing a training/eval example.
        All concrete adapters must yield records of the same shape:
        {
            "instruction": str,
            "input": str,
            "output": str
        }
        """
        pass

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """Return a dictionary containing metadata about the source (e.g. source type, config)."""
        pass
