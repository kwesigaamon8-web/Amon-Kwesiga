#!/usr/bin/env python3
"""Read-only research by real GitHub worker processes; no cryptocurrency mining on CI."""
import argparse
import json
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ORDER_FILE = Path("crypto-agents/chief_D_owner_orders.json")
TOPICS = (
    "free bitcoin ASIC miner", "bitcoin miner giveaway", "bitaxe hardware giveaway",
    "ASIC miner donation", "used ASIC miner donated", "bitcoin mining hardware grant",
    "GPU hardware donation", "free donated used computers", "open source mining hardware grant",
    "bitcoin miner hardware contest",
)
ROLES = ("DIRECTOR", "ASSISTANT_A", "ASSISTANT_B")
TERMS = re.compile(r"(?i)\b(bitaxe|asic|miner|mining|gpu|graphics card|computer|pc|hardware)\b")
OFFER = re.compile(r"(?i)\b(free|donat(?:e|ed|ion)|giveaway|grant|surplus|raffle|contest|sponsor|recycl(?:e|ing))\b")

def utc():
    return datetime.now(timezone.utc).isoformat()

def fetch_json(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read(500000))

def search(topic, headers):
    queries = [
        ("github", "https://api.github.com/search/issues?" + urllib.parse.urlencode(
            {"q": topic + " is:issue is:open", "per_page": 8, "sort": "updated"})),
        ("hackernews", "https://hn.algolia.com/api/v1/search_by_date?" + urllib.parse.urlencode(
            {"query": topic, "tags": "story", "hitsPerPage": 8})),
    ]
    leads, errors = [], []
    for provider, url in queries:
        try:
            data = fetch_json(url, headers if provider == "github" else {"User-Agent":"B1B2-Hardware-Research/1.0"})
            items = data.get("items", []) if provider == "github" else data.get("hits", [])
            if not isinstance(items, list):
                raise ValueError("unexpected source response")
            for record in items:
                title = str(record.get("title") or "")[:180]
                body = str(record.get("body") or record.get("story_text") or "")[:350]
                link = record.get("html_url") if provider == "github" else (record.get("url") or
                    "https://news.ycombinator.com/item?id=" + str(record.get("objectID", "")))
                if not isinstance(link, str) or not link.startswith("https://"):
                    continue
                if not (TERMS.search(title + " " + body) and OFFER.search(title + " " + body)):
                    continue
                leads.append({"source":provider, "title":title, "url":link,
                    "evidence_excerpt":body[:200], "offer_verified":False,
                    "owner_permission_verified":False, "uganda_eligibility_verified":False,
                    "shipping_cost_verified":False, "equipment_acquired":False})
        except Exception as exc:
            errors.append({"provider":provider,"error":str(exc)[:160]})
    return leads[:8], errors

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fleet", choices=["transferexperiment", "BountyScoutAI"], required=True)
    ap.add_argument("--director", choices=["D%02d"%n for n in range(1,11)], required=True)
    ap.add_argument("--output", default="hardware-reports")
    args = ap.parse_args()
    content = json.loads(ORDER_FILE.read_text(encoding="utf-8"))
    order_id = content["current_owner_order_id"]
    current = content["orders"][-1]
    if current["id"] != order_id or "BTC-SPREE" not in order_id:
        raise SystemExit("Latest Chief D owner order is not the BTC hardware mission")
    headers = {"User-Agent":"B1B2-Hardware-Research/1.0","Accept":"application/vnd.github+json"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    results=[]
    for offset, role in enumerate(ROLES):
        role_id = args.fleet + "/" + args.director + "/" + role
        topic_index = (int(args.director[1:])-1 + (0 if args.fleet=="transferexperiment" else 5) + offset*3) % len(TOPICS)
        topic=TOPICS[topic_index]
        started=utc()
        leads, errors=search(topic, headers)
        record = {"order_id":order_id,"worker_id":role_id,"fleet":args.fleet,
            "director":args.director,"role":role,"process_id":os.getpid(),
            "github_run_id":os.getenv("GITHUB_RUN_ID", "local"),
            "started_utc":started,"finished_utc":utc(),"task":"public free hardware discovery",
            "search_query":topic,"searches_attempted":2,"source_errors":errors,
            "unverified_leads":leads,"hardware_acquired":0,"miner_processes_started":0,
            "accepted_pool_shares":0,"verified_btc_received":0,
            "status":"sources_checked" if len(errors)<2 else "sources_unavailable",
            "note":"This is a real read-only search, not an actual mining device or verified donation."}
        path=output/(args.fleet+"-"+args.director+"-"+role+".json")
        path.write_text(json.dumps(record, indent=2),encoding="utf-8")
        results.append(record)
        print(json.dumps({"worker":role_id,"status":record["status"],"candidates":len(leads),"errors":len(errors)}), flush=True)
        time.sleep(0.25)
    print("ACTUALLY_ATTEMPTED_ROLE_REPORTS",len(results))
if __name__=="__main__":
    main()
