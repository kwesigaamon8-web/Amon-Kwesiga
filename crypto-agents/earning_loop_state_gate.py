"""Persist only genuine state advances from recurring BTC/USDC opportunity watches.

The hourly/15-minute scans remain read-only or narrowly sponsor-authorized. Their
timestamped JSON is uploaded as an Action artifact. Git commits are deliberately
reserved for a threshold crossing, a new sponsor claim ID or sponsor verdict:
re-running a check must not churn main or erase an existing claim.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import sys


def moment(record):
    stamp = record.get("checked_at_utc")
    if not isinstance(stamp, str):
        raise ValueError("Missing checked_at_utc")
    parsed = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("UTC timestamp must be timezone-aware")
    return parsed.astimezone(dt.timezone.utc)


def bucket(sets):
    """At most five persisted progress milestones, never per-game commits."""
    if not isinstance(sets, int) or isinstance(sets, bool) or sets < 0:
        return 0
    return min(4, sets // 25)


def material_change(previous, current, kind):
    if kind not in ("sponsor", "cup"):
        raise ValueError("Unknown state kind")
    if not isinstance(current, dict) or not isinstance(previous, dict):
        raise ValueError("Reports must be JSON objects")
    new_time = moment(current)
    if previous and new_time < moment(previous):
        return False, "stale_observation_does_not_overwrite_newer_state"
    if kind == "sponsor":
        old_claim = previous.get("submission_id")
        new_claim = current.get("submission_id")
        if old_claim and new_claim != old_claim:
            return False, "cannot_erase_or_replace_existing_claim"
        if new_claim and not old_claim:
            return True, "new_sponsor_submission_id"
        if old_claim and new_claim == old_claim:
            for key in ("platform_review_status", "awarded_cents", "platform_reports_paid"):
                if current.get(key) is not None and current.get(key) != previous.get(key):
                    return True, "sponsor_review_updated_" + key
        if current.get("qualifying") is True and previous.get("qualifying") is not True:
            return True, "ranked_set_qualification_observed"
        return False, "no_new_eligible_claim_or_sponsor_verdict"
    if previous.get("cup_qualified") is not True and current.get("cup_qualified") is True:
        return True, "cup_qualification_reached"
    if (previous.get("sponsor_bounty_ready_for_review") is not True and
            current.get("sponsor_bounty_ready_for_review") is True):
        return True, "public_sponsor_threshold_reached"
    for key in ("public_ranked_sets", "cup_ranked_sets"):
        if bucket(current.get(key)) > bucket(previous.get(key)):
            return True, key + "_25_set_milestone"
    if (current.get("public_ranked_sets", 0) >= 100 and
            previous.get("public_rating_above_starter") != current.get("public_rating_above_starter")):
        return True, "qualified_rating_eligibility_changed"
    return False, "no_new_ranked_milestone"


def self_test():
    now = "2026-11-19T20:00:00Z"
    later = "2026-11-19T20:15:00Z"
    first = {"checked_at_utc": now, "our_public_sets": 20,
             "submission_id": None, "qualifying": False}
    same = first | {"checked_at_utc": later, "our_public_sets": 22}
    assert material_change(first, same, "sponsor")[0] is False
    claimed = same | {"submission_id": "sub-17"}
    assert material_change(first, claimed, "sponsor")[0] is True
    assert material_change(claimed, same, "sponsor")[0] is False
    assert material_change(claimed, claimed | {"checked_at_utc": later,
        "platform_review_status": "accepted"}, "sponsor")[0] is True
    assert material_change(same, same | {"qualifying": True}, "sponsor")[0] is True
    old_cup = {"checked_at_utc": now, "cup_ranked_sets": 40,
               "public_ranked_sets": 20, "cup_qualified": False}
    repeat = old_cup | {"checked_at_utc": later, "cup_ranked_sets": 48}
    assert material_change(old_cup, repeat, "cup")[0] is False
    assert material_change(old_cup, repeat | {"cup_ranked_sets": 50}, "cup")[0] is True
    assert material_change(old_cup, repeat | {"cup_qualified": True}, "cup")[0] is True
    assert material_change(old_cup, repeat | {"checked_at_utc":"2026-11-19T19:00:00Z",
         "cup_qualified": True}, "cup")[0] is False
    assert material_change({}, first, "sponsor")[0] is False
    print("B1B2_MEANINGFUL_EARNING_LOOP_MILESTONES_TEST_PASS")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--kind", choices=("sponsor", "cup"))
    ap.add_argument("--old")
    ap.add_argument("--new")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not (args.kind and args.old and args.new):
        ap.error("--kind, --old and --new are required")
    old_path = Path(args.old)
    old = json.loads(old_path.read_text()) if old_path.is_file() else {}
    new = json.loads(Path(args.new).read_text())
    yes, reason = material_change(old, new, args.kind)
    print("B1B2_EARNING_LOOP_STATE_GATE", json.dumps({
        "kind": args.kind, "persist_commit": yes, "reason": reason,
        "new_claim_id": new.get("submission_id") if args.kind == "sponsor" else None,
        "crypto_received_proven_by_gate": False,
    }))
    # 3 is an explicit benign "no change"; errors exit nonzero normally.
    return 0 if yes else 3


if __name__ == "__main__":
    sys.exit(main())
