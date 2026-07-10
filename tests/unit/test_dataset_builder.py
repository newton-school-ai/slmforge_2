from slmforge.data import DatasetBuilder, generate_card
from slmforge.data.sources import SyntheticSource, LocalSource


def test_builder_splits_deterministic():
    # Arrange
    source1 = SyntheticSource(generator="gen1", size=10, seed=1)
    source2 = SyntheticSource(generator="gen2", size=10, seed=2)
    sources = [source1, source2]

    # Act
    dataset_dict_1 = DatasetBuilder.build(sources, seed=42)
    dataset_dict_2 = DatasetBuilder.build(sources, seed=42)
    dataset_dict_diff_seed = DatasetBuilder.build(sources, seed=99)

    # Assert
    # Check that identical seed produces identical splits
    for split in ["train", "val", "eval"]:
        assert len(dataset_dict_1[split]) == len(dataset_dict_2[split])
        for r1, r2 in zip(dataset_dict_1[split], dataset_dict_2[split]):
            assert r1 == r2

    # Check that different seed produces different splits (shuffling is different)
    # With 20 items, different seed should result in different order
    diff_order = False
    for split in ["train", "val", "eval"]:
        if len(dataset_dict_1[split]) > 0:
            for r1, r3 in zip(dataset_dict_1[split], dataset_dict_diff_seed[split]):
                if r1 != r3:
                    diff_order = True
                    break
    assert diff_order, "Shuffling with different seeds should produce different order."


def test_builder_split_ratios():
    # Arrange
    source = SyntheticSource(generator="ratio_gen", size=10, seed=1)

    # Act
    # N = 10: 80% is 8, 10% is 1, 10% is 1
    dd = DatasetBuilder.build([source], seed=42)

    # Assert
    assert len(dd["train"]) == 8
    assert len(dd["val"]) == 1
    assert len(dd["eval"]) == 1

    # N = 20: 80% is 16, 10% is 2, 10% is 2
    source_large = SyntheticSource(generator="ratio_gen", size=20, seed=1)
    dd_large = DatasetBuilder.build([source_large], seed=42)
    assert len(dd_large["train"]) == 16
    assert len(dd_large["val"]) == 2
    assert len(dd_large["eval"]) == 2

    # N = 2: train = 1, val = 0, eval = 1 (small dataset fallback)
    source_small = SyntheticSource(generator="ratio_gen", size=2, seed=1)
    dd_small = DatasetBuilder.build([source_small], seed=42)
    assert len(dd_small["train"]) == 1
    assert len(dd_small["val"]) == 0
    assert len(dd_small["eval"]) == 1


def test_builder_no_leak():
    # Arrange
    # Use distinct instructions in synthetic source to perform content set check
    source = SyntheticSource(generator="leak_gen", size=30, seed=42)

    # Act
    dd = DatasetBuilder.build([source], seed=42)

    # Get set of instructions in each split
    train_insts = set(record["instruction"] for record in dd["train"])
    val_insts = set(record["instruction"] for record in dd["val"])
    eval_insts = set(record["instruction"] for record in dd["eval"])

    # Assert
    # No leak: intersection of train and eval must be empty
    assert len(train_insts.intersection(eval_insts)) == 0
    assert len(train_insts.intersection(val_insts)) == 0
    assert len(val_insts.intersection(eval_insts)) == 0


def test_generate_card_format():
    # Arrange
    source_synth = SyntheticSource(generator="feedback_summariser", size=10, seed=42)
    # LocalSource returns 3 records from local.py dummy implementation
    source_local = LocalSource(path="/data/local_train.jsonl")

    # Set license on local source if possible to test override
    source_local.licence = "MIT"

    sources = [source_synth, source_local]
    dd = DatasetBuilder.build(sources, seed=42)

    # Act
    card_md = generate_card(
        build_id="build_2026_07_10_120000",
        sources=sources,
        dataset_dict=dd,
        seed=42,
    )

    # Assert
    # Verify section headings and table format
    assert "# Dataset Card -- build_2026_07_10_120000" in card_md
    assert "## Sources" in card_md
    assert "| Type | Identifier | Size | Licence |" in card_md
    assert "|------|-----------|------|---------|" in card_md

    # Check synthetic source row formatting (seed is included, default licence Pod-authored)
    assert "| synthetic | feedback_summariser | 10 (seed=42) | Pod-authored |" in card_md

    # Check local source row formatting (licence is custom MIT, size is 3)
    assert "| local | /data/local_train.jsonl | 3 | MIT |" in card_md

    # Check splits and schema
    assert "## Splits" in card_md
    assert "- Train: 80%" in card_md
    assert "- Val: 10%" in card_md
    assert "- Held-out eval: 10% (seeded, frozen)" in card_md
    assert "## Schema" in card_md
    assert '{"instruction": "...", "input": "...", "output": "..."}' in card_md
