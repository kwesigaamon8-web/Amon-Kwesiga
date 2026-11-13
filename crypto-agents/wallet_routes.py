"""Read-only owner receiving route directory with strict privacy controls.

Complete owner routes are supplied ONLY as encrypted GitHub Actions repository
secret OWNER_WALLET_DIRECTORY_JSON, not committed to the public repository.
All active roles may check *route IDs*; never include complete directory in
public reports, AI prompts, logs, issues, or search requests.
"""
import json
import os

def directory():
    secret=os.environ.get("OWNER_WALLET_DIRECTORY_JSON","")
    if not secret:
        return None
    try:
        data=json.loads(secret)
        expected={"self_custody","binance_exchange_potential_usdc_routes",
                  "unknown_network_entries_not_payment_ready"}
        if not isinstance(data,dict) or not expected.issubset(data):
            return None
        return data
    except (ValueError,TypeError):
        return None

def route_ids():
    doc=directory()
    if not doc:
        return ["btc-mainnet-public","ethereum-usdc-public"], "private_directory_not_configured"
    names=[]
    for group in doc["self_custody"].values():
        names += [entry["id"] for entry in group]
    names += [entry["id"] for entry in doc["binance_exchange_potential_usdc_routes"]]
    names += ["unknown-network-"+str(i+1) for i in range(
        len(doc["unknown_network_entries_not_payment_ready"]))]
    return names, "private_directory_available"

def private_directory_status():
    keys,status=route_ids()
    return {"status":status,"route_ids":keys,
        "note":"Complete addresses remain private. An agent must never publish the directory or claim permission to transfer, log in or sign."}

def payment_route(route_id, verified_payer=False, verified_network=False):
    """Private selector. Disables exchange routes until both flags are true.

    Application code must never serialize this return value to a report/log.
    It is only suitable for owner-authorized payment request preparation.
    """
    if not verified_payer or not verified_network:
        return None
    doc=directory()
    if not doc:
        return None
    for group in doc["self_custody"].values():
        for entry in group:
            if entry["id"] == route_id:
                return entry
    # A custodial route also needs manual confirmation of current Binance
    # deposit network, asset, memo and exchange credit acceptance. Not yet
    # supported by this read-only research fleet.
    return None
