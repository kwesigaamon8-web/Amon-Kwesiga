"""One logical D10 payment director, read-only: BOTH B fleets, one evidence report.

This job is a settlement/reconciliation audit, not a social account, wallet
custodian, payment processor, or assertion that outside AI agents owe money.
BTC monitoring is a snapshot of currently visible public output data; it
doesn't claim new incoming receipts, net earnings, or contributor identities.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("crypto-agents")
OUT = Path("d10-payment-reports")
OUT.mkdir(parents=True, exist_ok=True)

cfg = json.loads((ROOT / "b_collection_assignments.json").read_text(encoding="utf-8"))
ledger = json.loads((ROOT / "verified_receivables.json").read_text(encoding="utf-8"))
assert cfg["director_operations"]["payment_director_id"] == "D10"
assert ledger["payment_director"] == "D10"
assert set(cfg["fleets"]) == {"transferexperiment", "BountyScoutAI"}
assert isinstance(ledger["claims"], list)

mandatory = {
    "id", "fleet", "payer_original_url", "deliverable_url", "acceptance_url",
    "agreed_asset", "agreed_network", "amount", "due_date", "payment_status"
}

def valid_public_link(url):
    return isinstance(url, str) and url.startswith("https://") and len(url) <= 1024

def scan_public_btc_outputs(address):
    # The last page of public txs may be empty even when older txs exist.
    url = "https://mempool.space/api/address/" + address + "/txs"
    request = urllib.request.Request(url, headers={
        "User-Agent": "B-D10-ReadOnlyReconciliation/1.0",
        "Accept": "application/json"
    })
    try:
        with urllib.request.urlopen(request, timeout=12) as reply:
            txs = json.loads(reply.read(1000000))
        if not isinstance(txs, list):
            raise ValueError("Explorer did not return a list")
        matching = []
        for tx in txs[:25]:
            if not isinstance(tx, dict) or not isinstance(tx.get("vout"), list):
                continue
            txid = tx.get("txid", "")
            if not isinstance(txid, str) or len(txid) != 64:
                continue
            for index, output in enumerate(tx["vout"]):
                if output.get("scriptpubkey_address") != address:
                    continue
                amount = output.get("value")
                if not isinstance(amount, int) or amount < 0:
                    continue
                matching.append({
                    "txid": txid,
                    "vout": index,
                    "value_sats": amount,
                    "confirmed": bool((tx.get("status") or {}).get("confirmed")),
                    "explorer": "https://mempool.space/tx/" + txid,
                    "reason_for_payment": "unknown",
                    "proved_external_client_income": False,
                })
        return {
            "status": "last_page_scanned",
            "scope": "Most recent at most 25 returned transactions, NOT a complete history",
            "visible_matching_outputs": matching[:25],
            "verified_new_since_prior_run": "not_assessed_no_baseline",
            "payment_purpose_classification": "not_assessed",
            "wallet_balance_claim": "none"
        }
    except Exception as exc:
        return {
            "status": "public_explorer_unavailable",
            "error": type(exc).__name__ + ": " + str(exc)[:160],
            "verified_new_since_prior_run": "unknown",
            "wallet_balance_claim": "none"
        }

invalid = []
awaiting_independent_confirmation = []
for item in ledger["claims"]:
    if not isinstance(item, dict):
        invalid.append("Non-object claim")
        continue
    cid = str(item.get("id") or "unknown")[:80]
    if not mandatory.issubset(item):
        invalid.append(cid + ": missing required evidence fields")
        continue
    if item["fleet"] not in cfg["fleets"]:
        invalid.append(cid + ": invalid receiving account")
        continue
    if not all(valid_public_link(item[f]) for f in
               ("payer_original_url", "deliverable_url", "acceptance_url")):
        invalid.append(cid + ": invalid public evidence URL")
        continue
    if str(item["agreed_asset"]) != cfg["fleets"][item["fleet"]]["asset"]:
        invalid.append(cid + ": unsupported coin in this BTC-only director registry")
        continue
    if str(item["agreed_network"]) != cfg["fleets"][item["fleet"]]["network"]:
        invalid.append(cid + ": wrong network")
        continue
    if not str(item.get("amount", "")).strip():
        invalid.append(cid + ": missing agreed amount")
        continue
    if str(item["payment_status"]).upper() != "ACCEPTED_UNPAID":
        continue
    # A manually supplied link is NOT enough by itself to establish a debt.
    # Director D10 must independently check the payer, acceptance and terms.
    awaiting_independent_confirmation.append({
        "id": cid, "fleet": item["fleet"],
        "payer_evidence": item["payer_original_url"],
        "accepted_work_evidence": item["acceptance_url"],
        "verified_contract_due": False,
        "contact_actually_sent": False,
        "status": "payment_evidence_requires_independent_validation",
        "next_step": "Inspect payer's original acceptance and actual terms; send a firm demand only through an authenticated authorized payer channel if amount is truly due."
    })

accounts = {}
for fleet, details in cfg["fleets"].items():
    accounts[fleet] = {
        "account": details["account"],
        "asset": details["asset"],
        "network": details["network"],
        "receiving_address": details["address"],
        "unverified_claims_for_review": [
            c for c in awaiting_independent_confirmation if c["fleet"] == fleet
        ],
        "original_account_request": details["approved_public_notice"],
        "btc_output_snapshot": scan_public_btc_outputs(details["address"]),
    }

report = {
    "as_of_utc": datetime.now(timezone.utc).isoformat(),
    "logical_payment_director": "D10",
    "scope": "Both B1 and B2 fleet accounts, one non-custodial director",
    "accounts": accounts,
    "claims_in_registry": len(ledger["claims"]),
    "claims_awaiting_independent_validation": len(awaiting_independent_confirmation),
    "rejected_or_incomplete_claims": invalid,
    "due_payments_independently_verified_by_this_job": 0,
    "payer_requests_sent_by_this_job": 0,
    "new_earnings_verified_by_this_job": "not_assessed",
    "disclaimer": (
        "No automatic payment collection, payout request or authenticated Moltbook outreach. "
        "Public BTC outputs can be self-transfers, historic coins or donations; they are not classified as income. "
        "Missing public-claim records do NOT establish that no unpaid invoice exists elsewhere. "
        "Existing user BTC Payment Watch is responsible for deduplicated new-deposit alerts."
    )
}
(OUT / "D10_TWO_ACCOUNT_PAYMENT_REPORT.json").write_text(
    json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
rows = [
    "# Director D10 — Both Accounts Payment Evidence",
    "",
    "UTC: " + report["as_of_utc"],
    "",
    "One logical payment director D10; D01–D09 keep running independent paid-work missions.",
    "",
    "Registered external acceptance claims: " + str(len(ledger["claims"])),
    "Claims needing independent validation: " + str(len(awaiting_independent_confirmation)),
    "Direct payer settlement requests sent by this job: 0",
    "No automatically verified new client earnings from this audit.",
    ""
]
for fleet, details in accounts.items():
    scan = details["btc_output_snapshot"]
    rows.extend([
        "## " + fleet + " / " + details["account"],
        "BTC mainnet: " + details["receiving_address"],
        "Explorer status: " + scan["status"],
        "Matching recent public transaction outputs (not classified as client income): " +
           str(len(scan.get("visible_matching_outputs", []))),
        "Public support notice: " + details["original_account_request"],
        ""
    ])
rows.extend([
    "## Next real action",
    "D10: obtain an actual external client acceptance/award with agreed amount, "
    "not just a task listing or internal model run. If a proven debt exists, "
    "use an AUTHENTICATED payer contact to request settlement; track the actual "
    "outgoing demand and confirm the correct network on receipt.",
    "",
    report["disclaimer"],
])
(OUT / "D10_TWO_ACCOUNT_PAYMENT_REPORT.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
print("D10_PAYMENT_AUDIT", json.dumps({
    "accounts": list(accounts),
    "registered_claims": report["claims_in_registry"],
    "needs_validation": report["claims_awaiting_independent_validation"],
    "payment_requests_sent": 0,
    "explorer_statuses": {k: v["btc_output_snapshot"]["status"] for k, v in accounts.items()},
    "independently_verified_earnings": "not_assessed"
}))
