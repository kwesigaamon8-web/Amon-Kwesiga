"""Read-only Hondō / LN Church Base-USDC paid-task discovery for B1/B2.

Source: https://kari.mayim-mayim.com/agent-taskboard.html
Do not claim, purchase, pay, sign, register, complete, or provide a payout address.
A task listing is not a job acceptance or deposit. No private credentials.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

URL = "https://kari.mayim-mayim.com/api/agent/tasks?limit=25"
REPORT = Path("paid-opportunity-reports/hondo-base-usdc.json")
DISALLOWED = re.compile(
    r"(?i)(?:paid_service_trial|purchase|buy|deposit|pay.?first|fee.?required|stake|"
    r"swap|token.?purchase|private.?key|seed.?phrase|wallet.?signature)"
)
USEFUL = re.compile(r"(?i)(?:structured_response|endpoint_choice_reason|"
                    r"scheduled_http_get_batch|instant_site_visit|research|"
                    r"observation|evaluation)")


def list_rows(payload):
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("tasks", "items", "results", "data", "offers"):
        value = payload.get(key)
        if isinstance(value, list):
            return list_rows(value)
        if isinstance(value, dict):
            rows = list_rows(value)
            if rows:
                return rows
    return []


def first(row, keys):
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return None


def nonnegative_number(v):
    if isinstance(v, bool) or v is None:
        return None
    try:
        value = float(str(v))
        return value if 0 <= value < 1e12 else None
    except (ValueError, TypeError, OverflowError):
        return None


def check_one(row):
    task_id = first(row, ("task_id", "taskId", "id"))
    if not isinstance(task_id, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{6,100}", task_id):
        return None
    task_type = str(first(row, ("task_type", "taskType", "type")) or "")[:100]
    status = str(first(row, ("status", "public_status", "task_status")) or "")[:30]
    remaining = nonnegative_number(first(row, (
        "capacity_remaining", "remaining_capacity", "remaining_slots",
        "capacityAvailable", "available_slots", "slots_remaining")))
    # Some public list projections expose a nested capacity object.
    if remaining is None and isinstance(row.get("capacity"), dict):
        remaining = nonnegative_number(first(row["capacity"],
                                            ("remaining", "available", "capacity_remaining")))
    claimable = first(row, ("claimable", "is_claimable", "can_claim"))
    if not isinstance(claimable, bool):
        claimable = None
    reward_raw = first(row, ("reward_usdc", "reward_amount_usdc", "rewardUsdc", "reward"))
    reward = nonnegative_number(reward_raw)
    if isinstance(reward_raw, dict):
        reward = nonnegative_number(first(reward_raw, ("amount", "usdc_amount", "value")))
    reason = []
    if status.upper() != "OPEN":
        reason.append("not_explicitly_open")
    if claimable is not True:
        reason.append("not_explicitly_claimable")
    if remaining is None or remaining <= 0:
        reason.append("remaining_capacity_not_proven")
    if reward is None or reward <= 0:
        reason.append("positive_usdc_reward_not_proven")
    if DISALLOWED.search(task_type):
        reason.append("possible_paid_action_or_wallet_risk")
    if not USEFUL.search(task_type):
        reason.append("task_type_requires_manual_definition_review")
    return {
        "task_id": task_id,
        "task_type": task_type,
        "advertised_status": status,
        "claimable": claimable,
        "remaining_slots": remaining,
        "advertised_usdc": reward,
        "detail_url": "https://kari.mayim-mayim.com/api/agent/tasks/" + task_id,
        "status": "POTENTIAL_FREE_TASK_REVIEW_DEFINITION" if not reason else "HOLD",
        "blockers": reason,
        "claim_attempted": False,
        "payout_address_supplied": False,
        "accepted_work": False,
        "verified_owner_deposit": False
    }


def self_test():
    assert list_rows({"data": {"tasks": [{"id": "task_123456"}]}}) == [{"id": "task_123456"}]
    sample = {"task_id": "task_123456", "task_type": "structured_response.v3",
              "status": "OPEN", "claimable": True, "capacity_remaining": 2,
              "reward_usdc": "0.15"}
    good = check_one(sample)
    assert good["status"] == "POTENTIAL_FREE_TASK_REVIEW_DEFINITION"
    assert check_one({**sample, "task_type": "paid_service_trial.v1"})["status"] == "HOLD"
    assert check_one({**sample, "claimable": False})["status"] == "HOLD"
    assert check_one({**sample, "capacity_remaining": 0})["status"] == "HOLD"
    assert check_one({**sample, "capacity_remaining": None})["status"] == "HOLD"
    assert check_one({**sample, "reward_usdc": 0})["status"] == "HOLD"
    assert check_one({**sample, "task_id": "../../../secret"}) is None
    assert check_one({**sample, "reward_usdc": "NaN"})["status"] == "HOLD"
    print("HONDO_BASE_USDC_SCOUT_SELF_TEST_PASS: no purchases, no unverified slots")


def run():
    errors = []
    rows, candidates = [], []
    try:
        req = urllib.request.Request(URL, headers={
            "User-Agent": "B1B2-ReadOnly-Hondo-Paid-Task-Scout/1.0",
            "Accept": "application/json"
        })
        with urllib.request.urlopen(req, timeout=14) as response:
            payload = json.load(response)
        if not isinstance(payload, (list, dict)):
            raise ValueError("Unrecognized task response")
        if isinstance(payload, dict) and (
                payload.get("error") or payload.get("errors") or
                payload.get("success") is False):
            raise ValueError("Task API returned error")
        rows = list_rows(payload)
        if not rows and isinstance(payload, dict) and not any(
                x in payload for x in ("tasks", "items", "results", "data", "offers")):
            raise ValueError("Empty unrecognized list schema")
        candidates = [x for row in rows if (x := check_one(row)) is not None]
    except Exception as exc:
        errors.append(type(exc).__name__ + ": " + str(exc)[:160])
    ready = [x for x in candidates if x["status"].startswith("POTENTIAL")]
    data = {
        "observed_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": URL,
        "source_terms": "https://kari.mayim-mayim.com/agent-taskboard.html",
        "network": "Base", "asset": "USDC", "chain_id": 8453,
        "source_status": "ERROR_UNKNOWN_AVAILABILITY" if errors else "READ_ONLY_LIST_CHECKED",
        "source_errors": errors, "rows_seen": len(rows),
        "potential_claimable_count": len(ready), "screened": candidates[:25],
        "buyer_acceptance_proven": False, "earnings_proven": False,
        "owner_wallet_receipts_proven": False, "actions_posted": 0,
        "next": "Fetch official task definition and verify all steps are free, available, non-sensitive and payout-compatible; explicit receiving address and claim snapshot must be validated before claim. No payment until actually settled."
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("HONDO_READ_ONLY_USDC", json.dumps({
        "source_status": data["source_status"], "rows": len(rows),
        "potential": len(ready), "errors": errors,
        "candidate_ids": [x["task_id"] for x in ready[:5]]
    }))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    self_test() if args.self_test else run()
