import os
import json
from unittest.mock import MagicMock, patch
from slmforge.data.prefetch import prefetch
from slmforge.data.sources.public import PublicHFSource


def test_prefetch_basic(tmp_path, monkeypatch):
    # Change current working directory to a tmp_path to avoid polluting the workspace
    monkeypatch.chdir(tmp_path)

    # Mock datasets.load_dataset
    mock_ds = MagicMock()
    mock_ds.info.license = "MIT"

    with patch("datasets.load_dataset", return_value=mock_ds) as mock_load:
        cache_dir = prefetch("test_dataset")

        # Verify load_dataset was called with correct args
        mock_load.assert_called_once_with(
            "test_dataset", cache_dir=os.path.join("data", "cache", "test_dataset")
        )

        # Verify metadata.json was written
        meta_path = os.path.join(cache_dir, "metadata.json")
        assert os.path.exists(meta_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            assert meta["dataset_id"] == "test_dataset"
            assert meta["license"] == "MIT"

        # Test subsequent call is a no-op (doesn't call datasets.load_dataset again)
        mock_load.reset_mock()
        cache_dir2 = prefetch("test_dataset")
        assert cache_dir2 == cache_dir
        mock_load.assert_not_called()


def test_prefetch_missing_license(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    mock_ds = MagicMock()
    # Mocking info to not have license
    del mock_ds.info.license

    with patch("datasets.load_dataset", return_value=mock_ds):
        cache_dir = prefetch("test_dataset_no_license")
        meta_path = os.path.join(cache_dir, "metadata.json")
        assert os.path.exists(meta_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            assert meta["license"] == "Unspecified"


def test_public_hf_source_reads_from_cache(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    dataset_id = "test_cached_ds"
    cache_dir = os.path.join("data", "cache", dataset_id)
    os.makedirs(cache_dir, exist_ok=True)

    # Write mock metadata.json
    with open(os.path.join(cache_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump({"dataset_id": dataset_id, "license": "Creative-Commons-BY-4.0"}, f)

    # Check PublicHFSource metadata
    source = PublicHFSource(dataset_id=dataset_id)
    metadata = source.metadata()
    assert metadata["license"] == "Creative-Commons-BY-4.0"

    # Check that generate_card displays the cached license
    from slmforge.data.card import get_source_license

    assert get_source_license(source) == "Creative-Commons-BY-4.0"


def test_public_hf_source_iter_records_cached(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    dataset_id = "test_cached_ds"
    cache_dir = os.path.join("data", "cache", dataset_id)
    os.makedirs(cache_dir, exist_ok=True)

    # Write mock metadata.json
    with open(os.path.join(cache_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump({"dataset_id": dataset_id, "license": "MIT"}, f)

    # Mock records in dataset
    mock_records = [
        {"instruction": "Hi", "input": "there", "output": "friend"},
        {"instruction": "Bye", "input": "now", "output": "buddy"},
    ]

    # We mock datasets.load_dataset to return a mock DatasetDict or Dataset
    mock_ds = {"train": mock_records}

    source = PublicHFSource(dataset_id=dataset_id)
    with patch("datasets.load_dataset", return_value=mock_ds) as mock_load:
        records = list(source.iter_records())
        mock_load.assert_called_once_with(dataset_id, cache_dir=cache_dir)
        assert len(records) == 2
        assert records[0] == {"instruction": "Hi", "input": "there", "output": "friend"}
        assert records[1] == {"instruction": "Bye", "input": "now", "output": "buddy"}


def test_public_hf_source_iter_records_fallback(tmp_path, monkeypatch):
    # No cache directory exists
    monkeypatch.chdir(tmp_path)

    source = PublicHFSource(dataset_id="non_existent_cache")
    records = list(source.iter_records())
    # Should fallback to 3 dummy records
    assert len(records) == 3
    assert records[0]["instruction"] == "Public HF instruction 0 from non_existent_cache"
