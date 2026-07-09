import json
import csv
import pandas as pd
from slmforge.data import detect_format, ingest_path, preview_source
from slmforge.data.sources import LocalSource


def test_jsonl_ingestion(tmp_path):
    file_path = tmp_path / "test.jsonl"
    data = [
        {"instruction": "i1", "input": "in1", "output": "out1"},
        {"Instruction": "i2", "Input": "in2", "Output": "out2"},  # case insensitivity
        {"instruction": "i3"},  # missing keys
        {"text": "only text field"},  # fallback heuristic
        {"random_key": "some value"},  # first field fallback
    ]
    with open(file_path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

    records = list(ingest_path(str(file_path)))
    assert len(records) == 5

    assert records[0] == {"instruction": "i1", "input": "in1", "output": "out1"}
    assert records[1] == {"instruction": "i2", "input": "in2", "output": "out2"}
    assert records[2] == {"instruction": "i3", "input": "", "output": ""}
    assert records[3] == {"instruction": "only text field", "input": "", "output": ""}
    assert records[4] == {"instruction": "some value", "input": "", "output": ""}


def test_csv_ingestion(tmp_path):
    file_path = tmp_path / "test.csv"
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["instruction", "input", "output"])
        writer.writerow(["c1", "in1", "out1"])
        writer.writerow(["c2", "in2", "out2"])

    records = list(ingest_path(str(file_path)))
    assert len(records) == 2
    assert records[0] == {"instruction": "c1", "input": "in1", "output": "out1"}
    assert records[1] == {"instruction": "c2", "input": "in2", "output": "out2"}


def test_parquet_ingestion(tmp_path):
    file_path = tmp_path / "test.parquet"
    df = pd.DataFrame(
        [
            {"instruction": "p1", "input": "in1", "output": "out1"},
            {"instruction": "p2", "input": "in2", "output": "out2"},
        ]
    )
    df.to_parquet(file_path)

    records = list(ingest_path(str(file_path)))
    assert len(records) == 2
    assert records[0] == {"instruction": "p1", "input": "in1", "output": "out1"}
    assert records[1] == {"instruction": "p2", "input": "in2", "output": "out2"}


def test_txt_folder_ingestion(tmp_path):
    folder_path = tmp_path / "txt_files"
    folder_path.mkdir()

    with open(folder_path / "file1.txt", "w", encoding="utf-8") as f:
        f.write("Content of file 1")
    with open(folder_path / "file2.txt", "w", encoding="utf-8") as f:
        f.write("Content of file 2")
    # Subdir test
    subdir = folder_path / "sub"
    subdir.mkdir()
    with open(subdir / "file3.txt", "w", encoding="utf-8") as f:
        f.write("Content of file 3")

    records = list(ingest_path(str(folder_path)))
    assert len(records) == 3
    # Order should be alphabetical by filepath
    assert records[0]["instruction"] == "Content of file 1"
    assert records[1]["instruction"] == "Content of file 2"
    assert records[2]["instruction"] == "Content of file 3"


def test_format_detection_no_extension(tmp_path):
    # CSV file without extension
    csv_file = tmp_path / "csv_no_ext"
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write("instruction,input,output\nhello,world,test\n")

    # JSONL file without extension
    jsonl_file = tmp_path / "jsonl_no_ext"
    with open(jsonl_file, "w", encoding="utf-8") as f:
        f.write('{"instruction": "hello", "input": "world", "output": "test"}\n')

    # Parquet file without extension
    parquet_file = tmp_path / "parquet_no_ext"
    df = pd.DataFrame([{"instruction": "p1", "input": "in1", "output": "out1"}])
    df.to_parquet(parquet_file)

    # Directory for txt files
    txt_folder = tmp_path / "folder_no_ext"
    txt_folder.mkdir()

    assert detect_format(str(csv_file)) == "csv"
    assert detect_format(str(jsonl_file)) == "jsonl"
    assert detect_format(str(parquet_file)) == "parquet"
    assert detect_format(str(txt_folder)) == "txt-folder"


def test_preview_source(tmp_path):
    file_path = tmp_path / "preview.jsonl"
    data = [{"instruction": f"i{i}", "input": f"in{i}", "output": f"out{i}"} for i in range(10)]
    with open(file_path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

    # Preview with default n=5
    preview = preview_source(str(file_path))
    assert len(preview) == 5
    assert preview[0]["instruction"] == "i0"
    assert preview[4]["instruction"] == "i4"

    # Preview with custom n=2
    preview_2 = preview_source(str(file_path), n=2)
    assert len(preview_2) == 2
    assert preview_2[0]["instruction"] == "i0"
    assert preview_2[1]["instruction"] == "i1"


def test_local_source_adapter_integration(tmp_path):
    file_path = tmp_path / "local_test.csv"
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["instruction", "input", "output"])
        writer.writerow(["local_i", "local_in", "local_out"])

    local_source = LocalSource(path=str(file_path))
    records = list(local_source.iter_records())

    assert len(records) == 1
    assert records[0] == {"instruction": "local_i", "input": "local_in", "output": "local_out"}
