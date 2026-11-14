#!/usr/bin/env python3
"""Convert JSON arrays of flat objects into CSV, Python 3.10+, stdlib only."""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

class InputError(ValueError):
    """Input is not a JSON array of flat objects."""

def cell(value: Any, *, excel_safe: bool = False) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (str, int, float)):
        output = str(value)
        if excel_safe and isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
            return "'" + output
        return output
    raise InputError("Nested JSON objects/arrays are not supported; flat values only")

def convert(source: Path, destination: Path, *, excel_safe: bool = False) -> tuple[int, list[str]]:
    if source.resolve() == destination.resolve():
        raise InputError("Source and destination must be different paths")
    try:
        with source.open("r", encoding="utf-8-sig") as f:
            records = json.load(f)
    except json.JSONDecodeError as e:
        raise InputError(f"Invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}") from e
    if not isinstance(records, list) or any(not isinstance(r, dict) for r in records):
        raise InputError("Expected a JSON array of objects")
    fields = list(dict.fromkeys(k for rec in records for k in rec))
    rows = [{key: cell(rec.get(key), excel_safe=excel_safe) for key in fields} for rec in records]
    with destination.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        if fields:
            writer.writeheader()
            writer.writerows(rows)
    return len(records), fields

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert flat JSON records to CSV")
    parser.add_argument("input", type=Path, help="JSON source file")
    parser.add_argument("output", type=Path, help="CSV destination file")
    parser.add_argument("--excel-safe", action="store_true", help="Prefix spreadsheet formulas in string cells with apostrophe")
    args = parser.parse_args(argv)
    try:
        n, fields = convert(args.input, args.output, excel_safe=args.excel_safe)
    except (InputError, OSError, UnicodeError) as e:
        print(f"json-to-csv: {e}", file=sys.stderr)
        return 2
    print(f"Converted {n} rows, {len(fields)} columns to {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
