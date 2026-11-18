"""Read-only Base mainnet native USDC balance probe; never signs or spends.

Owner-supplied B1 address is a claimed receiving route, not independently proven
ownership/custody. Current balance is NOT verified earnings or new deposits.
"""
from __future__ import annotations

import json
import re
import urllib.request
from decimal import Decimal
from datetime import datetime, timezone

OWNER_CLAIMED_B1 = "0x734989a439F146885C12907cd9Dd191b03d5B07e"
CIRCLE_BASE_NATIVE_USDC = "0x833589fCD6eDb6E08f4c7C32D4f71B54bdA02913"
CHAIN_ID = 8453
RPCS = ("https://mainnet.base.org", "https://base-rpc.publicnode.com")


def rpc(url, method, params, n=1):
    payload = json.dumps({"jsonrpc":"2.0","id":n,"method":method,"params":params}).encode()
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type":"application/json",
                                    "Accept":"application/json",
                                    "User-Agent":"B1B2-ReadOnly-BaseUSDC-Balance/1.0"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as response:
        data = response.read(65537)
    if len(data) > 65536:
        raise ValueError("Unreasonably large RPC response")
    body = json.loads(data)
    if body.get("id") != n or not isinstance(body.get("result"), str) or body.get("error"):
        raise ValueError("Unverifiable or failed RPC response")
    return body["result"]


def inspect(provider):
    chain = rpc(provider, "eth_chainId", [], 1)
    if not re.fullmatch(r"0x[0-9a-fA-F]+", chain) or int(chain, 16) != CHAIN_ID:
        raise ValueError("Not Base mainnet")
    if not re.fullmatch(r"0x[0-9a-fA-F]{40}", OWNER_CLAIMED_B1):
        raise ValueError("Incorrect owner-supplied receiving address format")
    # ERC-20 balanceOf(address), 4-byte keccak selector 0x70a08231.
    calldata = "0x70a08231" + OWNER_CLAIMED_B1.lower()[2:].rjust(64, "0")
    raw = rpc(provider, "eth_call", [{"to":CIRCLE_BASE_NATIVE_USDC,"data":calldata},"latest"], 2)
    if not re.fullmatch(r"0x[0-9a-fA-F]{64}", raw):
        raise ValueError("Bad native USDC balanceOf ABI result")
    units = int(raw,16)
    return {"native_usdc_micro_units":units,
            "public_address_balance_usdc":str(Decimal(units)/Decimal(1_000_000))}


def verify(sources):
    good, bad = [], []
    for url in sources:
        domain = url.split("/")[2]
        try:
            good.append({"rpc":domain,**inspect(url)})
        except Exception as exc:
            bad.append({"rpc":domain,"status":type(exc).__name__})
    if not good:
        return {"status":"UNAVAILABLE_DO_NOT_CLAIM_BALANCE","rpc_errors":bad}
    values={x["native_usdc_micro_units"] for x in good}
    if len(values)>1:
        return {"status":"RPC_DISAGREEMENT_HOLD","observations":good,"rpc_errors":bad}
    return {"status":"TWO_RPC_AGREE" if len(good)==2 else "ONE_RPC_ONLY",
            "public_address_balance_usdc":good[0]["public_address_balance_usdc"],
            "native_usdc_micro_units":good[0]["native_usdc_micro_units"],
            "verified_rpc_sources":[x["rpc"] for x in good],"rpc_errors":bad,
            "owner_control_verified":False,"income_or_new_deposit_verified":False,
            "network_approval_for_receiving_confirmed":False}


def self_test():
    assert CHAIN_ID==8453
    assert OWNER_CLAIMED_B1.startswith("0x") and len(OWNER_CLAIMED_B1)==42
    assert CIRCLE_BASE_NATIVE_USDC.lower()=="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
    assert str(Decimal(1250000)/Decimal(1000000))=="1.25"
    print("BASE_USDC_READONLY_4_POLICY_TESTS_PASS")


if __name__=="__main__":
    import sys
    if "--self-test" in sys.argv:
        self_test()
    else:
        print("B1_BASE_NATIVE_USDC_PUBLIC_BALANCE",
              json.dumps({"observed_at_utc":datetime.now(timezone.utc).isoformat(),
                          "network":"Base mainnet", "chain_id":CHAIN_ID,
                          "contract":CIRCLE_BASE_NATIVE_USDC,
                          "owner_claimed_address":OWNER_CLAIMED_B1,
                          **verify(RPCS)}))
