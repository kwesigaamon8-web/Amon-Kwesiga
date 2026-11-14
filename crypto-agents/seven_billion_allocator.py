"""Bounded real-worker selection from a seven-billion-role *target*.

7,000,000,000 is a planned namespace of uniquely addressable H-level role
identities, NOT active agents. Split: 3.5B per company, 350M per director.
Each daily paid-free-worker run may execute a small, unique, reproducible
sample with independent model calls and normal receipts. No 7B API calls.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

DIRECTORS=10
FLEETS=("transferexperiment","BountyScoutAI")
PER_DIRECTOR=350_000_000
PER_FLEET=3_500_000_000
TOTAL=7_000_000_000
BASE_W=750
S=150
G=500
H=666
H_UNIVERSE_PER_DIRECTOR=BASE_W*S*G*H
MULTIPLIER=65_537
assert TOTAL==len(FLEETS)*DIRECTORS*PER_DIRECTOR
assert math.gcd(MULTIPLIER,H_UNIVERSE_PER_DIRECTOR)==1
assert PER_DIRECTOR < H_UNIVERSE_PER_DIRECTOR

def role_for_slot(fleet, director, run_number, slot, capacity=20):
    """Return one provably unique target H identity for this run/slot."""
    if fleet not in FLEETS or not re.fullmatch(r"D(?:0[1-9]|10)",director):
        raise ValueError("Fleet or director invalid")
    if type(run_number)!=int or run_number<0:
        raise ValueError("Invalid chronological run number")
    if type(capacity)!=int or not (1<=capacity<=50):
        raise ValueError("Invalid bounded worker capacity")
    if type(slot)!=int or not (0<=slot<capacity):
        raise ValueError("Invalid slot")
    ordinal=(run_number*capacity+slot)%PER_DIRECTOR
    salt=int.from_bytes(hashlib.sha256((fleet+"/"+director).encode()).digest()[:8],"big")
    code=(ordinal*MULTIPLIER+salt)%H_UNIVERSE_PER_DIRECTOR
    w=code%BASE_W;code//=BASE_W
    s=code%S;code//=S
    g=code%G;code//=G
    h=code%H
    role=(f"{director}-M{w//50+1:02d}-W{w%50+1:02d}"
          f"-S{s+1:03d}-G{g+1:03d}-H{h+1:03d}")
    company_index=FLEETS.index(fleet)
    d=int(director[1:])-1
    global_target_index=company_index*PER_FLEET+d*PER_DIRECTOR+ordinal
    return {
      "workforce_namespace":fleet,"role_id":role,
      "globally_unique_worker_id":fleet+"/"+role,
      "target_index":global_target_index,
      "director_target_rank":ordinal,
      "target_total_role_identities":TOTAL,
      "target_per_company":PER_FLEET,
      "target_per_director":PER_DIRECTOR,
      "actual_model_execution":"NOT_PROVEN_BY_ALLOCATION",
      "inherited_owner_command":"OWNER-20261114-073213",
    }

def self_test():
    found_ids=set()
    indexes=set()
    director_codes=set()
    for fleet in FLEETS:
        for d in range(1,11):
            director=f"D{d:02d}"
            for cycle in (1,27,100):
                for slot in range(20):
                    x=role_for_slot(fleet,director,cycle,slot)
                    assert x["globally_unique_worker_id"] not in found_ids
                    assert x["target_index"] not in indexes
                    found_ids.add(x["globally_unique_worker_id"])
                    indexes.add(x["target_index"])
                    director_codes.add(fleet+"/"+director)
                    assert x["role_id"].startswith(director+"-M")
                    assert re.search(r"-S\d{3}-G\d{3}-H\d{3}$",x["role_id"])
    assert len(found_ids)==1200
    assert len(indexes)==1200
    assert len(director_codes)==20
    for i in range(3):
        x=role_for_slot("transferexperiment","D01",1000+i,17)
        assert x["director_target_rank"]==((1000+i)*20+17)%PER_DIRECTOR
    # Prove distinct 7-billion-target indices at boundaries without iterating.
    a=role_for_slot("transferexperiment","D01",0,0)
    b=role_for_slot("BountyScoutAI","D10",0,0)
    assert a["target_index"]==0
    assert b["target_index"]==6_650_000_000
    return {"test":"PASS","checked_unique_worker_ids":1200,
            "per_company_pool":PER_FLEET,"combined_role_target":TOTAL,
            "actual_models_launched_by_this_test":0}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--fleet",choices=FLEETS)
    parser.add_argument("--director")
    parser.add_argument("--cycle",type=int,default=1)
    parser.add_argument("--slot",type=int,default=0)
    args=parser.parse_args()
    if args.self_test:
        print("SEVEN_BILLION_ALLOCATION_TEST",json.dumps(self_test()))
        return
    if not args.fleet or not args.director:
        raise SystemExit("Provide fleet and director or --self-test")
    print(json.dumps(role_for_slot(args.fleet,args.director,args.cycle,args.slot),indent=2))

if __name__=="__main__":
    main()
