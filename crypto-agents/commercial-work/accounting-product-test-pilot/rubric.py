#!/usr/bin/env python3
"""Original, offline bookkeeping-software testing rubric generator and validator.

This is a reusable sample, NOT a completed customer assignment or 36
platforms tested. Requires Python 3.11+ standard library only.
"""
from __future__ import annotations
import argparse
import csv
import json
import pathlib
from collections import Counter
from datetime import date

TASKS=(
 ("01","SETUP_AND_DASHBOARD","Set up a fictional company and record dashboard observations"),
 ("02","INVOICING_AND_PAYMENTS","Create 4 fictional invoices; record full and partial payments"),
 ("03","RECORD_EXPENSES","Record 3 fictional expenses without real bank connections"),
 ("04","BANK_RECONCILIATION","Import supplied sample statement; reconcile and explain unmatched lines"),
 ("05","PROFIT_AND_LOSS","Generate and export a Profit & Loss report"),
)
FIELDS=("provider","task_number","task","test_date","minutes_elapsed","score_1_to_5",
        "test_status","expected_steps","observed_behavior","evidence_screenshot",
        "friction_and_issues","test_data_class")
STATUSES=("NOT_TESTED","IN_PROGRESS","COMPLETED","BLOCKED")
TEST_CLASS="SYNTHETIC_DATA_ONLY"

def init_rows(providers):
    if not providers or len(set(providers))!=len(providers):
        raise ValueError("Provider names must be supplied once each")
    rows=[]
    for provider in providers:
        if not isinstance(provider,str) or not provider.strip():
            raise ValueError("Empty provider name")
        for n,task,steps in TASKS:
            rows.append({
                "provider":provider,
                "task_number":n,
                "task":task,
                "test_date":"",
                "minutes_elapsed":"",
                "score_1_to_5":"",
                "test_status":"NOT_TESTED",
                "expected_steps":steps,
                "observed_behavior":"",
                "evidence_screenshot":"",
                "friction_and_issues":"",
                "test_data_class":TEST_CLASS,
            })
    return rows

def write_csv(rows, filename):
    path=pathlib.Path(filename)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing work: {path}")
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=FIELDS,extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)

def read_csv(filename):
    with pathlib.Path(filename).open("r",newline="",encoding="utf-8-sig") as handle:
        reader=csv.DictReader(handle)
        if reader.fieldnames!=list(FIELDS):
            raise ValueError("Unexpected columns: use an untouched original template")
        return list(reader)

def validate_rows(rows):
    if not rows:raise ValueError("Empty rubric")
    issues=[]
    statuses=Counter()
    by_provider={}
    for idx,row in enumerate(rows,start=2):
        p=row.get("provider") or ""
        by_provider.setdefault(p,[]).append(row)
        st=row.get("test_status")
        if st not in STATUSES:issues.append(f"CSV row {idx}: invalid test status {st!r}")
        else:statuses[st]+=1
        if row.get("test_data_class")!=TEST_CLASS:
            issues.append(f"CSV row {idx}: unexpected data classification")
        score=row.get("score_1_to_5") or ""
        if score and score not in ("1","2","3","4","5"):
            issues.append(f"CSV row {idx}: score must be a whole number 1-5")
        mins=row.get("minutes_elapsed") or ""
        if mins:
            try:
                m=float(mins)
                if not 0<=m<=1440:raise ValueError()
            except ValueError:
                issues.append(f"CSV row {idx}: minutes must be 0-1440")
        if st=="COMPLETED":
            required=("test_date","minutes_elapsed","score_1_to_5","observed_behavior","evidence_screenshot")
            missing=[name for name in required if not row.get(name)]
            if missing:issues.append(f"CSV row {idx}: completed entry missing "+", ".join(missing))
            else:
                try:date.fromisoformat(row["test_date"])
                except ValueError:issues.append(f"CSV row {idx}: test date must be YYYY-MM-DD")
        if st=="NOT_TESTED" and (row.get("score_1_to_5") or row.get("evidence_screenshot")):
            issues.append(f"CSV row {idx}: untested task has invented rating/evidence")
    expected={(n,task) for n,task,_ in TASKS}
    for provider,entries in by_provider.items():
        keys=[(x.get("task_number"),x.get("task")) for x in entries]
        if len(keys)!=len(TASKS) or set(keys)!=expected:
            issues.append(f"Provider {provider!r}: must have one entry for each of five tasks")
    return {
        "schema":"B1_B2_BOOKKEEPING_PLATFORM_QA_RUBRIC_V1",
        "provider_count":len(by_provider),
        "expected_task_count":len(by_provider)*len(TASKS),
        "actual_task_count":len(rows),
        "status_counts":dict(statuses),
        "platforms_actually_completed":sum(
            all(x["test_status"]=="COMPLETED" for x in entries)
            for entries in by_provider.values()),
        "valid":not issues,
        "errors":issues,
        "note":"An empty or in-progress template is not a performed software test, accepted work or payment."
    }

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="action",required=True)
    create=sub.add_parser("init")
    create.add_argument("--out",required=True)
    create.add_argument("--providers",type=int,default=36)
    check=sub.add_parser("validate")
    check.add_argument("csv_file")
    args=ap.parse_args()
    if args.action=="init":
        if not 1<=args.providers<=100:
            ap.error("Provider count must be from 1 to 100")
        rows=init_rows([f"UNASSIGNED_PROVIDER_{i:02d}" for i in range(1,args.providers+1)])
        write_csv(rows,args.out)
        print(json.dumps({"created":args.out,"provider_slots":args.providers,
            "task_rows":len(rows),"tasks_actually_tested":0,
            "scores_assigned":0,"client_data_loaded":False}))
    else:
        try:report=validate_rows(read_csv(args.csv_file))
        except (OSError,ValueError) as exc:ap.error(str(exc))
        print(json.dumps(report,indent=2))
        if not report["valid"]:raise SystemExit(1)

if __name__=="__main__":main()
