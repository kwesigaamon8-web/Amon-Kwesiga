"""Evidence-only parallel opportunity scout: one real HTTP check per lane.

This is NOT an independent language-model agent, accepted job, outreach,
or blockchain receipt. Each scheduled matrix runner produces a source
snapshot for one of 8 different earning routes, with explicit error states.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from datetime import datetime, timezone
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
CATALOG = ROOT / "parallel-crypto-revenue-lanes.json"
OUT = Path("parallel-revenue-reports")
ALLOWED_HOSTS = {
    "raw.githubusercontent.com", "github.com", "make.fun",
    "superteam.fun",
}
SIGNALS = re.compile(r"(?i)\b(?:btc|usdc|sol|paid|reward|prize|bounty|payment|apply|submit|eligible|deadline|winner|remote|job)\b")


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "svg", "noscript"):
            self.depth += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "svg", "noscript") and self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if not self.depth:
            s = " ".join(data.split())
            if s:
                self.chunks.append(s[:600])


def load_lanes():
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    return data["lanes"]


def self_test():
    lanes = load_lanes()
    assert len(lanes) == 8, "Eight independent sources required"
    directors = set()
    urls = set()
    for lane_id, info in lanes.items():
        assert re.fullmatch(r"[a-z0-9-]+", lane_id)
        u = urllib.parse.urlsplit(info["source"])
        assert u.scheme == "https" and u.hostname in ALLOWED_HOSTS
        assert info["source"] not in urls
        urls.add(info["source"])
        assert info["fleet"] in ("transferexperiment", "BountyScoutAI")
        for d in info["directors"]:
            assert re.fullmatch(r"D(?:0[1-9]|10)", d)
            role = (info["fleet"], d)
            assert role not in directors, f"Double-assigned director: {role}"
            directors.add(role)
    assert len(directors) == 20
    assert len({x[0] for x in directors}) == 2
    print("PARALLEL_LANES_SELF_TEST_PASS", json.dumps({
        "independent_lane_sources":len(urls),
        "distinct_planning_directors":len(directors),
        "real_ai_model_calls_in_test":0,
        "crypto_payments_claimed":0,
    }))


def scan(lane):
    info = load_lanes()[lane]
    url = info["source"]
    report = {
        "lane":lane, "company":info["fleet"],
        "director_roles_assigned_not_live_agents":info["directors"],
        "target_source":url, "work_goal":info["goal"],
        "payment_conditions":info["payment"],
        "owner_task_stage_at_configuration":info["stage"],
        "checked_at_utc":datetime.now(timezone.utc).isoformat(),
        "source_check":"NOT_STARTED",
        "source_http_status":None,
        "source_sha256":None,
        "source_text_signals":[],
        "authenticated_application_or_submission_made":False,
        "independent_model_calls_made":0,
        "accepted_contract_verified":False,
        "bitcoin_or_other_crypto_payment_verified":False,
    }
    problem = None
    try:
        req=urllib.request.Request(url,headers={
            "User-Agent":"B1B2-Original-Work-Research/1.0 (public source verification)",
            "Accept":"text/html,text/plain,application/json",
        })
        with urllib.request.urlopen(req,timeout=14) as response:
            raw=response.read(170000)
            report["source_http_status"]=response.status
        report["source_sha256"]=hashlib.sha256(raw).hexdigest()
        decoded=raw.decode("utf-8",errors="replace")
        if "<html" in decoded[:1500].lower() or "<!doctype" in decoded[:500].lower():
            parser=VisibleText()
            parser.feed(decoded)
            tokens=parser.chunks
        else:
            tokens=[s.strip() for s in decoded.splitlines() if s.strip()]
        matches=[]
        for token in tokens:
            if SIGNALS.search(token) and token not in matches:
                matches.append(token[:280])
            if len(matches)>=12:
                break
        report["source_text_signals"]=matches
        report["source_check"]="HTTP_FETCHED_NOT_VERIFIED_AS_OPEN_OR_PAID"
        if not matches:
            report["source_check"]="HTTP_FETCHED_NO_RELEVANT_VISIBLE_TEXT"
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,OSError,ValueError) as exc:
        problem=type(exc).__name__
        if isinstance(exc,urllib.error.HTTPError):
            report["source_http_status"]=exc.code
        report["source_check"]="HTTP_SOURCE_BLOCKED_OR_FAILED"
        report["source_error_type"]=problem
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/(lane+".json")).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    md=[
        "### "+lane+" — "+report["source_check"],
        "- Source: "+url,
        "- Checked UTC: "+report["checked_at_utc"],
        "- Responsible planning roles (not active models): "+info["fleet"]+" / "+", ".join(info["directors"]),
        "- Actual independent model calls: **0**",
        "- Approved external submissions / client acceptance: **0 verified**",
        "- Received cryptocurrency: **0 verified**",
        "- Important: source HTTP success does not prove the listing is open, funded, eligible or payable.",
        "- Next original work: "+info["goal"],
    ]
    if problem:
        md.append("- HTTP/source blocker: "+problem)
    for signal in report["source_text_signals"][:4]:
        md.append("- Source text excerpt: "+signal.replace("|","/"))
    (OUT/(lane+".md")).write_text("\n".join(md)+"\n",encoding="utf-8")
    print("PARALLEL_REVENUE_SOURCE_RESULT",json.dumps(report,ensure_ascii=False))
    return 1 if problem else 0


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--lane",choices=list(load_lanes()))
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    if args.self_test:
        self_test()
    else:
        if not args.lane:
            p.error("Specify --lane")
        sys.exit(scan(args.lane))
