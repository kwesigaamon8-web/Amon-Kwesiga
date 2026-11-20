"""Acceptance tests for one self-correcting engine available to 11.25T roles.

Executed samples only; never claim these tests provisioned the other role IDs.
"""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
import sys

sys.path.insert(0, "crypto-agents")
from b_certified_agent_service_router import OFFSETS
from enigma_universal_owner_order import GRAND_TOTAL, PER_ROOT
from hierarchy_command_core import task_context, execute as full_execute, ROLE_ACTIONS
from self_correcting_role_runtime import (
    MAX_EXECUTION_ATTEMPTS, safe_view, safe_https_url,
    verify_authority, verify_result, execute, digest, SCHEMA
)

OUT = Path("self-correction-evidence/role-hierarchy")


def reject(func, marker):
    try:
        func()
    except (ValueError, TypeError) as exc:
        if marker not in str(exc):
            raise AssertionError(f"Wrong rejection: {exc}") from exc
    else:
        raise AssertionError("Expected rejection not enforced: " + marker)


def main():
    assert GRAND_TOTAL == 11_255_658_980_400
    assert 30 * PER_ROOT == GRAND_TOTAL
    assert MAX_EXECUTION_ATTEMPTS == 2
    base = task_context(OFFSETS["W"], expected={"W"})
    assert verify_authority(base)["authority_verified"]
    bad_parent = dict(base, parent="UNKNOWN/WRONG")
    reject(lambda: verify_authority(bad_parent), "SELF_HEAL_PARENT_CHAIN_INVALID")
    bad_order = dict(base, owner_command=dict(base["owner_command"], owner_order_id="ATTACK"))
    reject(lambda: verify_authority(bad_order), "SELF_HEAL_STALE_OR_TAMPERED_OWNER_ORDER")
    bad_route = dict(base, packet=dict(base["packet"], immediate_parent="WRONG"))
    reject(lambda: verify_authority(bad_route), "SELF_HEAL_ROLE_NOT_AUTHORITATIVE")
    bad_index = dict(base, role_index=GRAND_TOTAL)
    reject(lambda: verify_authority(bad_index), "SELF_HEAL_ROLE_INDEX_INVALID")
    reject(lambda: verify_authority(dict(base, role_index=True)),
           "SELF_HEAL_ROLE_INDEX_INVALID")
    reject(lambda: safe_view({"url": "https://example.com"}), "SELF_HEAL_SOURCE_NOT_A_LIST")

    assert safe_https_url(" https://example.com/job ") == "https://example.com/job"
    for url in ("http://example.com", "https://user:pass@example.com",
                "https://127.0.0.1/private", "https://example.com:8080",
                "https://example.com/#fragment", "https://example.com/\nsecret"):
        assert safe_https_url(url) is None, url
    sample = [
        {"url": " https://example.com/task ", "payment_verified": True,
         "scope_commitment_accepted": True,
         "platform_submission_status": "SENT_VERIFIED_UNTRUSTED"},
        {"url": "https://example.com/task"},
        {"url": "http://bad.example.com/unsafe"},
        {"missing": True},
        "invalid",
        {"url": "https://another.example.com/job", "payment_verified": False},
    ]
    clone = json.loads(json.dumps(sample))
    clean, corrections = safe_view(sample)
    assert sample == clone, "Original source data was modified"
    assert len(clean) == 2
    assert len(corrections) == 7, corrections
    assert clean[0]["payment_verified"] is False
    assert clean[0]["scope_commitment_accepted"] is False
    assert clean[0]["platform_submission_status"] == "HOLD_INDEPENDENT_SUBMISSION_EVIDENCE"
    assert all(r["url"].startswith("https://") for r in clean)
    # A truly corrected local source can be retested independently without claiming payer contact.
    action, report = execute(base, sample, ROLE_ACTIONS["W"])
    assert action["action"] == "WORKER_SHARED_CODE_LEAD_EVIDENCE_REVIEW"
    assert report["schema"] == SCHEMA
    assert report["status"] == "VERIFIED_LOCAL_TASK_AFTER_REPAIR"
    assert report["attempts"] == 1
    assert report["correction_count"] == 7
    assert not report["model_inference_completed"] and not report["wallet_or_email_accessed"]
    assert not report["other_virtual_workers_notified"]
    assert report["task_output_sha256"] == digest(action)

    # Explicit bounded local retry proves a recoverable pure-function fault
    # is not mistaken for 11T workers remotely repairing themselves.
    attempts = [0]
    def transient(ctx, rows):
        attempts[0] += 1
        if attempts[0] == 1:
            raise ValueError("Transient local parse state")
        return ROLE_ACTIONS["W"](ctx, rows)
    _, retried = execute(base, sample, transient)
    assert retried["attempts"] == 2
    assert len(retried["local_errors_before_retest"]) == 1
    reject(lambda: execute(base, sample, lambda *_: {"action": "fake"}),
           "SELF_HEAL_LOCAL_TASK_FAILED_AFTER_BOUNDED_RETEST")
    action_empty, blocked = execute(base, [{"url": "ftp://invalid"}], ROLE_ACTIONS["W"])
    assert blocked["status"] == "BLOCKED_NO_SAFE_PUBLIC_SOURCE"
    assert action_empty["action"] == "WORKER_SOURCE_BLOCKER"
    assert not blocked["genuine_paid_customer_verified"]

    # No fake bulk provisioning: we really invoke 210 existing role programs
    # in this process (30 divisions * 7 tier executions). The same shared code
    # is not cloned into trillions of worker files.
    counts = Counter()
    root_status = []
    for root in range(30):
        for tier in ("D", "A", "M", "W", "S", "G", "H"):
            idx = root * PER_ROOT + OFFSETS[tier]
            result = full_execute(idx, expected={tier})
            proof = result["self_correction"]
            assert proof["schema"] == SCHEMA
            assert proof["role_index"] == str(idx)
            assert proof["role_id"] == result["role_id"]
            assert proof["immediate_parent"] == result["supervisor"]
            assert proof["tier"] == tier
            assert proof["status"] == "VERIFIED_LOCAL_TASK_NO_REPAIR"
            assert proof["authority_verified"] is True
            assert proof["task_output_sha256"] == digest(result["task_result"])
            assert not proof["external_source_contacted"]
            assert not proof["other_virtual_workers_notified"]
            assert result["ai_model_inference_completed"] is False
            assert result["payment_received_verified"] is False
            counts[tier] += 1
            root_status.append({
                "root": root, "tier": tier, "role": result["role_id"],
                "index": str(idx), "status": proof["status"],
                "sha256": proof["task_output_sha256"],
                "process_id": proof["real_python_pid"],
            })
    assert sum(counts.values()) == 210
    assert all(counts[x] == 30 for x in ("D", "A", "M", "W", "S", "G", "H"))
    summary = {
        "schema": "B1B2_SELF_CORRECTING_ALL_11T_ADDRESSABLE_ROLES_PROOF_V1",
        "all_defined_role_positions_addressable": GRAND_TOTAL,
        "total_root_divisions": 30,
        "actual_local_python_role_invocations": len(root_status),
        "invocations_by_tier": dict(counts),
        "source_correction_negative_cases_passed": True,
        "stale_order_and_wrong_parent_rejected": True,
        "pure_local_retry_bounded_to": MAX_EXECUTION_ATTEMPTS,
        "all_divisions_use_one_shared_repair_code": True,
        "wallet_email_and_external_account_access": 0,
        "independently_completed_model_calls_in_this_test": 0,
        "real_buyer_submissions": 0,
        "verified_crypto_receipts": 0,
        "11t_concurrently_active_workers": False,
        "per_role_receipts": root_status,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "self-correcting-all-roots-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print("B1B2_ONE_CODE_ALL_ROLES_SELF_CORRECTION_PASS", json.dumps({
        key: value for key, value in summary.items() if key != "per_role_receipts"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
