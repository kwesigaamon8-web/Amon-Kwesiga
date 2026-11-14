"""Original test cases for customer-ready CSV-to-JSON CLI."""
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from csv_to_json import ConversionError,parse_csv,main

def test_missing_values():
    assert parse_csv("name,qty\nAda,2\nBob\n")==[{"name":"Ada","qty":"2"},{"name":"Bob","qty":""}]

def test_escaped_commas():
    assert parse_csv('name,note\n"A, B","said ""yes"""\n')[0]["note"]=='said "yes"'

def test_semicolons():
    assert parse_csv("name;amount\nAda;2\nBob;3\n")[1]["amount"]=="3"

def test_tabs():
    assert parse_csv("a\tb\n1\t2\n",delimiter="\t")[0]=={"a":"1","b":"2"}

def test_unicode():
    assert parse_csv("name,city\nMø,Łódź\n")[0]["city"]=="Łódź"

def test_bom():
    assert parse_csv("\ufeffname,city\nA,Kampala\n")[0]=={"name":"A","city":"Kampala"}

def test_duplicate_header():
    with pytest.raises(ConversionError,match="Duplicate"):
        parse_csv("a,a\n1,2\n")

def test_extra_columns():
    with pytest.raises(ConversionError,match="columns"):
        parse_csv("a,b\n1,2,3\n")

def test_bad_quote():
    with pytest.raises(ConversionError,match="Malformed"):
        parse_csv('a,b\n"unclosed,1\n')

def test_empty():
    with pytest.raises(ConversionError,match="empty"):
        parse_csv(" \n ")

def test_cli_pretty(tmp_path):
    source=tmp_path/"source.csv"
    dest=tmp_path/"output.json"
    source.write_text("id;name\n1;Uganda\n",encoding="utf-8")
    assert main([str(source),"-o",str(dest),"--indent","4"])==0
    assert json.loads(dest.read_text())==[{"id":"1","name":"Uganda"}]

def test_cli_jsonlines(tmp_path):
    source=tmp_path/"source.csv"
    dest=tmp_path/"output.jsonl"
    source.write_text("id,name\n1,Ada\n2,Bob\n")
    assert main([str(source),"-o",str(dest),"--json-lines"])==0
    assert [json.loads(x)["name"] for x in dest.read_text().splitlines()]==["Ada","Bob"]

def test_cli_missing_source(tmp_path):
    assert main([str(tmp_path/"no.csv")])==2

def test_cli_invalid_indent(tmp_path):
    source=tmp_path/"a.csv"
    source.write_text("a\n1\n")
    with pytest.raises(SystemExit):
        main([str(source),"--indent","99"])

def test_pipe_separator():
    assert parse_csv('a|b\n"x|y"|2\n',delimiter="|")[0]["a"]=="x|y"
