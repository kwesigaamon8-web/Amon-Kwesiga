"""Make original B-agent organizational roles useful for BOUNDED source checks.

Each CPU-executed check is REAL code work attributed to a distinct configured
role tier. It is NOT a separate LLM, independent AI agent, online Moltbook
account, customer contract, or verified crypto payment. The goal is to send
better-evidenced candidate work to the limited ACTUAL AI workers.

The full original 750,377,265,360 role namespace is addressable on demand.
No hundreds-of-billions iteration or external account login is attempted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

from b_registered_account_worker_map import role_at_global_index, ROLES_PER_ACCOUNT
from b_certified_agent_service_router import FLEETS, PER_DIRECTOR, OFFSETS, ROLES_PER_DIRECTOR

ISSUE=re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/issues/([0-9]+)$")
CHECKS=("D","A","M","W","S","G","H")
LIMIT=45

def role_for_check(fleet,source_url,tier):
    if fleet not in FLEETS or tier not in CHECKS:raise ValueError("Invalid account or tier")
    digest=hashlib.sha256((fleet+"|"+source_url+"|"+tier).encode("utf-8")).digest()
    director=int.from_bytes(digest[:4],"big")%10
    ordinal=int.from_bytes(digest[4:12],"big")%PER_DIRECTOR[tier]
    ix=FLEETS.index(fleet)*ROLES_PER_ACCOUNT+director*ROLES_PER_DIRECTOR+OFFSETS[tier]+ordinal
    p=role_at_global_index(ix)
    assert p["company"]==fleet and p["tier"]==tier
    return {"role_id":fleet+"/"+p["worker_role"],"global_original_role_index":ix,
            "registered_agent":p["registered_agent_handle"]}

def inspect_evidence(candidate,tier):
    """A real deterministic audit computation. UNVERIFIED stays unverified."""
    checks=candidate.get("checks")
    checks=checks if isinstance(checks,dict) else {}
    url=candidate["original_url"]
    title=str(candidate.get("title") or "")[:170]
    if tier=="D":
        good=bool(ISSUE.fullmatch(url))
        return {"check":"Original source link format","result":"SOURCE_LINK_FORM_VALID" if good else "INVALID_SOURCE_LINK",
                "client_permission_proven":False}
    if tier=="A":
        original=str(candidate.get("original_repo") or "")
        source_match=ISSUE.fullmatch(url)
        match=bool(source_match and original==source_match.group(1)+"/"+source_match.group(2))
        return {"check":"Original GitHub repository provenance","result":"REPO_PATH_MATCHES_SOURCE" if match else "NOT_CONFIRMED_FROM_PROSPECT_METADATA",
                "client_permission_proven":False}
    if tier=="M":
        return {"check":"Client authority and willingness","result":"NEEDS_REAL_SPONSOR_AND_ELIGIBILITY_CONFIRMATION",
                "client_permission_proven":False}
    if tier=="W":
        claimed=(checks.get("explicit_paid_work_reward") is True and
                 checks.get("mentions_specific_reward_amount") is True)
        secondary=(candidate.get("secondary_payer_history_claim") is True and
                   isinstance(candidate.get("secondary_amount_usd_claim"),(int,float)))
        return {"check":"Actual monetary offer evidence","result":("UNVERIFIED_PRIMARY_DESCRIPTION_SIGNAL" if claimed
                else "UNVERIFIED_SECONDARY_LISTING_CLAIM" if secondary else "NO_CONFIRMED_REWARD_AMOUNT"),
                "real_funded_bounty_proven":False}
    if tier=="S":
        scoped=checks.get("describes_actual_work") is True
        return {"check":"Specific work scope","result":"WORK_TERMS_REQUIRE_SOURCE_REVIEW" if scoped
                else "WORK_SCOPE_NOT_YET_CONFIRMED",
                "title_context":title,"deliverable_accepted_by_buyer":False}
    if tier=="G":
        sufficient=all(checks.get(k) is True for k in (
            "no_obvious_deposit_or_key_request",
            "not_automated_digest_or_secondary_mirror",
            "not_marked_already_awarded_in_description"))
        return {"check":"Source-screen risk control","result":"PRELIMINARY_SCREEN_ONLY" if sufficient
                else "UNSCREENED_OR_INCOMPLETE_SOURCE_CHECKS",
                "security_or_platform_approval_proven":False}
    if tier=="H":
        network=candidate.get("payout_network_accepted")
        return {"check":"Owner-wallet settlement compatibility",
                "result":"NO_VERIFIED_NETWORK_OR_PAYER_APPROVAL" if network is None
                else "CLAIM_REQUIRES_OWNER_RECONFIRMATION",
                "wallet_address_shared_to_external_party":False,
                "correct_network_receipt_proven":False}
    raise ValueError("Unsupported audit role tier")

def inspect_feed(feed,limit=LIMIT):
    if type(limit)!=int or not 0<=limit<=LIMIT:raise ValueError("Candidate limit out of range")
    if not isinstance(feed,dict):raise ValueError("Source must be JSON dictionary")
    sourced=feed.get("candidates") or []
    if not isinstance(sourced,list):raise ValueError("Candidates must be a list")
    reviewed=[]
    tasks=[]
    seen=set()
    for candidate in sourced:
        if len(reviewed)>=limit:break
        if not isinstance(candidate,dict):continue
        fleet=candidate.get("assigned_fleet")
        url=candidate.get("original_url")
        if fleet not in FLEETS or not isinstance(url,str) or not ISSUE.fullmatch(url):
            continue
        if candidate.get("status")!="POSSIBLE_PAID_TASK_UNVERIFIED":continue
        if url in seen:continue
        seen.add(url)
        findings=[]
        for tier in CHECKS:
            role=role_for_check(fleet,url,tier)
            inspection=inspect_evidence(candidate,tier)
            task_id=hashlib.sha256((fleet+"/"+url+"/"+tier).encode("utf-8")).hexdigest()[:18]
            result={"source_url":url,"task_id":task_id,"role_tier":tier,
              **role,
              "actual_rule_engine_check_executed":True,
              "execution_type":"REAL_PYTHON_CPU_RULE_CHECK_NOT_AI_MODEL",
              "check_output":inspection,
              "external_customer_contact":False,
              "paid_work_delivered":False,
              "crypto_receipt_claimed":False}
            tasks.append(result)
            findings.append({"tier":tier,"task_id":task_id,"finding":inspection["result"]})
        reviewed.append({
            "source_url":url,"title":str(candidate.get("title") or "")[:170],
            "company":fleet,
            "assigned_company_director":candidate.get("assigned_company_director"),
            "status":"NEEDS_DIRECT_BUYER_FUNDING_ELIGIBILITY_AND_NETWORK_CHECK",
            "candidate_is_not_a_verified_paid_job":True,
            "preliminary_cpu_checks_completed":len(CHECKS),
            "review_findings":findings,
            "next_real_AI_worker_action":"Open the original issue and its current comments, "
                 "check sponsor/maintainer authority, scope, prior award status, true funding, "
                 "eligibility and accepted currency; prepare one ORIGINAL focused fix or "
                 "proposal only after consent and supported evidence.",
        })
    unique=set(x["role_id"] for x in tasks)
    by_fleet={f:{"source_prospects_screened":sum(1 for x in reviewed if x["company"]==f),
                 "real_python_review_tasks_executed":sum(1 for x in tasks if x["registered_agent"]==f),
                 "distinct_configured_roles_attributed":len(set(x["role_id"] for x in tasks if x["registered_agent"]==f)),
                 "independent_AI_model_processes_started_by_this_batch":0}
             for f in FLEETS}
    return {"schema":"B_TWO_REGISTERED_AGENTS_BOUNDED_REAL_CPU_TASK_BATCH_V1",
      "processed_at_utc":datetime.now(timezone.utc).isoformat(),
      "full_organization_addressable_role_capacity":750_377_265_360,
      "per_agent_role_capacity":ROLES_PER_ACCOUNT,
      "actual_software_processes":"ONE_PYTHON_CHECK_ENGINE",
      "real_CPU_check_tasks_executed":len(tasks),
      "distinct_configured_roles_receiving_task_attribution":len(unique),
      "actual_independent_AI_models_started_by_this_program":0,
      "actual_external_agent_platform_messages_sent":0,
      "actual_funded_buyers_or_contracts_verified":0,
      "actual_crypto_payments_verified":0,
      "source_scan_errors_reported":feed.get("source_errors") or [],
      "source_candidates_input":len(sourced),
      "prospects_preliminarily_reviewed":len(reviewed),
      "registered_agent_accounts":by_fleet,
      "prospects":reviewed,
      "auditable_CPU_tasks":tasks,
      "limitations":"Rule engine provides pre-screening, not live LLM inference, maintainer consent, an accepted job, credential, client contact, or payment. Original issue/comments and payout terms still require human or authorized real AI verification."}

def save(out,report):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/"delegated-agent-work.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# B1/B2 — bounded real prospect review under registered agent accounts","",
       "Two organizational handles: transferexperiment and BountyScoutAI.",
       "Original role namespace: **750,377,265,360 configured positions**.",
       f"Real Python source-check tasks completed: **{report['real_CPU_check_tasks_executed']}**.",
       f"Distinct role IDs attributed these tasks: **{report['distinct_configured_roles_receiving_task_attribution']}**.",
       f"Genuine independent AI model processes launched by this batch: **0**.",
       "Paying customers, accepted contracts, incoming cryptocurrencies proved: **0**.","",
       "Each check is a real CPU rule executed on source metadata and attributed to a potential delegated role; it is NOT an independent active AI agent.","",
       "| Account | Source prospects reviewed | CPU checks | Role IDs referenced |",
       "|---|---:|---:|---:|"]
    for fleet,x in report["registered_agent_accounts"].items():
        lines.append(f"| {fleet} | {x['source_prospects_screened']} | {x['real_python_review_tasks_executed']} | {x['distinct_configured_roles_attributed']} |")
    lines+=["","## Prospect due diligence queue — external payer not verified"]
    for p in report["prospects"][:15]:
        lines.append(f"- **{p['company']}** {p['title']} — {p['source_url']}. "
                     "Seven preliminary checks done; sponsor, eligibility and network still require real approval")
    if not report["prospects"]:
        lines.append("- No eligible formatted candidate sources available in the current feed. Do not invent prospect checks.")
    lines+=["","Next steps: activate real model workers on the most credible original issues, produce original specific work, contact only permitted buyers and report actual acceptance and independently confirmed receipts."]
    (out/"delegated-agent-work.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("B_AGENT_REAL_CPU_TASK_BATCH",json.dumps({
       "source_candidates":report["source_candidates_input"],
       "prospects_reviewed":report["prospects_preliminarily_reviewed"],
       "real_cpu_checks":report["real_CPU_check_tasks_executed"],
       "unique_attributed_role_ids":report["distinct_configured_roles_receiving_task_attribution"],
       "independent_ai_model_calls_by_this_batch":0,"actual_crypto_receipts":0}))

def self_test():
    example={
       "status":"POSSIBLE_PAID_TASK_UNVERIFIED",
       "original_url":"https://github.com/paid/repo/issues/42",
       "original_repo":"paid/repo",
       "assigned_fleet":"transferexperiment","title":"$50 fix deterministic CSV export",
       "checks":{"explicit_paid_work_reward":True,"mentions_specific_reward_amount":True,
         "describes_actual_work":True,"no_obvious_deposit_or_key_request":True,
         "not_automated_digest_or_secondary_mirror":True,
         "not_marked_already_awarded_in_description":True}}
    second={**example,"assigned_fleet":"BountyScoutAI",
            "original_url":"https://github.com/paid/repo/issues/43",
            "checks":{},"title":"Unverified second client issue"}
    feed={"candidates":[example,example,second,
      {"original_url":"file:///etc/passwd","assigned_fleet":"transferexperiment","status":"POSSIBLE_PAID_TASK_UNVERIFIED"},
      {**example,"original_url":"https://github.com/paid/repo/issues/99","status":"REVIEW_OR_REJECT"}]}
    out=inspect_feed(feed)
    assert out["prospects_preliminarily_reviewed"]==2
    assert out["real_CPU_check_tasks_executed"]==14
    assert out["actual_independent_AI_models_started_by_this_program"]==0
    assert out["registered_agent_accounts"]["BountyScoutAI"]["real_python_review_tasks_executed"]==7
    assert set(x["role_tier"] for x in out["auditable_CPU_tasks"])==set(CHECKS)
    for row in out["auditable_CPU_tasks"]:
        assert row["actual_rule_engine_check_executed"] is True
        assert row["registered_agent"] in FLEETS
        assert row["role_id"].startswith(row["registered_agent"]+"/")
        assert row["crypto_receipt_claimed"] is False
    assert inspect_feed({"candidates":[]})["real_CPU_check_tasks_executed"]==0
    try:inspect_feed(feed,10000)
    except ValueError:pass
    else:raise AssertionError("Unbounded candidate batch allowed")
    print("B_REGISTERED_AGENT_REAL_DELEGATED_CPU_CHECKS_SELFTEST_PASS",
       json.dumps({"test_prospects":2,"bounded_CPU_checks":14,
                   "distinct_tiers":7,"real_models_started":0,"actual_payments":0}))

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--self-test",action="store_true")
    cli.add_argument("--feed",default="paid-opportunity-reports/new-earning-lanes.json")
    cli.add_argument("--out",default="registered-agent-work-batches")
    args=cli.parse_args()
    if args.self_test:self_test()
    else:
        try:feed=json.loads(Path(args.feed).read_text(encoding="utf-8"))
        except (OSError,ValueError):feed={"candidates":[],"source_errors":["FEED_MISSING_OR_INVALID"]}
        save(args.out,inspect_feed(feed))
