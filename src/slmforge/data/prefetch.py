import os
import json
import datasets


def prefetch(dataset_id: str) -> str:
    """Prefetch a public Hugging Face dataset and cache it locally.

    Args:
        dataset_id: The Hugging Face dataset identifier.

    Returns:
        The directory path where the dataset is cached.
    """
    cache_dir = os.path.join("data", "cache", dataset_id)
    meta_path = os.path.join(cache_dir, "metadata.json")

    # If cache metadata exists, we can treat it as a no-op (cache hit)
    if os.path.exists(meta_path):
        return cache_dir

    # Download and cache dataset via datasets.load_dataset
    # Specifying cache_dir=cache_dir ensures cache is located inside data/cache/<dataset_id>
    ds = datasets.load_dataset(dataset_id, cache_dir=cache_dir)

    # Extract license metadata from dataset info
    license_str = "Unspecified"
    if hasattr(ds, "info") and getattr(ds.info, "license", None):
        license_str = str(ds.info.license)
    elif isinstance(ds, dict) and len(ds) > 0:
        first_split = list(ds.keys())[0]
        first_ds = ds[first_split]
        if hasattr(first_ds, "info") and getattr(first_ds.info, "license", None):
            license_str = str(first_ds.info.license)

    # Write metadata writeback
    os.makedirs(cache_dir, exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({"dataset_id": dataset_id, "license": license_str}, f, indent=2)

    return cache_dir
