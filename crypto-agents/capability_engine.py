"""ORD-026: implementable evidence-first planning/checking for every activated role.
No external calls here. This helper cannot prove a payer, contract or receipt.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

PACK = json.loads(Path("crypto-agents/capability_pack.json").read_text(encoding="utf-8"))
RISK = re.compile(r"\b(pay(?:ment)?\s+first|deposit fee|activation fee|send crypto|seed phrase|private key|wallet connect|guaranteed return|airdrop claim|advance fee|pay to apply)\b", re.I)
PAY_SIGNAL = re.compile(r"\b(paid|bounty|contract|hiring|remote job|freelance|bookkeep|accountant|reward|earn|task)\b", re.I)
EXPLICIT_CRYPTO = re.compile(r"\b(BTC|Bitcoin|USDC|ETH|Solana|crypto|stablecoin)\b", re.I)

def _extract(evidence):
    """Convert only recorded source evidence into a compact candidate set."""
    if not isinstance(evidence, list):
        return []
    rows = []
    for raw in evidence[:8]:
        if not isinstance(raw, dict):
            continue
        possible = raw.get("candidates") if isinstance(raw.get("candidates"), list) else [raw]
        for item in possible[:2]:
            if not isinstance(item, dict):
                continue
            link = str(item.get("url") or "")
            if not link.startswith("https://") or len(link) > 450:
                continue
            rows.append({
                "url": link,
                "title": str(item.get("title") or "Untitled source")[:120],
                "excerpt": str(item.get("excerpt") or item.get("evidence_excerpt") or item.get("description") or "")[:300],
                "source_status": str(item.get("source_status") or item.get("status") or "unverified")[:70]
            })
    # Avoid duplicate links, but never invent links or payer evidence.
    return list({x["url"]: x for x in rows}.values())[:4]

def capability_review(agent_id: str, parent_id: str, assignment: str, evidence, tools=None):
    rows = _extract(evidence)
    reviewed = []
    for row in rows:
        txt = row["title"] + " " + row["excerpt"]
        flags = []
        if RISK.search(txt):
            flags.append("Potential fee, wallet or credential scam signal: independently verify and avoid paying")
        if not PAY_SIGNAL.search(txt):
            flags.append("No clear paid-work signal in excerpt")
        if not EXPLICIT_CRYPTO.search(txt):
            flags.append("No explicit cryptocurrency settlement evidenced")
        # This is a triage weight only, never a payment probability/offer confirmation.
        triage = 1 + (2 if PAY_SIGNAL.search(txt) else 0) + (1 if EXPLICIT_CRYPTO.search(txt) else 0) - (3 if RISK.search(txt) else 0)
        reviewed.append({
            "url": row["url"], "title": row["title"],
            "triage_weight_not_payment_probability": triage,
            "unverified": True,
            "source_status": row["source_status"],
            "risk_and_unknowns": flags + [
                "Original payer, current availability, scope, acceptance and real amount not yet authenticated",
                "Country eligibility and coin/token network settlement not yet confirmed"
            ]
        })
    reviewed.sort(key=lambda x: x["triage_weight_not_payment_probability"], reverse=True)
    available = tools if isinstance(tools, list) else []
    attempted = sum(1 for x in available if isinstance(x, dict) and x.get("status") in ("source_checked","public_source_checked"))
    next_action = ("Open and independently verify the original payer and payment terms at " + reviewed[0]["url"]
                   if reviewed else "Choose another permitted original-source public job or bounty search")
    return {
        "capability_pack": PACK["version"],
        "agent_id": str(agent_id),
        "parent_id": str(parent_id),
        "assigned_task": str(assignment)[:280],
        "plan": [
            "Find a current primary-source paid assignment in a feasible area",
            "Check original payer, deliverable, deadline, country eligibility and no-fee terms",
            "Confirm crypto asset, exact network and owner-approved receiving route",
            "Prepare truthful offer or handoff; only send via already permitted authenticated action"
        ],
        "candidate_reviews": reviewed,
        "tools_reported_available": len(available),
        "read_only_site_checks_recorded": attempted,
        "critical_challenge": "A search hit, posted bounty or AI-generated statement is not accepted paid work or a verified deposit",
        "best_next_authorized_step": next_action,
        "delivery_requirement": "Individual evidence-backed document with role ID, parent, real tool/model status, results, unknowns, next step and payment verification status",
        "no_unsupported_capability_claim": True,
        "independent_payment_receipts_verified": [],
        "status": "deterministic_triage_executed_no_external_side_effects"
    }

def short_model_context(review):
    """Prioritize useful facts early in the small 1.8k character prompt window."""
    if not isinstance(review, dict):
        return ""
    return json.dumps({
        "plan": review.get("plan", [])[:2],
        "best_next": review.get("best_next_authorized_step", ""),
        "source_reviews": [
            {"url": r.get("url"),"unknowns":r.get("risk_and_unknowns", [])[:2]}
            for r in review.get("candidate_reviews", [])[:2]
        ],
        "no_claimed_payment": True,
        "mandatory_document": True
    }, ensure_ascii=False)[:950]
