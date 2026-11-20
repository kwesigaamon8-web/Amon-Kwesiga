"""Independent evidence-first audit of every finite B1/B2 worker subprocess artifact.
No virtual worker slot, CI green check, source search or claim is counted as a customer.
Inputs are original GitHub Actions artifacts, not self-reported organization counts.
"""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

SHARDS = tuple(f"{fleet}-S{n:02d}" for fleet in ("B1", "B2") for n in range(1, 16))
WORKERS = 30
REQUIRED_PROMPT = "crypto-agents/customer-acquisition/OWNER_STRICT_CUSTOMER_WORKER_PROMPT.md"


def examine(root, expected_order, output, strict_prompt_required=False):
    root, output = Path(root), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    rows, failures, seen_ids, candidate_index = [], [], set(), defaultdict(set)
    for shard in SHARDS:
        directory = root / shard
        snapshot_file = directory / "snapshot.json"
        manifest_file = directory / "manifest.json"
        snapshot, manifest = {}, {}
        for f, name in ((snapshot_file, "snapshot"), (manifest_file, "manifest")):
            try:
                parsed = json.loads(f.read_text(encoding="utf-8"))
                if not isinstance(parsed, dict):
                    raise ValueError("not_object")
            except (OSError, ValueError, TypeError) as exc:
                parsed = {}
                failures.append(f"{shard}:invalid_{name}:{type(exc).__name__}")
            if name == "snapshot":
                snapshot = parsed
            else:
                manifest = parsed
        if manifest.get("shard") != shard or manifest.get("owner_order_id") != expected_order:
            failures.append(f"{shard}:manifest_or_order_mismatch")
        if manifest.get("child_process_successes") != WORKERS:
            failures.append(f"{shard}:not_30_successful_executions")
        if snapshot.get("owner_order_id") != expected_order:
            failures.append(f"{shard}:snapshot_order_mismatch")
        candidates = snapshot.get("items") or []
        if not isinstance(candidates, list):
            candidates = []
            failures.append(f"{shard}:invalid_snapshot_items")
        if snapshot.get("fetch_status") == "ok" and len(candidates) == 0:
            failures.append(f"{shard}:empty_source_response")
        for slot in range(1, WORKERS + 1):
            worker_id = f"{shard}-W{slot:02d}"
            worker_file = directory / f"{worker_id}.json"
            errors = []
            try:
                worker = json.loads(worker_file.read_text(encoding="utf-8"))
                if not isinstance(worker, dict):
                    raise ValueError("not_object")
            except (OSError, ValueError, TypeError) as exc:
                worker = {}
                errors.append("worker_record_missing_or_invalid:" + type(exc).__name__)
            if worker_id in seen_ids:
                errors.append("duplicate_worker_id")
            seen_ids.add(worker_id)
            if worker.get("worker_id") != worker_id:
                errors.append("worker_identity_mismatch")
            if worker.get("company") != shard[:2] or worker.get("shard") != shard:
                errors.append("reporting_parent_or_company_mismatch")
            if worker.get("owner_order_id") != expected_order:
                errors.append("did_not_receive_expected_order")
            if not isinstance(worker.get("pid"), int) or worker.get("pid", 0) <= 0:
                errors.append("no_os_process_id")
            if not isinstance(worker.get("parent_pid"), int) or worker.get("parent_pid", 0) <= 0:
                errors.append("no_parent_os_process_id")
            task = worker.get("task") or {}
            if (task.get("id") != worker_id or task.get("shard") != shard
                or task.get("slot") != slot or task.get("reports_to") != shard):
                errors.append("assigned_task_identity_mismatch")
            try:
                ts = datetime.fromisoformat(str(worker["executed_utc"]).replace("Z", "+00:00"))
                if ts.tzinfo is None:
                    errors.append("execution_time_missing_timezone")
            except (KeyError, ValueError, TypeError):
                errors.append("no_valid_execution_timestamp")
            if worker.get("source_query") != snapshot.get("source_query"):
                errors.append("source_query_not_in_shard_snapshot")
            if worker.get("snapshot_search_success") != (snapshot.get("fetch_status") == "ok"):
                errors.append("source_status_not_consistent")
            if strict_prompt_required and worker.get("strict_owner_customer_prompt_source") != REQUIRED_PROMPT:
                errors.append("strict_owner_prompt_not_inherited")
            expected_issue = candidates[slot - 1] if len(candidates) >= slot else None
            seen = expected_issue is not None
            if bool(worker.get("source_issue_seen")) != seen:
                errors.append("worker_source_presence_incorrect")
            if worker.get("worker_status") != ("reviewed_snapshot_issue" if seen else "no_issue_for_slot"):
                errors.append("task_completion_status_incorrect")
            assessment = worker.get("assessment")
            if seen:
                if not isinstance(assessment, dict):
                    errors.append("missing_issue_assessment")
                    assessment = {}
                else:
                    if assessment.get("issue_id") != expected_issue.get("id"):
                        errors.append("source_issue_id_mismatch")
                    if assessment.get("source_url") != expected_issue.get("html_url"):
                        errors.append("source_url_mismatch")
                    if assessment.get("title") != str(expected_issue.get("title") or "")[:200]:
                        errors.append("source_title_mismatch")
                    for field in ("payer_verified", "customer_acceptance_verified", "incoming_crypto_verified"):
                        if assessment.get(field) is not False:
                            errors.append("unsupported_claim:" + field)
                    if (assessment.get("possible_paid_lead_unverified")
                        and not assessment.get("source_url")):
                        errors.append("lead_without_source")
            elif assessment is not None:
                errors.append("fabricated_assessment_without_source")
            # A modern worker must prove it actually read the full order text and
            # computed a unique task, rather than merely reproducing an owner ID.
            task_proof = worker.get("actual_distinct_ordered_task")
            actual_task_verified = False
            full_order_read = False
            source_diagnostic_done = False
            if "order_text_actually_read" in worker or "actual_distinct_ordered_task" in worker:
                public_doc = json.loads(Path("crypto-agents/PUBLIC_AGENT_COMMAND.json").read_text(encoding="utf-8"))
                prompt_content = Path("crypto-agents/customer-acquisition/OWNER_STRICT_CUSTOMER_WORKER_PROMPT.md").read_text(encoding="utf-8")
                expected_owner_hash = hashlib.sha256(str(public_doc["owner_command"]).encode("utf-8")).hexdigest()
                expected_prompt_hash = hashlib.sha256(prompt_content.encode("utf-8")).hexdigest()
                if (worker.get("order_text_actually_read") is True
                    and worker.get("owner_instruction_sha256") == expected_owner_hash
                    and worker.get("strict_prompt_sha256") == expected_prompt_hash):
                    full_order_read = True
                else:
                    errors.append("full_canonical_order_not_cryptographically_matched")
                if isinstance(task_proof, dict) and task_proof.get("evidence_sha256"):
                    digest = task_proof["evidence_sha256"]
                    payload = {k: v for k,v in task_proof.items() if k != "evidence_sha256"}
                    actual_hash = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
                    required_action = ("SPECIFIC_PUBLIC_BUYER_SOURCE_ASSESSMENT" if seen else "SOURCE_FAILURE_DIAGNOSIS")
                    if (digest == actual_hash and task_proof.get("action") == required_action
                        and task_proof.get("worker_specialty") == task.get("specialty")
                        and task_proof.get("verified_external_customer") is False
                        and task_proof.get("contact_authorized") is False):
                        if seen and (task_proof.get("source_url_reviewed") != expected_issue.get("html_url")
                                     or task_proof.get("source_issue_id_reviewed") != expected_issue.get("id")):
                            errors.append("specific_task_review_did_not_match_source")
                        elif not seen and task_proof.get("source_query_examined") != snapshot.get("source_query"):
                            errors.append("source_failure_diagnosis_missing_query")
                        else:
                            actual_task_verified = True
                            source_diagnostic_done = not seen
                    else:
                        errors.append("individual_task_action_or_hash_failed")
                else:
                    errors.append("individual_task_execution_proof_missing")
            if worker.get("verified_paid_work") or worker.get("new_wallet_receipts_verified"):
                errors.append("unsupported_income")
            if (worker.get("emails_read_or_sent") or worker.get("wallet_transactions")
                or worker.get("external_applications_or_posts")):
                errors.append("unauthorized_external_action_claim")
            url = assessment.get("source_url", "") if isinstance(assessment, dict) else ""
            possible = bool(assessment.get("possible_paid_lead_unverified")) if isinstance(assessment, dict) else False
            if possible and re.search(r"github\.com/(?:kwesigaamon8-web/Amon-Kwesiga|[^/]+/(?:bounty-plaza|bounty-bot))/issues/", url, re.I):
                errors.append("owner_or_bounty_mirror_misclassified_as_buyer")
            if possible and url:
                candidate_index[url].add(worker_id)
            process_recorded = bool(worker) and "no_os_process_id" not in errors
            order_recorded = worker.get("owner_order_id") == expected_order
            task_assessed = bool(seen and isinstance(assessment, dict) and
                                 not any(e in errors for e in ("missing_issue_assessment", "source_url_mismatch",
                                                                "source_issue_id_mismatch", "source_title_mismatch")))
            no_source = not seen
            row = {
                "worker_id": worker_id, "company": shard[:2], "parent_shard": shard,
                "expected_order_id": expected_order,
                "process_recorded": process_recorded, "order_in_record": order_recorded,
                "task_assigned": task.get("id") == worker_id,
                "full_owner_order_text_digest_verified": full_order_read,
                "actual_individual_task_evidence_verified": actual_task_verified,
                "source_failure_diagnostic_executed": source_diagnostic_done,
                "source_fetch_status": snapshot.get("fetch_status", "not_recorded"),
                "source_url": url, "source_issue_present": seen,
                "source_triage_completed": task_assessed,
                "unverified_lead_flag": possible,
                "original_buyer_verified": False,
                "source_original_independently_refetched": bool(worker.get("original_issue_source_independently_refetched")),
                "client_contact_evidence": "NONE",
                "paid_client_acceptance_evidence": "NONE",
                "verified_payment_evidence": "NONE",
                "model_inference_evidence": bool(worker.get("ai_inference_completed")),
                "worker_result": ("SOURCE_TRIAGED_NO_VERIFIED_CUSTOMER" if task_assessed
                                  else "BLOCKED_NO_SOURCE" if no_source else "EVIDENCE_INVALID"),
                "forensic_errors": ";".join(errors),
            }
            # PROVE OR LEAVE: neither an exit code nor an order ID constitutes a
            # proven, task-capable worker. Do not delete mathematical role IDs.
            # A verified bounded source task qualifies; a source-failure diagnosis
            # is meaningful diagnostics but not customer-source execution.
            proof_conditions = (
                process_recorded and order_recorded
                and task.get("id") == worker_id
                and full_order_read and actual_task_verified
                and task_assessed and seen and not errors
            )
            if proof_conditions:
                roster_status = "PROVEN_FINITE_TASK_EXECUTED"
                reason = "REPLAYABLE_SOURCE_ASSESSMENT_WITH_ORDER_AND_TASK_PROOF"
            elif source_diagnostic_done and full_order_read and not errors:
                roster_status = "INACTIVE_REASSIGN_SOURCE_UNAVAILABLE"
                reason = "SOURCE_FAILURE_DIAGNOSIS_ONLY_NOT_CUSTOMER_WORK"
            elif errors:
                roster_status = "REMOVED_FROM_ACTIVE_NO_VALID_PROOF"
                reason = ";".join(errors)[:300]
            else:
                roster_status = "REMOVED_FROM_ACTIVE_NO_VALID_PROOF"
                reason = "NO_VERIFIED_COMPLETE_TASK_OUTPUT"
            row["active_roster_status"] = roster_status
            row["active_roster_evidence_reason"] = reason
            row["reassignment_required"] = roster_status != "PROVEN_FINITE_TASK_EXECUTED"
            if errors:
                failures.extend(f"{worker_id}:{err}" for err in errors)
            rows.append(row)

    summary = {
        "audit_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "900 individually named bounded Python subprocesses across 30 B1/B2 shards",
        "target_order": expected_order, "expected_worker_records": len(SHARDS) * WORKERS,
        "worker_records_examined": len(rows), "workers_with_any_error": sum(bool(r["forensic_errors"]) for r in rows),
        "workers_with_process_evidence": sum(r["process_recorded"] for r in rows),
        "workers_with_matching_order": sum(r["order_in_record"] for r in rows),
        "workers_with_specific_assigned_task": sum(r["task_assigned"] for r in rows),
        "workers_with_source_triage": sum(r["source_triage_completed"] for r in rows),
        "workers_with_full_owner_instruction_digest": sum(r["full_owner_order_text_digest_verified"] for r in rows),
        "workers_with_actual_individual_task_receipts": sum(r["actual_individual_task_evidence_verified"] for r in rows),
        "workers_with_source_failure_diagnostic": sum(r["source_failure_diagnostic_executed"] for r in rows),
        "workers_allowed_in_proven_finite_task_roster": sum(r["active_roster_status"] == "PROVEN_FINITE_TASK_EXECUTED" for r in rows),
        "workers_removed_from_active_roster_no_valid_proof": sum(r["active_roster_status"] == "REMOVED_FROM_ACTIVE_NO_VALID_PROOF" for r in rows),
        "workers_inactive_reassign_source_unavailable": sum(r["active_roster_status"] == "INACTIVE_REASSIGN_SOURCE_UNAVAILABLE" for r in rows),
        "workers_blocked_without_source": sum(r["worker_result"] == "BLOCKED_NO_SOURCE" for r in rows),
        "unverified_lead_flags_not_customers": sum(r["unverified_lead_flag"] for r in rows),
        "distinct_unverified_lead_urls": len(candidate_index),
        "actual_independently_verified_buyers": 0,
        "actual_external_proposals_sent": 0,
        "actual_model_inference_records": sum(r["model_inference_evidence"] for r in rows),
        "actual_accepted_paid_jobs": 0, "actually_verified_crypto_receipts": 0,
        "virtual_roles_not_audited_as_live_agents": 11255658980400,
        "all_900_identity_and_task_records_intact": len(failures) == 0 and len(rows) == 900,
        "all_900_completed_real_customer_task": False,
        "limitations": [
            "PID and timestamp are GitHub Actions worker self-reports, not hardware attestation",
            "A search result classification is only bounded Python work, not independently contacted customer",
            "The 11.25 trillion virtual role IDs cannot each be audited as running agents",
            "0 verified buyers or payments by this subprocess implementation",
        ], "sample_errors": failures[:80],
    }
    with (output / "worker-forensic-audit.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output / "worker-activity-roster.json").write_text(
        json.dumps({
            "owner_order_id": expected_order,
            "proof_gate": "Individual specific source task + owner instruction digest + verified record hashes",
            "not_proof_of_trillions_of_live_workers": True,
            "proven_finite_task_workers": [r["worker_id"] for r in rows if r["active_roster_status"] == "PROVEN_FINITE_TASK_EXECUTED"],
            "inactive_or_removed": [{"worker_id": r["worker_id"], "status": r["active_roster_status"], "reason": r["active_roster_evidence_reason"]}
                                     for r in rows if r["active_roster_status"] != "PROVEN_FINITE_TASK_EXECUTED"],
        }, indent=2) + "\n", encoding="utf-8"
    )
    (output / "worker-forensic-audit.json").write_text(
        json.dumps({"summary": summary, "workers": rows}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    md = ["# FORENSIC AUDIT OF INDIVIDUAL B1/B2 WORKER EXECUTION", "",
          f"Order: \`{expected_order}\`", "",
          "| Test | Actual evidence |", "|---|---:|"]
    for field in ("worker_records_examined", "workers_with_any_error", "workers_with_process_evidence",
                  "workers_with_matching_order", "workers_with_specific_assigned_task",
                  "workers_with_source_triage", "workers_with_full_owner_instruction_digest",
                  "workers_with_actual_individual_task_receipts",
                  "workers_with_source_failure_diagnostic",
                  "workers_allowed_in_proven_finite_task_roster",
                  "workers_removed_from_active_roster_no_valid_proof",
                  "workers_inactive_reassign_source_unavailable",
                  "workers_blocked_without_source",
                  "distinct_unverified_lead_urls", "actual_independently_verified_buyers",
                  "actual_external_proposals_sent", "actual_model_inference_records",
                  "actual_accepted_paid_jobs", "actually_verified_crypto_receipts"):
        md.append(f"| {field.replace('_', ' ')} | {summary[field]:,} |")
    md += ["", "## Findings",
           "- Each named worker has its own CSV row and machine-readable JSON record.",
           "- A matching order ID means a subprocess recorded that order, not that a separate AI model understood it.",
           "- A finite source-triage task can be completed without having won a customer.",
           "- NO_SOURCE is operationally blocked, not commercially completed.",
           "- No independent original-source fetch, authenticated proposal, acceptance, or chain payment is evidenced here.",
           "- Virtual role allocations cannot be treated as activated workers or jobs.",
           "", "## Corrective action",
           "Review all blocked or misclassified rows, repair rate limiting / search-source coverage,",
           "assign a qualified buyer to a real authorized bidding account, test the specific deliverable,",
           "and verify the resulting proposal and payment independently. Avoid self-authored issue hits.",
           "", f"Anomalies: {len(failures)}; first examples: " +
           (", ".join(failures[:10]) if failures else "none in identity/order/assessment integrity checks"), ""]
    (output / "REPORT.md").write_text("\n".join(md), encoding="utf-8")
    print("B1B2_FORENSIC_WORKER_SUMMARY " + json.dumps(summary, sort_keys=True))
    return summary


def self_test():
    """Detect false positives without accessing a network or running external work."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "evidence"
        for shard in SHARDS:
            d = root / shard
            d.mkdir(parents=True)
            snap = {"owner_order_id": "UNIT", "fetch_status": "ok", "source_query": "sample",
                    "items": [{"id": i, "title": "Paid sample", "html_url": f"https://github.com/test/repo/issues/{i}"}
                              for i in range(30)]}
            (d / "snapshot.json").write_text(json.dumps(snap))
            (d / "manifest.json").write_text(json.dumps(
                {"shard": shard, "owner_order_id": "UNIT", "child_process_successes": 30}))
            for slot in range(1, 31):
                wid = f"{shard}-W{slot:02d}"
                record = {"worker_id": wid, "company": shard[:2], "shard": shard,
                          "owner_order_id": "UNIT", "pid": 7, "parent_pid": 1,
                          "task": {"id": wid, "shard": shard, "slot": slot, "reports_to": shard},
                          "source_query": "sample", "snapshot_search_success": True,
                          "source_issue_seen": True, "worker_status": "reviewed_snapshot_issue",
                          "executed_utc": datetime.now(timezone.utc).isoformat(),
                          "assessment": {
                              "issue_id": slot - 1, "title": "Paid sample",
                              "source_url": f"https://github.com/test/repo/issues/{slot-1}",
                              "payer_verified": False, "customer_acceptance_verified": False,
                              "incoming_crypto_verified": False,
                              "possible_paid_lead_unverified": True},
                          "ai_inference_completed": False}
                (d / f"{wid}.json").write_text(json.dumps(record))
        out = examine(root, "UNIT", Path(tmp) / "out")
        assert out["worker_records_examined"] == 900
        assert out["workers_with_source_triage"] == 900
        assert out["workers_with_any_error"] == 0
        assert out["workers_allowed_in_proven_finite_task_roster"] == 0
        assert out["workers_removed_from_active_roster_no_valid_proof"] == 900
        assert out["actually_verified_crypto_receipts"] == 0
    print("FORENSIC_AUDIT_SELF_TEST_PASS")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="thousand-fleet-evidence")
    parser.add_argument("--order", default="")
    parser.add_argument("--out", default="forensic-audit-evidence")
    parser.add_argument("--strict-prompt", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    a = parser.parse_args()
    if a.self_test:
        self_test()
    else:
        if not a.order:
            parser.error("--order required for evidence audit")
        examine(a.root, a.order, a.out, a.strict_prompt)
