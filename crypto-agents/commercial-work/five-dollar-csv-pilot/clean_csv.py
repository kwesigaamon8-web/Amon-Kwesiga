#!/usr/bin/env python3
"""Fixed-scope, read-only-input CSV cleanup trial; no network, keys, or payment activity.

Contract: up to 100 data rows, 20 columns and 256 KiB source input. Trim
outer whitespace, keep first normalized identical row, skip fully blank rows.
Do not normalize amounts, dates, identifiers, or interpret values as numbers.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

MAX_BYTES = 256 * 1024
MAX_ROWS = 100
MAX_COLUMNS = 20


class InvalidCSV(ValueError):
    pass


def clean(raw: bytes) -> tuple[str, dict]:
    if len(raw) > MAX_BYTES:
        raise InvalidCSV(f"Source exceeds {MAX_BYTES} byte trial limit")
    if b"\x00" in raw:
        raise InvalidCSV("NUL bytes are not permitted")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InvalidCSV("Input must be UTF-8 CSV") from exc
    if not text.strip():
        raise InvalidCSV("Empty CSV")
    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        source_rows = list(reader)
    except csv.Error as exc:
        raise InvalidCSV("Malformed CSV quoting") from exc
    if not source_rows:
        raise InvalidCSV("Missing header row")
    header = [value.strip() for value in source_rows[0]]
    if not header or not all(header):
        raise InvalidCSV("Header names must be nonempty")
    if len(header) > MAX_COLUMNS:
        raise InvalidCSV(f"CSV exceeds {MAX_COLUMNS} column limit")
    if len(set(header)) != len(header):
        raise InvalidCSV("Duplicate headers after whitespace trimming")
    kept: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    duplicates = 0
    blanks = 0
    formula_risks = 0
    for number, values in enumerate(source_rows[1:], start=2):
        if number - 1 > MAX_ROWS:
            raise InvalidCSV(f"CSV exceeds {MAX_ROWS} source data-row limit")
        if not values or all(not v.strip() for v in values):
            blanks += 1
            continue
        if len(values) != len(header):
            raise InvalidCSV(f"Data record {number} has {len(values)} columns; expected {len(header)}")
        normalized = tuple(v.strip() for v in values)
        if normalized in seen:
            duplicates += 1
            continue
        seen.add(normalized)
        kept.append(list(normalized))
        formula_risks += sum(1 for v in normalized if v.startswith(("=", "+", "@")) or
                             (v.startswith("-") and not v[1:].replace(".", "", 1).isdigit()))
    dest = io.StringIO(newline="")
    writer = csv.writer(dest, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(kept)
    report = {
        "source_rows": len(source_rows) - 1,
        "columns": len(header),
        "clean_rows": len(kept),
        "exact_duplicate_rows_removed": duplicates,
        "blank_rows_removed": blanks,
        "formula_like_cells_not_evaluated": formula_risks,
        "action": "Trim each header/cell, drop fully blank rows, remove identical normalized rows; preserve text IDs and order",
        "scope": "Fixed trial, not accounting assurance; no external data uploaded",
        "caution": "If loading as an Excel spreadsheet, review formula-like cells first. This tool does not escape or execute spreadsheet formulas.",
    }
    assert report["source_rows"] == report["clean_rows"] + duplicates + blanks
    return dest.getvalue(), report


def cli() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path, help="Non-sensitive UTF-8 CSV up to 100 data rows")
    p.add_argument("--clean", type=Path, required=True, help="New output CSV; refuses overwrite")
    p.add_argument("--report", type=Path, required=True, help="New JSON statistics file; refuses overwrite")
    args = p.parse_args()
    src = args.source.resolve()
    dest = args.clean.resolve()
    rep = args.report.resolve()
    if len({src, dest, rep}) != 3:
        p.error("Source, cleaned output and report must use distinct paths")
    if dest.exists() or rep.exists():
        p.error("Output files already exist; will not overwrite")
    try:
        data, summary = clean(src.read_bytes())
    except (OSError, InvalidCSV) as exc:
        p.error(str(exc))
    for location in (dest, rep):
        if not location.parent.is_dir():
            p.error(f"Output directory does not exist: {location.parent}")
    with dest.open("x", encoding="utf-8", newline="") as output:
        output.write(data)
    with rep.open("x", encoding="utf-8") as output:
        json.dump(summary, output, indent=2, ensure_ascii=False)
        output.write("\n")
    print("CSV_PILOT_COMPLETE " + json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
