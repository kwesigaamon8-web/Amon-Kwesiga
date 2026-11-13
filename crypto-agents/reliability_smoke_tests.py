"""Offline, fast regression tests for B: no models, network, or third-party logins.

Always run before large AI worker fleets. Tests genuine generated report
semantics without treating synthetic fixtures as real workers or earnings.
"""
from __future__ import annotations
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import importlib.util

ROOT=pathlib.Path(__file__).resolve().parents[1]
AGENTS=ROOT/"crypto-agents"
TESTS=[]

def verify(name,condition):
    TESTS.append({"test":name,"passed":bool(condition)})
    if not condition:raise AssertionError(name)

def call(script,cwd,role=None):
    env=dict(os.environ)
    if role:env["ROLE_ID"]=role
    r=subprocess.run([sys.executable,str(AGENTS/script)],cwd=cwd,env=env,
                     text=True,capture_output=True,timeout=20)
    if r.returncode:
        raise AssertionError(script+" exited "+str(r.returncode)+"\n"+
                             r.stdout[-1600:]+"\n"+r.stderr[-1600:])
    return r.stdout

# 1: Catch all Python syntax errors, including nested scripts not imported yet.
x=subprocess.run([sys.executable,"-m","compileall","-q",str(AGENTS)],
                 cwd=ROOT,text=True,capture_output=True,timeout=30)
verify("all_python_scripts_compile",x.returncode==0)

# 1b: W/S/G/H are all scheduled to use real finite model capacity.
sys.path.insert(0,str(AGENTS))
from fair_agent_scheduler import (select_roles, role_for_ordinal,
    activation_summary,TOTAL_HIERARCHY,TOTAL_BY_DIRECTOR)
verify("all_375b_identities_addressable_not_live",TOTAL_HIERARCHY==375188632680)
roles=select_roles("D01",31,50)
fair=activation_summary("D01",31,50)
verify("four_tiers_get_real_model_slots",
    len(roles)==len(set(roles))==50 and
    all(12<=fair["activation_counts_by_tier"][t]<=13 for t in "WSGH"))
for tier in "WSGH":
    seen={role_for_ordinal("D01",tier,i) for i in range(3000)}
    expected=min(3000,TOTAL_BY_DIRECTOR[tier])
    verify("no_repeat_role_ids_sample_"+tier,len(seen)==expected)
verify("different_directors_have_distinct_roles",not(set(roles)&set(select_roles("D02",31,50))))

# 2: Owner order identity and invariant checks.
orders=json.loads((AGENTS/"owner_orders.json").read_text(encoding="utf-8"))
ids=[x["id"] for x in orders["orders"]]
verify("owner_orders_unique",len(ids)==len(set(ids)) and "ORD-040" in ids)
command=json.loads((AGENTS/"owner_command_chain.json").read_text(encoding="utf-8"))
verify("user_controls_b",command.get("highest_authority")=="OWNER")

# 3: Individual actual-run evidence generator does not fabricate payment.
with tempfile.TemporaryDirectory(prefix="B-offline-deliverables-") as tmp:
    here=pathlib.Path(tmp)
    (here/"reports").mkdir()
    (here/"company-reports").mkdir()
    (here/"reports"/"D01.json").write_text(json.dumps({
        "role":"D01","ai_analysis":{"status":"llm_completed"},
        "mission":"Investigate genuine Bitcoin-paying work",
        "unverified_leads":[{"title":"Unconfirmed lead","url":"https://example.org/"}],
        "execution_status":"source_checked"
    }),encoding="utf-8")
    (here/"company-reports"/"D01-M01.json").write_text(json.dumps({
        "manager_id":"D01-M01","workers_executed_this_cycle":1,
        "model_inference":{"status":"model_completed","analysis":"Sample only"},
        "unverified_leads":[{"title":"Candidate payer not verified","url":"https://example.org/listing"}]
    }),encoding="utf-8")
    out=call("agent_deliverables.py",here,"D01")
    obj=json.loads((here/"agent-deliverables"/"manifest-D01.json").read_text())
    verify("individual_deliverables_written",obj["individual_documents_generated"]>=1)
    verify("not_all_virtual_managers_claimed_active",len(obj["missing_expected_ids"])>=1)
    verify("no_fake_coin_income",obj["verified_coin_receipts"]==[] and
           obj["documents_are_not_earnings"] is True)
    verify("valid_report_rendered","## Actual work and result" in
           (here/"agent-deliverables"/"D01.md").read_text())

