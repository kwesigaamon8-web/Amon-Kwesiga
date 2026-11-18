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
    # API list 'description' is an IPFS CID; only 'descriptionText' from ?full=1 is task text.
    description = str(row.get("descriptionText") or "")[:64000]
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
    if row.get("reservedFor"):
        reasons.append("reserved_for_another_unverified_wallet")
    if row.get("workerBondRequired") is not False:
        reasons.append("worker_bond_missing_or_required")
    if not description:
        reasons.append("full_task_description_unavailable")
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
        "description_url": row.get("descriptionUrl"),
        "source_listing_url": row.get("url") if str(row.get("url") or "").startswith("https://www.basebounty.app/") else "https://www.basebounty.app/",
        "reserved_for": row.get("reservedFor"),
        "worker_bond_required": row.get("workerBondRequired"),
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
            "deadline": "2026-11-21T12:00:00Z", "workerBondRequired": False}
    payload = {"data": {"bounties": [
        base, dict(base, jobId=18, audience="agents"),
        dict(base, jobId=19, deadline="2026-11-01T00:00:00Z"),
        dict(base, jobId=20, descriptionText="Send private key for reward"),
        dict(base, jobId=21, workerPayoutUsdc="0.30"),
        dict(base, jobId=22, workerPayoutUsdc="NaN"),
        dict(base, jobId=23, reservedFor="0x1234567890123456789012345678901234567890"),
        dict(base, jobId=24, workerBondRequired=True),
        dict(base, jobId=25, descriptionText=None) ]}}
    rows, found = screen(payload, now)
    assert len(rows) == 9 and len(found) == 8
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
    rows, found, detail_errors = [], [], []
    try:
        req = urllib.request.Request(API, headers={"Accept": "application/json",
                                                   "User-Agent": "B1B2-ReadOnlyEarningScout/1.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            payload = json.load(resp)
        if not isinstance(payload, (list, dict)) or (
                isinstance(payload, dict) and any(k in payload for k in ("error", "errors"))):
            raise ValueError("source returned error payload")
        rows = rows_from_payload(payload)
        # Read up to 8 highest-value OPEN, non-bonded, non-reserved tasks. Never sign.
        eligible = sorted(
            (r for r in rows if str(r.get("status") or "").lower() == "open"
             and r.get("workerBondRequired") is False and not r.get("reservedFor")
             and str(r.get("audience") or "") not in ("agents", "agent", "agents_only")
             and (amount_decimal(r.get("workerPayoutUsdc")) or Decimal(0)) >= Decimal(2)),
            key=lambda r: amount_decimal(r.get("workerPayoutUsdc")) or Decimal(0),
            reverse=True
        )[:8]
        expanded = {}
        for item in eligible:
            jid = str(item.get("jobId") or "")
            if not re.fullmatch(r"[0-9]{1,20}", jid):
                continue
            url = "https://www.basebounty.app/api/v1/bounties/" + jid + "?full=1"
            try:
                req2 = urllib.request.Request(url, headers={"Accept": "application/json",
                                                            "User-Agent": "B1B2-ReadOnlyEarningScout/1.0"})
                with urllib.request.urlopen(req2, timeout=8) as response:
                    detail = json.load(response)
                full = detail.get("bounty") if isinstance(detail, dict) else None
                if not isinstance(full, dict) or str(full.get("jobId")) != jid:
                    raise ValueError("detail schema or job ID mismatch")
                expanded[jid] = {**item, **full}
            except Exception as ex:
                detail_errors.append(jid + ": " + type(ex).__name__ + ": " + str(ex)[:90])
        rows, found = screen([expanded.get(str(r.get("jobId")), r) for r in rows])
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
        "source_errors": errors, "detail_errors": detail_errors,
        "status": "SOURCE_ERROR_DO_NOT_CLAIM_ZERO" if errors else "SOURCE_SCREENED",
        "funds_spent": 0, "signed_actions": 0, "verified_deposits": 0,
        "next_action": "Read full original bounty; independently verify escrow, eligibility and payout. Wallet signature requires separate authorization. Never count listing as earnings."
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("BASEBOUNTY_READ_ONLY_SCOUT", json.dumps({
        "rows": len(rows), "candidates": len(found), "errors": errors, "detail_errors": len(detail_errors),
        "top": [(x["job_id"], x["worker_payout_usdc_advertised"], x["status"])
                for x in found[:5]]
    }))


if __name__ == "__main__":
    main()
