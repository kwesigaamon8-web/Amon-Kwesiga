#!/usr/bin/env python3
"""Summarize executed public hardware discovery without inventing donations."""
import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",default="combined-hardware")
    ap.add_argument("--output",default="hardware-summary")
    args=ap.parse_args()
    root=Path(args.input)
    records=[]
    invalid=[]
    for p in root.rglob("*.json"):
        try:
            obj=json.loads(p.read_text(encoding="utf-8"))
            if isinstance(obj,dict) and obj.get("task")=="public free hardware discovery":
                records.append(obj)
        except Exception as exc:
            invalid.append({"file":p.name,"error":str(exc)[:120]})
    unique={}
    for rec in records:
        for lead in rec.get("unverified_leads",[]):
            url=lead.get("url")
            if url and url not in unique:
                unique[url]={**lead, "found_by":rec["worker_id"]}
    ranked=sorted(unique.values(),key=lambda x:(x.get("source")!="github",x.get("title","")))[:50]
    out={"timestamp_utc":datetime.now(timezone.utc).isoformat(),
         "order_ids":sorted({r["order_id"] for r in records}),
         "real_role_reports":len(records),
         "distinct_run_ids":sorted({r.get("github_run_id","") for r in records}),
         "real_fleets":dict(Counter(r["fleet"] for r in records)),
         "source_checks_attempted":sum(r["searches_attempted"] for r in records),
         "source_errors":sum(len(r["source_errors"]) for r in records),
         "deduplicated_unverified_hardware_leads":len(unique),
         "actual_mining_hardware_acquired_verified":0,
         "active_mining_devices_verified":0,
         "btc_receipts_verified_from_these_reports":0,
         "top_unverified_candidates":ranked,
         "invalid_reports":invalid,
         "method":"Actual public search calls by scoped CI processes, NOT 11 trillion live workers; verify donor availability/consent before any claim."}
    dest=Path(args.output); dest.mkdir(parents=True,exist_ok=True)
    (dest/"summary.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
    lines=["# B1/B2 Free Hardware Research — actual execution report","",
           "Order(s): "+", ".join(out["order_ids"]),"",
           "- Actual role reports: "+str(len(records)),
           "- Distinct GitHub run IDs: "+str(len(out["distinct_run_ids"])),
           "- Public source checks attempted: "+str(out["source_checks_attempted"]),
           "- Source errors: "+str(out["source_errors"]),
           "- Unique unverified hardware leads: "+str(len(unique)),
           "- Confirmed donated/acquired hardware: **0**",
           "- New mining devices/received BTC independently verified: **0**","",
           "## Unverified candidate sources"]
    for item in ranked[:25]:
        lines.append("- ["+item["title"].replace("]","")[:85]+"]("+item["url"]+") ("+item["found_by"]+")")
    lines.append("\nAll offers require independent contact, country eligibility, consent, shipping cost and ongoing electricity validation. No mining on GitHub-hosted runners.")
    (dest/"summary.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in out.items() if k not in ("top_unverified_candidates","invalid_reports")},indent=2))
if __name__=="__main__":
    main()
