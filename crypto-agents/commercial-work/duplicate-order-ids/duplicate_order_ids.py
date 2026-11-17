#!/usr/bin/env python3
"""Check external order IDs for duplicate values without changing source CSV.

Original B1/B2 commission sample. Python standard library only.
CSV row numbers include the first header row as row 1.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

COLUMN="external_order_id"

def find_duplicates(path: Path) -> dict[str, object]:
    """Return duplicate IDs and all matching CSV row positions, never write input."""
    seen: dict[str,list[int]]=defaultdict(list)
    with path.open("r",encoding="utf-8-sig",newline="") as handle:
        reader=csv.DictReader(handle)
        headers=reader.fieldnames or []
        if COLUMN not in headers:
            raise ValueError("CSV is missing the required 'external_order_id' header")
        for row_num,row in enumerate(reader,start=2):
            value=row.get(COLUMN)
            if not isinstance(value,str):
                raise ValueError(f"Malformed CSV row {row_num}: missing order ID column")
            order_id=value.strip()
            if order_id:
                seen[order_id].append(row_num)
    dup={key:positions for key,positions in seen.items() if len(positions)>1}
    return {"source_file":str(path),"column":COLUMN,
            "duplicate_ids":dup,"duplicate_id_count":len(dup),
            "duplicate_row_count":sum(len(v) for v in dup.values()),
            "note":"Source CSV unchanged. Empty IDs ignored; missing values should be reviewed separately."}

def main() -> None:
    parser=argparse.ArgumentParser(description="Find repeated external_order_id values in a CSV without changing it.")
    parser.add_argument("csv_file",type=Path,help="Input CSV with external_order_id header.")
    parser.add_argument("--json",action="store_true",help="Print machine-readable JSON")
    args=parser.parse_args()
    try:
        result=find_duplicates(args.csv_file)
    except (OSError,UnicodeError,csv.Error,ValueError) as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(result,indent=2))
    else:
        print(f"Duplicate order IDs: {result['duplicate_id_count']}")
        if not result["duplicate_ids"]:
            print("No duplicate nonempty external order IDs found.")
        for key,rows in sorted(result["duplicate_ids"].items()):
            print(f"  {key} — CSV rows {', '.join(map(str,rows))}")

if __name__=="__main__":
    main()
