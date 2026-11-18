"""B1/B2 read-only BaseBounty source scout; never takes jobs or signs transactions.

Official public docs: https://www.basebounty.app/developers
No wallet, key, payment, signup, GitHub issue, or external submission is used here.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import urllib.request
from decimal import Decimal, InvalidOperation
from pathlib import Path

API = "https://www.basebounty.app/api/v1/bounties?status=open"
OUT = Path("paid-opportunity-reports/basebounty-base-usdc.json")
RISK = re.compile(r"(?i)\b(private key|seed phrase|send funds|pay upfront|deposit first|fake reviews|spam|guaranteed return)\b")
SKILL = re.compile(r"(?i)\b(python|javascript|typescript|documentation|data|csv|excel|test|api|research|reconcil|audit|accounting|bookkeep|bug|report|financial)\b")


def rows_from_payload(value):
    """Gracefully handle documented board as either array or common wrapped JSON."""
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    if isinstance(value, dict):
        for key in ("bounties", "jobs", "items", "data", "results"):
            v = value.get(key)
            if isinstance(v, list):
                return rows_from_payload(v)
            if isinstance(v, dict):
                nested = rows_from_payload(v)
                if nested:
                    return nested
    return []


def amount_decimal(raw):
    if raw is None or isinstance(raw, bool):
        return None
    try:
        value = Decimal(str(raw).strip())
        return value if value.is_finite() and value >= 0 else None
    except (ValueError, InvalidOperation):
        return None


def expiry_utc(raw):
    if raw is None or raw == "":
        return None
    try:
        if isinstance(raw, (float, int)) and not isinstance(raw, bool):
            n = float(raw)
            if n > 1e12:
                n /= 1000
            return dt.datetime.fromtimestamp(n, tz=dt.timezone.utc)
        if isinstance(raw, str) and re.fullmatch(r"\d{10,13}", raw):
            return expiry_utc(int(raw))
        if isinstance(raw, str):
            t = dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if t.tzinfo is None:
                t = t.replace(tzinfo=dt.timezone.utc)
            return t.astimezone(dt.timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None
    return None


def first(row, names):
    for n in names:
        if row.get(n) is not None:
            return row.get(n)
    return None


def classify(row, now):
    uid = first(row, ("jobId", "id", "bountyId"))
    if isinstance(uid, bool) or not re.fullmatch(r"[0-9]{1,20}", str(uid or "")):
        return None
    payout = amount_decimal(first(row, ("workerPayoutUsdc", "rewardUsdc", "reward")))
    if payout is None:
        return None
    status = str(row.get("status") or "").lower()
    audience = str(first(row, ("audience", "workerType", "eligibility")) or "").lower()
    title = str(first(row, ("title", "name")) or "")[:140]
    description = str(first(row, ("descriptionText", "description", "task")) or "")[:1000]
    deadline = expiry_utc(first(row, ("deadline", "deadlineAt", "expiry", "expiresAt", "endTime")))
    reasons = []
    if status != "open":
        reasons.append("not_open")
    if audience in ("agents", "agent", "agents_only"):
        reasons.append("erc8004_agent_identity_not_verified")
    if audience not in ("", "anyone", "humans", "human", "agents", "agent", "agents_only"):
        reasons.append("eligibility_unknown")
    if deadline and deadline <= now:
        reasons.append("expired")
    if not description and not title:
        reasons.append("no_task_spec_in_listing_check_full_record")
    if RISK.search(description + " " + title):
        reasons.append("unsafe_description")
    if payout < Decimal("2"):
        reasons.append("below_2_usdc_priority_floor")
    # A job's open status is not an independently verified escrow balance or guaranteed payout.
    return {
        "job_id": str(uid),
        "api_url": "https://www.basebounty.app/api/v1/bounties/" + str(uid) + "?full=1",
        "chain_id": 8453, "asset": "USDC",
        "title": title, "description_excerpt": description[:250],
        "worker_payout_usdc_advertised": str(payout),
        "audience": audience or "not_supplied",
        "deadline_utc": deadline.isoformat() if deadline else None,
        "fit": bool(SKILL.search(title + " " + description)),
        "status": "SOURCE_OPEN_WALLET_ACTION_REQUIRED" if not reasons else "HOLD",
        "blockers": reasons,
        "signing_key_available": False, "job_taken": False,
        "submitted": False, "accepted": False, "deposit_verified": False,
    }


def screen(payload, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    rows = rows_from_payload(payload)
    found = []
    for row in rows:
        result = classify(row, now)
        if result is not None:
            found.append(result)
    found.sort(key=lambda x: (
        x["status"].startswith("SOURCE_OPEN"), x["fit"],
        Decimal(x["worker_payout_usdc_advertised"])), reverse=True)
    return rows, found


def self_test():
    now = dt.datetime(2026, 11, 18, tzinfo=dt.timezone.utc)
    base = {"jobId": 17, "title": "Python CSV reconciliation",
            "descriptionText": "Fix invoice reconciliation tests",
            "status": "open", "audience": "anyone", "workerPayoutUsdc": "25.5",
            "deadline": "2026-11-21T12:00:00Z"}
    payload = {"data": {"bounties": [
        base, dict(base, jobId=18, audience="agents"),
        dict(base, jobId=19, deadline="2026-11-01T00:00:00Z"),
        dict(base, jobId=20, descriptionText="Send private key for reward"),
        dict(base, jobId=21, workerPayoutUsdc="0.30"),
        dict(base, jobId=22, workerPayoutUsdc="NaN") ]}}
    rows, found = screen(payload, now)
    assert len(rows) == 6 and len(found) == 5
    assert found[0]["job_id"] == "17" and found[0]["status"].startswith("SOURCE_OPEN")
    assert all(x["status"] == "HOLD" for x in found[1:])
    assert all(x["deposit_verified"] is False for x in found)
    assert classify(dict(base, jobId="bad"), now) is None
    assert rows_from_payload({"error": "503 source unavailable"}) == []
    print("BASEBOUNTY_SCOUT_SELF_TEST_PASS: units, nested rows, eligibility, expiry, risk, payout")


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        return self_test()
    errors = []
    rows, found = [], []
    try:
        req = urllib.request.Request(API, headers={"Accept": "application/json",
                                                   "User-Agent": "B1B2-ReadOnlyEarningScout/1.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            payload = json.load(resp)
        if not isinstance(payload, (list, dict)) or (
                isinstance(payload, dict) and any(k in payload for k in ("error", "errors"))):
            raise ValueError("source returned error payload")
        rows, found = screen(payload)
        if not rows and isinstance(payload, dict) and not any(
                k in payload for k in ("bounties", "jobs", "items", "data", "results")):
            raise ValueError("unrecognized response schema; empty market not verified")
    except Exception as ex:
        errors.append(type(ex).__name__ + ": " + str(ex)[:160])
    report = {
        "checked_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "public_source": API, "docs": "https://www.basebounty.app/developers",
        "network": "Base mainnet", "chain_id": 8453,
        "read_only": True, "source_rows": len(rows),
        "candidate_count": len(found), "candidates_unverified": found[:40],
        "source_errors": errors,
        "status": "SOURCE_ERROR_DO_NOT_CLAIM_ZERO" if errors else "SOURCE_SCREENED",
        "funds_spent": 0, "signed_actions": 0, "verified_deposits": 0,
        "next_action": "Read full original bounty; independently verify escrow, eligibility and payout. Wallet signature requires separate authorization. Never count listing as earnings."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("BASEBOUNTY_READ_ONLY_SCOUT", json.dumps({
        "rows": len(rows), "candidates": len(found), "errors": errors,
        "top": [(x["job_id"], x["worker_payout_usdc_advertised"], x["status"])
                for x in found[:5]]
    }))


if __name__ == "__main__":
    main()
