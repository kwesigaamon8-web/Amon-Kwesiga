"""Constant-memory IDs for 374,625,000,000 defined H-tier research roles.

562,500,000 G-tier parents each define exactly 666 uniquely scoped H-tier
children. These are software-role definitions; no independent social account,
concurrent host, human recruit or completed model execution is implied.
"""
from pathlib import Path
import json
import re
from microcompany_factory import verify_id as verify_g_parent

CFG=json.loads(Path("crypto-agents/mega_branch_666.json").read_text(encoding="utf-8"))
assert CFG["existing_micro_worker_parent_identities"]==562500000
assert CFG["new_worker_roles_per_branch"]==666
assert len(CFG["sectors"])==18 and len(CFG["methods"])==37
H_ID=re.compile(r"^(D(?:0[1-9]|10)-M(?:0[1-9]|1[0-5])-W(?:0[1-9]|[1-4][0-9]|50)-S(?:00[1-9]|0[1-9][0-9]|1[0-4][0-9]|150)-G(?:00[1-9]|0[1-9][0-9]|[1-4][0-9][0-9]|500))-H(00[1-9]|0[1-9][0-9]|[1-5][0-9][0-9]|6[0-5][0-9]|66[0-6])$")

def describe_branch_worker(parent_id,parent_name,slot):
    if not verify_g_parent(parent_id):
        raise ValueError("Not a valid 562,500,000-role micro-worker parent")
    if type(slot) is not int or not 1 <= slot <= 666:
        raise ValueError("Branch worker slot must be between 1 and 666")
    sector=CFG["sectors"][(slot-1)//37]
    task=CFG["methods"][(slot-1)%37]
    return {
        "id":f"{parent_id}-H{slot:03d}",
        "name":f"{parent_name}-BranchWorker-{slot:03d}",
        "parent_id":parent_id,
        "branch_id":"BR-"+parent_id,
        "level":"mega_branch_worker",
        "sector":sector,"assigned_task":task,
        "mission":f"Independently {task.lower()} for legitimate cryptocurrency-paid opportunities in {sector}. Keep exact original evidence and report only to {parent_id}.",
        "ultimate_success":"Real legally earned spendable cryptocurrency independently verified credited at owner-approved correct-network addresses.",
        "reports_to_one":parent_id,
        "status":"defined_not_executed",
        "external_social_account_created":False,
        "actual_model_inference_completed":False
    }

def verify_branch_worker_id(child_id):
    m=H_ID.fullmatch(str(child_id))
    if not m:return False
    parent,slot=m.group(1),int(m.group(2))
    return verify_g_parent(parent) and 1<=slot<=666

def rotating_slot(parent_id,cycle):
    if not verify_g_parent(parent_id) or type(cycle) is not int:
        raise ValueError("Invalid parent micro-worker ID or cycle")
    offset=sum(ord(c) for c in parent_id)%666
    return ((cycle+offset)%666)+1

def structural_proof():
    assert CFG["new_branch_count"]==562500000
    assert CFG["new_role_identities"]==562500000*666
    assert CFG["all_level_total_role_identities"]==375188632680
    assert len(set(CFG["sectors"]))==18 and len(set(CFG["methods"]))==37
    examples=[]
    # Validate key edge cases and multiple parents, rather than allocating 374.625bn rows.
    for parent in ("D01-M01-W01-S001-G001","D05-M09-W29-S075-G250","D10-M15-W50-S150-G500"):
        for slot in (1,37,38,111,333,665,666):
            obj=describe_branch_worker(parent,parent,slot)
            assert verify_branch_worker_id(obj["id"])
            assert obj["reports_to_one"]==parent
            assert obj["sector"] and obj["assigned_task"]
            if len(examples)<3:examples.append(obj["id"])
        assert not verify_branch_worker_id(parent+"-H000")
        assert not verify_branch_worker_id(parent+"-H667")
    return {
      "parent_G_level_identifiers_defined":562500000,
      "H_workers_per_parent":666,
      "unique_H_worker_identifiers_defined":374625000000,
      "total_system_role_identifiers_defined":375188632680,
      "identity_parent_mapping_proof":"PASS",
      "examples":examples,
      "note":"Only mathematical role definitions proven; no active agents or received cryptocurrency are implied."
    }

if __name__=="__main__":
    print(json.dumps(structural_proof(),indent=2))
