"""Evidence-gated finite ENIGMA public-data report runner.

A successful CLI invocation proves only that one Python process generated a
report from a dated, manually checked public snapshot. It does NOT prove a
separately autonomous AI worker, customer acceptance or cryptocurrency income.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import sys

ROLE = re.compile(r"^D(?:0[1-9]|10)-M(?:0[1-9]|1[0-5])-W(?:0[1-9]|[1-4][0-9]|50)(?:-S[0-9]{3}(?:-G[0-9]{3}(?:-H[0-9]{3})?)?)?$")
ALLOWED_COUNTRIES = ("Kenya", "Uganda", "Tanzania")
SOURCE = "https://data.worldbank.org/?locations=KE-UG-TZ"

def validate_roles(worker_id: str, parent_id: str) -> None:
    if not ROLE.fullmatch(worker_id):
        raise ValueError("unsupported or non-canonical worker role ID")
    if worker_id.rsplit("-", 1)[0] != parent_id:
        raise ValueError("worker-parent mismatch")

def validate_snapshot(data: dict, topic: str) -> dict:
    if data.get("schema") != "ENIGMA_OPEN_DATA_SNAPSHOT_V1":
        raise ValueError("unsupported input schema")
    if data.get("data_source_url") != SOURCE:
        raise ValueError("unrecognized evidence source")
    if data.get("license_status") != "CHECK_INDICATOR_TERMS_BEFORE_REDISTRIBUTING_RAW_DATA":
        raise ValueError("missing source license caution")
    if data.get("source_independent_numeric_crosscheck") != "NOT_PERFORMED":
        raise ValueError("this limited sample may not claim independent secondary source verification")
    if tuple(data.get("countries", ())) != ALLOWED_COUNTRIES:
        raise ValueError("country order mismatch")
    if topic not in ("digital", "macro"):
        raise ValueError("unsupported topic")
    t = data["topics"][topic]
    indicators = t["indicators"]
    if len(indicators) < 2:
        raise ValueError("insufficient indicator breadth")
    expected_year = 2024 if topic == "digital" else 2025
    for indicator in indicators:
        if indicator["year"] != expected_year:
            raise ValueError("mixed time period in report")
        vals = indicator["values"]
        if set(vals) != set(ALLOWED_COUNTRIES):
            raise ValueError("incomplete country observations")
        if any(not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0 or v > 100 for v in vals.values()):
            raise ValueError("invalid percentage/rate observation")
    if not t.get("question") or not t.get("buyer_use") or len(t.get("next_decisions", [])) < 3:
        raise ValueError("missing decision-useful analysis")
    return t

def render(data: dict, topic: str, worker_id: str, parent_id: str, run_id: str) -> str:
    validate_roles(worker_id, parent_id)
    t = validate_snapshot(data, topic)
    content = json.dumps(data, sort_keys=True).encode("utf-8")
    sha = hashlib.sha256(content).hexdigest()
    year = 2024 if topic == "digital" else 2025
    lines = [
        f"# ENIGMA automatically formatted report: {topic.upper()} — East Africa ({year})",
        "", f"**Execution record:** run_id \`{run_id}\`, assigned virtual role \`{worker_id}\`, parent \`{parent_id}\`.",
        "**Claim boundary:** This process is a finite Python report formatter; it does not prove an independently running AI agent, independent source crawl, prospective buyer or money earned.",
        f"**Question:** {t['question']}",
        f"**Buyer use:** {t['buyer_use']}",
        "", "## Dated observations",
        "| World Bank indicator / reporting year | Kenya | Uganda | Tanzania | Units |",
        "|---|---:|---:|---:|---|",
    ]
    for i in t["indicators"]:
        v = i["values"]
        lines.append(f"| {i['label']} ({i['code']}) / {i['year']} | {v['Kenya']} | {v['Uganda']} | {v['Tanzania']} | {i['unit']} |")
    first = t["indicators"][0]["values"]
    gap = round(max(first.values())-min(first.values()), 2)
    lines += ["",f"**Original descriptive calculation:** Highest minus lowest published rounded country observation on \`{t['indicators'][0]['code']}\`: **{gap} percentage points**. This is a simple comparison, NOT causal evidence or a forecast.",
    "", "## Buyer questions to verify before deciding"]
    lines += [f"- {item}" for item in t["next_decisions"]]
    lines += ["","## Provenance and license",
        f"- Numeric observation source: [{data['data_source_name']}]({data['data_source_url']}) (published years stated in table).",
        f"- Dataset metadata: {data['dataset_metadata_url']}",
        f"- World Bank terms: {data['license_url']}; verify third-party indicator rights before any raw-data redistribution.",
        f"- Input snapshot date: {data['collected_at_utc']}. Independently re-downloaded series: NO.",
        f"- Reproducible input SHA-256: \`{sha}\`.",
        "- No private/person-level data, scraping, live API contact, unverified current market prices, or exclusive raw-data ownership claimed.",
        "", "## Delivery and money gates",
        "- This is a public **demonstration**, not a customer-commissioned report. New buyer: NONE VERIFIED.",
        "- Quote, acceptance, deliverable handed to customer: NONE VERIFIED.",
        "- Verified approved-chain BTC/Base-native-USDC incoming TXID: NOT_VERIFIED.",
        "- Custom scopes and prices: https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/docs/world-open-data-reports.html",
        ]
    return "\n".join(lines)+"\n"

def self_test(data: dict) -> None:
    for topic, worker, parent in (("digital","D01-M01-W01","D01-M01"),("macro","D02-M01-W02","D02-M01")):
        result=render(data,topic,worker,parent,"SELFTEST")
        assert "NOT_VERIFIED" in result and "World Bank" in result
        assert f"assigned virtual role \`{worker}\`" in result
    cases = []
    wrong = copy.deepcopy(data);wrong["topics"]["digital"]["indicators"][0]["year"]=2023
    cases.append((wrong,"digital","D01-M01-W01","D01-M01"))
    wrong = copy.deepcopy(data);wrong["topics"]["macro"]["indicators"][0]["values"].pop("Uganda")
    cases.append((wrong,"macro","D01-M01-W01","D01-M01"))
    wrong = copy.deepcopy(data);wrong["license_status"]="OPEN_ALL_DATA"
    cases.append((wrong,"digital","D01-M01-W01","D01-M01"))
    cases.append((data,"digital","D01-M01-W01","D02-M01"))
    cases.append((data,"digital","D99-M01-W01","D99-M01"))
    for item in cases:
        try:
            render(*item, "SELFTEST")
        except ValueError:
            pass
        else:
            raise AssertionError("unsafe report was accepted")
    print("OPEN_DATA_PILOT_PASS: 2 positive formats, 5 negative guards, no false sale/AI claims")

def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="crypto-agents/open-data-worker/world_bank_east_africa_snapshot_2026-11-22.json")
    p.add_argument("--topic",choices=("digital","macro"),default="digital")
    p.add_argument("--worker-id",default="D01-M01-W01")
    p.add_argument("--parent-id",default="D01-M01")
    p.add_argument("--output",default="open-data-report.md")
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    source=Path(a.input)
    data=json.loads(source.read_text(encoding="utf-8"))
    if a.self_test:
        self_test(data);return
    run_id=os.environ.get("GITHUB_RUN_ID", "LOCAL_CLI_EXECUTION")
    report=render(data,a.topic,a.worker_id,a.parent_id,run_id)
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(report,encoding="utf-8")
    print(json.dumps({"status":"EXECUTED_PYTHON_PROCESS_ONLY","output":str(out),"role":a.worker_id,"report_type":a.topic,"authenticated_ai_agent_count":0,"buyer_acceptance":"NONE","incoming_txid":"NOT_VERIFIED","run_id":run_id}))

if __name__ == "__main__":
    main()
