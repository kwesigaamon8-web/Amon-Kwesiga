"""Verify owner directives ORD-021, ORD-022, ORD-023 and ORD-029 cascade to last H-tier.
This checks role definitions and model-prompt wiring, NOT successful agent execution.
"""
import json
import os
from pathlib import Path
from subagent_factory import describe_child
from microcompany_factory import describe_micro_worker
from mega_branch_factory import describe_branch_worker, verify_branch_worker_id
from command_chain_receipts import configured_assignment, structural_check

ROOT = Path("crypto-agents")
ORDER_ID = "ORD-021"
ORDER_IDS = {"ORD-021", "ORD-022", "ORD-023", "ORD-029", "ORD-035"}

def verify():
    registry = json.loads((ROOT / "owner_orders.json").read_text(encoding="utf-8"))
    shared = json.loads((ROOT / "shared_understanding.json").read_text(encoding="utf-8"))
    assert ORDER_IDS.issubset({o.get("id") for o in registry["orders"]})
    assert shared["owner_order_cascade"]["id"] == ORDER_ID
    assert "WORLDWIDE" in shared["owner_intent"]["worldwide"]
    assert "ORD-022" in shared["owner_intent"]["tool_improvement"]
    assert "ORD-023" in shared["owner_intent"]["immediate_independent_execution"]
    assert "ORD-029" in shared["owner_intent"]["agent_freedom"]
    source = (ROOT / "company_ai_review.py").read_text(encoding="utf-8")
    for marker in ('"standing_owner_order"', '"additional_owner_order"', '"independence_order"', '"immediate_independent_work"', '"tools_and_sites_improvement"', 'SHARED["owner_intent"]["worldwide"]', 'hchild["mission"]'):
        assert marker in source, f"Missing model prompt cascade marker: {marker}"
    assert structural_check()["status"]=="PASS"
    checked = 0
    for director in (1, 5, 10):
        for manager in (1, 15):
            for worker in (1, 50):
                parent = f"D{director:02d}-M{manager:02d}-W{worker:02d}"
                for s in (1, 150):
                    child = describe_child(parent, parent, s)
                    assert child["parent_id"] == parent and child["owner_order_id"] == ORDER_ID
                    assert "WORLDWIDE" in child["objective"]
                    assert ORDER_IDS.issubset(set(child["owner_order_ids"]))
                    assert "ORD-023" in child["independent_after_order"]
                    assert "ORD-022" in child["tool_improvement_mandate"]
                    for g in (1, 500):
                        micro = describe_micro_worker(child["id"], child["agent_name"], g)
                        assert micro["parent_id"] == child["id"] and micro["owner_order_id"] == ORDER_ID
                        assert "WORLDWIDE" in micro["independent_research_objective"]
                        assert ORDER_IDS.issubset(set(micro["owner_order_ids"]))
                        assert "ORD-023" in micro["independent_after_order"]
                        assert "ORD-022" in micro["tool_improvement_mandate"]
                        for h in (1, 666):
                            last = describe_branch_worker(micro["id"], micro["name"], h)
                            assert last["parent_id"] == micro["id"] and last["owner_order_id"] == ORDER_ID
                            assert "WORLDWIDE" in last["mission"]
                            assert ORDER_IDS.issubset(set(last["owner_order_ids"]))
                            assert "ORD-023" in last["independent_after_order"]
                            assert "ORD-022" in last["tool_improvement_mandate"]
                            assert verify_branch_worker_id(last["id"])
                            assert last["status"] == "defined_not_executed"
                            assert configured_assignment(last["id"])["direct_supervisor"]==micro["id"]
                            checked += 1
    return {
        "standing_orders": sorted(ORDER_IDS),
        "sampled_complete_owner_to_H_paths": checked,
        "tested_directors": ["D01", "D05", "D10"],
        "first_and_last_manager_worker_S_G_H_slots_tested": True,
        "last_layer_reached": "H-level 666-role branch",
        "structural_cascade": "PASS",
        "model_prompt_wiring": "PASS",
        "last_tier_immediate_independent_execution_rule": "PASS",
        "live_tool_scout_execution": "NOT VERIFIED",
        "active_model_inferences_verified": False,
        "payments_verified": False
    }

if __name__ == "__main__":
    result = verify()
    out = Path("owner-order-cascade-audit")
    out.mkdir(parents=True, exist_ok=True)
    (out / "AUDIT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("ORD-021 / ORD-022 / ORD-023 cascade definition audit: PASS. " + str(result["sampled_complete_owner_to_H_paths"]) + " sampled paths. No live-agent or coin-receipt claim.\n")
