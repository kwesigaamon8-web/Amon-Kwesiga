#!/usr/bin/env python3
"""Country-routed authorized bounty research for the 11.26T VIRTUAL B1/B2 role namespace.

O(1) role queries, one selected bounty at a time, and NO network access or live
testing. Does not create model processes, post a finding, sign wallets or earn money.
Run at repository root: python crypto-agents/authorized_bounty_pipeline.py --self-test
"""
from __future__ import annotations
import argparse
import json
import random
from enigma_universal_owner_order import GRAND_TOTAL, PER_ROOT, assigned_country, envelope

ACTIVE_PROGRAM = {
    "id": "IMMUNEFI-01-THRESHOLD-NETWORK",
    "name": "Threshold Network",
    "platform": "Immunefi",
    "program": "https://immunefi.com/bug-bounty/thresholdnetwork/information/",
    "scope": "https://immunefi.com/bug-bounty/thresholdnetwork/scope/",
    "resources": "https://immunefi.com/bug-bounty/thresholdnetwork/resources/",
    "rules": "https://immunefi.com/rules/",
    "source_repo": "https://github.com/threshold-network/solidity-contracts",
    "first_in_scope_asset_name": "TokenholderGovernor",
    "first_in_scope_asset_address_ethereum": "0xd101f2b25bcbf992bdf55db67c104fe7646f5447",
    "first_local_source_path": "contracts/governance/BaseTokenholderGovernor.sol",
    "first_local_source_blob_sha": "4da8e704c67a85c863a249366a9f127307ba0e2d",
    "first_asset_onchain_testing_permitted": False,
    "deprecated_staking_contracts_excluded": True,
    "status": "PUBLICLY_LISTED_RULES_REVIEWED_NO_VULNERABILITY_CLAIM",
    "payout_usd_max_advertised": 150000,
    "payout_asset": "USDC_Ethereum_OR_T_Ethereum_AT_DAO_DISCRETION",
    "payout_asset_choice_by_whitehat": False,
    "payout_ethereum_wallet_owner_compatibility_verified": False,
    "public_testnet_or_mainnet_testing_authorized": False,
    "local_fork_or_offline_review_only": True,
    "kyc_requirement_from_program": "NO_KYC_FOR_PAYOUT",
    "bug_submission_authentication_verified": False,
    "live_exploit_or_poc_executed": False,
    "verified_payout": False,
}
# Future targets are NOT open work assignments; individual terms must be re-read.
FUTURE_PROGRAMS = (
    {"id": "IMMUNEFI-02-OPENZEPPELIN",
     "url": "https://immunefi.com/bug-bounty/openzeppelin/information/",
     "status": "WAITING_ONE_BY_ONE; ETHEREUM_MAINNET_PAYOUT_AND_KYC_REQUIRED"},
    {"id": "IMMUNEFI-03-IMMUNEFI",
     "url": "https://immunefi.com/bug-bounty/immunefi/information/",
     "status": "WAITING_ONE_BY_ONE; RULES_AND_KYC_REVIEW_REQUIRED"},
)
TASKS = (
    ("RULES", "Confirm current sponsor bounty rules, eligibility, embargo and exact deployed in-scope contract/code revision."),
    ("SCOPE", "Document exact in-scope contracts, accepted impact and prohibited targets; do not touch live systems."),
    ("SOURCE", "Study a small approved source file offline; record immutable upstream commit and testable invariant."),
    ("INVARIANT", "Write an invariant hypothesis and distinguish intended logic from known design tradeoffs."),
    ("LOCAL_TEST", "Construct unit-test-only harmless local regression to verify invariant, no live system activity."),
    ("KNOWN_ISSUES", "Compare candidate to disclosed audits, issues and excluded vulnerabilities before reporting."),
    ("INDEPENDENT_REVIEW", "Check impact and reproducible PoC against program terms; reject scanner-only speculation."),
    ("PAYMENT_QA", "Verify allowed submission path, eligibility, and correct Ethereum wallet asset/network before payout."),
)

