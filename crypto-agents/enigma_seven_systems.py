"""Enigma: 7 account-aligned systems x 8 independently auditable AI role calls.
Gmail/Google connections are owned by ChatGPT, NOT inherited by GitHub Actions.
No email addresses, account IDs, OAuth tokens or private contents are stored.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

OWNER = "Enigma"
SITE = "https://amon-kwesiga.onrender.com/studio/"
SYSTEMS = (
    ("G01","Product Engineering","Build and verify original helpful software"),
    ("G02","Country Research","Test market problems against dated primary evidence"),
    ("G03","Humanitarian Applications","Design accessible, low-bandwidth local tools"),
    ("G04","Open-source and Security","Review copyrights, attribution and software safety"),
    ("G05","Buyer Conversion","Evaluate opted-in enquiries and scope paid work"),
    ("G06","Delivery and Acceptance","Plan real deliverables and client approval tests"),
    ("G07","BTC and Mining Evidence","Audit correct-chain payments and mining economics"),
)
ROLES = (
    ("R01","Researcher","Frame a falsifiable question and evidence plan"),
    ("R02","Source checker","Identify reliable sources and missing facts"),
    ("R03","Tool builder","Propose one safe, bounded original software improvement"),
    ("R04","QA tester","Suggest reproducible software and data checks"),
    ("R05","Accessibility reviewer","Check local languages, privacy and low-data use"),
    ("R06","Buyer needs analyst","Specify opt-in real customer problems without fake leads"),
    ("R07","Payment reviewer","Require correct-network payment evidence; never invent receipts"),
    ("R08","Supervisor","Prioritize next tests and blockers with acceptance criteria"),
)
GUARDRAILS = (
    "No email sending, drafting, forwarding, replying, changing labels or deleting.",
    "No Gmail reading through GitHub; connected Gmail stays within ChatGPT.",
    "No false external account registration, unapproved OAuth or impersonation.",
    "No unsolicited spam, bulk posting or scraping of private contacts.",
    "No private wallet keys, spending, payouts, silent mining or fake receipts.",
)

def roles_for(system):
    match = [x for x in SYSTEMS if x[0] == system]
    if not match:
        raise ValueError("Expected G01..G07")
    sid, title, focus = match[0]
    for rid, label, task in ROLES:
        yield {
            "agent_id":f"ENIGMA-{sid}-{rid}", "owner":OWNER,
            "google_account_alias":"CONNECTED_GOOGLE_"+sid,
            "google_connection_scope":"READ_ONLY_THROUGH_CHATGPT_ONLY",
            "system":title, "system_focus":focus, "role":label, "task":task,
            "source_software":SITE+"global-1000.html",
            "country_research":SITE+"ENIGMA_COUNTRY_MARKET_RESEARCH.md",
            "buyer_form":"https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/new?template=paid-work-request.yml",
            "payment_route":SITE+"payment.html", "policy":list(GUARDRAILS),
            "model_call_completed":False, "model_inference_status":"NOT_STARTED",
            "output":None, "emails_sent":0, "external_accounts_created":0,
            "external_posts_published":0, "crypto_receipt_verified":False,
        }

def run_system(system, enable_model=False, generator=None, output_dir=None):
    folder=Path(output_dir) if output_dir else Path("enigma-seven-agent-artifacts")/system
    folder.mkdir(parents=True,exist_ok=True)
    load_failure=None
    if enable_model and generator is None:
        try:
            from transformers import pipeline
            generator=pipeline("text-generation",model=os.getenv(
                "ENIGMA_MODEL_ID","HuggingFaceTB/SmolLM2-135M-Instruct"),device=-1)
        except Exception as e:
            load_failure=type(e).__name__
    results=[]
    for agent in roles_for(system):
        if enable_model and generator is not None:
            prompt=("Enigma assistant. Produce three short evidence-first, actionable "
                    "recommendations. Do not claim to have accessed Gmail, social media, "
                    "live markets, blockchains, customers, payment accounts or links. "
                    "No email, mass marketing or false identity.\nSYSTEM: "+
                    agent["system"]+"; "+agent["system_focus"]+
                    "\nROLE: "+agent["role"]+"; "+agent["task"]+
                    "\nSOFTWARE: "+agent["source_software"]+"\nANSWER:")
            try:
                response=generator(prompt,max_new_tokens=96,do_sample=False,return_full_text=False)
                answer=str(response[0].get("generated_text") or "").strip()
                if not answer:
                    raise ValueError("Empty model output")
                agent["output"]=answer[:1800]
                agent["prompt_digest_sha256"]=hashlib.sha256(prompt.encode()).hexdigest()
                agent["model_call_completed"]=True
                agent["model_inference_status"]="ACTUAL_MODEL_CALL_COMPLETED_FACT_CHECK_REQUIRED"
            except Exception as e:
                agent["model_inference_status"]="MODEL_ERROR_"+type(e).__name__
        elif enable_model:
            agent["model_inference_status"]="MODEL_UNAVAILABLE_"+str(load_failure or "UNKNOWN")
        agent["observed_utc"]=datetime.now(timezone.utc).isoformat()
        (folder/(agent["agent_id"]+".json")).write_text(
            json.dumps(agent,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        results.append(agent)
    outcome={
        "owner":OWNER,"system_id":system,
        "roles_defined":len(results),
        "verified_model_calls_in_this_run":sum(r["model_call_completed"] for r in results),
        "model_requested":enable_model,
        "new_google_accounts_created":0,
        "new_external_accounts_linked":0,
        "github_access_to_google_mailboxes":False,
        "emails_sent":0,"external_posts":0,"bitcoin_receipts_verified":0,
        "artifact_files":[x["agent_id"]+".json" for x in results],
        "reported_utc":datetime.now(timezone.utc).isoformat(),
    }
    (folder/"summary.json").write_text(json.dumps(outcome,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(outcome,sort_keys=True))
    return outcome

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--system",required=True,choices=[r[0] for r in SYSTEMS])
    ap.add_argument("--model",action="store_true")
    ap.add_argument("--output",default=None)
    args=ap.parse_args()
    run_system(args.system,args.model,output_dir=args.output)
