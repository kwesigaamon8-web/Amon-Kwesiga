"""Evidence-only B1/B2 intelligence inboxes from *actual attempted* worker outputs.

Run after hierarchical_reporting.py in each real-worker GitHub Actions job.
No internet, external posting, model invocations, email or wallet access.
The 750,377,265,360 configured role IDs are never enumerated as workers.
"""
from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from hierarchical_reporting import chain

FLEETS = {"transferexperiment": "B1", "BountyScoutAI": "B2"}
DEFINED_PER_FLEET = 375_188_632_680
GOOD = "MODEL_COMPLETED_NEEDS_REVIEW"
GRADE = "QUALIFIED_SOURCE_BACKED_AI_RESEARCH"
MAX_ATTEMPTS = 10000
MAX_INBOX_ITEMS = 25


def clip(value, limit=260):
    return " ".join(str(value or "").replace("|", " ").split())[:limit]


def load(path):
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else None
    except (OSError, UnicodeError, ValueError):
        return None


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def actionable_worker(fleet, record, filename):
    """Reject wrong-company, wrong-path, incomplete identity or fake live evidence."""
    identifier = record.get("worker_id", "")
    if not isinstance(identifier, str) or not identifier.startswith(fleet + "/"):
        return None, "BAD_OR_CROSS_FLEET_ID"
    local = identifier[len(fleet) + 1:]
    if filename != local + ".json":
        return None, "FILE_ID_MISMATCH"
    try:
        ancestry = chain(local)
    except ValueError:
        return None, "INVALID_ROLE_ANCESTRY"
    if record.get("director") != fleet + "/" + ancestry[0]:
        return None, "WRONG_DIRECTOR"
    if record.get("direct_parent") != fleet + "/" + ancestry[-2]:
        return None, "WRONG_PARENT"
    status = clip(record.get("actual_execution_status"), 90)
    if not status:
        return None, "MISSING_EXECUTION_STATUS"
    grade = clip(record.get("strict_grade") or "NOT_GRADED", 90)
    defects = [clip(x, 180) for x in (record.get("strict_defects") or [])
               if isinstance(x, str)][:5]
    sources = [x for x in (record.get("source_links_unverified_as_paying") or [])
               if isinstance(x, str) and x.startswith("https://") and len(x) < 500][:3]
    next_action = clip(record.get("next_action"), 300)
    if status != GOOD:
        kind, priority = "EXECUTION_OR_MODEL_FAILURE", 1
        owner = "B2"
        decision = "Investigate model/process failure; do not claim successful AI work"
    elif grade != GRADE:
        kind, priority = "EVIDENCE_OR_QUALITY_GAP", 2
        owner = "B2"
        decision = "Review source quality and defect evidence before making a product claim"
    elif sources:
        kind, priority = "PUBLIC_LEAD_NEEDS_BUYER_VERIFICATION", 3
        owner = "B1"
        decision = "Verify relevance, terms, contact permission and buyer identity before outreach"
    else:
        kind, priority = "NO_VERIFIED_BUYER_SIGNAL", 4
        owner = FLEETS[fleet]
        decision = "Find a real product/buyer-specific next step; no sales inferred"
    # All activity stays under the actual B fleet supervisor tree and is visible to Chief D.
    route = [fleet + "/" + n for n in reversed(ancestry)] + [FLEETS[fleet], "CHIEF_D"]
    return {
        "worker_id": identifier,
        "routing_chain": route,
        "actual_execution_status": status,
        "strict_grade": grade,
        "kind": kind,
        "priority": priority,
        "action_owner": owner,
        "director": fleet + "/" + ancestry[0],
        "next_action": next_action,
        "recommended_supervisor_action": decision,
        "evidence_urls_unverified_as_buyer_or_payment": sources,
        "strict_defects": defects,
        "manager_or_director_model_acknowledgement_verified": False,
        "buyer_contact_or_payment_verified_by_router": False
    }, None