def task_for_index(index: int) -> dict:
    """On-demand scoped task for one logical slot; NOT execution or receipt."""
    if type(index) is not int or not 0 <= index < GRAND_TOTAL:
        raise ValueError("Virtual role index is out of bounds")
    parent = envelope(index)
    root_index = index // PER_ROOT
    local_index = index % PER_ROOT
    lane_idx = local_index % len(TASKS)
    lane, instruction = TASKS[lane_idx]
    return {
        "schema": "B1_B2_AUTHORIZED_BOUNTY_ONE_BY_ONE_V1",
        "active_target": ACTIVE_PROGRAM,
        "future_targets_wait_for_prior_target_review": FUTURE_PROGRAMS,
        "virtual_role_index": index,
        "division_index": root_index,
        "configured_virtual_roles_in_division": PER_ROOT,
        "configured_global_role_count": GRAND_TOTAL,
        "actual_independent_active_workers_claimed": 0,
        "role": parent["recipient"]["role"],
        "role_country_assignment": assigned_country(index),
        "owner_order_id": parent["owner_order_id"],
        "parent_fleet": parent["recipient"]["verified_parent"],
        "worker_lane": lane,
        "task": instruction,
        "btc_mainnet_reference_only": parent["owner_wallet_and_country_instructions"]["both_btc_mainnet_receivers"],
        "allowed_activity": "PUBLIC_SCOPE_AND_SOURCE_READ_OFFLINE_LOCAL_UNIT_TESTS",
        "forbidden_activity": [
            "LIVE_MAINNET_OR_PUBLIC_TESTNET_ATTACKS",
            "SCANNING_OR_PROBING_THIRD_PARTY_SYSTEMS",
            "SOCIAL_ENGINEERING",
            "SENDING_BUG_REPORTS_WITHOUT_QUALIFYING_ORIGINAL_POC",
            "PUBLIC_DISCLOSURE_OF_UNPATCHED_FINDINGS",
            "CLAIMING_CRYPTO_RECEIPTS_WITHOUT_TXID",
            "GMAIL_ACCESS_OR_EMAIL_SENDING",
            "WALLET_SPENDING_OR_SIGNING",
        ],
        "must_check_before_submission": [
            "program still live and exact target in scope",
            "impact and reproducible local-only proof of concept",
            "prior audits and duplicates ruled out",
            "submission through authenticated platform dashboard",
            "owner-authorized researcher identity and program rules",
            "payout chain, asset, destination ownership and token support verified",
        ],
        "individual_worker_actual_execution_evidenced": False,
        "report_submitted": False,
        "paid_reward_verified": False,
    }

def overview() -> dict:
    return {
        "target": ACTIVE_PROGRAM,
        "division_count": 30,
        "country_allocations_per_division": None,
        "configured_virtual_role_slots": GRAND_TOTAL,
        "each_virtual_role_mapped": True,
        "lane_count": len(TASKS),
        "real_agent_completions_evidenced": 0,
        "submitted_validated_bugs": 0,
        "confirmed_crypto_payouts": 0,
    }

def self_test():
    assert GRAND_TOTAL == 11255658980400 and 30 * PER_ROOT == GRAND_TOTAL
    tested = set()
    rng = random.Random(20261120)
    for root in range(30):
        for local in [0,1,2,3,4,5,6,7,PER_ROOT//2,PER_ROOT-1]:
            tested.add(root*PER_ROOT+local)
    tested.update(rng.randrange(GRAND_TOTAL) for _ in range(60))
    observed_lanes = set()
    for idx in sorted(tested):
        packet = task_for_index(idx)
        assert packet["division_index"] == idx // PER_ROOT
        assert packet["configured_global_role_count"] == GRAND_TOTAL
        assert packet["active_target"]["id"] == ACTIVE_PROGRAM["id"]
        assert packet["active_target"]["first_in_scope_asset_name"] == "TokenholderGovernor"
        assert packet["active_target"]["deprecated_staking_contracts_excluded"]
        assert packet["role_country_assignment"]["root_system_index"] == idx // PER_ROOT
        assert len(packet["btc_mainnet_reference_only"]) == 2
        assert packet["individual_worker_actual_execution_evidenced"] is False
        assert packet["paid_reward_verified"] is False
        observed_lanes.add(packet["worker_lane"])
    assert observed_lanes == {t[0] for t in TASKS}
    for wrong in (-1, GRAND_TOTAL, True, 5.0, None):
        try: task_for_index(wrong)
        except ValueError: pass
        else: raise AssertionError("Accepted invalid worker index")
    print("BOUNTY_ONE_BY_ONE_ALL_11T_VIRTUAL_ROLES_TEST_PASS",
          json.dumps({"virtual_roles":GRAND_TOTAL,"divisions":30,
             "role_samples":len(tested),"lanes":len(TASKS),
             "first_target":ACTIVE_PROGRAM["id"],"live_worker_deliveries":0,
             "actual_payouts":0},sort_keys=True))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--index",type=int)
    group.add_argument("--overview",action="store_true")
    group.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    if args.index is not None: print(json.dumps(task_for_index(args.index),indent=2))
    elif args.overview: print(json.dumps(overview(),indent=2))
    else: self_test()
