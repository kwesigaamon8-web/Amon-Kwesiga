"""Read-only and network-specific B1/B2 Bitcoin public address health snapshot.

Only shows chain output statistics. Neither an on-chain output nor a balance
proves earned revenue or provenance of sender. Never handles wallet credentials.
"""
from __future__ import annotations

import datetime as dt
import json
import urllib.request

ADDRESSES = {
    "B1": "bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z",
    "B2": "bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9",
}
SERVERS = (
    "https://mempool.space/api/address/",
    "https://blockstream.info/api/address/",
)
FIELDS = ("funded_txo_count", "funded_txo_sum", "spent_txo_count", "spent_txo_sum", "tx_count")


def checked_read(item, address):
    if not isinstance(item, dict) or item.get("address") != address:
        raise ValueError("Explorer returned wrong BTC receiving address")
    snapshot = {}
    for key in ("chain_stats", "mempool_stats"):
        stats = item.get(key)
        if not isinstance(stats, dict):
            raise ValueError("Missing BTC chain statistics")
        part = {}
        for name in FIELDS:
            v = stats.get(name)
            if not isinstance(v, int) or isinstance(v, bool) or v < 0:
                raise ValueError("Invalid BTC explorer count: " + name)
            part[name] = v
        if part["spent_txo_sum"] > part["funded_txo_sum"]:
            raise ValueError("Invalid negative funded-minus-spent BTC observation")
        snapshot[key] = part
    return snapshot


def query_source(base, address):
    req = urllib.request.Request(
        base + address, headers={"Accept": "application/json",
                                "User-Agent": "B1B2-Onchain-ReadOnly-Check/1.0"})
    with urllib.request.urlopen(req, timeout=12) as r:
        raw = r.read(65537)
    if len(raw) > 65536:
        raise ValueError("Unexpectedly large chain response")
    return checked_read(json.loads(raw), address)


def inspect(address):
    reports, failures = [], []
    for base in SERVERS:
        try:
            reports.append({"source": base.split("/")[2], "summary": query_source(base, address)})
        except Exception as e:
            failures.append({"source": base.split("/")[2], "reason": type(e).__name__})
    if not reports:
        return {"status": "UNAVAILABLE_NO_VERIFIED_BTC_OBSERVATION", "source_failures": failures}
    consensus = all(r["summary"] == reports[0]["summary"] for r in reports[1:])
    if len(reports) > 1 and not consensus:
        return {"status": "EXPLORERS_DISAGREE_HOLD", "sources": [r["source"] for r in reports],
                "source_failures": failures, "balance_or_deposit_claim": "NONE"}
    output = reports[0]["summary"]
    onchain = output["chain_stats"]
    pending = output["mempool_stats"]
    return {
        "status": "TWO_EXPLORERS_AGREE" if len(reports) > 1 else "ONE_EXPLORER_ONLY",
        "sources": [r["source"] for r in reports],
        "source_failures": failures,
        "confirmed_historical_outputs_received_sats": onchain["funded_txo_sum"],
        "confirmed_historical_outputs_received_count": onchain["funded_txo_count"],
        "historical_confirmed_spent_sats": onchain["spent_txo_sum"],
        "observed_confirmed_unspent_sats": onchain["funded_txo_sum"] - onchain["spent_txo_sum"],
        "observed_mempool_output_sats": pending["funded_txo_sum"],
        "observed_mempool_output_count": pending["funded_txo_count"],
        "earnings_verified": False,
        "new_since_last_run_verified": False,
        "no_client_purpose_or_ownership_inferred": True,
    }


def selftest():
    addr = ADDRESSES["B1"]
    sample = {"address": addr, "chain_stats": {k: 0 for k in FIELDS},
              "mempool_stats": {k: 0 for k in FIELDS}}
    assert checked_read(sample, addr)["chain_stats"]["funded_txo_sum"] == 0
    sample["address"] = ADDRESSES["B2"]
    try:
        checked_read(sample, addr)
    except ValueError:
        pass
    else:
        raise AssertionError("Cross-fleet address confusion accepted")
    sample["address"] = addr
    sample["chain_stats"]["spent_txo_sum"] = 100
    try:
        checked_read(sample, addr)
    except ValueError:
        pass
    else:
        raise AssertionError("Impossible BTC accounting accepted")
    print("BTC_ADDRESS_SNAPSHOT_3_POLICY_TESTS_PASS")


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        selftest()
    else:
        result = {"observed_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                  "networks": "bitcoin mainnet ONLY",
                  "accounts": {n: {"address": a, **inspect(a)} for n, a in ADDRESSES.items()}}
        print("B1B2_ONCHAIN_READONLY_ADDRESS_CHECK " + json.dumps(result, ensure_ascii=False))
