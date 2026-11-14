"""Assign genuine rotating B worker IDs to recurring GitHub Actions executions.

The IDs do NOT become active merely because a shift is scheduled. Activity
requires the worker's actual OS PID + independent successful model response.
D10 stays reserved for genuinely accepted receivables and payment verification.
"""
from __future__ import annotations
import argparse,json,re
from datetime import datetime,timezone

FLEETS=("transferexperiment","BountyScoutAI")
PER_COMPANY=9*15*50
WORKERS_PER_SHIFT=5

def select(fleet,cycle,slot=0):
    if fleet not in FLEETS: raise ValueError("unknown fleet")
    cycle=int(cycle)
    if cycle<1:raise ValueError("cycle must be >=1")
    slot=int(slot)
    if not 0<=slot<WORKERS_PER_SHIFT:raise ValueError("slot out of bounds")
    offset=0 if fleet==FLEETS[0] else PER_COMPANY//2
    # Five distinct real worker slots per company per shift; 6750-worker cycle in 1350 shifts.
    idx=((cycle-1)*WORKERS_PER_SHIFT+slot+offset)%PER_COMPANY
    director=idx%9+1
    manager=(idx//9)%15+1
    worker=(idx//(9*15))%50+1
    identifier=f"D{director:02d}-M{manager:02d}-W{worker:02d}"
    return {
       "fleet":fleet,"cycle":cycle,"slot":slot,"worker_id":identifier,
       "report_parent":f"D{director:02d}-M{manager:02d}",
       "actual_model_executed":False,
       "task_status":"SCHEDULED_NOT_YET_EXECUTED",
       "local_payment_director":fleet+"/D10",
       "real_execution_proof_needed":["os_process_pid","model_inference_status","individual_artifact"],
       "money_received_verified":False,
    }

def self_test():
    seen=[select("transferexperiment",i,j)["worker_id"] for i in range(1,PER_COMPANY//WORKERS_PER_SHIFT+1) for j in range(WORKERS_PER_SHIFT)]
    assert len(set(seen))==PER_COMPANY
    assert seen[0]!=select("BountyScoutAI",1)["worker_id"]
    assert len({select("transferexperiment",1,s)["worker_id"] for s in range(WORKERS_PER_SHIFT)})==WORKERS_PER_SHIFT
    assert WORKERS_PER_SHIFT==5
    assert all(re.fullmatch(r"D0[1-9]-M(?:0[1-9]|1[0-5])-W(?:0[1-9]|[1-4]\d|50)",x) for x in seen)
    assert all("-D10" not in x for x in seen)
    assert select("transferexperiment",PER_COMPANY//WORKERS_PER_SHIFT+1)["worker_id"]==seen[0]
    print("B_ROTATION_TEST_PASS",PER_COMPANY,"eligible worker roles per B fleet; scheduled != executed")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--fleet",choices=FLEETS)
    parser.add_argument("--cycle",type=int)
    parser.add_argument("--slot",type=int,default=0)
    a=parser.parse_args()
    if a.self_test:self_test()
    else:
        if not a.fleet or not a.cycle:parser.error("specify --fleet and --cycle")
        print(json.dumps(select(a.fleet,a.cycle,a.slot)))
