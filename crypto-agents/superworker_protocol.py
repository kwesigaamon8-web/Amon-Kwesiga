"""Role-specific self-reviewing superworker protocol for actually invoked B agents."""
from __future__ import annotations
from ability_based_dispatch import dispatch

PHASES=("VERIFY_SOURCE","PLAN_REAL_EARNING","BUILD_ORIGINAL_WORK","QA_REVIEW",
        "AUTHORIZED_DELIVERY","VERIFY_ACCEPTANCE_AND_PAYMENT","REPORT_TO_PARENT")
def create(fleet,role,specialty,level):
 if fleet not in ("transferexperiment","BountyScoutAI"):raise ValueError("Unknown company")
 chosen=dispatch(fleet,role,specialty,role[:3],level)
 parts=role.split("-")
 chain=[fleet+"/"+ "-".join(parts[:i]) for i in range(len(parts)-1,0,-1)]
 chain+=["CHIEF_D","HUMAN_OWNER"]
 if chain[0]!=chosen["reports_to"]:raise ValueError("Changed immediate parent")
 return {
  "version":"B_SUPERWORKER_20261116_V1",
  "identity":fleet+"/"+role,
  "primary_lane":chosen["primary_lane"],
  "specific_task":chosen["one_actual_primary_action"],
  "optional_secondary_lane":chosen["optional_secondary_lane"],
  "supervisor_chain":chain,
  "phases":list(PHASES),
  "skills":["research using only actual available tools","original document/data/code drafting",
    "test and self-review","select strongest feasible real paid task","truthful source citations",
    "authenticated buyer contact only when connected and allowed",
    "consenting real ASIC partner economics, not mining without hardware"],
  "must_report":["real worker run ID or NOT_RUN","original payer/source link or NONE",
    "original work produced and QA evidence or NONE","actual submission/acceptance or NOT_SENT",
    "correct asset, chain, actual credit TXID or NOT_VERIFIED",
    "one blocker and next feasible action"],
  "account_credentials_granted":False,"new_server_created":False,
  "live_model_called_by_profile":False,"sha256_miner_started":False,
  "paid_customer_verified":False,
  "financial_gate":"Own-company D10 verifies authentic buyer receipt; physical ASIC mining needs operator consent"
 }
if __name__=="__main__":
 from pprint import pprint
 pprint(create("transferexperiment","D01-M01-W01","original code","W"))
