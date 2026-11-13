"""Verify owner directive ORD-021 propagates from a director to an H-level role.
This checks role definitions and model-prompt wiring, NOT successful agent execution.
"""
import json
import os
from pathlib import Path
from subagent_factory import describe_child
from microcompany_factory import describe_micro_worker
from mega_branch_factory import describe_branch_worker, verify_branch_worker_id

ROOT = Path("crypto-agents")
ORDER_ID = "ORD-021"

def verify():
    registry = json.loads((ROOT / "owner_orders.json").read_text(encoding="utf-8"))
    shared = json.loads((ROOT / "shared_understanding.json").read_text(encoding="utf-8"))
    assert any(o.get("id") == ORDER_ID for o in registry["orders"])
    assert shared["owner_order_cascade"]["id"] == ORDER_ID
    assert "WORLDWIDE" in shared["owner_intent"]["worldwide"]
    source = (ROOT / "company_ai_review.py").read_text(encoding="utf-8")
    for marker in ('"standing_owner_order"', '"inherited_owner_instruction"', 'SHARED["owner_intent"]["worldwide"]', 'hchild["mission"]'):
        assert marker in source, f"Missing model prompt cascade marker: {marker}"
    checked = 0
    for director in (1, 5, 10):
        for manager in (1, 15):
            for worker in (1, 50):
                parent = f"D{director:02d}-M{manager:02d}-W{worker:02d}"
                for s in (1, 150):
                    child = describe_child(parent, parent, s)
                    assert child["parent_id"] == parent and child["owner_order_id"] == ORDER_ID
                    assert "WORLDWIDE" in child["objective"]
                    for g in (1, 500):
                        micro = describe_micro_worker(child["id"], child["agent_name"], g)
                        assert micro["parent_id"] == child["id"] and micro["owner_order_id"] == ORDER_ID
                        assert "WORLDWIDE" in micro["independent_research_objective"]
                        for h in (1, 666):
                            last = describe_branch_worker(micro["id"], micro["name"], h)
                            assert last["parent_id"] == micro["id"] and last["owner_order_id"] == ORDER_ID
                            assert "WORLDWIDE" in last["mission"]
                            assert verify_branch_worker_id(last["id"])
                            assert last["status"] == "defined_not_executed"
                            checked += 1
    return {
        "standing_order": ORDER_ID,
        "sampled_complete_owner_to_H_paths": checked,
        "tested_directors": ["D01", "D05", "D10"],
        "first_and_last_manager_worker_S_G_H_slots_tested": True,
        "last_layer_reached": "H-level 666-role branch",
        "structural_cascade": "PASS",
        "model_prompt_wiring": "PASS",
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
            f.write("ORD-021 cascade definition audit: PASS. " + str(result["sampled_complete_owner_to_H_paths"]) + " sampled paths. No live-agent or coin-receipt claim.\n")
