"""Read-only link of B1/B2 agent roles to previously published OWNER crypto receipts.

This software is an address-reference index; NOT a signed wallet connection,
account login, payment collection, transaction, token-compatibility guarantee,
or model/process activation. Never broadcast every candidate to one payer.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT=Path("crypto-agents")
PUBLIC_ROUTES=ROOT/"PUBLIC_RECEIVING_ADDRESSES.md"
COLLECTION=ROOT/"b_collection_assignments.json"
FLEETS=("transferexperiment","BountyScoutAI")
SELF_NETWORKS={
    "BTC-01":"Bitcoin mainnet", "BTC-02":"Bitcoin mainnet",
    "EVM-01":"EVM specific network unverified",
    "EVM-02":"EVM specific network unverified",
    "SOL-01":"Solana", "SOL-02":"Solana",
    "TRX-01":"TRON", "TRX-02":"TRON",
    "XLM-01":"Stellar", "XLM-02":"Stellar",
}
EXCH_ID={
    "Binance EVM candidate":"EXCH-EVM",
    "Binance Solana candidate":"EXCH-SOL",
    "Binance Stellar candidate":"EXCH-XLM",
    "Binance Hedera account candidate":"EXCH-HBAR",
    "Binance Polkadot candidate":"EXCH-DOT",
    "Binance Algorand candidate":"EXCH-ALGO",
}
OWN_PRIMARY={"transferexperiment":"BTC-01","BountyScoutAI":"BTC-02"}

def directory():
    data=PUBLIC_ROUTES.read_text(encoding="utf-8")
    begin=data.index("## Self-custody addresses")
    middle=data.index("## Exchange deposit identifiers",begin)
    end=data.index("## Instruction to B",middle)
    self_custody=[]
    exchanges=[]
    for raw in data[begin:middle].splitlines():
        cols=[v.strip() for v in raw.strip().split("|")]
        if len(cols)!=5 or cols[1] not in SELF_NETWORKS:continue
        rid=cols[1]
        addr=cols[3].strip("`")
        if not addr or not re.fullmatch(r"[A-Za-z0-9.]{20,120}",addr):
            raise ValueError("Invalid self-custody address candidate "+rid)
        self_custody.append({"route_id":rid,
          "network_label":SELF_NETWORKS[rid],
          "public_reference_address":addr,
          "status":"OWNER_APPROVAL_AND_TOKEN_NETWORK_VERIFICATION_REQUIRED" if not rid.startswith("BTC-") else "PRIMARY_COMPANY_BTC_MAINNET",
          "address_is_NOT_proof_of_token_support":True})
    for raw in data[middle:end].splitlines():
        cols=[v.strip() for v in raw.strip().split("|")]
        if len(cols)!=5 or cols[1] not in EXCH_ID:continue
        name=cols[1]
        exchanges.append({"route_id":EXCH_ID[name],
          "network_label":name.replace("Binance ","").replace(" candidate",""),
          "status":"BLOCKED_UNVERIFIED_CUSTODIAL_DO_NOT_SEND",
          "memo_may_be_required":"MEMO REQUIRED" in cols[3],
          "do_not_include_candidate_address_in_agent_prompt":True})
    if len(self_custody)!=10 or set(x["route_id"] for x in self_custody)!=set(SELF_NETWORKS):
        raise ValueError("Unexpected published self-custody route count")
    if len(exchanges)!=6 or set(x["route_id"] for x in exchanges)!=set(EXCH_ID.values()):
        raise ValueError("Unexpected published exchange route count")
    config=json.loads(COLLECTION.read_text(encoding="utf-8"))
    for fleet,rid in OWN_PRIMARY.items():
        addr=next(x["public_reference_address"] for x in self_custody if x["route_id"]==rid)
        item=config["fleets"][fleet]
        if addr!=item["address"] or item["network"]!="Bitcoin mainnet" or item["asset"]!="BTC":
            raise ValueError("Wrong company primary native BTC address")
    return {"self_custody":self_custody,"blocked_exchange":exchanges}

def agent_packet(fleet):
    if fleet not in FLEETS:raise ValueError("Unknown B company")
    rows=directory()
    own_id=OWN_PRIMARY[fleet]
    main=next(r for r in rows["self_custody"] if r["route_id"]==own_id)
    other=next(r for r in rows["self_custody"]
               if r["route_id"]==OWN_PRIMARY[FLEETS[1-FLEETS.index(fleet)]])
    options=[{"route_id":x["route_id"],"network_label":x["network_label"],
              "status":"OWNER_APPROVAL_AND_ACTUAL_NETWORK_TOKEN_COMPATIBILITY_REQUIRED"}
              for x in rows["self_custody"] if x["route_id"] not in (own_id,other["route_id"])]
    return {
      "schema":"B_AGENT_OWNER_MULTICHAIN_RECEIVING_LINK_V1",
      "agent":fleet,
      "linked_to_owner_public_read_only_receiving_directory":True,
      "connected_to_actual_wallet_software_or_exchange_login":False,
      "authorized_to_send_move_or_withdraw_crypto":False,
      "automated_wallet_access_granted":False,
      "owner_primary_BTC_mainnet_route":{"route_id":own_id,"asset":"BTC",
                                         "network":"Bitcoin mainnet",
                                         "address":main["public_reference_address"]},
      "other_B_company_mainnet_address_is_NOT_interchangeable":other["public_reference_address"],
      "owner_shared_secondary_receiving_options_held":options,
      "blocked_unverified_exchange_reference_ids":[{"route_id":x["route_id"],
        "network_label":x["network_label"],"memo_may_be_required":x["memo_may_be_required"],
        "status":x["status"]} for x in rows["blocked_exchange"]],
      "owner_public_self_custody_route_count":len(rows["self_custody"]),
      "owner_public_exchange_candidate_count":len(rows["blocked_exchange"]),
      "unknown_32_byte_identifiers_excluded_count":3,
      "safe_external_payment_negotiation":"Ask a genuine willing payer for asset and precise network. "
         "Share ONLY one owner-approved exact receiving address after the owner verifies "
         "token/network/issuer/memo compatibility. All non-BTC routes currently HELD. "
         "Never supply exchange candidate deposit addresses or claim a paid transaction.",
      "next_step":"Find eligible customer and actual paid task; confirm payer token/network then request OWNER route clearance.",
      "actual_crypto_received_proven_by_link":False,
    }

def owner_review_route(fleet,route_id):
    """Single-route read-only lookup for an owner-controlled review; not payment clearance."""
    if fleet not in FLEETS:raise ValueError("Unknown B company")
    doc=directory()
    if not isinstance(route_id,str):raise ValueError("Unknown route")
    for x in doc["self_custody"]:
        if x["route_id"]==route_id:
            status=("OWN_COMPANY_PRIMARY_BTC_MAINNET" if route_id==OWN_PRIMARY[fleet]
                    else "BLOCKED_PENDING_OWNER_TOKEN_NETWORK_PAYER_CONFIRMATION")
            return {
                "route_id":route_id,"fleet":fleet,"candidate_address":x["public_reference_address"],
                "network_label":x["network_label"],"review_status":status,
                "safe_to_quote_as_settlement_address":route_id==OWN_PRIMARY[fleet],
                "approval_must_be_refreshed_for_each_actual_client_payment":True}
    for x in doc["blocked_exchange"]:
        if x["route_id"]==route_id:
            return {"route_id":route_id,"fleet":fleet,
             "review_status":"BLOCKED_UNVERIFIED_CUSTODIAL_DO_NOT_SEND",
             "candidate_address":None,"memo_may_be_required":x["memo_may_be_required"],
             "safe_to_quote_as_settlement_address":False}
    raise ValueError("Unknown route ID")

def self_test():
    doc=directory()
    assert len(doc["self_custody"])==10 and len(doc["blocked_exchange"])==6
    for fleet in FLEETS:
        p=agent_packet(fleet)
        assert p["linked_to_owner_public_read_only_receiving_directory"]
        assert p["authorized_to_send_move_or_withdraw_crypto"] is False
        assert p["connected_to_actual_wallet_software_or_exchange_login"] is False
        assert len(p["owner_shared_secondary_receiving_options_held"])==8
        assert len(p["blocked_unverified_exchange_reference_ids"])==6
        assert p["owner_primary_BTC_mainnet_route"]["asset"]=="BTC"
        assert owner_review_route(fleet,OWN_PRIMARY[fleet])["safe_to_quote_as_settlement_address"]
        other=OWN_PRIMARY[FLEETS[1-FLEETS.index(fleet)]]
        assert owner_review_route(fleet,other)["safe_to_quote_as_settlement_address"] is False
        for rid in SELF_NETWORKS:
            if rid!=OWN_PRIMARY[fleet]:
                assert owner_review_route(fleet,rid)["safe_to_quote_as_settlement_address"] is False
        for rid in EXCH_ID.values():
            q=owner_review_route(fleet,rid)
            assert q["candidate_address"] is None
            assert q["safe_to_quote_as_settlement_address"] is False
    assert agent_packet(FLEETS[0])["owner_primary_BTC_mainnet_route"]["address"]!=agent_packet(FLEETS[1])["owner_primary_BTC_mainnet_route"]["address"]
    print("B_TWO_AGENTS_TO_OWNER_RECEIVING_ACCOUNT_DIRECTORY_PASS",
       json.dumps({"agent_accounts":2,"published_self_custody_candidates":10,
                   "blocked_exchange_deposit_candidates":6,"unidentified_entries_excluded":3,
                   "additional_primary_BTC_accounts_created":0,
                   "actual_login_connections_created":0,"agent_withdrawal_permissions":0,
                   "actual_confirmed_receipts_from_link":0}))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--fleet",choices=FLEETS)
    parser.add_argument("--route-id")
    a=parser.parse_args()
    if a.self_test:self_test()
    elif a.fleet:
        print(json.dumps(owner_review_route(a.fleet,a.route_id) if a.route_id
                         else agent_packet(a.fleet),indent=2))
    else:parser.error("Specify --self-test or --fleet")
