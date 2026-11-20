"""Single B1/B2 owner-order and immediate-parent validator for real worker startup.

Original role addressing (ORIGINAL/fleet/role) and the legacy human-facing
fleet routes (fleet/role) refer to the SAME legitimate parent, but MUST be
normalized explicitly. This fixes the failure seen in every Nov20 recurring
model worker job without accepting mismatched companies or altered orders.
"""
from __future__ import annotations
import argparse
import json

def verify(fleet, role, actual_parent=None):
    from directive_cascade import prompt_for_worker
    from hierarchy_command_core import task_context
    from b_certified_agent_service_router import role_index

    order=prompt_for_worker(fleet,role,
        "Perform one permitted source-qualified task; report verified output or precise source blocker")
    original=task_context(role_index(fleet,role),expected={"W","S","G","H"})
    claimed=actual_parent or order["immediate_parent"]
    expected_parent="ORIGINAL/"+claimed
    expected_role="ORIGINAL/"+fleet+"/"+role
    checks={
        "canonical_original_fleet":original["root_id"]=="ORIGINAL/"+fleet,
        "canonical_leaf":original["role_id"]==expected_role,
        "same_direct_parent":original["parent"]==expected_parent,
        "cascade_parent_is_real_local_ancestor":claimed==fleet+"/"+role.rsplit("-",1)[0],
        "same_exact_current_order":original["owner_command"]["owner_order_id"]==order["owner_order_id"],
        "same_unaltered_owner_text":original["owner_command"]["owner_sha256"]==order["owner_instruction_sha256"],
        "same_full_standing_prompt":original["owner_command"]["standard_sha256"]==order["standard_prompt_sha256"],
        "full_model_prompt_includes_exact_owner_instruction":
            original["owner_command"]["full_owner_instruction"] in order["model_prompt"],
    }
    if not all(checks.values()):
        raise ValueError("OWNERSHIP_ROUTE_PREFLIGHT_FAIL: "+json.dumps({
            "fleet":fleet,"worker":role,"parent":claimed,
            "central_parent":original["parent"],
            "checks":checks},sort_keys=True))
    return {
        "status":"CURRENT_OWNER_COMMAND_RECEIVED_BY_REAL_PYTHON_PREFLIGHT",
        "fleet":fleet,"worker_role":role,"tier":original["tier"],
        "canonical_role":original["role_id"],"canonical_parent":original["parent"],
        "cascade_parent":order["immediate_parent"],
        "current_owner_order_id":order["owner_order_id"],
        "owner_instruction_sha256":order["owner_instruction_sha256"],
        "checks":checks,"real_model_inference_completed":False,
        "actual_external_customer_contact":False,
        "all_virtual_worker_roles_started":False,
    }

def self_test():
    sample=["D01-M01-W01","D10-M15-W50",
            "D02-M03-W04-S001","D02-M03-W04-S001-G001",
            "D02-M03-W04-S001-G001-H001",
            "D06-M11-W25-S070-G107-H099"]
    reports=[]
    for fleet in ("transferexperiment","BountyScoutAI"):
        for role in sample:
            row=verify(fleet,role)
            assert all(row["checks"].values())
            reports.append(row)
    assert len(reports)==12
    try:
        verify("transferexperiment","D01-M01-W01",actual_parent="BountyScoutAI/D01-M01")
    except ValueError as ex:
        assert "OWNERSHIP_ROUTE_PREFLIGHT_FAIL" in str(ex)
    else:
        raise AssertionError("Tampered parent route incorrectly accepted")
    try:
        verify("BountyScoutAI","D01-M01-W01",actual_parent="BountyScoutAI/D01-M02")
    except ValueError as ex:
        assert "OWNERSHIP_ROUTE_PREFLIGHT_FAIL" in str(ex)
    else:
        raise AssertionError("Wrong manager incorrectly accepted")
    return {"actual_python_preflight_invocations":12,
            "root_companies":2,"hierarchy_levels_tested":["W","S","G","H"],
            "wrong_fleet_parent_rejected":True,"wrong_local_manager_rejected":True,
            "actual_ai_model_comprehension_tests_completed":0}

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--fleet",choices=("transferexperiment","BountyScoutAI"))
    parser.add_argument("--role")
    args=parser.parse_args()
    if args.self_test:print("WORKER_STARTUP_PARENT_PREFLIGHT_PASS "+json.dumps(self_test()))
    elif args.fleet and args.role:print("WORKER_STARTUP_PARENT_OK "+json.dumps(verify(args.fleet,args.role)))
    else:parser.error("Use --self-test or --fleet F --role R")
