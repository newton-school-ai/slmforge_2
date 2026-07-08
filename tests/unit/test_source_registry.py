import pytest
from slmforge.data.sources import (
    get_source_class,
    SyntheticSource,
    PublicHFSource,
    LocalSource,
    InternalSource,
)


def test_registry_resolves_correct_adapters() -> None:
    assert get_source_class("synthetic") is SyntheticSource
    assert get_source_class("public") is PublicHFSource
    assert get_source_class("local") is LocalSource
    assert get_source_class("internal") is InternalSource


def test_registry_rejects_unknown_source_type() -> None:
    with pytest.raises(ValueError) as excinfo:
        get_source_class("unknown_type")
    assert "Unknown source type" in str(excinfo.value)


def test_internal_raises_not_implemented_error() -> None:
    internal = InternalSource()
    with pytest.raises(NotImplementedError) as excinfo:
        internal.iter_records()
    assert "Internal sources are not yet implemented" in str(excinfo.value)

    with pytest.raises(NotImplementedError) as excinfo:
        internal.metadata()
    assert "Internal sources are not yet implemented" in str(excinfo.value)


def test_all_adapters_yield_same_record_shape() -> None:
    # Instantiate concrete adapters with dummy values
    synthetic = SyntheticSource(generator="dummy_gen", size=5, seed=42)
    public = PublicHFSource(dataset_id="dummy_hf")
    local = LocalSource(path="/dummy/path")

    expected_keys = {"instruction", "input", "output"}

    for adapter in [synthetic, public, local]:
        records = list(adapter.iter_records())
        assert len(records) > 0
        for record in records:
            assert isinstance(record, dict)
            assert set(record.keys()) == expected_keys
            for key in expected_keys:
                assert isinstance(record[key], str)


def test_synthetic_source_honors_size() -> None:
    size = 12
    synthetic = SyntheticSource(generator="dummy_gen", size=size)
    records = list(synthetic.iter_records())
    assert len(records) == size
