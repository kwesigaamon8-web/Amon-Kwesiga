"""B1/B2 owner message addressing for all 750,377,265,360 *virtual* roles.

A compact deterministic mail-merge function, not a bulk messenger.
Only when a genuine worker process starts can it read its one addressed order.
No email, private messaging, social posting or customer outreach occurs here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
try:
    from .country_market_research import worker_country
except ImportError:
    from country_market_research import worker_country
from datetime import datetime, timezone

try:
    from .role_campaign_dispatch import (
        FLEETS, ALL_ROLES, PER_FLEET, assignment,
        fleet_for_global_index, role_from_local_index
    )
except ImportError:
    from role_campaign_dispatch import (
        FLEETS, ALL_ROLES, PER_FLEET, assignment,
        fleet_for_global_index, role_from_local_index
    )

VERSION = "B1B2-CAMPAIGN-MSG-V1-20261120"
ALLOWED_POSTING = "NO_EXTERNAL_PUBLISHING_OR_MASS_MESSAGES_FROM_THIS_ENGINE"
LIVE_DIRECTORY = (
    "https://github.com/kwesigaamon8-web/Amon-Kwesiga/"
    "blob/main/docs/LIVE_SITE.md"
)
BUYER_ROUTE = (
    "https://github.com/kwesigaamon8-web/Amon-Kwesiga/"
    "issues/new?template=paid-work-request.yml"
)
VOLUNTEER_ROUTE = (
    "https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/36"
)
PAYMENT_SAFETY = (
    "https://github.com/kwesigaamon8-web/Amon-Kwesiga/"
    "blob/main/docs/payment.html"
)


def build_message(fleet: str, role: str) -> dict:
    """Address one message in O(1) space; virtual assignment, not a send."""
    assigned = assignment(fleet, role)
    jurisdiction_task = worker_country(assigned["global_index_zero_based"])
    digest = hashlib.sha256(
        (VERSION + "|" + fleet + "/" + role).encode("utf-8")
    ).hexdigest()[:20]
    id_ = VERSION + "-" + digest
    company = assigned["fleet_agent"]
    summary = (
        "OWNER FREE SOFTWARE CAMPAIGN: 67 original free tools and applications "
        "(55 browser utilities, 12 mini-apps). Public code and source links only. "
        "No account, donation or payment required to use free software."
    )
    tasks = [
        "Confirm the product functions by testing original source. "
        "Never copy non-permissively licensed code.",
        assigned["work_order"],
        "COUNTRY RESEARCH "+jurisdiction_task["country_or_territory_code"]+
        ": "+jurisdiction_task["candidate_issue_to_investigate"]+
        " Cross-check World Bank and current local primary sources; never treat a hypothesis as a verified problem.",
        "Research real interested audiences and their actual posting rules; "
        "only post using a connected, legitimately authorized account "
        "when the community permits that original, useful content.",
        "Report proof of actual tests, permissions and public publishing URLs; "
        "otherwise explicitly mark DRAFT_ONLY or NO_POST.",
        "Send work evidence along the existing parent/director path to "
        + company + " and Chief D. Do not fabricate buyers, metrics or payments.",
    ]
    return {
        "schema": VERSION,
        "message_id": id_,
        "message_address": fleet + "/" + role,
        "global_index_zero_based": assigned["global_index_zero_based"],
        "recipient": {"fleet": fleet, "role": role, "agent": company},
        "routing": {
            "parent": assigned["parent_id"],
            "director": assigned["director_id"],
            "reported_to_agent": company,
            "final_reporting": "Chief D",
        },
        "region_assignment": assigned["region_research_assignment"],
        "country_market_research": jurisdiction_task,
        "languages_for_editorial_research": assigned["suggested_languages"],
        "product": {
            "name": assigned["software_focus"],
            "path": assigned["source_path"],
            "stable_live_site": LIVE_DIRECTORY,
        },
        "subject": "Owner-approved B1/B2 worldwide free software release and evidence task",
        "summary": summary,
        "required_actions": tasks,
        "calls_to_action": {
            "free_software": LIVE_DIRECTORY,
            "voluntary_contributions": VOLUNTEER_ROUTE,
            "specific_paid_work_request": BUYER_ROUTE,
            "optional_BTC_mainnet_support_only": PAYMENT_SAFETY,
        },
        "permission_rules": {
            "no_email_read_draft_or_send": True,
            "no_unsolicited_bulk_posts_or_dms": True,
            "no_improper_identity_or_platform_bypass": True,
            "no_proprietary_code_copy": True,
            "no_wallet_signing_or_transfers": True,
            "no_unverified_external_post_claims": True,
            "no_private_customer_data": True,
            "external_post_requires_connected_account_and_platform_permission": True,
        },
        "delivery_status": "VIRTUAL_ADDRESS_ONLY_NOT_SENT",
        "received_by_real_worker_process": False,
        "AI_model_read_receipt_verified": False,
        "external_platform_posted": False,
        "verified_external_post_url": None,
        "verified_buyer_acceptance": False,
        "verified_crypto_payment": "NOT_ASSESSED",
        "workforce_roles_defined_not_active_count": ALL_ROLES,
        "worker_execution_count_proved_by_message": 0,
        "note": (
            "This addresses a role definition only. Reading this in a real "
            "worker process establishes process access, not autonomous "
            "model comprehension, external delivery, marketing reach or revenue."
        ),
    }


def worker_process_order(fleet: str, role: str) -> dict:
    """Invoked only by an actual worker process; still not model comprehension."""
    msg = build_message(fleet, role)
    msg["delivery_status"] = "READ_BY_ACTUAL_WORKER_PROCESS_AT_START"
    msg["received_by_real_worker_process"] = True
    msg["worker_process_read_utc"] = datetime.now(timezone.utc).isoformat()
    msg["worker_execution_count_proved_by_message"] = 1
    return msg


def model_instruction(msg: dict) -> str:
    """Bounded plain instruction inserted into a real process's model prompt."""
    if msg.get("delivery_status") != "READ_BY_ACTUAL_WORKER_PROCESS_AT_START":
        raise ValueError("Only process-read messages may be injected into model")
    line = (
        " B1B2 OWNER INTERNAL MESSAGE " + msg["message_id"] + "; "
        "RECIPIENT " + msg["message_address"] + "; "
        "DIRECTOR " + msg["routing"]["director"] + "; "
        "TASK " + msg["required_actions"][1] + "; "
        "REGION " + msg["region_assignment"] + "; "
        "COUNTRY_RESEARCH " + msg["country_market_research"]["country_or_territory_code"] +
        " (unverified local problem; research first); "
        "PRODUCT " + msg["product"]["name"] + "; "
        "SOURCE " + msg["product"]["path"] + "; "
        "PUBLIC SOFTWARE " + msg["product"]["stable_live_site"] + ". "
        "No email, spam, bulk social messaging, fake active agents, "
        "copied proprietary code, invented customers or money. "
        "Only permitted posts with real URLs. Report to "
        + msg["routing"]["reported_to_agent"] + " then Chief D."
    )
    if len(line) > 1650:
        raise ValueError("Owner message exceeds bounded prompt size")
    return line


def main():
    p = argparse.ArgumentParser(
        description="Address virtual B1/B2 messages (no external sending)"
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--global-index", type=int)
    group.add_argument("--role")
    group.add_argument("--sample", type=int)
    p.add_argument("--fleet", choices=FLEETS)
    args = p.parse_args()
    if args.global_index is not None:
        fleet, local = fleet_for_global_index(args.global_index)
        records = [build_message(fleet, role_from_local_index(local))]
    elif args.role:
        if not args.fleet:
            p.error("--fleet required with --role")
        records = [build_message(args.fleet, args.role)]
    else:
        if not (1 <= args.sample <= 20):
            p.error("sample must be 1-20")
        records = []
        for i in range(args.sample):
            index = i * (ALL_ROLES - 1) // max(1, args.sample - 1)
            fleet, local = fleet_for_global_index(index)
            records.append(build_message(fleet, role_from_local_index(local)))
    print(json.dumps({
        "message_space_available": ALL_ROLES,
        "message_templates_materialized_in_this_call": len(records),
        "actual_messages_transmitted_to_live_accounts": 0,
        "actual_social_media_posts_sent": 0,
        "mode": ALLOWED_POSTING,
        "items": records,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
