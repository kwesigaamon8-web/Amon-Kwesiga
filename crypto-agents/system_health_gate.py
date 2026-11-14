"""Preflight that FAILS CLOSED on two-fleet operational regressions.

This tests runnable code + truthful reporting, not external earnings or seven
billion living workers. No internet, credentials, blockchain access or paid
compute is required. The two heavy workflows are not launched by git pushes.
"""
from __future__ import annotations
import ast
import json
import re
from pathlib import Path

ROOT=Path("crypto-agents")
FLOW=Path(".github/workflows")
OUT=Path("system-health-reports")
OUT.mkdir(exist_ok=True)

def contains(source,pattern,desc,errors):
    if not re.search(pattern,source,re.M):
        errors.append(desc)
def test():
    errors=[]
    orders=json.loads((ROOT/"chief_D_owner_orders.json").read_text(encoding="utf-8"))
    cfg=json.loads((ROOT/"b_collection_assignments.json").read_text(encoding="utf-8"))
    assert orders["orders"][-1]["id"]==orders["current_owner_order_id"]
    assert cfg["hierarchy"]["chief_director"]=="D"
    assert set(cfg["hierarchy"]["companies"])=={"transferexperiment","BountyScoutAI"}
    for fleet in ("transferexperiment","BountyScoutAI"):
        b=cfg["hierarchy"]["companies"][fleet]
        if b["directors"]!=10 or b["reports_to"]!="D" or b["local_payment_director"]!=fleet+"/D10":
            errors.append("Board/ChiefD/local-payments mismatch for "+fleet)
    workflows={
       "transferexperiment":"real-ai-workers.yml",
       "BountyScoutAI":"bountyscoutai-real-ai-workers.yml",
    }
    plans={}
    for fleet,file in workflows.items():
        txt=(FLOW/file).read_text(encoding="utf-8")
        # Avoid an accidental trigger storm. Heavy CI can only run on time
        # or an explicit workflow dispatch, never a source code push.
        if re.search(r"(?m)^  push:",txt):
            errors.append("HEAVY_WORKFLOW_PUSH_RELAUNCH_ENABLED "+file)
        contains(txt,r"(?m)^  workflow_dispatch:\s*$",file+" cannot be manually dispatched",errors)
        contains(txt,r"(?m)^  schedule:\s*$",file+" lacks bounded schedule",errors)
        contains(txt,r"(?m)^  cancel-in-progress: false\s*$",file+" may cancel running AI work",errors)
        contains(txt,r"(?m)^\s*max-parallel:\s*3\s*$",file+" parallel capacity changed",errors)
        contains(txt,r"(?m)^\s*REAL_AI_PROCESSES_PER_DIRECTOR:\s*'20'\s*$",file+" worker capacity changed",errors)
        contains(txt,r"(?m)^\s*WORKFORCE_ID:\s*"+re.escape(fleet)+r"\s*$",file+" fleet label missing",errors)
        contains(txt,r"(?m)^      - name: Grade each REAL worker independently",file+" lacks strict scoring",errors)
        contains(txt,r"(?m)^      - name: Cross-audit EVERY actual worker",file+" lacks reciprocal audit",errors)
        contains(txt,r"(?m)^    name: Verify true AI processes",file+" no postrun process verification",errors)
        plans[fleet]={
            "workflow":file,
            "push_retrigger_disabled":not bool(re.search(r"(?m)^  push:",txt)),
            "daily_attempt_ceiling":200,
            "verified_model_completions_by_this_check":"not_assessed",
        }

    expected_files=("ai_process_worker.py","ai_process_launcher.py",
        "seven_billion_allocator.py","command_ack_gate.py",
        "strict_worker_accountability.py","everyone_peer_audit.py",
        "command_chain_receipts.py","subagent_audit.py",
        "owner_order_distribution.py","director_work_orders.py",
        "agents.py","chief_D_reporting.py","b_address_understanding.py",
        "cross_fleet_idea_exchange.py","unique_funding_tasks.py",
        "secondary_software_study.py","public_code_reader.py")
    for file in expected_files:
        text=(ROOT/file).read_text(encoding="utf-8")
        try:ast.parse(text,filename=file)
        except SyntaxError as e:errors.append("PYTHON_SYNTAX_FAILURE "+file+" "+str(e))
    launcher=(ROOT/"ai_process_launcher.py").read_text(encoding="utf-8")
    worker=(ROOT/"ai_process_worker.py").read_text(encoding="utf-8")
    software=(ROOT/"secondary_software_study.py").read_text(encoding="utf-8")
    code_reader=(ROOT/"public_code_reader.py").read_text(encoding="utf-8")
    if not all(s in code_reader for s in ("PUBLIC","MAX_BYTES","source_check_status",
                                         "api_for","read_only_excerpt","TimeoutError")):
        errors.append("PUBLIC_SOFTWARE_CODE_READER_MISSING_OR_NOT_BOUNDED")
    if not all(k in software for k in ("WORLD_SOURCES","GitLab","Codeberg","SourceHut",
                                       "PyPI","npm","Hugging Face Spaces","legal_reuse_rule")):
        errors.append("GLOBAL_SOFTWARE_SOURCE_STUDY_MISSING_OR_LICENSE_GATE_BYPASSED")
    if not all(k in worker for k in ("SECOND_DISTINCT" if False else "SOFTWARE_SECOND",
                                      "assess_software_study",
                                      "second_study_actual_model_result","SOFTWARE_SOURCE_EVIDENCE")):
        errors.append("REAL_B_WORKER_SOFTWARE_STUDY_MODEL_RESULT_NOT_GRADED")
    exchange=(ROOT/"cross_fleet_idea_exchange.py").read_text(encoding="utf-8")
    if not all(k in exchange for k in ("compile_digest","make_actions","actual_model_idea_excerpts","assigned_company_director","coin_receipt_confirmed")):
        errors.append("TWO_COMPANY_IDEA_PROVENANCE_OR_DIRECTOR_REVIEW_MISSING")
    if not all(k in worker for k in ("SHARED_IDEA_FEED","SHARED_IDEA_EXAMPLES","TEN_IDEA_MENU")):
        errors.append("REAL_B_WORKERS_ARE_NOT_READING_OPPOSITE_COMPANY_IDEAS")
    wallet_training=(ROOT/"b_address_understanding.py").read_text(encoding="utf-8")
    if not all(v in wallet_training for v in ("company_1","company_2","local_payment_director","Bitcoin mainnet","USDC","Base")):
        errors.append("COMPANY_WALLET_TRAINING_MAP_MISSING")
    if not all(v in worker for v in ("evaluate_address_mapping","address_understanding_model_status","separately_checked_address_understanding")):
        errors.append("INDIVIDUAL_B_WORKER_ADDRESS_UNDERSTANDING_NOT_GRADED")
    auditor=(ROOT/"strict_worker_accountability.py").read_text(encoding="utf-8")
    command=(ROOT/"command_chain_receipts.py").read_text(encoding="utf-8")
    child=(ROOT/"subagent_audit.py").read_text(encoding="utf-8")
    catalog=(ROOT/"subagent_factory.py").read_text(encoding="utf-8")
    for file,text,terms in (
        ("launcher",launcher,("role_for_slot(","subprocess.run(","real_model_completed")),
        ("worker",worker,("LATEST_CHIEF_D_INSTRUCTION","latest_command_model_acknowledgement","WORKFORCE_ID")),
        ("audit",auditor,("MODEL_INFERENCE_NOT_COMPLETED","LATEST_CHIEF_D_ORDER_NOT_ACKNOWLEDGED")),
        ("command",command,("current_organization_route","CHIEF_D","chief_D_latest_owner_order")),
    ):
        for key in terms:
            if key not in text:errors.append("MISSING_REAL_EXECUTION_CHECK "+file+" "+key)
    if 'base["deterministic_child_identities"]' in child:
        errors.append("OLD_SUBAGENT_CATALOG_KEY_STILL_USED")
    if 'base["unique_deterministic_children"]' not in child or '"unique_deterministic_children":count*150' not in catalog:
        errors.append("SUBAGENT_CATALOG_AND_AUDIT_KEY_DRIFT")
    scout=(ROOT/"paid_task_scout.py").read_text(encoding="utf-8")
    if not all(x in scout for x in ("original_url","verified_funding","ugandan_eligibility","github_original_issue_open")):
        errors.append("PAID_LEAD_SCOUT_NO_LONGER_EVIDENCE_GATED")
    return {"status":"PASS" if not errors else "FAIL",
      "chief_D_current_order":orders["current_owner_order_id"],
      "two_companies":plans,"separate_local_directors":20,
      "seven_billion_roles_goal":7000000000,
      "source_programs_grammar_checked":len(expected_files),
      "regressions":errors,
      "claims_not_supported":"No verified income, payer contact, complete worker execution or model understanding established by this structural test."}

if __name__=="__main__":
    r=test()
    (OUT/"SYSTEM_HEALTH.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    print("B_SYSTEM_HEALTH",json.dumps(r))
    if r["status"]!="PASS":
        raise SystemExit(1)
