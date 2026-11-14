"""Validate safe, company-specific public receiving-route instruction + real AI response.

This contains only the two receiving addresses already intentionally published in
the owner's company public GitHub payment notices and the optional Base USDC
route already approved for training in b_collection_assignments.json.
Other exchange/memo routes are NOT published, guessed, or accepted.
The deterministic assignment test is NOT a model-comprehension test.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

CFG_FILE=Path("crypto-agents/b_collection_assignments.json")
FLEET_1="transferexperiment"
FLEET_2="BountyScoutAI"

def routes():
    cfg=json.loads(CFG_FILE.read_text(encoding="utf-8"))
    entries=cfg["fleets"]
    if set(entries)!={FLEET_1,FLEET_2}:
        raise ValueError("Separate B company destinations changed")
    primary={}
    for fleet in (FLEET_1,FLEET_2):
        item=entries[fleet]
        addr=item["address"]
        if (item["network"],item["asset"])!=("Bitcoin mainnet","BTC"):
            raise ValueError("Incorrect primary BTC network or asset: "+fleet)
        if not re.fullmatch(r"bc1q[ac-hj-np-z02-9]{38}",addr):
            raise ValueError("Unexpected BTC mainnet receiving-address format for "+fleet)
        primary[fleet]=addr
    if primary[FLEET_1]==primary[FLEET_2]:
        raise ValueError("Two company BTC receiving addresses must not be identical")
    base=entries[FLEET_1].get("possible_secondary_route") or {}
    if (base.get("asset"),base.get("network"))!=("USDC","Base"):
        raise ValueError("Optional B1 USDC must remain Base-specific")
    if not re.fullmatch(r"0x[0-9A-Fa-f]{40}",base.get("address","")):
        raise ValueError("Unexpected optional USDC address format")
    if base.get("status")!="verify_compatibility_before_sending":
        raise ValueError("Base route is not authorized as automatically payment-ready")
    return {
      "company_1": {"fleet":FLEET_1,"btc_mainnet":primary[FLEET_1],
                    "optional_USDC_Base":base["address"],
                    "optional_status":"HOLD_UNTIL_RECEIVER_NETWORK_AND_ASSET_CONFIRMED",
                    "local_payment_director":FLEET_1+"/D10","reports_to":"D"},
      "company_2": {"fleet":FLEET_2,"btc_mainnet":primary[FLEET_2],
                    "local_payment_director":FLEET_2+"/D10","reports_to":"D"},
      "chief_director":"D",
      "other_network_routes":"NOT_APPROVED_IN_THIS_PUBLIC_DIRECTORY",
      "exchange_deposit_memos":"REQUIRE_MANUAL_OWNER_VERIFICATION"
    }

def prompt(fleet):
    data=routes()
    if fleet not in (FLEET_1,FLEET_2):
        raise ValueError("Unknown company")
    own="company_1" if fleet==FLEET_1 else "company_2"
    return (
      "You work for "+fleet+". Prove you know the correct company, coin/network, "
      "separate owner receiving addresses, payment director and Chief D. "
      "Use only these confirmed PUBLIC receiving details: "
      "B1 transferexperiment BTC Bitcoin mainnet "+data["company_1"]["btc_mainnet"]+
      "; B2 BountyScoutAI BTC Bitcoin mainnet "+data["company_2"]["btc_mainnet"]+
      "; B1 optional USDC Base "+data["company_1"]["optional_USDC_Base"]+
      " is HOLD pending recipient and network compatibility confirmation. "
      "No other network/memo/address is ready. The company you belong to is "+fleet+
      ", your own local payment director is "+data[own]["local_payment_director"]+
      ", and the ONE overall Chief D is above both separate company boards. "
      "Never share keys, request wallet passwords, or credit a BTC payment to an EVM address. "
      "Respond in 5 short distinct lines using these exact headings: "
      "B1 BTC: ... ; B2 BTC: ... ; B1 USDC Base: ... (HOLD); "
      "My company and D10: ... ; Chief D and safety: ... . "
      "Say the coin/network on the relevant line. Do not invent actual deposits."
    )

def evaluate(fleet,answer):
    data=routes()
    if fleet not in (FLEET_1,FLEET_2):
        raise ValueError("Unknown worker fleet")
    lines=str(answer or "").splitlines()
    b1=[line for line in lines if re.search(r"\b(?:B1|Company\s*1|transferexperiment)\b",line,re.I)]
    b2=[line for line in lines if re.search(r"\b(?:B2|Company\s*2|BountyScoutAI)\b",line,re.I)]
    base=[line for line in lines if re.search(r"\b(?:USDC|Base)\b",line,re.I)]
    b1_correct=any(data["company_1"]["btc_mainnet"] in x and "btc" in x.lower() for x in b1)
    b2_correct=any(data["company_2"]["btc_mainnet"] in x and "btc" in x.lower() for x in b2)
    reversed_or_confused=any(data["company_2"]["btc_mainnet"] in x for x in b1) or any(
       data["company_1"]["btc_mainnet"] in x for x in b2)
    b1_base_correct=any(data["company_1"]["optional_USDC_Base"] in x and
        ("hold" in x.lower() or "verify" in x.lower()) and
        "base" in x.lower() and "usdc" in x.lower() for x in base)
    own_correct=bool(re.search(re.escape(fleet)+r"\s*/\s*D10",str(answer),re.I))
    chief_correct=bool(re.search(r"\bChief\s+D\b",str(answer),re.I))
    network_correct=("bitcoin mainnet" in str(answer).lower())
    no_payment_claim=not bool(re.search(r"(?i)\b(?:received|paid\s+in|deposited|confirmed\s+receipt|funded\s+my\s+wallet)\b",str(answer)))
    # The full private wallet directory, passphrases and custodial memo details
    # never appear in public prompts. Unknown/other routes require owner check.
    fields={
      "B1_BTC_correct":b1_correct,"B2_BTC_correct":b2_correct,
      "no_B1_B2_address_mixup":not reversed_or_confused,
      "B1_USDC_Base_explicit_HOLD":b1_base_correct,
      "correct_own_local_D10":own_correct,
      "chief_D_above_both_boards":chief_correct,
      "Bitcoin_mainnet_explicit":network_correct,
      "no_claim_of_received_money":no_payment_claim,
    }
    passed=bool(answer.strip()) and all(fields.values())
    return {
      "fleet":fleet,"status":"MODEL_ADDRESS_MAPPING_ACK_REQUIRES_HUMAN_CHECK" if passed else "NOT_VERIFIED_NEEDS_PARENT_REVIEW",
      "fields":fields,
      "model_output_excerpt":str(answer)[:1800],
      "actual_model_execution_proved_by_evaluator":False,
      "bank_or_other_networks_payment_ready":False,
      "wrong_address_is_a_blocker":True,
      "meaning":"Even a passing text check is only a model's address-mapping acknowledgement, not proof of future correct behavior or actual coin receipts."
    }

def self_test():
    d=routes()
    b1=d["company_1"]["btc_mainnet"]
    b2=d["company_2"]["btc_mainnet"]
    base=d["company_1"]["optional_USDC_Base"]
    for fleet in (FLEET_1,FLEET_2):
        response=(
          f"B1 BTC: {b1} Bitcoin mainnet\n"
          f"B2 BTC: {b2} Bitcoin mainnet\n"
          f"B1 USDC Base: {base} HOLD verify network\n"
          f"My company and D10: {fleet}/D10\n"
          "Chief D and safety: Chief D oversees both. No payment claimed; all others verify first."
        )
        ok=evaluate(fleet,response)
        assert ok["status"]=="MODEL_ADDRESS_MAPPING_ACK_REQUIRES_HUMAN_CHECK",ok
        swap=response.replace(f"B1 BTC: {b1}",f"B1 BTC: {b2}")
        assert evaluate(fleet,swap)["status"]=="NOT_VERIFIED_NEEDS_PARENT_REVIEW"
        no_base=response.replace(base,"invalid")
        assert evaluate(fleet,no_base)["status"]=="NOT_VERIFIED_NEEDS_PARENT_REVIEW"
    return {"status":"PASS","two_distinct_BTC_mainnet_destinations":True,
            "Base_USDC_must_be_HOLD":True,
            "chief_D_distinct_from_two_local_D10":True,
            "actual_model_workers_launched_by_this_test":0}

if __name__=="__main__":
    print("B_WALLET_ADDRESS_MAP_TEST",json.dumps(self_test()))
