"""Six Enigma AI research roles, one per separately connected mailbox alias.

Read-only Gmail is available to ChatGPT through its own account connections;
NOT to GitHub runners. This public code stores no mailbox addresses, IDs or
tokens and never attempts Gmail access, messages, account creation or posting.

Actual model calls: only a successful call in run_agents(enable_model=True).
"""
from __future__ import annotations
import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

OWNER = "Enigma"
ROLE_NAMES = (
    ("ENIGMA-01", "Software verifier", "QA the original 1,000 program IDs and test failures", "SW-001 to SW-1000 are browser configurations, not 1,000 standalone SaaS businesses"),
    ("ENIGMA-02", "Humanity research analyst", "Find reliable country problems and check evidence before claiming demand", "249 ISO country/territory task slots, not 249 finished market studies"),
    ("ENIGMA-03", "Open-source reviewer", "Check licenses, notices, tests and safe reuse before copying code", "Do not copy unlicensed source; public code is not necessarily open source"),
    ("ENIGMA-04", "Customer opportunity analyst", "Propose actionable scope for buyer-initiated public enquiries", "No paid buyer or signed agreement is established by a generated proposal"),
    ("ENIGMA-05", "BTC payments evidence auditor", "Distinguish publicly visible BTC receipts from guesses or donations", "No payment received without independent correct-chain transaction proof"),
    ("ENIGMA-06", "Account connection auditor", "Review what six Gmail connections can do without granting them to runners", "Six ChatGPT Gmail connections are NOT six new platform identities or agent credentials"),
)
POLICY = (
    "Never send, forward, reply to, draft, delete, label or alter any email.",
    "No Gmail credentials, email contents or connected account IDs are available in GitHub.",
    "No unsolicited mass messaging, impersonation, signup, scraping, or remote account access.",
    "No wallet signing, spending, transfers, unapproved payment route changes or CPU mining on visitor devices.",
    "Virtual roles are not executing AI agents; only actual completed inference counts.",
)
STUDIO = "https://amon-kwesiga.onrender.com/studio/"
BUYER_REQUEST = "https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/new?template=paid-work-request.yml"

def role_packet(row):
    agent_id, title, task, limitation = row
    number = int(agent_id.split("-")[1])
    return {
        "id": agent_id,
        "owner": OWNER,
        "account_alias": "CONNECTED_GMAIL_%02d" % number,
        "title": title, "mission": task, "limitation": limitation,
        "gmail_connection_scope": "CHATGPT_ONLY_READ_ALLOWED_BY_OWNER_NO_GITHUB_OAUTH",
        "external_social_account_created": False,
        "connected_github_mailbox_credentials": False,
        "email_messages_sent": 0,
        "payment_route_url": STUDIO + "payment.html",
        "proposed_buyer_route": BUYER_REQUEST,
        "software": STUDIO + "global-1000.html",
        "evidence_sources": [
            STUDIO + "ENIGMA_COUNTRY_MARKET_RESEARCH.md",
            "https://datahelpdesk.worldbank.org/knowledgebase/articles/889392",
            "https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions",
        ],
        "safety_rules": list(POLICY),
        "model_inference_status": "NOT_RUN",
        "model_call_completed": False,
        "response": None,
    }

def run_agents(enable_model=False, generator=None, output_dir=None):
    """Run six distinct model prompts. Credentials and email are never accessed.

    For a real execution, generator is an existing transformers pipeline or other
    callable with the same interface; one successful call per agent is counted.
    """
    reports = []
    if output_dir is None:
        output_dir = Path("enigma-agent-reports")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_error = None
    if enable_model and generator is None:
        try:
            from transformers import pipeline
            generator = pipeline("text-generation",
                model=os.environ.get("ENIGMA_MODEL_ID", "HuggingFaceTB/SmolLM2-135M-Instruct"),
                device=-1)
        except Exception as exc:
            model_error = type(exc).__name__ + ": " + str(exc)[:180]
    for row in ROLE_NAMES:
        packet = role_packet(row)
        packet["executed_utc"] = datetime.now(timezone.utc).isoformat()
        if enable_model and generator is not None:
            prompt = (
                "You are a bounded research/quality-control assistant for Enigma. "
                "Provide 3 specific checks or practical actions grounded ONLY in evidence below. "
                "Never claim to have opened Gmail, sent messages, established buyers, "
                "accessed a wallet or run outside this call. "
                "No email or mass outreach. Return short plain text.\n"
                "ROLE: " + packet["title"] + "\n"
                "TASK: " + packet["mission"] + "\n"
                "KNOWN LIMIT: " + packet["limitation"] + "\n"
                "SOURCE: " + str(packet["evidence_sources"]) + "\n"
                "ANSWER:"
            )
            try:
                response = generator(prompt, max_new_tokens=96,
                                     do_sample=False, return_full_text=False)
                text = str(response[0].get("generated_text", "")).strip()
                if not text:
                    raise ValueError("Empty model output")
                packet["model_inference_status"] = "MODEL_COMPLETED_OUTPUT_NOT_FACT_VERIFIED"
                packet["model_call_completed"] = True
                packet["response"] = text[:2500]
            except Exception as exc:
                packet["model_inference_status"] = "MODEL_ERROR:" + type(exc).__name__
        elif enable_model:
            packet["model_inference_status"] = "MODEL_UNAVAILABLE:" + str(model_error or "UNKNOWN")
        (output_dir / (packet["id"] + ".json")).write_text(
            json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        reports.append(packet)
    summary = {
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "agents_defined": len(ROLE_NAMES),
        "account_aliases": len(ROLE_NAMES),
        "accounts_linked_to_github_runners": 0,
        "new_external_accounts_created": 0,
        "model_calls_completed": sum(int(r["model_call_completed"]) for r in reports),
        "email_messages_sent": 0,
        "onchain_payments_verified": 0,
        "reported_agent_artifacts": [r["id"] + ".json" for r in reports],
        "model_execution_requested": enable_model,
        "caveat": "The six Gmail connections remain exclusively under ChatGPT, not GitHub. Do not treat six role files as six live model processes.",
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return summary

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", action="store_true",
                        help="Attempt real local CPU inference; never uses Gmail")
    parser.add_argument("--out", default="enigma-agent-reports")
    args = parser.parse_args()
    run_agents(enable_model=args.model, output_dir=args.out)

if __name__ == "__main__":
    main()
