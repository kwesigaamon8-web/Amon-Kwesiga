"""Original zero-dependency CSV -> JSON utility, Python 3.10+."""
from __future__ import annotations
import argparse
import csv
import io
import json
import sys
from pathlib import Path

class ConversionError(ValueError):
    """Invalid CSV, invalid source or invalid destination."""

def parse_csv(text: str, delimiter: str | None = None, *, skip_blank: bool = True) -> list[dict[str,str]]:
    if not text.strip():
        raise ConversionError("CSV input is empty")
    if delimiter is None:
        try:
            delimiter = csv.Sniffer().sniff(text[:8192], delimiters=",;\t|").delimiter
        except csv.Error:
            delimiter = ","
    if len(delimiter) != 1:
        raise ConversionError("Delimiter must be exactly one character")
    try:
        reader = csv.reader(io.StringIO(text,newline=""),delimiter=delimiter,strict=True)
        header = next(reader,None)
        if header is None:
            raise ConversionError("CSV header is missing")
        header[0] = header[0].lstrip("\ufeff")
        if not all(h.strip() for h in header):
            raise ConversionError("Empty CSV header name")
        if len(header)!=len(set(header)):
            raise ConversionError("Duplicate CSV header names; JSON object would lose data")
        result=[]
        for row in reader:
            if skip_blank and not row:
                continue
            if len(row)>len(header):
                raise ConversionError(f"Data row ending on CSV line {reader.line_num} has {len(row)} columns but header has {len(header)}")
            result.append(dict(zip(header,row+[""]*(len(header)-len(row)))))
        return result
    except csv.Error as exc:
        raise ConversionError(f"Malformed CSV: {exc}") from exc

def convert_file(source: str | Path, *, delimiter: str | None = None, encoding: str = "utf-8-sig") -> list[dict[str,str]]:
    try:
        return parse_csv(Path(source).read_text(encoding=encoding),delimiter)
    except (OSError,UnicodeError) as exc:
        raise ConversionError(f"Cannot read input: {exc}") from exc

def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description="Convert CSV/TSV to JSON")
    parser.add_argument("input",help="CSV/TSV source filename")
    parser.add_argument("-o","--output",default="-",help="JSON output path or '-' for stdout")
    parser.add_argument("-d","--delimiter",help="Separator or 'tab' (default autodetect)")
    parser.add_argument("--indent",type=int,default=2,help="Pretty print indentation 0-8")
    parser.add_argument("--encoding",default="utf-8-sig",help="Text input encoding")
    parser.add_argument("--json-lines",action="store_true",help="Output JSONL instead of array")
    args=parser.parse_args(argv)
    if not 0<=args.indent<=8:
        parser.error("--indent must be from 0 to 8")
    sep="\t" if args.delimiter=="tab" else args.delimiter
    try:
        rows=convert_file(args.input,delimiter=sep,encoding=args.encoding)
        if args.json_lines:
            result="".join(json.dumps(r,ensure_ascii=False)+"\n" for r in rows)
        else:
            result=json.dumps(rows,ensure_ascii=False,indent=args.indent)+"\n"
        if args.output=="-":
            sys.stdout.write(result)
        else:
            try:
                Path(args.output).write_text(result,encoding="utf-8")
            except OSError as exc:
                raise ConversionError(f"Cannot write output: {exc}") from exc
        return 0
    except ConversionError as exc:
        print(f"csv-to-json: {exc}",file=sys.stderr)
        return 2

if __name__=="__main__":
    raise SystemExit(main())
