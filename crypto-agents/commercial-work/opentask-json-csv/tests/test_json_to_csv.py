import csv
import json
import pytest
from json_to_csv import InputError, convert, main

def sample(tmp_path, records):
    p = tmp_path / "records.json"
    p.write_text(json.dumps(records), encoding="utf-8")
    return p, tmp_path / "out.csv"

def load(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def test_missing_keys_and_stable_columns(tmp_path):
    src, dest = sample(tmp_path, [{"name": "A", "age": 19}, {"city": "Kampala", "name": "B"}])
    assert convert(src, dest) == (2, ["name", "age", "city"])
    assert load(dest) == [{"name": "A", "age": "19", "city": ""}, {"name": "B", "age": "", "city": "Kampala"}]

def test_quotes_commas_newlines_boolean_null(tmp_path):
    src, dest = sample(tmp_path, [{"v": 'a, "b"\nnew', "bool": True, "none": None}])
    convert(src, dest)
    assert load(dest) == [{"v": 'a, "b"\nnew', "bool": "true", "none": ""}]

def test_optional_excel_safe_flag(tmp_path):
    src, dest = sample(tmp_path, [{"expr": "=1+1", "safe": "normal"}])
    convert(src, dest, excel_safe=True)
    assert load(dest)[0] == {"expr": "'=1+1", "safe": "normal"}

def test_default_does_not_mutate_strings(tmp_path):
    src, dest = sample(tmp_path, [{"expr": "=1+1"}])
    convert(src, dest)
    assert load(dest)[0]["expr"] == "=1+1"

def test_empty_input_writes_empty_csv(tmp_path):
    src, dest = sample(tmp_path, [])
    assert convert(src, dest) == (0, [])
    assert dest.read_text() == ""

def test_invalid_json(tmp_path):
    src = tmp_path / "bad.json"
    src.write_text("[{broken", encoding="utf-8")
    with pytest.raises(InputError, match="Invalid JSON"):
        convert(src, tmp_path / "out.csv")

def test_non_list_rejected(tmp_path):
    src, dest = sample(tmp_path, {"name": "A"})
    with pytest.raises(InputError, match="array"):
        convert(src, dest)

def test_nested_object_rejected_without_partial_file(tmp_path):
    src, dest = sample(tmp_path, [{"x": 1}, {"x": {"nested": 2}}])
    with pytest.raises(InputError, match="Nested"):
        convert(src, dest)
    assert not dest.exists()

def test_no_overwrite_source(tmp_path):
    src, _ = sample(tmp_path, [{"ok": True}])
    with pytest.raises(InputError, match="different"):
        convert(src, src)

def test_command_line_success(tmp_path):
    src, dest = sample(tmp_path, [{"qty": 1}])
    assert main([str(src), str(dest)]) == 0
    assert load(dest)[0]["qty"] == "1"

def test_command_line_bad_input(tmp_path):
    assert main([str(tmp_path / "missing.json"), str(tmp_path / "out.csv")]) == 2
