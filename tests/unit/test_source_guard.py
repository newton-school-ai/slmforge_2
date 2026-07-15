import pytest
from slmforge.data import validate
from slmforge.data.sources import LocalSource, PublicHFSource, SyntheticSource, InternalSource
from slmforge.api.schemas import (
    LocalSource as LocalSourceSchema,
    PublicSource as PublicSourceSchema,
    SyntheticSource as SyntheticSourceSchema,
    InternalSource as InternalSourceSchema,
)


def test_validate_valid_sources():
    # Test valid dictionaries
    validate({"type": "local", "path": "/data/train.jsonl"})
    validate({"type": "public", "dataset_id": "cnn_dailymail"})
    validate({"type": "synthetic", "generator": "feedback_summariser"})

    # Test valid source adapter instances
    local_src = LocalSource(path="/data/train.jsonl")
    public_src = PublicHFSource(dataset_id="cnn_dailymail")
    synthetic_src = SyntheticSource(generator="feedback_summariser", size=100)
    internal_src = InternalSource()

    validate(local_src)
    validate(public_src)
    validate(synthetic_src)
    validate(internal_src)

    # Test valid schemas
    validate(LocalSourceSchema(path="/data/train.jsonl"))
    validate(PublicSourceSchema(id="cnn_dailymail"))
    validate(SyntheticSourceSchema(generator="feedback_summariser", size=100))
    validate(InternalSourceSchema())

    # Test valid string paths
    validate("/data/train.jsonl")
    validate("cnn_dailymail")


def test_validate_unregistered_type():
    with pytest.raises(ValueError) as excinfo:
        validate({"type": "unregistered_type"})
    assert "Unregistered source type" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        validate("unregistered_type")
    assert "Unregistered source type" in str(excinfo.value)


def test_validate_forbidden_internal_path():
    # Dicts
    with pytest.raises(ValueError) as excinfo:
        validate({"type": "local", "path": "_internal/leak/x.txt"})
    assert "Forbidden source containing '_internal' path" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        validate({"type": "local", "path": "/Users/kushal/Desktop/_internal/data.csv"})
    assert "Forbidden source containing '_internal' path" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        validate({"type": "public", "dataset_id": "sub/_internal/dataset"})
    assert "Forbidden source containing '_internal' path" in str(excinfo.value)

    # Source adapter instance
    bad_local = LocalSource(path="_internal/data.jsonl")
    with pytest.raises(ValueError) as excinfo:
        validate(bad_local)
    assert "Forbidden source containing '_internal' path" in str(excinfo.value)

    # Schema
    bad_schema = LocalSourceSchema(path="_internal/data.jsonl")
    with pytest.raises(ValueError) as excinfo:
        validate(bad_schema)
    assert "Forbidden source containing '_internal' path" in str(excinfo.value)

    # String path
    with pytest.raises(ValueError) as excinfo:
        validate("_internal/leak/x.txt")
    assert "Forbidden source containing '_internal' path" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo:
        validate("/Users/kushal/_internal/leak/x.txt")
    assert "Forbidden source containing '_internal' path" in str(excinfo.value)
