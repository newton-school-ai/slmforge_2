import random
from typing import List
import datasets
from slmforge.data.sources.base import Source


class DatasetBuilder:
    """Builder class to compile and split dataset records from various sources."""

    @staticmethod
    def build(sources: List[Source], seed: int = 42) -> datasets.DatasetDict:
        """Collects records from all sources, shuffles them with a seed, and splits them 80/10/10.

        Args:
            sources: List of data sources to fetch records from.
            seed: Seed used for deterministic shuffling.

        Returns:
            A datasets.DatasetDict containing 'train', 'val', and 'eval' splits.
        """
        combined_records = []
        for source in sources:
            combined_records.extend(list(source.iter_records()))

        N = len(combined_records)

        # 80% train, 10% val, 10% eval
        train_count = int(N * 0.8)
        val_count = int(N * 0.1)

        # Handle edge cases for small datasets (N >= 3) to ensure splits are non-empty
        if N >= 3:
            if val_count == 0:
                val_count = 1
                train_count -= 1
            eval_count = N - train_count - val_count
            if eval_count == 0:
                eval_count = 1
                train_count -= 1
        else:
            eval_count = N - train_count - val_count

        # Deterministically shuffle the combined records copy
        shuffled_records = list(combined_records)
        rng = random.Random(seed)
        rng.shuffle(shuffled_records)

        # Slice into splits
        train_records = shuffled_records[:train_count]
        val_records = shuffled_records[train_count : train_count + val_count]
        eval_records = shuffled_records[train_count + val_count :]

        # Convert to Hugging Face Dataset objects
        train_dataset = datasets.Dataset.from_list(train_records)
        val_dataset = datasets.Dataset.from_list(val_records)
        eval_dataset = datasets.Dataset.from_list(eval_records)

        return datasets.DatasetDict(
            {
                "train": train_dataset,
                "val": val_dataset,
                "eval": eval_dataset,
            }
        )
