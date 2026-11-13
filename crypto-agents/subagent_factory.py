"""Compact deterministic identity factory for 1,125,000 child roles.

An identity is a stable role definition. Only a role with an actual report from
the open-weight model is counted as active AI. No human or social accounts.
"""
import json
import re
from pathlib import Path

ROOT=Path("crypto-agents")
SPEC=json.loads((ROOT/"subagent_factory.json").read_text(encoding="utf-8"))
TASKS=SPEC["independent_scope_templates"]
assert len(TASKS)==150

def describe_child(parent_id, parent_name, slot):
    if not re.fullmatch(r"D(?:0[1-9]|10)-M(?:0[1-9]|1[0-5])-W(?:0[1-9]|[1-4]\d|50)",str(parent_id)):
        raise ValueError("Parent ID is not a configured specialist worker")
    if type(slot)!=int or not (1<=slot<=150):
        raise ValueError("Child slot must be an integer 1-150")
    task=TASKS[slot-1]
    slug=re.sub(r"[^a-z0-9]+","-",task["specific_role"].lower()).strip("-")
    return {
        "id":f"{parent_id}-S{slot:03d}",
        "agent_name":f"{parent_name}-Subagent-{slot:03d}-{slug}",
        "parent_id":parent_id,"level":"delegated_subagent",
        "owner_order_id":"ORD-021","owner_order_ids":["ORD-021","ORD-022"],"order_inherited_from":parent_id,
        "tool_improvement_mandate":SPEC["tool_improvement_order"],
        "sector":task["sector"],"assigned_role":task["specific_role"],
        "objective":"Independently research WORLDWIDE for legitimate crypto-paid assignments; confirm payer, actual paid deliverable, location eligibility, no upfront fee, approved payment network and verified incoming credit. Specific responsibility: "+task["independent_objective"],
        "reporting_chain":"subagent -> assigned worker -> assigned manager -> assigned director -> owner",
        "ultimate_owner_order":"Find legitimate paid work with independently verified receipts; respect unique-parent command chain.",
        "status":"defined_not_yet_executed"
    }

def select_slot(parent_id, cycle):
    if type(cycle)!=int: raise ValueError("Cycle must be integer")
    offset=sum(ord(ch) for ch in parent_id)%150
    return ((cycle+offset)%150)+1

def verify_catalog():
    count=0
    examples=[]
    for d in range(1,11):
        for m in range(1,16):
            for w in range(1,51):
                parent=f"D{d:02d}-M{m:02d}-W{w:02d}"
                count+=1
                if len(examples)<3:
                    examples.append(describe_child(parent,parent,1))
                for slot in (1,75,150):
                    c=describe_child(parent,parent,slot)
                    assert c["parent_id"]==parent and c["id"].startswith(parent+"-S")
    return {"parent_worker_ids_checked":count,"children_per_parent":150,
            "unique_deterministic_children":count*150,"sample_children":examples,
            "catalog_status":"valid_definitions_not_activation"}

if __name__=="__main__":
    print(json.dumps(verify_catalog(),indent=2))
