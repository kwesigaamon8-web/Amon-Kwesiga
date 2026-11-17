"""Safety/evidence regression for B1 B2 inward-only real-money priority.

No network calls, wallet keys, account login, signatures or transfers.
Prevents a later edit from silently counting marketing/AI tasks as income.
"""
import json
from pathlib import Path

ROOT=Path("crypto-agents")
config=json.loads((ROOT/"b_collection_assignments.json").read_text(encoding="utf-8"))
orders=json.loads((ROOT/"chief_D_owner_orders.json").read_text(encoding="utf-8"))
public=json.loads((ROOT/"public_payment_routes.json").read_text(encoding="utf-8"))
src=(ROOT/"chief_D_reporting.py").read_text(encoding="utf-8")
policy=config["cash_first_payment_priority"]
assert policy["owner_instruction_id"]=="OWNER-20261117-061348-INBOUND-MONEY-IS-KEY"
assert any(o.get("id")=="OWNER-20261117-061348-INBOUND-MONEY-IS-KEY"
           and o.get("origin")=="explicit_human_owner_conversation"
           for o in orders["orders"]), "Owner cash-first order was lost"
assert orders["orders"][-1]["id"]==orders["current_owner_order_id"]
assert "INBOUND_ONLY" in policy["owner_wallets"]
assert policy["expected_wallet_signatures"]==0
assert policy["guarantees_created_by_this_configuration"]==0
assert policy["public_income_claims_without_TXID"]==0
assert len(policy["expected_customer_journey"])==7
assert policy["expected_customer_journey"][-1]=="PAYMENT_CLASSIFIED_WITH_INDEPENDENT_EVIDENCE"
assert policy["chief_D_report_order"][0]=="INCOMING_SETTLED_MONEY_CONFIRMED"
assert public["routing_direction"]=="INBOUND_RECEIVING_ONLY"
assert public["any_outgoing_transaction_authorized"] is False
assert all(x["allowed_to_send"] is False for x in public["self_custody_candidate_routes"])
assert all(x["status"]=="BLOCKED_UNVERIFIED_CUSTODIAL_DO_NOT_SEND"
           for x in public["blocked_exchange_reference_only"])
assert "## ACTUAL INCOMING MONEY — OWNER'S TOP PRIORITY" in src
assert "incoming_paid_client_receipts_independently_classified_in_this_report" in src
assert "new_payment_NOT_PROVEN_is_not_a_claim_of_zero_wallet_balance" in src
assert len(config["fleets"])==2
assert config["fleets"]["transferexperiment"]["address"]=="bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z"
assert config["fleets"]["BountyScoutAI"]["address"]=="bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9"
print("CASH_FIRST_INBOUND_ONLY_OWNER_POLICY_PASS",json.dumps({
    "public_receiving_routes":len(public["self_custody_candidate_routes"]),
    "company_BTC_destinations":2,
    "outgoing_crypto_authorized":False,
    "independently_verified_new_payment_from_test":False,
    "owner_priority":"verified_inbound_money_first"
}))