# 4: Independent reasoning chooses a bounded plan with an explicit action.
spec=importlib.util.spec_from_file_location("agent_cognition",AGENTS/"agent_cognition.py")
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
plan=module.deterministic_plan(
    "D01-M01-W01","Bookkeeping", [{"title":"Example","url":"https://example.com/job"}],
    {"coin":"BTC","network":"Bitcoin","official_source_url":"https://bitcoin.org",
     "earning_source_url":"https://example.com/jobs"},
    {"state_available":False,"previous_run_count":0}
)
verify("cognition_has_specific_work_and_safe_scope",
       len(plan["plan_steps"])>=3 and plan["source_to_verify"].startswith("https://")
       and plan["external_side_effects_allowed"] is False)
checkpoint=module.checkpoint("D01-M01-W01",plan,"model_completed","Original reply",
                             {"status":"model_completed","response":"Check compensation"},
                             "source_checked")
verify("cognition_checkpoint_is_not_payment_or_live_agent",
       checkpoint["verified_coin_receipt"] is False and
       checkpoint["continuation_requires_another_actual_worker_run"] is True)

# 5: Separate Director D evidence gate counts true model output but never fake cash.
with tempfile.TemporaryDirectory(prefix="B-offline-director-") as tmp:
    here=pathlib.Path(tmp)
    reports=here/"combined-ai-processes"/"ai-process-reports"
    reports.mkdir(parents=True)
    wid="D01-M01-W01"
    (reports/"manifest-D01.json").write_text(json.dumps({
        "subprocesses_invoked":1,
        "worker_processes_selected":[wid],
        "real_model_completed":1
    }),encoding="utf-8")
    (reports/(wid+".json")).write_text(json.dumps({
        "worker_id":wid,"inference_status":"model_completed","os_process_pid":1234,
        "model_response":"One concrete answer, though sponsorship is not confirmed.",
        "source_check_status":"source_checked",
        "source_items":[{"title":"Research example","url":"https://example.org/offer"}],
        "cognitive_checkpoint":{"next_action":"Check original payer and pay terms"},
        "cognitive_critical_review":{"status":"model_completed","actually_second_inference":True},
        "verified_wallet_receipts":[{"amount":"999999 BTC","claimed_without_proof":True}]
    }),encoding="utf-8")
    call("director_D_results_gate.py",here)
    d=json.loads((here/"director-D-results"/"DIRECTOR_D_RESULTS.json").read_text())
    verify("director_d_evidence_gate_real_models",d["actual_model_completions_confirmed"]==1)
    verify("director_d_source_and_next_step",d["workers_with_public_source_links"]==1
           and d["workers_with_specific_next_action"]==1)
    verify("director_d_excludes_fake_receipts",d["confirmed_owner_crypto_receipts_by_this_audit"]==0
           and d["payer_and_compensation_verified_by_this_audit"]==0)
    verify("director_d_missing_directors_are_not_counted",d["directors_with_manifests"]==1)

# 6: The next independent run receives real saved checkpoints when valid.
with tempfile.TemporaryDirectory(prefix="B-offline-memory-") as tmp:
    here=pathlib.Path(tmp)
    reports=here/"combined-ai-processes"/"ai-process-reports"
    reports.mkdir(parents=True)
    wid="D01-M01-W01"
    (reports/"manifest-D01.json").write_text(json.dumps({
        "worker_processes_selected":[wid]
    }),encoding="utf-8")
    (reports/(wid+".json")).write_text(json.dumps({
        "worker_id":wid,"inference_status":"model_completed","os_process_pid":1234,
        "completed_at_utc":"2026-11-13T18:40:00+00:00",
        "activation_evidence":{"unique_os_pid":1234},
        "cognitive_checkpoint":{"coin":"BTC","source_url":"https://example.com/payer",
           "next_action":"Verify offered compensation and eligibility",
           "critic_status":"model_completed","public_source_status":"source_checked"}
    }),encoding="utf-8")
    call("agent_state_aggregate.py",here)
    state=json.loads((here/"agent-state"/"latest.json").read_text(encoding="utf-8"))
    verify("real_checkpoint_aggregation",state["new_finished_worker_checkpoints"]==1
           and state["stored_distinct_worker_checkpoints"]==1)
    verify("memory_does_not_fake_continuous_agent",state["continuous_live_agents_claimed"] is False
           and state["workers"][wid]["currently_running"] is False)

print("B_RELIABILITY_TESTS",json.dumps({
    "passed":len(TESTS),"failed":0,"tests":TESTS
},ensure_ascii=False))
