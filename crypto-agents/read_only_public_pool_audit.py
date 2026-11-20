"""Evidence-only Public Pool BTC miner audit for owner-shared B1/B2 Bitcoin addresses.

Public API GETs only, never Stratum connections, hashing, transactions, secrets or
earnings claims. A pool-reported worker does not prove owner authorization or income.
Runs with Python stdlib on an existing software repository; no CPU mining.
"""
from __future__ import annotations
import datetime as dt
import json
import math
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

BASE="https://public-pool.io:40557/api/client/"
ADDRS={
 "B1":"bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z",
 "B2":"bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9",
}
OUT=Path("mining-evidence/public-pool-wallet-audit.json")
SOURCE="https://web.public-pool.io/"
SCHEMES={
 "solo":{"tls_port":4333,"reward":"Only a found block pays this wallet"},
 "pplns":{"tls_port":14333,"reward":"Only actual pool block payouts allocated by valid recent work; not FPPS"},
}

def finite_nonnegative(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)):
        return None
    if not math.isfinite(value) or value<0:
        return None
    return value

def parse_payload(body,company):
    if not isinstance(body,dict):
        return {"status":"UNREADABLE_POOL_RESPONSE","reported_worker_count":None}
    d=body.get("data") if isinstance(body.get("data"),dict) else body
    workers=d.get("workers")
    if not isinstance(workers,list):
        return {"status":"WORKERS_NOT_IN_POOL_RESPONSE","reported_worker_count":None,
                "reported_wallet_hashrate_hs":None}
    valid=[x for x in workers if isinstance(x,dict)]
    if len(valid)!=len(workers):
        return {"status":"INVALID_WORKER_SCHEMA","reported_worker_count":None,
                "reported_wallet_hashrate_hs":None}
    rates=[finite_nonnegative(x.get("hashRate")) for x in valid]
    rate=sum(rates) if all(v is not None for v in rates) else None
    # Count only reported records. Current live status depends on lastSeen and pool semantics.
    return {
        "status":"WORKER_ROWS_PUBLICLY_REPORTED",
        "reported_worker_count":len(valid),
        "reported_wallet_hashrate_hs":rate,
        "reported_worker_hashrates_hs":rates[:10],
        "active_authorized_asic_count_verified":0,
        "device_owner_optin_verified":False,
        "solo_vs_pplns_connection_port_verified":False,
        "pool_accrued_btc_verified":False,
        "actual_onchain_mining_reward_verified":False,
        "possible_stale_workers":True,
    }

def get_url(url):
    if url not in [BASE+a for a in ADDRS.values()]:
        raise ValueError("Unexpected external URL")
    req=urllib.request.Request(url,headers={
        "Accept":"application/json",
        "User-Agent":"B1B2-Pool-Audit-Nonmining/1.0"})
    with urllib.request.urlopen(req,timeout=12) as response:
        if response.status!=200:
            raise ValueError("HTTP response not 200")
        return json.loads(response.read(600000))

def check(loader=get_url):
    results=[]
    for company,addr in ADDRS.items():
        try:
            parsed=parse_payload(loader(BASE+addr),company)
        except (OSError,ValueError,TimeoutError,urllib.error.URLError) as exc:
            parsed={"status":"POOL_SOURCE_UNAVAILABLE","source_error_type":type(exc).__name__,
                    "reported_worker_count":None,"reported_wallet_hashrate_hs":None}
        results.append({"company":company,"public_btc_mainnet_address":addr,
                        "pool_source_endpoint":BASE+addr,**parsed})
    return {
      "checked_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
      "public_pool_official_url":SOURCE,
      "mining_pool_mode_details":SCHEMES,
      "source_kind":"READ_ONLY_PUBLIC_POOL_ADDRESS_QUERY",
      "wallets":results,
      "configured_role_ids":750377265360,
      "role_ids_are_not_mining_devices":True,
      "authorized_asic_miners_independently_verified":0,
      "confirmed_owner_mining_payouts_btc":None,
      "confirmed_new_owner_mining_payouts":False,
      "onchain_payment_verification_is_separate":True,
      "private_keys_accessed":False,
      "mining_or_compute_hashing_started":False,
      "external_posts_sent":0,
      "email_accessed":False,
      "caution":"Live worker rows or accepted Stratum shares do not prove ownership, credited BTC, pool earnings, or network payout. Zero rows is not lifetime zero.",
    }

def self_test():
    assert parse_payload({"workers":[]},"B1")["reported_worker_count"]==0
    test=parse_payload({"workers":[{"hashRate":12345},{"hashRate":500}]},"B2")
    assert test["reported_worker_count"]==2
    assert test["reported_wallet_hashrate_hs"]==12845
    assert test["actual_onchain_mining_reward_verified"] is False
    assert parse_payload({"foo":"bar"},"B1")["reported_worker_count"] is None
    assert parse_payload({"workers":[{"hashRate":"999"}]},"B2")["reported_wallet_hashrate_hs"] is None
    assert parse_payload([],"B1")["status"]=="UNREADABLE_POOL_RESPONSE"
    assert parse_payload({"workers":[{"hashRate":False}]},"B1")["reported_wallet_hashrate_hs"] is None
    assert parse_payload({"workers":[{"hashRate":-1}]},"B1")["reported_wallet_hashrate_hs"] is None
    assert parse_payload({"workers":[4]},"B1")["status"]=="INVALID_WORKER_SCHEMA"
    assert SCHEMES["solo"]["tls_port"]==4333 and SCHEMES["pplns"]["tls_port"]==14333
    empty=check(loader=lambda url:{"workers":[]})
    assert len(empty["wallets"])==2 and empty["confirmed_new_owner_mining_payouts"] is False
    down=check(loader=lambda url: (_ for _ in ()).throw(OSError("offline")))
    assert all(x["status"]=="POOL_SOURCE_UNAVAILABLE" for x in down["wallets"])
    print("B1B2_PUBLIC_POOL_OWNER_ADDRESS_SELF_TEST_PASS")

if __name__=="__main__":
    if "--self-test" in sys.argv:
        self_test()
    else:
        data=check()
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
        print("B1B2_REAL_POOL_PUBLIC_WALLET_READ_ONLY_RESULT",json.dumps({
           "checked_at_utc":data["checked_at_utc"],
           "B1":data["wallets"][0]["status"],
           "B1_worker_rows":data["wallets"][0]["reported_worker_count"],
           "B2":data["wallets"][1]["status"],
           "B2_worker_rows":data["wallets"][1]["reported_worker_count"],
           "asic_miners_verified":0,
           "mining_payouts_verified":False,
           "miner_processes_executed":0,
        }))
