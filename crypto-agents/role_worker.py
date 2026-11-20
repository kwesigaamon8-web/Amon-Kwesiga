"""ONE worker program for EVERY actual W/S/G/H role.

* Default --role-index: execute source/ledger QA and leave an evidence receipt.
* --actual-model --fleet --role: execute the existing AI inference adapter
  THROUGH THIS SAME worker entrypoint and central owner-command gate.
No per-worker source copies, no independent virtual worker activation claims.
"""
from __future__ import annotations
import argparse
import os
import runpy
import sys
from hierarchy_command_core import main_for_tiers, task_context
from b_certified_agent_service_router import role_index

def real_ai_mode():
    parser=argparse.ArgumentParser()
    parser.add_argument("--actual-model",action="store_true",required=True)
    parser.add_argument("--fleet",required=True,choices=("transferexperiment","BountyScoutAI"))
    parser.add_argument("--role",required=True)
    args=parser.parse_args()
    role=task_context(role_index(args.fleet,args.role),expected={"W","S","G","H"})
    if role["owner_command"]["owner_order_id"]!=role["packet"]["owner_order_id"]:
        raise ValueError("Reject stale AI worker command at the shared entrypoint")
    if role["parent"]!=role["packet"]["immediate_parent"]:
        raise ValueError("Worker's manager does not match centralized code")
    os.environ["WORKFORCE_ID"]=args.fleet
    # The model adapter does the actual CPU model attempt and independent
    # comprehension check. It runs IN THIS actual worker process, not a
    # fictional extra employee. It is not a second worker command source.
    sys.argv=["crypto-agents/ai_process_worker.py",args.role]
    runpy.run_path("crypto-agents/ai_process_worker.py",run_name="__main__")

if __name__ == "__main__":
    if "--actual-model" in sys.argv:
        real_ai_mode()
    else:
        main_for_tiers(["W","S","G","H"])
