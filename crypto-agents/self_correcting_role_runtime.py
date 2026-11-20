"""One auditable, fail-closed, self-correcting runtime for every B1/B2 role.

This module is shared by all 30 root namespaces across 11,255,658,980,400
LAZILY ADDRESSABLE role IDs. A role gains an execution/repair receipt ONLY when
a real Python process invokes its code. No 11T processes, AI model calls, miner
hashing, wallet payments, communications, or new accounts are created.

Repair means validating and re-deriving a safe IN-MEMORY public-lead view:
strip harmless URL whitespace, discard unsafe/malformed/duplicate source links,
and reject self-asserted buyer acceptance or payment flags. The source ledger,
owner order, role tree, code, and wallet addresses are NEVER edited.

An expired/altered owner instruction or failed task/output integrity check is
not automatically "corrected": it is blocked for a real authorized review.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
import re
from urllib.parse import urlsplit

GRAND_TOTAL = 11_255_658_980_400
TIERS = frozenset(("D", "A", "M", "W", "S", "G", "H"))
MAX_RECORDS = 1000
MAX_EXECUTION_ATTEMPTS = 2
SCHEMA = "B1B2_ONE_SHARED_SELF_CORRECTING_ROLE_RUNTIME_V1"


def digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), default=str).encode("utf-8")).hexdigest()


def verify_authority(ctx, authoritative=None):
    """Fail closed; cannot invent or rewrite a human owner instruction."""
    from directive_cascade import read_owner
    owner = authoritative if authoritative is not None else read_owner()
    if not isinstance(ctx, dict) or not isinstance(owner, dict):
        raise ValueError("SELF_HEAL_AUTHORITY_INVALID")
    idx = ctx.get("role_index")
    if type(idx) is not int or not 0 <= idx < GRAND_TOTAL:
        raise ValueError("SELF_HEAL_ROLE_INDEX_INVALID")
    path = ctx.get("path")
    if (not isinstance(path, list) or len(path) < 4
            or path[:2] != ["HUMAN_OWNER", "CHIEF_D"]
            or path[-1] != ctx.get("role_id")
            or path[-2] != ctx.get("parent")
            or ctx.get("tier") not in TIERS):
        raise ValueError("SELF_HEAL_PARENT_CHAIN_INVALID")
    order = ctx.get("owner_command") or {}
    packet = ctx.get("packet") or {}
    if (owner.get("owner_order_id") != order.get("owner_order_id")
            or owner.get("owner_sha256") != order.get("owner_sha256")
            or owner.get("standard_sha256") != order.get("standard_sha256")
            or owner.get("owner_order_id") != packet.get("owner_order_id")
            or owner.get("owner_sha256") != packet.get("owner_instruction_sha256")
            or owner.get("standard_sha256") != packet.get("standard_prompt_sha256")):
        raise ValueError("SELF_HEAL_STALE_OR_TAMPERED_OWNER_ORDER")
    if (ctx.get("role_id") != path[-1]
            or ctx.get("role_id") == ""
            or not ctx.get("role_id", "").startswith(ctx.get("root_id", "") + "/")
            or packet.get("immediate_parent") != ctx.get("parent")):
        raise ValueError("SELF_HEAL_ROLE_NOT_AUTHORITATIVE")
    return {
        "current_order_id": owner["owner_order_id"],
        "owner_instruction_sha256": owner["owner_sha256"],
        "standing_prompt_sha256": owner["standard_sha256"],
        "authority_verified": True,
    }


def safe_https_url(raw):
    if not isinstance(raw, str):
        return None
    url = raw.strip()
    if not url or len(url) > 2000 or any(ord(c) < 32 for c in url):
        return None
    try:
        p = urlsplit(url)
        if (p.scheme != "https" or not p.hostname or p.username is not None
                or p.password is not None or p.fragment or not p.netloc
                or p.hostname in ("localhost", "127.0.0.1", "::1")
                or p.hostname.endswith((".local", ".internal"))
                or not re.fullmatch(r"[A-Za-z0-9.-]+", p.hostname)):
            return None
        if p.port not in (None, 443):
            return None
    except ValueError:
        return None
    # Strict parse/shape checks are not a guarantee of legitimate buyers.
    return url


def safe_view(raw):
    """Never mutate source; return bounded, independently auditable correction."""
    if not isinstance(raw, list):
        raise ValueError("SELF_HEAL_SOURCE_NOT_A_LIST")
    if len(raw) > MAX_RECORDS:
        raise ValueError("SELF_HEAL_SOURCE_TOO_LARGE_REVIEW_REQUIRED")
    rows, fixes, seen = [], [], set()
    for position, item in enumerate(raw, 1):
        if not isinstance(item, dict):
            fixes.append({"row": position, "action": "EXCLUDE_NON_OBJECT_SOURCE"})
            continue
        original_url = item.get("url")
        url = safe_https_url(original_url)
        if url is None:
            fixes.append({"row": position, "action": "EXCLUDE_UNSAFE_OR_MISSING_HTTPS_URL"})
            continue
        identity = urlsplit(url)._replace(fragment="").geturl()
        if identity in seen:
            fixes.append({"row": position, "action": "EXCLUDE_DUPLICATE_PUBLIC_SOURCE"})
            continue
        seen.add(identity)
        row = dict(item)
        if original_url != url:
            fixes.append({"row": position, "action": "TRIM_URL_WHITESPACE_IN_MEMORY"})
            row["url"] = url
        # A source JSON claim is not buyer acceptance or chain evidence.
        # These are intentionally derived-view resets, never source edits.
        for unverified in ("payment_verified", "scope_commitment_accepted"):
            if row.get(unverified) is True:
                row[unverified] = False
                fixes.append({"row": position, "action": "HOLD_UNVERIFIED_" + unverified.upper()})
        status = str(row.get("platform_submission_status") or "NOT_SENT")
        if status.startswith("SENT_VERIFIED"):
            row["platform_submission_status"] = "HOLD_INDEPENDENT_SUBMISSION_EVIDENCE"
            fixes.append({"row": position, "action": "HOLD_UNVERIFIED_SUBMISSION_CLAIM"})
        rows.append(row)
    return rows, fixes


def verify_result(ctx, view, output):
    if not isinstance(output, dict) or not isinstance(output.get("action"), str):
        raise ValueError("SELF_HEAL_RESULT_NOT_AN_ACTION")
    audit = output.get("source_audit")
    if not isinstance(audit, dict) or audit.get("records_examined") != len(view):
        raise ValueError("SELF_HEAL_SOURCE_AUDIT_MISMATCH")
    if audit.get("payments_verified_by_this_process") != 0 or audit.get("contacts_sent_by_this_process") != 0:
        raise ValueError("SELF_HEAL_UNAUTHORIZED_CONTACT_OR_PAYMENT_CLAIM")
    if ctx["tier"] in ("W", "S", "G", "H") and output.get("tier") != ctx["tier"]:
        raise ValueError("SELF_HEAL_TIER_RESULT_MISMATCH")
    if output.get("new_payment_verified") is True or output.get("buyer_contacted") is True:
        raise ValueError("SELF_HEAL_UNSUPPORTED_EXTERNAL_ACTIVITY")
    return digest(output)


def execute(ctx, raw, action_function, authoritative=None):
    """One source-only operation with at most 2 safe local verification attempts.

    External operations are NEVER passed here. The caller is responsible for
    supplying its already-existing local deterministic, side-effect-free task.
    """
    proof = verify_authority(ctx, authoritative)
    if not callable(action_function):
        raise ValueError("SELF_HEAL_NO_AUTHORIZED_ACTION")
    original_hash = digest(raw)
    view, corrections = safe_view(raw)
    # No unverified sources means blocked. Still execute only the local
    # deterministic "no source" diagnosis; no network retry or fake customer.
    action, evidence = None, None
    errors = []
    for attempt in range(1, MAX_EXECUTION_ATTEMPTS + 1):
        try:
            action = action_function(ctx, [dict(r) for r in view])
            evidence = verify_result(ctx, view, action)
            break
        except (ValueError, TypeError, KeyError, IndexError) as exc:
            errors.append(type(exc).__name__ + ":" + str(exc)[:75])
            # Re-derive from untouched raw source before one pure local retry.
            view, rechecked = safe_view(raw)
            if rechecked != corrections:
                raise ValueError("SELF_HEAL_CORRECTION_NOT_DETERMINISTIC")
    if evidence is None:
        raise ValueError("SELF_HEAL_LOCAL_TASK_FAILED_AFTER_BOUNDED_RETEST")
    status = ("BLOCKED_NO_SAFE_PUBLIC_SOURCE" if not view
              else "VERIFIED_LOCAL_TASK_AFTER_REPAIR" if corrections
              else "VERIFIED_LOCAL_TASK_NO_REPAIR")
    receipt = {
        "schema": SCHEMA,
        "utc": datetime.now(timezone.utc).isoformat(),
        "role_index": str(ctx["role_index"]),
        "role_id": ctx["role_id"],
        "tier": ctx["tier"],
        "root_id": ctx["root_id"],
        "immediate_parent": ctx["parent"],
        "real_python_pid": os.getpid(),
        **proof,
        "input_source_sha256": original_hash,
        "safe_derived_view_sha256": digest(view),
        "source_rows": len(raw),
        "validated_public_rows": len(view),
        "corrections": corrections,
        "correction_count": len(corrections),
        "attempts": attempt,
        "local_errors_before_retest": errors,
        "status": status,
        "task_output_sha256": evidence,
        "canonical_source_changed": False,
        "external_source_contacted": False,
        "model_inference_completed": False,
        "wallet_or_email_accessed": False,
        "wallet_balance_or_payment_independently_verified": False,
        "other_virtual_workers_notified": False,
        "genuine_paid_customer_verified": False,
    }
    if receipt["task_output_sha256"] != digest(action):
        raise ValueError("SELF_HEAL_EVIDENCE_DRIFT")
    return action, receipt
