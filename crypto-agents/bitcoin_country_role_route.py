"""Assign EVERY virtual B1/B2 role a World Bank economy and mining reporting route.

No cryptomining takes place here. A country assignment, Stratum username, or
logical role number is NOT an active miner or a verified BTC receipt.
"""
from __future__ import annotations
import argparse,bisect,csv,json
from pathlib import Path
from enigma_universal_owner_order import GRAND_TOTAL,divisions
from country_bitcoin_worker_allocation import ROLES_PER_SYSTEM,ROUTES
DEFAULT=Path("crypto-agents/data/bitcoin_country_allocations.csv")

def parse_rows(path=DEFAULT):
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        entries=list(csv.DictReader(f))
    rows=[]
    for r in entries:
        n=int(r["Virtual roles per B system"])
        if n<=0:continue
        first=int(r["Per-system role start"])
        last=int(r["Per-system role end inclusive"])
        if n!=last-first+1:raise ValueError("Count and interval differ")
        rows.append((first,last,r["ISO3"],r["Country or economy"]))
    rows.sort()
    if not rows or rows[0][0]!=0 or rows[-1][1]!=ROLES_PER_SYSTEM-1:
        raise ValueError("Country data does not partition all slots")
    for a,b in zip(rows,rows[1:]):
        if a[1]+1!=b[0]:raise ValueError("Overlapping or missing slots")
    return rows

def route_one(global_role_index,rows):
    if type(global_role_index)is not int or not 0<=global_role_index<GRAND_TOTAL:
        raise ValueError("Outside organization")
    root_no,role_in_system=divmod(global_role_index,ROLES_PER_SYSTEM)
    roots=divisions()
    root=roots[root_no]
    firsts=[x[0] for x in rows]
    chosen=rows[bisect.bisect_right(firsts,role_in_system)-1]
    if not chosen[0]<=role_in_system<=chosen[1]:
        raise ValueError("Unassigned role")
    fleet="B1" if root["parent"]=="transferexperiment" else "B2"
    worker_name=f"{fleet}{chosen[2]}{root_no:02d}"
    return {
        "role_global_index":global_role_index,
        "root":root["id"],"registered_moltbook_parent":root["parent"],
        "assigned_country":chosen[3],"ISO3":chosen[2],
        "fleet":fleet,"virtual_role_number_in_root":role_in_system,
        "task":"Bitcoin SHA-256 mining planning and verification on expressly authorized devices ONLY",
        "btc_mainnet_receiver":ROUTES[fleet],
        "example_pool_user_not_an_active_connection":ROUTES[fleet]+"."+worker_name,
        "mining_pool_solo_only_if_locally_approved":"stratum+tcp://public-pool.io:3333",
        "actual_miner_deployed":False,"verified_hashrate_hs":0,
        "actual_block_reward_verified":False,
        "status":"COUNTRY_ASSIGNED_NOT_DEPLOYED_NOT_MINING",
    }

def self_test():
    toy=[(0,ROLES_PER_SYSTEM//2-1,"UGA","Uganda"),
         (ROLES_PER_SYSTEM//2,ROLES_PER_SYSTEM-1,"USA","United States")]
    for r in [0,ROLES_PER_SYSTEM//2-1,ROLES_PER_SYSTEM//2,
              ROLES_PER_SYSTEM-1,ROLES_PER_SYSTEM,GRAND_TOTAL-1]:
        out=route_one(r,toy)
        assert out["btc_mainnet_receiver"] in ROUTES.values()
        assert out["actual_miner_deployed"] is False
        assert out["verified_hashrate_hs"]==0
    assert route_one(0,toy)["fleet"]=="B1"
    assert route_one(ROLES_PER_SYSTEM,toy)["fleet"]=="B2"
    try:route_one(GRAND_TOTAL,toy)
    except ValueError:pass
    else:raise AssertionError("Out-of-bounds accepted")
    print("COUNTRY_MINING_ROUTE_SELF_TEST_PASS 30 root divisions all virtual")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--index",type=int)
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--csv",default=str(DEFAULT))
    a=p.parse_args()
    if a.self_test:self_test()
    elif a.index is not None:print(json.dumps(route_one(a.index,parse_rows(a.csv)),indent=2))
    else:p.error("Choose --self-test or --index")
