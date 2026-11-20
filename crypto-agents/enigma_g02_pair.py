"""Enigma G02: two independent B1/B2-style model workers for second Google alias.
Google/Gmail connections remain in ChatGPT, never transferred to Github runners.
Each worker has a distinct proposed Moltbook identity; only a claim is a real
external account registration. No outbound email/social posts or account signup.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

OWNER = "Enigma"
GOOGLE_SLOT = "G02"
AGENTS = {
    "A": {
        "id": "ENIGMA-G02-A",
        "proposed_moltbook_name": "EnigmaG02Scout",
        "company": "Enigma Market Research",
        "role": "Worldwide market research and original software needs assessment",
        "mission": "Research verified local problems across countries and propose helpful free and paid software",
        "secret_name": "MOLTBOOK_ENIGMA_G02_A_API_KEY",
    },
    "B": {
        "id": "ENIGMA-G02-B",
        "proposed_moltbook_name": "EnigmaG02Developer",
        "company": "Enigma Helpful Software Delivery",
        "role": "Software engineering, reproducible QA and buyer-initiated project scoping",
        "mission": "Deliver tested helpful software prototypes and recommend approved buyer-specific paid work",
        "secret_name": "MOLTBOOK_ENIGMA_G02_B_API_KEY",
    },
}
PROJECT = "https://github.com/kwesigaamon8-web/Amon-Kwesiga"
SOFTWARE = "https://amon-kwesiga.onrender.com/studio/global-1000.html"
PAYMENT = "https://amon-kwesiga.onrender.com/studio/payment.html"
API_BASE = "https://www.moltbook.com/api/v1"
RULES = (
    "No Gmail API use, sending, draft, reply, label changes, forwarding or deletion.",
    "No automatic registration, public posts or unsolicited mass messages.",
    "No money-spending, wallet signing, mining on visitor hardware, fake invoices or payment claims.",
    "B1/B2 are separate existing Moltbook identities, not impersonated by these agents.",
    "Only a successful model response and recorded evidence counts as executed AI work.",
)

def read_json(url, token=None, timeout=8):
    if not url.startswith("https://") or len(url) > 450:
        raise ValueError("HTTPS URL required")
    req = urllib.request.Request(url, headers={
        "Accept": "application/json", "User-Agent": "EnigmaG02-EvidenceResearch/1.0",
        **({"Authorization": "Bearer " + token} if token is not None else {}),
    })
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read(90001)
    if len(raw) > 90000:
        raise ValueError("Evidence response exceeds limit")
    return json.loads(raw)

def public_evidence(which, fetcher=read_json):
    """Read only published public information; do not assert it was researched if offline."""
    data = []
    errors = []
    if which == "A":
        locations = [
            ("world-bank-ug-internet", "https://api.worldbank.org/v2/country/UG/indicator/IT.NET.USER.ZS?format=json&per_page=2"),
            ("github-software-issues", "https://api.github.com/repos/kwesigaamon8-web/Amon-Kwesiga/issues?state=open&per_page=4"),
        ]
    else:
        locations = [
            ("github-latest-release", "https://api.github.com/repos/kwesigaamon8-web/Amon-Kwesiga/commits?per_page=2"),
            ("github-software-issues", "https://api.github.com/repos/kwesigaamon8-web/Amon-Kwesiga/issues?state=open&per_page=4"),
        ]
    for label,url in locations:
        try:
            payload=fetcher(url)
            if isinstance(payload,(dict,list)):
                evidence=json.dumps(payload, ensure_ascii=False, separators=(",",":"))[:1600]
                data.append({"label":label,"url":url,"payload_excerpt":evidence,"status":"RETRIEVED_RAW_NEEDS_VERIFICATION"})
            else:
                raise ValueError("Invalid source response")
        except (ValueError,TimeoutError,OSError,urllib.error.URLError,json.JSONDecodeError) as exc:
            errors.append({"label":label,"status":type(exc).__name__})
    return data,errors

def moltbook_status(which, token=None, fetcher=read_json):
    """Read-only identity check. Never register or post using this automation."""
    expected=AGENTS[which]["proposed_moltbook_name"]
    if not token:
        return {"identity":expected,"verified":False,"status":"NO_ACCOUNT_CREDENTIAL_CONFIGURED"}
    try:
        # Never allow caller-provided URLs or redirects to an alternate host.
        obj=fetcher(API_BASE+"/agents/me",token=token)
        agent=obj.get("agent") or obj.get("data") or obj
        name=agent.get("name","") if isinstance(agent,dict) else ""
        ok=isinstance(name,str) and name.casefold()==expected.casefold()
        return {"identity":expected,"verified":ok,
                "status":"IDENTITY_CONFIRMED" if ok else "IDENTITY_MISMATCH"}
    except (ValueError,TimeoutError,OSError,urllib.error.URLError,json.JSONDecodeError) as exc:
        return {"identity":expected,"verified":False,"status":"LOOKUP_FAILED_"+type(exc).__name__}

def execute(which, model=None, evidence_fetcher=read_json, output_dir=None):
    if which not in AGENTS:
        raise ValueError("Choose first-account agent A or B")
    spec=AGENTS[which]
    out=Path(output_dir or "enigma-g02-artifacts")
    out.mkdir(parents=True, exist_ok=True)
    model_error=None
    if model is None:
        try:
            from transformers import pipeline
            model=pipeline("text-generation",
                model=os.environ.get("ENIGMA_MODEL_ID","HuggingFaceTB/SmolLM2-135M-Instruct"),
                device=-1)
        except Exception as exc:
            model_error=type(exc).__name__
    evidence,errors=public_evidence(which,fetcher=evidence_fetcher)
    prompt=(
        "You are a separate evidence-limited Enigma AI worker. "
        "Write three practical next actions, their tests and evidence limits. "
        "Do not invent customers, social posts, actual sales, incoming cryptocurrency, "
        "interviews, uploaded code, emails, registrations or model calls. "
        "No emailing, mass outreach, wallet signing or private data. "
        "Owner: Enigma. Company: "+spec["company"]+". Role: "+spec["role"]+
        ". Mission: "+spec["mission"]+
        ". Free working software: "+SOFTWARE+". Payment page for voluntary support "
        "or customer-agreed bespoke work: "+PAYMENT+". "
        "Actual bounded primary-source excerpts fetched in THIS run (may be empty): "
        +json.dumps(evidence,ensure_ascii=True)[:3100]+
        ". Source retrieval issues: "+json.dumps(errors)+". OUTPUT:"
    )
    actual_call=False
    answer=None
    status="NO_MODEL_AVAILABLE_"+str(model_error or "NOT_STARTED")
    if model is not None:
        try:
            response=model(prompt, max_new_tokens=160,do_sample=False,return_full_text=False)
            answer=str(response[0].get("generated_text") or "").strip()
            if not answer:
                raise ValueError("Empty model response")
            actual_call=True
            status="MODEL_CALL_COMPLETED_CONTENT_NEEDS_FACT_CHECK"
        except (Exception,) as exc:
            status="MODEL_ERROR_"+type(exc).__name__
            answer=None
    agent={
        "observed_utc":datetime.now(timezone.utc).isoformat(),
        "owner":OWNER,"system":"G02_ONLY",
        "google_account_alias":"CONNECTED_GOOGLE_G02_CHATGPT_ONLY",
        "agent_id":spec["id"],"proposed_external_identity":spec["proposed_moltbook_name"],
        "company":spec["company"],"mission":spec["mission"],
        "evidence":evidence,"source_errors":errors,
        "prompt_sha256":hashlib.sha256(prompt.encode()).hexdigest(),
        "model_inference_status":status,"actual_model_call_completed":actual_call,
        "generated_work_notes":answer,
        "moltbook_connection":moltbook_status(which,os.environ.get(spec["secret_name"],"").strip()),
        "owner_claim_verified":False,
        "gmail_connected_to_github":False,"gmail_read_in_run":False,
        "emails_sent":0,"external_posts_sent":0,"accounts_registered":0,
        "verified_customer_sales":0,"verified_crypto_receipts":0,
        "btc_payment_reference":PAYMENT,
        "policy":list(RULES),
    }
    file=out/(spec["id"]+".json")
    file.write_text(json.dumps(agent,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"agent_id":spec["id"],"actual_model_call_completed":actual_call,
        "source_records":len(evidence),"source_errors":len(errors),
        "moltbook_connection":agent["moltbook_connection"]["status"],
        "email_messages_sent":0,"external_accounts_registered":0,
        "evidence_file":str(file)},sort_keys=True))
    return agent

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--agent",required=True,choices=("A","B"))
    parser.add_argument("--output",default="enigma-g02-artifacts")
    args=parser.parse_args()
    execute(args.agent,output_dir=args.output)
