"""Safety and consistency tests for owner-shared public receiving routes.

Does NOT connect wallets, sign, authenticate, validate wallet ownership, or
prove token/chain compatibility or receipt. Runs in GitHub Actions offline.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
CAT=json.loads((HERE/"public_payment_routes.json").read_text(encoding="utf-8"))
SOURCE=(HERE/"PUBLIC_RECEIVING_ADDRESSES.md").read_text(encoding="utf-8")
CFG=json.loads((HERE/"b_collection_assignments.json").read_text(encoding="utf-8"))
IDS=("BTC-01","BTC-02","EVM-01","EVM-02","SOL-01","SOL-02","TRX-01","TRX-02","XLM-01","XLM-02")
PAYABLE={"BTC-01":"transferexperiment","BTC-02":"BountyScoutAI"}

def src_routes():
    part=SOURCE.split("## Self-custody addresses",1)[1].split("## Exchange deposit identifiers",1)[0]
    entries={}
    for line in part.splitlines():
        cells=[x.strip() for x in line.split("|")]
        if len(cells)==5 and cells[1] in IDS:
            entries[cells[1]]=cells[3].strip(chr(96))
    return entries

def validate():
    assert CAT["schema"]=="B1_B2_PUBLIC_RECEIVING_DIRECTORY_V1"
    assert CAT["no_private_keys_or_exchange_memos"] is True
    assert CAT["no_signing_or_transfer_privileges"] is True
    assert CAT["not_verified_wallet_ownership"] is True
    assert CAT["verified_new_income_from_this_directory"] is False
    rows=CAT["self_custody_candidate_routes"]
    assert len(rows)==len(IDS) and tuple(x["route_id"] for x in rows)==IDS
    source=src_routes()
    assert set(source)==set(IDS)
    assert len({x["receiving_address"] for x in rows})==len(rows)
    assert all(x["receiving_address"]==source[x["route_id"]] for x in rows)
    assert all(x["ownership_independently_verified"] is False and x["authorised_for_auto_transfers"] is False for x in rows)
    for r in rows:
        rid=r["route_id"]
        if rid in PAYABLE:
            fleet=PAYABLE[rid]
            assert r["company"]==fleet
            assert (r["asset"],r["chain"])==("BTC","bitcoin-mainnet")
            assert r["payment_status"]=="owner_shared_btc_mainnet_reconfirm_before_invoice"
            assert r["receiving_address"]==CFG["fleets"][fleet]["address"]
            assert CFG["fleets"][fleet]["network"]=="Bitcoin mainnet"
            assert re.fullmatch(r"bc1q[ac-hj-np-z02-9]{38}",r["receiving_address"])
        else:
            assert r["company"] is None and r["chain"] is None and r["asset"] is None
            assert r["payment_status"]=="HOLD_UNVERIFIED_NETWORK_TOKEN_OWNER_COMPATIBILITY"
    ex=CAT["blocked_exchange_reference_only"]
    assert len(ex)==6 and len({x["route_id"] for x in ex})==6
    assert all(x["status"]=="BLOCKED_UNVERIFIED_CUSTODIAL_DO_NOT_SEND" and
               x["public_payment_route"] is False and x["address_withheld_from_payer_manifest"] is True
               and "address" not in x
               for x in ex)
    assert tuple(CAT["separate_B1_B2_BTC_mainnet_routes"])==("BTC-01","BTC-02")
    return {"passed":True,"self_custody_records":len(rows),"btc_company_routes":2,
        "held_other_network_records":8,"held_exchange_identifiers":len(ex),
        "wallet_software_connected":False,"wallet_spending_permissions":False,
        "owner_wallet_ownership_proven":False,"payment_verified":False}

if __name__=="__main__":
    print("B1_B2_PUBLIC_RECEIVE_ROUTE_CONTRACT",json.dumps(validate()))
