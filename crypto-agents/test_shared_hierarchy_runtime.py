"""Executable acceptance tests for one role program per hierarchy tier.

Proves ONLY actual finite Python invocations, shared code routing and current
owner-order integrity. Zero remote AI understanding, external platform messages,
customer acceptance or wallet receipts are created by this test.
"""
from __future__ import annotations
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0,"crypto-agents")
from b_certified_agent_service_router import OFFSETS,ROLES_PER_DIRECTOR
from enigma_universal_owner_order import PER_ROOT, GRAND_TOTAL, recipient
from directive_cascade import read_owner
from hierarchy_command_core import ASSIGNED_CODES,task_context,sha

OUT=Path("shared-role-command-evidence")

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    owner=read_owner()
    assert GRAND_TOTAL==11_255_658_980_400
    assert PER_ROOT==375_188_632_680
    assert len(ASSIGNED_CODES)==7 and len(set(ASSIGNED_CODES.values()))==4
    results=[]
    for root in range(30):
        for tier in ("D","A","M","W","S","G","H"):
            idx=root*PER_ROOT+OFFSETS[tier]
            context=task_context(idx,expected={tier})
            path=ASSIGNED_CODES[tier]
            proc=subprocess.run([sys.executable,path,
                                 "--role-index",str(idx),"--out",str(OUT)],
                                capture_output=True,text=True,timeout=30)
            if proc.returncode!=0:
                raise RuntimeError(f"Executable failed root={root} tier={tier}: {proc.stderr[-1200:]}")
            record_path=OUT/f"role-{idx}-{tier}.json"
            r=json.loads(record_path.read_text(encoding="utf-8"))
            assert r["role_id"]==context["role_id"]
            assert r["root_id"]==context["root_id"]
            assert r["owner_order_id"]==owner["owner_order_id"]
            assert r["owner_instruction_sha256"]==owner["owner_sha256"]
            assert r["complete_standing_protocol_sha256"]==owner["standard_sha256"]
            assert r["full_owner_to_role_path"][-1]==r["role_id"]
            assert r["full_owner_to_role_path"][-2]==r["supervisor"]
            assert r["reused_role_program"]==path
            assert r["process_pid"]>0 and r["real_python_task_executed"] is True
            assert r["ai_model_inference_completed"] is False
            assert r["individual_model_comprehension_demonstrated"] is False
            assert r["external_customer_contacted"] is False
            assert r["payment_received_verified"] is False
            assert r["other_virtual_roles_notified"] is False
            assert sha(json.dumps(r["task_result"],sort_keys=True,ensure_ascii=False))==r["task_evidence_sha256"]
            assert r["task_result"]["source_audit"]["records_examined"]>=1
            results.append({"root":r["root_id"],"tier":tier,"role":r["role_id"],
                "code":r["reused_role_program"],"pid":r["process_pid"],
                "task_sha256":r["task_evidence_sha256"]})
    assert len(results)==210
    assert len({(x["root"],x["tier"]) for x in results})==210
    counts=Counter(x["tier"] for x in results)
    assert all(counts[t]==30 for t in ("D","A","M","W","S","G","H"))
    # Fail closed: a D code cannot execute as an M; a worker cannot claim a
    # non-existent role index; neither can mutate the owner registry.
    director_idx=0*PER_ROOT+OFFSETS["D"]
    false_manager=subprocess.run([sys.executable,"crypto-agents/role_manager.py",
        "--role-index",str(director_idx),"--out",str(OUT)],capture_output=True,text=True,timeout=15)
    assert false_manager.returncode!=0
    invalid=subprocess.run([sys.executable,"crypto-agents/role_worker.py",
        "--role-index",str(GRAND_TOTAL),"--out",str(OUT)],capture_output=True,text=True,timeout=15)
    assert invalid.returncode!=0
    report={
        "schema":"ONE_OWNER_COMMAND_SINGLE_CODE_PER_ROLE_PROOF_V1",
        "current_owner_order_id":owner["owner_order_id"],
        "canonical_owner_sha256":owner["owner_sha256"],
        "root_divisions_sampled":30,
        "actual_python_role_processes_executed":len(results),
        "real_processes_by_tier":dict(counts),
        "unique_entrypoint_files":sorted(set(ASSIGNED_CODES.values())),
        "one_shared_role_execution_engine":"crypto-agents/hierarchy_command_core.py",
        "all_tested_processes_inherited_same_current_owner_command":True,
        "wrong_tier_code_rejected":True,"out_of_namespace_role_rejected":True,
        "all_virtual_11T_positions_live_or_notified":False,
        "individual_AI_model_comprehensions_proven_by_this_test":0,
        "authenticated_customer_proposals_sent_by_this_test":0,
        "verified_customer_payments_from_this_test":0,
        "role_execution_rows":results,
    }
    (OUT/"SHARED_ROLE_AUDIT.json").write_text(json.dumps(report,indent=2)+"\n")
    lines=["# One owner command — shared code by role category",
         "",f"Current order: \`{owner['owner_order_id']}\`", "",
         "**210 distinct finite Python role processes** were invoked: 30 root divisions × 7 tiers (D/A/M/W/S/G/H).",
         "Each process fetched the SAME canonical command, validated owner SHA and its direct supervisor,",
         "and produced a machine-readable actual bounded source-QA or delegation result.",
         "","| Hierarchy role | Shared executable | Real tested processes |",
         "|---|---|---:|"]
    for t in ("D","A","M","W","S","G","H"):
        lines.append(f"| {t} | \`{ASSIGNED_CODES[t]}\` | {counts[t]} |")
    lines+=["","**One shared core:** \`crypto-agents/hierarchy_command_core.py\`.",
       "No per-person code copies are created; each invocation supplies only its role ID, parent and task.",
       "Wrong-tier executable and out-of-namespace index correctly failed.",
       "","**Truth limit:** code reuse and command delivery in these real Python processes",
       "do not prove live independent generative AI, model comprehension, external customer contact",
       "or receipt of coins; the rest of the 11.25 trillion virtual positions remain configured, not running."]
    (OUT/"REPORT.md").write_text("\n".join(lines)+"\n")
    print("ONE_OWNER_COMMAND_ALL_HIERARCHY_ROLE_CODE_TEST_PASS "+
          json.dumps({k:v for k,v in report.items() if k!="role_execution_rows"},sort_keys=True))

if __name__=="__main__":main()
