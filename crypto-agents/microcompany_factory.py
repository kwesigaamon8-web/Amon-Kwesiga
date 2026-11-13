"""562,500,000 virtual specialized research roles in nested microcompanies.

Each of 1,125,000 existing subagents owns 500 distinct deterministic worker
identities. No entire 562.5m-row file and no fake hosted AI agents.
"""
import json
import re
from pathlib import Path

CONFIG=json.loads(Path("crypto-agents/microcompany_structure.json").read_text(encoding="utf-8"))
assert CONFIG["parent_roles"]==1125000
assert CONFIG["employees_per_microcompany"]==500
assert len(CONFIG["sector_catalog"])==20 and len(CONFIG["task_catalog"])==25
PARENT_PATTERN=re.compile(r"^D(?:0[1-9]|10)-M(?:0[1-9]|1[0-5])-W(?:0[1-9]|[1-4][0-9]|50)-S(?:00[1-9]|0[1-9][0-9]|1[0-4][0-9]|150)$")
MICROWORKER_PATTERN=re.compile(r"^(D(?:0[1-9]|10)-M(?:0[1-9]|1[0-5])-W(?:0[1-9]|[1-4][0-9]|50)-S(?:00[1-9]|0[1-9][0-9]|1[0-4][0-9]|150))-G([0-4][0-9][0-9]|500)$")

def describe_micro_worker(parent_id,parent_name,slot):
    if not PARENT_PATTERN.fullmatch(str(parent_id)):
        raise ValueError("Invalid parent subagent role ID")
    if type(slot)!=int or not 1<=slot<=500:
        raise ValueError("Micro-worker slot must be 1..500")
    section=(slot-1)//25
    task=(slot-1)%25
    sector=CONFIG["sector_catalog"][section]
    action=CONFIG["task_catalog"][task]
    return {
       "id":f"{parent_id}-G{slot:03d}",
       "name":f"{parent_name}-MicroWorker-{slot:03d}",
       "parent_id":parent_id,
       "owner_order_id":"ORD-021","owner_order_ids":["ORD-021","ORD-022","ORD-023"],"order_inherited_from":parent_id,
       "independent_after_order":CONFIG["independent_after_owner_order"],
       "tool_improvement_mandate":CONFIG["tool_improvement_order"],
       "company_id":"MC-"+parent_id,
       "level":"microcompany_worker",
       "assigned_sector":sector,
       "assigned_task":action,
       "independent_research_objective":f"Independently research WORLDWIDE and {action} for legitimate crypto-paid work involving {sector} or other viable industries. Confirm real payer, clear deliverable, eligibility, zero upfront fees, exact approved receiving network and independently verified credit before calling anything earned.",
       "chain":"micro-worker -> subagent microcompany head -> parent worker -> manager -> director -> OWNER",
       "mission":"Only legitimate transferable cryptocurrency actually received at owner-approved addresses is success.",
       "identity_status":"defined_not_running",
       "external_account_created":False,
       "independent_human_employee":False
    }

def verify_id(micro_worker_id):
    match=MICROWORKER_PATTERN.fullmatch(str(micro_worker_id))
    if not match:return False
    parent_id,number=match.group(1),int(match.group(2))
    return 1<=number<=500 and describe_micro_worker(parent_id,parent_id,number)["id"]==micro_worker_id

def select_micro_worker_slot(parent_subagent_id,cycle):
    if not PARENT_PATTERN.fullmatch(str(parent_subagent_id)):
        raise ValueError("Unknown parent ID")
    if type(cycle)!=int:raise ValueError("Cycle must be integer")
    # Static deterministic offset + changing cycle; every slot is reachable.
    offset=sum(ord(c) for c in parent_subagent_id)%500
    return ((cycle+offset)%500)+1

def audit_definitions():
    # Constant-memory proof: every eligible parent has exactly 500 fixed-width
    # unique suffixes; 7500 workers * 150 subagents * 500 = 562500000.
    assert CONFIG["parent_roles"]*CONFIG["employees_per_microcompany"]==562500000
    assert CONFIG["total_role_identities"]==563632680
    assert len(set(CONFIG["sector_catalog"]))==20
    assert len(set(CONFIG["task_catalog"]))==25
    examples=[]
    for d in (1,5,10):
        for m in (1,15):
            for w in (1,50):
                for s in (1,75,150):
                    parent=f"D{d:02d}-M{m:02d}-W{w:02d}-S{s:03d}"
                    ids=set()
                    for n in (1,25,26,125,250,499,500):
                        candidate=describe_micro_worker(parent,parent,n)
                        assert verify_id(candidate["id"])
                        assert candidate["parent_id"]==parent
                        ids.add(candidate["id"])
                    assert len(ids)==7
                    if len(examples)<3:
                        examples.append(describe_micro_worker(parent,parent,1))
    assert not verify_id("D01-M01-W01-S001-G000")
    assert not verify_id("D01-M01-W01-S001-G501")
    return {"microcompanies_defined":1125000,"unique_micro_workers_defined":562500000,
            "grand_total_roles_defined":563632680,"identity_formula_and_one_parent":"PASS",
            "sample_ids":[x["id"] for x in examples],
            "limitations":"Deterministic potential identities. Actual AI calls must be counted separately."}

if __name__=="__main__":
    print(json.dumps(audit_definitions(),indent=2))