def generate(fleet, reports, output, run_url=""):
    if fleet not in FLEETS:
        raise ValueError("Unknown B fleet")
    directory = Path(reports) / fleet / "workers"
    files = sorted(directory.glob("*.json")) if directory.is_dir() else []
    if len(files) > MAX_ATTEMPTS:
        raise ValueError("Too many reports for a bounded run")
    records = []
    rejected = Counter()
    seen = set()
    for path in files:
        raw = load(path)
        if raw is None:
            rejected["UNREADABLE_REPORT"] += 1
            continue
        result, reason = actionable_worker(fleet, raw, path.name)
        if reason:
            rejected[reason] += 1
            continue
        if result["worker_id"] in seen:
            rejected["DUPLICATE_ROLE_REPORT"] += 1
            continue
        seen.add(result["worker_id"])
        records.append(result)
    records.sort(key=lambda r: (r["priority"], r["worker_id"]))
    counts = Counter(r["kind"] for r in records)
    now = datetime.now(timezone.utc).isoformat()
    base = Path(output) / fleet
    base.mkdir(parents=True, exist_ok=True)
    save(base / "ALL_VALID_ATTEMPTS.json", {
        "schema": "B1B2-WORKER-EVIDENCE-V1", "fleet": fleet,
        "as_of_utc": now, "attempted_worker_records": len(records),
        "reports": records, "rejected": dict(rejected),
        "caveat": "Attempt evidence and software routing only; no parent model receipt, customer or payment implied"
    })
    docs = {}
    for inbox in ("B1", "B2"):
        # Each B reads its own entire company and any other company's items that fit its specialty.
        candidates = [r for r in records if FLEETS[fleet] == inbox or r["action_owner"] == inbox]
        selected = candidates[:MAX_INBOX_ITEMS]
        directors = Counter(r["director"] for r in candidates)
        data = {
            "schema": "B1B2-PRIORITY-INBOX-V1",
            "recipient": inbox, "source_fleet": fleet, "as_of_utc": now,
            "run_url": run_url, "configured_roles_in_source_fleet": DEFINED_PER_FLEET,
            "configured_roles_are_not_active_agents": True,
            "source_files_examined": len(files), "validated_attempt_reports": len(records),
            "inbox_eligible_attempt_reports": len(candidates),
            "top_items_limit": MAX_INBOX_ITEMS, "items_returned": len(selected),
            "priority_counts": dict(Counter(r["kind"] for r in candidates)),
            "director_counts": dict(sorted(directors.items())),
            "rejected_reports": dict(rejected),
            "actual_live_supervisor_acknowledgements_verified": 0,
            "customer_acceptances_verified": 0,
            "payments_verified_by_this_router": "NOT_ASSESSED",
            "items": selected,
            "caveat": "Generated artifacts are readable inboxes, NOT proof that a Moltbook agent read/acknowledged them"
        }
        save(base / (inbox + "_INBOX.json"), data)
        lines = ["# " + inbox + " intelligence inbox — from " + fleet, "",
                 "Run: " + (run_url or "local/incomplete link"),
                 "Recorded worker attempts: " + str(len(records)),
                 "Inbox-matching attempts: " + str(len(candidates)),
                 "Dormant or unreported defined roles are NOT counted as active.",
                 "No actual agent acknowledgement or money receipt is established by this report.", "",
                 "## Necessary actionable reports", ""]
        if not selected:
            lines.append("No validated worker reports or actionable signals in this batch.")
        for item in selected:
            links = ", ".join(item["evidence_urls_unverified_as_buyer_or_payment"]) or "none"
            lines += ["- **" + item["worker_id"] + "** — " + item["kind"] +
                      " (priority " + str(item["priority"]) + "); director " + item["director"] +
                      "; next: " + (item["next_action"] or item["recommended_supervisor_action"]) +
                      "; original public links (unverified): " + links]
        lines += ["", "## Reporting route",
                  "Worker H/G/S/W → actual parent path (software aggregation) → director → " +
                  FLEETS[fleet] + " → Chief D; cross-specialty copies to " + inbox + " where relevant.",
                  "A report file is not a claim that any parent independently ran an AI model or responded."]
        (base / (inbox + "_INBOX.md")).write_text("\n".join(lines) + "\n", encoding="utf-8")
        docs[inbox] = data
    chief = {
        "schema": "B1B2-CHIEF-ROUTING-STATUS-V1", "as_of_utc": now, "fleet": fleet,
        "primary_agent": FLEETS[fleet], "total_configured_both_fleets": 2 * DEFINED_PER_FLEET,
        "attempt_reports_validated": len(records),
        "source_files_examined": len(files),
        "rejected_reports": dict(rejected), "priority_counts": dict(counts),
        "b1_inbox_eligible": docs["B1"]["inbox_eligible_attempt_reports"],
        "b2_inbox_eligible": docs["B2"]["inbox_eligible_attempt_reports"],
        "verified_agent_read_receipts": 0,
        "verified_customer_acceptances": 0,
        "verified_payment_received": "NOT_ASSESSED",
        "notes": "Each fleet runs separately; never sum distinct daily runs into a concurrent agent count. B1/B2 inbox files are actual workflow artifacts, not autonomous account messages."
    }
    save(base / "CHIEF_D_STATUS.json", chief)
    return chief


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fleet", required=True, choices=sorted(FLEETS))
    parser.add_argument("--reports", default="hierarchical-reports")
    parser.add_argument("--out", default="b1b2-intelligence")
    args = parser.parse_args()
    run_url = ("https://github.com/" + os.environ["GITHUB_REPOSITORY"] +
               "/actions/runs/" + os.environ["GITHUB_RUN_ID"]
               if os.environ.get("GITHUB_REPOSITORY") and os.environ.get("GITHUB_RUN_ID") else "")
    result = generate(args.fleet, args.reports, args.out, run_url)
    print("B1B2_EVIDENCE_INBOXES", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
