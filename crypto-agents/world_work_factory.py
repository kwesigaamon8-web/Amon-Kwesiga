"""Worldwide B1/B2 task discovery, original-source checks and production packets.

Public discovery is bounded to one index + 12 authentic GitHub issue lookups.
A marketplace listing NEVER proves escrow, a sponsor, Uganda eligibility,
submission permission or the ability to settle to a BTC mainnet wallet.

This engine does not log into third-party sites, send messages, submit code
to arbitrary repos, spend cryptocurrency, browse private individuals or email.
Submission/payment operations are separate, evidence-gated host actions.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.parse
import urllib.request

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE/"world-work-factory"
sys.path.insert(0,str(HERE))
from btc_receiver_safety import require_all_owner_receivers
from bounty_eligibility_audit import evaluate as bounty_evaluate
from directive_cascade import read_owner

BOUNTY_FEED="https://muhib-karim.github.io/bounty-radar/bounties.json"
FEED_HOST="muhib-karim.github.io"
GH_HOST="api.github.com"
ALLOWED_REPO=re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/issues/([1-9]\d*)$")
MAX_FEED=80
MAX_ORIGINAL_LOOKUPS=12
MAX_BODY=30000
MAX_BYTES=2_400_000
B1="bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z"
B2="bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9"
STAGES=("DISCOVERED","ORIGINAL_SOURCE_CHECKED","FUNDED_ELIGIBLE","SCOPE_ACCEPTED",
        "DELIVERABLE_TESTED","SUBMITTED_VERIFIED","SPONSOR_ACCEPTED",
        "PAYMENT_REQUEST_CONFIRMED","ONCHAIN_PAYMENT_VERIFIED")
PAYOUT_RAILS=("bitcoin-mainnet", "base-usdc", "stacks-sbtc", "unknown")
STOP_WORDS=(
    "manual pull requests from human engineers are not reviewed",
    "external pull requests are not reviewed",
    "unsolicited prs will not be reviewed",
    "not open to external contributors",
)

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(payload):
    return hashlib.sha256(json.dumps(payload,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest()

def root_owner():
    d=read_owner()
    return {"owner_order_id":d["owner_order_id"],"owner_sha256":d["owner_sha256"]}

def allowed(url):
    p=urllib.parse.urlsplit(url)
    return p.scheme=="https" and p.hostname in (FEED_HOST,GH_HOST) and p.port in (None,443) and not p.username and not p.password

def fetch(url):
    if not allowed(url):
        raise ValueError("WORLD_WORK_SOURCE_NOT_ALLOWLISTED")
    headers={"User-Agent":"B1B2-WorldTaskFactory/1.0","Accept":"application/vnd.github+json,application/json"}
    if urllib.parse.urlsplit(url).hostname==GH_HOST:
        if os.environ.get("GH_TOKEN"):
            headers["Authorization"]="Bearer "+os.environ["GH_TOKEN"]
        headers["X-GitHub-Api-Version"]="2022-11-28"
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=16) as rsp:
        final=rsp.geturl()
        if not allowed(final):raise ValueError("WORLD_WORK_REDIRECT_UNAPPROVED")
        raw=rsp.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:raise ValueError("WORLD_WORK_SOURCE_TOO_LARGE")
    return json.loads(raw.decode("utf-8"))

def seed_from_feed(data):
    if not isinstance(data,dict) or not isinstance(data.get("bounties"),list):
        raise ValueError("UNEXPECTED_BOUNTY_INDEX_SCHEMA")
    out=[];seen=set()
    for x in data["bounties"][:MAX_FEED]:
        if not isinstance(x,dict):continue
        link=str(x.get("url") or "")
        m=ALLOWED_REPO.fullmatch(link)
        if not m or link in seen:continue
        seen.add(link)
        amount=x.get("amountUsd")
        if not isinstance(amount,(int,float)) or isinstance(amount,bool) or not (amount>0 and amount<1e8):
            amount=None
        out.append({
            "id":f"{m.group(1)}_{m.group(2)}_{m.group(3)}".lower(),
            "original_url":link,
            "original_api_url":f"https://api.github.com/repos/{m.group(1)}/{m.group(2)}/issues/{m.group(3)}",
            "source_feed":BOUNTY_FEED,
            "feed_title":str(x.get("title") or "")[:180],
            "advertised_usd_or_unknown":amount,
            "feed_escrow_claim":str(x.get("escrow") or "unknown")[:130],
            "feed_open_pr_count":x.get("openCompetingPrs") if type(x.get("openCompetingPrs")) is int else None,
            "fee_or_escrow_independently_verified":False,
            "priority_score_from_untrusted_feed":x.get("score") if type(x.get("score")) is int else None,
            "funding_verified":False,"eligible_from_uganda_verified":False,
            "compatible_b1_b2_payment_verified":False,
            "original_issue_checked":False,"platform_submission_authorized":False,
            "external_submission_sent":False,"buyer_accepted":False,
            "btc_deposit_verified":False,
            "stage":"DISCOVERED",
        })
    return out

def qualify(row, issue, repo=None):
    """Inspect original source. Never promote a task to FUNDED_ELIGIBLE by inference."""
    result=dict(row)
    if not isinstance(issue,dict) or issue.get("pull_request") or issue.get("state")!="open":
        result.update(stage="REJECTED_SOURCE_NOT_OPEN",blockers=["ORIGINAL_ISSUE_NOT_OPEN"])
        return result
    body=str(issue.get("body") or "")[:MAX_BODY]
    title=str(issue.get("title") or "")[:180]
    result["original_issue_checked"]=True
    result["original_title"]=title
    result["original_updated_at"]=str(issue.get("updated_at") or "")
    result["original_comments_count"]=issue.get("comments") if type(issue.get("comments")) is int else None
    result["original_issuer"]=str((issue.get("user") or {}).get("login") or "")[:80]
    result["original_source_sha256"]=hashlib.sha256((title+"\n"+body).encode()).hexdigest()
    eligibility=bounty_evaluate(issue,[],repo or {})
    reasons=list(eligibility.get("flags",[]))
    if any(w in body.lower() for w in STOP_WORDS):
        reasons.append("SPONSOR_FORBIDS_UNSOLICITED_EXTERNAL_PRS")
    # A real open issue can still be unfunded/unavailable; default to HOLD.
    result["blockers"]=sorted(set(reasons))
    if eligibility.get("critical_blocker"):
        result["stage"]="REJECTED_EXTERNAL_SUBMISSION"
    elif "NO_EXPLICIT_REWARD_IN_SOURCE" in reasons:
        result["stage"]="HOLD_ISSUER_REWARD_UNCONFIRMED"
    elif "SOME_COMMENTS_UNREAD" in reasons:
        result["stage"]="HOLD_RECENT_SPONSOR_COMMENTS_UNREAD"
    else:
        result["stage"]="ORIGINAL_SOURCE_CHECKED"
    result["funding_verified"]=False
    result["eligible_from_uganda_verified"]=False
    result["compatible_b1_b2_payment_verified"]=False
    result["claimed_bounty_is_earned"]=False
    result["requires_sponsor_confirmation"]=[
        "Verified available budget/escrow under sponsor control",
        "Uganda eligibility, available assignment slot and original contribution route",
        "Explicit correct B1/B2 compatible payout network and amount",
        "Sponsor approval or permitted claim process before contribution",
    ]
    return result

def discover(feed_fetch=fetch, issue_fetch=fetch):
    owner=root_owner()
    report={"schema":"B1B2_WORLD_TO_PAID_WORK_DISCOVERY_V1",
            "at_utc":now(),"owner":owner,
            "index_url":BOUNTY_FEED,"index_status":"UNAVAILABLE",
            "original_issue_checks_attempted":0,
            "original_issue_checks_succeeded":0,
            "leads":[],"error_types":[],"confirmed_funded_eligible_jobs":0,
            "external_submissions_sent":0,"received_funds_verified":0}
    try:
        raw=feed_fetch(BOUNTY_FEED)
        seeds=seed_from_feed(raw)
        report["index_status"]="PUBLIC_FEED_READ_"+str(len(seeds))+"_CANDIDATES"
        report["feed_generated_at"]=raw.get("generatedAt")
    except (ValueError,OSError,TimeoutError,KeyError,TypeError) as e:
        report["error_types"].append(type(e).__name__)
        return report
    rows=[]
    for i,row in enumerate(seeds):
        if i>=MAX_ORIGINAL_LOOKUPS:
            row["stage"]="QUEUED_ORIGINAL_VERIFICATION"
            rows.append(row)
            continue
        report["original_issue_checks_attempted"]+=1
        try:
            source=issue_fetch(row["original_api_url"])
            out=qualify(row,source)
            if out["original_issue_checked"]:
                report["original_issue_checks_succeeded"]+=1
            rows.append(out)
        except (ValueError,OSError,TimeoutError,KeyError,TypeError) as e:
            row["stage"]="HOLD_ORIGINAL_SOURCE_UNAVAILABLE"
            row["original_error_type"]=type(e).__name__
            rows.append(row)
    report["leads"]=rows
    report["stage_counts"]={s:sum(x["stage"]==s for x in rows) for s in sorted({x["stage"] for x in rows})}
    return report

def portfolio_build():
    """Produce one real, tested, useful original deliverable, but NOT a paid order."""
    import importlib.util
    task=HERE/"commercial-work/invoice-payment-reconciliation"
    sys.path.insert(0,str(task))
    from reconcile import reconcile
    invoice=[
        {"invoice_id":"INV-001","customer":"Synthetic Customer A","amount":"100.00"},
        {"invoice_id":"INV-002","customer":"Synthetic Customer B","amount":"75.00"},
        {"invoice_id":"INV-003","customer":"Synthetic Customer C","amount":"50.00"},
    ]
    paid=[
        {"payment_id":"PMT-001","invoice_id":"INV-001","amount":"40.00"},
        {"payment_id":"PMT-002","invoice_id":"INV-001","amount":"60.00"},
        {"payment_id":"PMT-003","invoice_id":"INV-002","amount":"80.00"},
        {"payment_id":"PMT-004","invoice_id":"UNKNOWN","amount":"20.00"},
    ]
    result=reconcile(invoice,paid)
    assert result["totals"]=={
        "invoiced":"225.00","allocated_paid":"180.00",
        "unmatched_paid":"20.00","outstanding":"50.00"}
    assert {x["status"] for x in result["invoices"]}=={"paid","overpaid","unpaid"}
    test=subprocess.run([sys.executable,str(task/"test_reconcile.py")],
                        cwd=ROOT,capture_output=True,text=True,timeout=25)
    if test.returncode:
        raise RuntimeError("ACTUAL_CSV_RECONCILIATION_TEST_FAILED:"+test.stderr[-300:])
    target=OUT/"deliverables"/"invoice-reconciliation-synthetic-example"
    target.mkdir(parents=True,exist_ok=True)
    (target/"report.json").write_text(json.dumps(result,indent=2)+"\n")
    md="# Original invoice/payment matching proof — ready to demonstrate\n\n"
    md+="This is TESTED ORIGINAL work on **fictional records only**, not paid customer delivery.\n\n"
    md+="Invoice total: 225.00; allocated payments: 180.00; outstanding 50.00; unmatched 20.00.\n\n"
    md+="Cases covered: paid, overpaid, unpaid, partial and unmatched-payment handling (additional cases in unit tests).\n\n"
    md+="Original production source: crypto-agents/commercial-work/invoice-payment-reconciliation/reconcile.py\n\n"
    md+="Existing original tests: crypto-agents/commercial-work/invoice-payment-reconciliation/test_reconcile.py\n\n"
    md+="**Not yet submitted to an external customer; no fee agreed and no payment due from this example.**\n"
    (target/"DELIVERABLE_REPORT.md").write_text(md)
    proof={"status":"ORIGINAL_PUBLIC_PORTFOLIO_DELIVERABLE_TESTED",
           "artifact_dir":str(target.relative_to(ROOT)),
           "result_sha256":sha(result),"real_python_test_return_code":test.returncode,
           "completed_utc":now(),"client_or_payer":None,
           "accepted_paid_scope":False,"externally_submitted":False,
           "earnings_verified":False}
    (target/"evidence.json").write_text(json.dumps(proof,indent=2)+"\n")
    return proof

def payment_request(task, fleet):
    """After sponsor approval, produce a non-transmitted native Bitcoin invoice message."""
    from btc_receiver_safety import require_approved_receiver
    wallets={"B1":("transferexperiment",B1),"B2":("BountyScoutAI",B2)}
    if fleet not in wallets:raise ValueError("UNKNOWN_FLEET")
    actual_name,addr=wallets[fleet]
    require_approved_receiver(actual_name,addr)
    if not isinstance(task,dict):raise ValueError("INVALID_TASK")
    requirements=("accepted_deliverable_url","sponsor_acceptance_url",
                  "agreed_sats","payer_identity","btc_mainnet_settlement_explicit")
    if any(not task.get(k) for k in requirements):
        raise ValueError("PAYMENT_REQUEST_BLOCKED_MISSING_PAYER_ACCEPTANCE")
    if type(task["agreed_sats"]) is not int or task["agreed_sats"]<=0:
        raise ValueError("PAYMENT_AMOUNT_NOT_POSITIVE_SATOSHIS")
    if not str(task["accepted_deliverable_url"]).startswith("https://") or not str(task["sponsor_acceptance_url"]).startswith("https://"):
        raise ValueError("NO_PUBLIC_ACCEPTANCE_SOURCE")
    message=("Thank you for accepting the completed scope. Reference: "+
             task["accepted_deliverable_url"]+". Acceptance: "+task["sponsor_acceptance_url"]+
             ". Please settle the agreed "+str(task["agreed_sats"])+
             " satoshis on native Bitcoin MAINNET ONLY to "+addr+
             ". After payment, please share the mainnet transaction ID for verification. "+
             "Do not send Lightning, sBTC/Stacks, testnet BTC or unrelated assets to this address.")
    return {"network":"bitcoin-mainnet","fleet":fleet,"address":addr,
            "draft_message_not_sent":message,"ready_to_request_but_not_sent":True,
            "payment_verified":False}

def save(report,proof=None):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"discovery.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    lines=["# Worldwide task-to-payment production board","",
           "Owner order: "+report["owner"]["owner_order_id"],
           "Public index: "+report["index_url"],
           "Index: "+report["index_status"],
           "Original issues inspected: "+str(report["original_issue_checks_succeeded"])+"/"+
           str(report["original_issue_checks_attempted"]),
           "Confirmed funded, Uganda-eligible, correct-network offers: 0",
           "Authenticated external submissions sent: 0",
           "Earned BTC receipt verified by this research: 0","",
           "## Workflow stages","",
           "DISCOVERED → ORIGINAL_SOURCE_CHECKED → FUNDED_ELIGIBLE → SCOPE_ACCEPTED → DELIVERABLE_TESTED → SUBMITTED_VERIFIED → SPONSOR_ACCEPTED → PAYMENT_REQUEST_CONFIRMED → ONCHAIN_PAYMENT_VERIFIED","",
           "Every stage requires separate proof, and none is automatically inferred from a public bounty board.","",
           "## Public original-source opportunities inspected",""]
    for row in report["leads"][:25]:
        lines+=["- "+row["feed_title"]+" — "+row["stage"]+" — "+row["original_url"]+
                (" — "+",".join(row.get("blockers",[])) if row.get("blockers") else "")]
    lines+=["","## Completed original demonstration (not customer work)",
            "- "+(proof["artifact_dir"] if proof else "Not run"),
            "- No submitted claim or outstanding invoice was created from the synthetic example.",
            "","## Real payment request gate",
            "- Require the original issuer to accept the work and agree on the precise BTC-mainnet fee.",
            "- Only then create a payer-facing request to an approved B1/B2 Bitcoin mainnet address.",
            "- Outbound message/PR requires permitted signed-in third-party account action.",
            "- Confirm incoming output with two independent explorers and payer reference; TXID alone does not prove earnings.",
            "","## No-permission actions",
            "No reading/sending/drafting emails, impersonation, bulk postings, private-key use, spending or miner use on cloud servers. "
            "The feed may be stale; unscreened offers are not proof of money."]
    (OUT/"REPORT.md").write_text("\n".join(lines)+"\n")
    print("B1B2_WORLD_TASK_FACTORY_RESULT "+json.dumps({
        "source_status":report["index_status"],
        "discovered":len(report["leads"]),
        "original_checked":report["original_issue_checks_succeeded"],
        "blocked_or_held":sum(x["stage"]!="ORIGINAL_SOURCE_CHECKED" for x in report["leads"]),
        "funded_verified":0,"outbound_submissions":0,
        "tested_original_deliverable":bool(proof),"earnings_verified":0}))

def self_test():
    require_all_owner_receivers()
    assert len(STAGES)==9
    assert not allowed("https://api.github.com.evil.com/x")
    assert not allowed("http://api.github.com/x")
    assert not allowed("https://bad.io")
    assert len(seed_from_feed({"bounties":[
        {"url":"https://github.com/Example/Project/issues/12","amountUsd":50,"title":"fix bug"},
        {"url":"https://github.com/Example/Project/issues/12","amountUsd":50},
        {"url":"https://evil.com/x","amountUsd":200}]}))==1
    seed=seed_from_feed({"bounties":[
        {"url":"https://github.com/IES-BoilerRoom/grpc-http2-hpack-framing/issues/2",
         "amountUsd":350,"title":"Example"}]})[0]
    blocked=qualify(seed,{"state":"open","title":"$350 bounty","body":
                          "Automated conformance mirror; manual pull requests from human engineers are not reviewed on this mirror.",
                          "user":{"login":"IES-BoilerRoom"}})
    assert blocked["stage"]=="REJECTED_EXTERNAL_SUBMISSION"
    assert not blocked["funding_verified"]
    original=qualify(seed,{"state":"open","title":"Fix bug","body":"Maintainer bounty pays $350, all contributors welcome",
                           "user":{"login":"Example"}})
    assert original["stage"]=="ORIGINAL_SOURCE_CHECKED"
    assert not original["eligible_from_uganda_verified"]
    try:payment_request({"agreed_sats":1000},"B1")
    except ValueError:pass
    else:raise AssertionError("PAYMENT_BEFORE_SPONSOR_ACCEPTANCE_WAS_POSSIBLE")
    try:payment_request({"accepted_deliverable_url":"https://github.com/foo/bar/pull/1",
                         "sponsor_acceptance_url":"https://github.com/foo/bar/issues/1",
                         "agreed_sats":1000,"payer_identity":"Client",
                         "btc_mainnet_settlement_explicit":False},"B2")
    except ValueError:pass
    else:raise AssertionError("WRONG_NETWORK_PAYMENT_REQUEST_POSSIBLE")
    print("B1B2_WORLD_WORK_SOURCE_PAYMENT_GATES_PASS")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--discover",action="store_true")
    ap.add_argument("--build-portfolio",action="store_true")
    args=ap.parse_args()
    self_test()
    if args.self_test:return
    report=discover() if args.discover else {
        "owner":root_owner(),"index_url":BOUNTY_FEED,"index_status":"NOT_CHECKED",
        "original_issue_checks_succeeded":0,"original_issue_checks_attempted":0,
        "leads":[]}
    proof=portfolio_build() if args.build_portfolio else None
    save(report,proof)

if __name__=="__main__":main()
