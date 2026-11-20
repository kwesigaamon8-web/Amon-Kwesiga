"""Full tracked-repository forensic inspection of hierarchy, owner-order routes,
workflow execution gates, prompt integrity and figures. Read-only.

A role count, configured instruction, hashed prompt or green validation must
NEVER be mistaken for real model comprehension or completed customer work.
"""
from __future__ import annotations
import argparse
import ast
import collections
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path.cwd()
CODE=ROOT/"crypto-agents"
OUT=ROOT/"hierarchy-forensic-evidence"
EXPECTED_VIRTUAL=11_255_658_980_400
EXPECTED_ORIGINAL=750_377_265_360

def read_json(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def sha(s):
    return hashlib.sha256(str(s).encode("utf-8")).hexdigest()

def tracked():
    return [p for p in subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0") if p]

def main():
    import yaml
    sys.path.insert(0,str(CODE))
    from directive_cascade import read_owner,prompt_for_global_leaf,execution_receipt
    from enigma_universal_owner_order import GRAND_TOTAL, TOTAL_ROLES, PER_ROOT, divisions, recipient, envelope
    from b_registered_account_worker_map import ROLES_PER_ACCOUNT,role_at_global_index
    from directive_understanding_gate import self_test as grade_selftest,grade
    from b_certified_agent_service_router import PER_DIRECTOR,OFFSETS

    now=datetime.now(timezone.utc).isoformat()
    files=tracked()
    by_extension=collections.Counter((Path(p).suffix.lower() or "none") for p in files)
    sizes={}
    missing=[]
    for p in files:
        q=ROOT/p
        if q.is_file():sizes[p]=q.stat().st_size
        else:missing.append(p)

    # Full source inventory: compile EVERY tracked Python source; parse EVERY
    # tracked JSON including large ledgers and EVERY workflow YAML via BaseLoader.
    py=[p for p in files if p.endswith(".py")]
    js=[p for p in files if p.endswith(".json")]
    workflows=[p for p in files if p.startswith(".github/workflows/") and p.endswith((".yml",".yaml"))]
    markdown=[p for p in files if p.endswith(".md")]
    py_fail=[]
    for p in py:
        try:
            ast.parse((ROOT/p).read_text(encoding="utf-8-sig"),filename=p)
        except Exception as exc:
            py_fail.append({"path":p,"error":type(exc).__name__,"detail":str(exc)[:180]})
    json_fail=[]
    for p in js:
        try:read_json(p)
        except Exception as exc:
            json_fail.append({"path":p,"error":type(exc).__name__,"detail":str(exc)[:180]})
    workflow_fail=[]
    wf_rows=[]
    for p in workflows:
        try:
            doc=yaml.load((ROOT/p).read_text(encoding="utf-8"),Loader=yaml.BaseLoader)
            if not isinstance(doc,dict):raise ValueError("workflow_root_not_mapping")
            jobs=doc.get("jobs") or {}
            if not isinstance(jobs,dict):raise ValueError("jobs_not_mapping")
            triggers=doc.get("on") or {}
            if isinstance(triggers,str):triggers={triggers:{}}
            elif isinstance(triggers,list):triggers={x:{} for x in triggers}
            if not isinstance(triggers,dict):triggers={}
            conditions={key:str(value.get("if","")) for key,value in jobs.items() if isinstance(value,dict)}
            skip_gate=" ".join(conditions.values())
            wf_rows.append({
                "path":p,"name":doc.get("name",Path(p).name),
                "job_count":len(jobs),"scheduled":("schedule" in triggers),
                "dispatch":("workflow_dispatch" in triggers),
                "push_trigger":("push" in triggers),
                "workflow_run_trigger":("workflow_run" in triggers),
                "skip_execute_on_push":("github.event_name != 'push'" in skip_gate or
                                        "github.event_name != \"push\"" in skip_gate),
                "execute_job_defined":("execute" in jobs),
                "execute_job_if":conditions.get("execute","")[:180],
            })
        except Exception as exc:
            workflow_fail.append({"path":p,"error":type(exc).__name__,"detail":str(exc)[:180]})

    owner=read_owner()
    chief=read_json("crypto-agents/chief_D_owner_orders.json")
    public=read_json("crypto-agents/PUBLIC_AGENT_COMMAND.json")
    legacy=read_json("crypto-agents/owner_orders.json")
    hierarchy=read_json("crypto-agents/company_hierarchy.json")
    if isinstance(legacy.get("orders"),list):
        old_last=legacy["orders"][-1].get("id")
    else:old_last=None
    consistency={
        "chief_current":chief.get("current_owner_order_id"),
        "chief_last_id":chief["orders"][-1].get("id"),
        "public_current":public.get("command_id"),
        "chief_and_public_exact_instruction_equal":chief["orders"][-1]["instruction"]==public["owner_command"],
        "sha256_owner_instruction":sha(public["owner_command"]),
        "order_registry_current_sha_matches":sha(chief["orders"][-1]["instruction"])==owner["owner_sha256"],
        "chief_order_count":len(chief.get("orders",[])),
        "legacy_owner_order_count":len(legacy.get("orders",[])),
        "legacy_last_order_id":old_last,
        "legacy_order_log_not_synchronized_to_current":old_last!=chief["current_owner_order_id"],
        "public_no_email_constraints":any("EMAIL" in str(v).upper() for v in public.get("hard_constraints",[])),
        "origin_field_claims_human":chief["orders"][-1].get("origin")=="explicit_human_owner_conversation",
        "human_signed_authentication_available":False,
    }
    assert consistency["chief_and_public_exact_instruction_equal"]
    assert consistency["chief_current"]==consistency["chief_last_id"]==consistency["public_current"]

    systems=divisions()
    assert GRAND_TOTAL==EXPECTED_VIRTUAL and TOTAL_ROLES==EXPECTED_ORIGINAL
    assert len(systems)==30 and sum(x["roles"] for x in systems)==GRAND_TOTAL
    assert len(hierarchy["companies"])==10
    assert all(len(x["managers"])==15 and len(x["assistant_ids"])==2 for x in hierarchy["companies"])
    assert all(all(m["worker_count"]==50 for m in x["managers"]) for x in hierarchy["companies"])
    levels={k:int(v) for k,v in PER_DIRECTOR.items()}
    math={
        "original_named_accounts":2,
        "original_roles":EXPECTED_ORIGINAL,
        "original_roles_per_account":ROLES_PER_ACCOUNT,
        "enigma_named_agent_identifiers":14,
        "enigma_root_divisions":28,
        "total_root_divisions":len(systems),
        "roles_per_root":PER_ROOT,
        "total_virtual_role_namespace":GRAND_TOTAL,
        "directors_per_root":10,
        "managers_per_director":15,
        "workers_per_manager":50,
        "assistants_per_director":2,
        "total_director_slots":30*10,
        "total_assistant_slots":30*10*2,
        "total_manager_slots":30*10*15,
        "total_first_tier_W_slots":30*10*15*50,
        "per_director_tier_role_counts":levels,
        "per_director_tier_role_sum":sum(levels.values()),
        "company_hierarchy_managers_per_company_is_a_misleading_field_name":True,
        "all_numbers_are_configured_capacity_not_activations":True,
    }
    assert sum(levels.values())*20==EXPECTED_ORIGINAL

    # Verify root-level addressability and direct parent paths at START/MID/END
    # for all 30 divisions; demand actual complete prompts, not only IDs.
    bad_routes=[]
    samples=[]
    for root in range(30):
        for location,label in ((0,"first"),(PER_ROOT//2,"middle"),(PER_ROOT-1,"last_H")):
            index=root*PER_ROOT+location
            try:
                info=recipient(index)
                env=envelope(index)
                pack=prompt_for_global_leaf(index,"Review a permitted original client request, or report a source blocker")
                receipt=execution_receipt(pack)
                full=info["owner_to_worker_path"]
                assert env["owner_order_id"]==consistency["chief_current"]
                assert env["owner_order_sha256"]==consistency["sha256_owner_instruction"]
                assert pack["model_prompt"].count(owner["full_owner_instruction"])==1
                assert pack["model_prompt"].count(owner["standard_prompt"])==1
                assert pack["owner_instruction_sha256"]==sha(owner["full_owner_instruction"])
                assert full[-1]==info["role"] and full[-2]==info["immediate_parent"]
                assert full[:2]==["HUMAN_OWNER","CHIEF_D"]
                assert receipt["model_response_present"] is False
                samples.append({"root":root+1,"position":label,"index":str(index),"leaf":info["role"],
                    "parent":info["immediate_parent"],
                    "order_hash_matched":True,"actual_model_responded":False})
            except Exception as exc:
                bad_routes.append({"root":root+1,"position":label,"error":str(exc)[:200]})
    assert len(samples)==90 and not bad_routes
    fixture=grade_selftest()

    # Detect real gaps and misleading green checks with exact source evidence.
    enigma=next((w for w in wf_rows if w["path"]==".github/workflows/enigma-all-b1b2-systems.yml"),None)
    b1=next((w for w in wf_rows if w["path"]==".github/workflows/real-ai-workers.yml"),None)
    b2=next((w for w in wf_rows if w["path"]==".github/workflows/bountyscoutai-real-ai-workers.yml"),None)
    old_id_refs=[]
    old_owner_pat=re.compile(r'(?<![A-Z])(?:OWNER-20\d{6}-\d{5,6}[A-Z0-9-]*|ORD-\d{3})')
    for p in py:
        raw=(ROOT/p).read_text(encoding="utf-8-sig")
        literals=old_owner_pat.findall(raw)
        if literals and not p.endswith(("owner_order_distribution.py","directive_cascade.py")):
            old_id_refs.append({"path":p,"unique_static_order_literals":len(set(literals)),
                                "examples":sorted(set(literals))[:4]})
    evidence_gaps=[
        {"severity":"CRITICAL","id":"NO_TRILLION_ACTUAL_PROCESSES",
         "finding":"11.25T roles are an invertible address space; actual compute/model instances, subscriptions and credentials are not provisioned at that scale.",
         "impact":"Cannot universally deliver, acknowledge, understand or execute each owner directive."},
        {"severity":"CRITICAL","id":"NO_MANAGER_BY_MANAGER_REAL_DELIVERY",
         "finding":"Role parent ancestry is stored in packets; many intermediate manager/agent roles are virtual and do not independently run and forward messages.",
         "impact":"A H-leaf fetch of GitHub is NOT a genuine chain of parent acknowledgments."},
        {"severity":"HIGH","id":"UNSIGNED_HUMAN_ORIGIN",
         "finding":"Owner authenticity is labelled in a versioned JSON field, but no owner cryptographic signature / signed command token is verified.",
         "impact":"Repo write access can impersonate the human owner unless branch protection and signing controls are added."},
        {"severity":"HIGH","id":"TWO_HISTORICAL_ORDER_REGISTRIES",
         "finding":"Legacy owner_orders.json stays separate from the newer chief_D_owner_orders.json; source code refers to both.",
         "impact":"Workers can ingest old order history and current command via distinct paths unless consistency verified at startup."},
        {"severity":"HIGH","id":"ACK_EQUALS_PARAPHRASE_ONLY",
         "finding":"Textual understanding checks use regex and a caller-provided accepted_task_proof flag; no independent verifier is attached to that flag.",
         "impact":"A green acknowledgement is not independently accepted work or reliable comprehension."},
        {"severity":"HIGH","id":"OLD_EMBEDDED_ORDER_IDS",
         "finding":"Many scripts contain historical hard-coded ORDER/ORD IDs.",
         "impact":"Prompts may spend time following superseded instructions instead of the latest owner's priority."},
        {"severity":"HIGH","id":"ENIGMA_EXECUTION_GATED",
         "finding":"The Enigma workflow execution matrix is deliberately skipped on normal push events; validation and consolidation can succeed alone.",
         "impact":"Order updates do not automatically invoke the 28 actual Enigma model processes."},
        {"severity":"HIGH","id":"PLATFORM_ACCESS_ABSENT",
         "finding":"Social media/account/marketplace credentials and authenticated authorized account capabilities are not provisioned for virtual roles.",
         "impact":"Instruction can be assigned but social searches or buyer outreach cannot be executed by all workers."},
        {"severity":"MEDIUM","id":"COUNTING_LABEL_CONFUSION",
         "finding":"company_hierarchy.json says managers_per_company=15, although it defines 15 managers for EACH of 10 directors.",
         "impact":"Ambiguous terminology can misrepresent total manager and worker counts."},
        {"severity":"MEDIUM","id":"NO_END_TO_END_COMMERCIAL_PROOF",
         "finding":"A model or Python process result and a public search candidate do not prove an external buyer accepted work or paid.",
         "impact":"Revenue outcome must be shown separately from model inference, leads and code success."},
    ]
    # Do not misrepresent scan/fixture results as real AI work.
    results={
        "schema":"B1B2_COMPREHENSIVE_HIERARCHY_FORENSIC_V1",
        "audited_utc":now,"head_commit":subprocess.check_output(["git","rev-parse","HEAD"]).decode().strip(),
        "scope":{"tracked_files_total":len(files),"source_bytes_scanned":sum(sizes.values()),
                "python_files_parsed":len(py),"json_files_parsed":len(js),
                "markdown_files_in_inventory":len(markdown),
                "github_action_workflows_yaml_parsed":len(workflows),
                "python_syntax_errors":py_fail,"json_parse_errors":json_fail,
                "workflow_yaml_parse_errors":workflow_fail,
                "missing_tracked_files":missing,
                "files_by_extension":dict(by_extension)},
        "owner_command_consistency":consistency,
        "hierarchy_figures":math,
        "root_path_and_prompt_integrity":{
            "root_divisions_mathematically_covered":30,
            "real_root_processes_launched_by_THIS_STATIC_AUDIT":0,
            "original_middle_and_H_address_paths_checked":len(samples),
            "route_failures":bad_routes,
            "sample_records":samples},
        "comprehension_gate":{
            "synthetic_positive_negative_fixture_cases":fixture,
            "real_models_invoked_in_this_audit":0,
            "all_virtual_role_comprehensions_verified":False,
            "cannot_certify_any_11T_independent_acknowledgements":True},
        "workflow_controls":{
            "workflow_files":len(wf_rows),
            "schedule_workflows":sum(x["scheduled"] for x in wf_rows),
            "push_workflows":sum(x["push_trigger"] for x in wf_rows),
            "workflow_dispatch_workflows":sum(x["dispatch"] for x in wf_rows),
            "workflows_with_execute_job_gated_on_normal_push":[x["path"] for x in wf_rows if x["skip_execute_on_push"]],
            "Enigma":enigma,"B1_original_models":b1,"B2_original_models":b2,
            "workflow_details":wf_rows},
        "legacy_order_reference_inventory":old_id_refs,
        "risk_register":evidence_gaps,
        "truth_boundary":{
            "all_virtual_positions_reached":False,
            "every_manager_independently_accepted_command":False,
            "every_worker_actual_model_inference":False,
            "every_worker_proved_owner_comprehension":False,
            "each_worker_performed_a_paid_task":False,
            "new_paid_customers_or_crypto_receipts_verified_by_this_audit":0,
            "github_order_versioning_works_for_checked_paths":True,
        },
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"COMPLETE_FORENSIC_RESULTS.json").write_text(
        json.dumps(results,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    rows=[
        "# B1/B2/Chief D — Comprehensive hierarchy forensic audit",
        "",f"Repository head: \`{results['head_commit']}\`; audit date: {now}.",
        "", "## Evidence inventory",
        "| Source | Count | Result |","|---|---:|---|",
        f"| Tracked repository files | {len(files)} | Each path catalogued |",
        f"| Python source files | {len(py)} | AST parsed: {len(py)-len(py_fail)} valid, {len(py_fail)} failures |",
        f"| JSON files | {len(js)} | Parsed: {len(js)-len(json_fail)} valid, {len(json_fail)} failures |",
        f"| GitHub Actions workflows | {len(workflows)} | YAML parsed: {len(workflows)-len(workflow_fail)} valid, {len(workflow_fail)} failures |",
        f"| Markdown documents | {len(markdown)} | Inventoried, NOT all semantically reviewed |",
        f"| Mathematically distinct root divisions | 30 | 90 root boundary/mid/leaf paths validated |",
        f"| Comprehension grade fixtures | {fixture['cases_passed']} | Synthetic only; real model calls 0 |",
        "",
        "## Exact hierarchy figures",
        "| Metric | Configured value |", "|---|---:|",
    ]
    for key in ("original_named_accounts","enigma_named_agent_identifiers","total_root_divisions",
                "directors_per_root","managers_per_director","workers_per_manager",
                "total_director_slots","total_assistant_slots","total_manager_slots",
                "total_first_tier_W_slots","total_virtual_role_namespace"):
        rows.append(f"| {key.replace('_',' ')} | {math[key]:,} |")
    rows+=["",
        "**Counting note:** All counts are role allocations; real runtime must be measured independently.",
        f"**Canonical owner directive:** \`{consistency['chief_current']}\`",
        f"**Exact current instruction SHA-256:** \`{consistency['sha256_owner_instruction']}\`",
        "",
        "## Critical controls and problems"]
    for x in evidence_gaps:
        rows.append(f"- **{x['severity']} — {x['id']}:** {x['finding']} **Consequence:** {x['impact']}")
    rows+=["","## Correct implementation plan (in execution order)",
        "1. **Single authenticated order ingress:** approve one exact human instruction, version it, add owner signature or stronger repository write protections, and reject unauthorized/stale changes.",
        "2. **One canonical immutable command envelope:** include exact order ID, original message digest, full safety constraints, version, target role and parent, scoped task, deadline, acceptance tests and authorized tool capabilities.",
        "3. **Real-worker registry:** distinguish CONFIGURED from PROVISIONED/RUNNING. Record real compute runtime, actual API credentials/grants, model ID and expiration. Do not call a virtual address a live worker.",
        "4. **Durable task delivery:** use a persistent queue (one parent-to-child message with message ID and lease) for each REAL worker only; each hop checks hash, signs its acknowledgement and retries with backoff, timeout and a dead-letter queue.",
        "5. **Active understanding gate:** each actual AI model paraphrases the latest order, reports its parent, applies it to a novel safety challenge, and produces an original evidence-backed task; supervisor grades independently. Inadequate answers → REINSTRUCT_AND_RETEST.",
        "6. **Task execution and account permissions:** every real worker has an available lawful tool/source, produces a reproducible output, preserves buyer/finance provenance, and respects no-email, no-spend, no-spam and platform rules.",
        "7. **Recursive supervisor receipt:** parent validates child process/task completion and sends a signed summary upward; Chiefs report separate totals for sent, delivered, acknowledged, comprehended, executed, accepted, and paid.",
        "8. **Roll out by observed capacity:** first prove 1 H worker, 30 roots, 300 directors, 4,500 managers, and practical resource-bounded batches; only scale after real independent receipts and compute/accounts exist. Trillions of live processes are not currently feasible.",
        "9. **Continuous regression and forensic alert:** run static repository audit on every order change, dynamic sampled delivery tests, and alert on stale SHA, missing real model response, execution-skip gates, disallowed external actions or unverifiable payment claims.",
        "",
        "## Verdict",
        "**NOT VERIFIED:** every one of the 11,255,658,980,400 virtual positions independently receiving, understanding and executing all orders. The current system has verifiable on-demand addressing, finite Python/model executions, and partial order delivery controls. That is not an all-worker online broadcast network.",
        "",
        "Machine-readable details: COMPLETE_FORENSIC_RESULTS.json; includes all tracked file counts, parse exceptions, each workflow classification, code-literal inventory and 90 role route samples."]
    (OUT/"REPORT.md").write_text("\n".join(rows)+"\n",encoding="utf-8")
    print("COMPREHENSIVE_FORENSIC_SUMMARY "+json.dumps({
        "tracked_files":len(files),"python_files":len(py),"json_files":len(js),
        "workflow_files":len(workflows),
        "python_syntax_errors":len(py_fail),"json_errors":len(json_fail),
        "yaml_errors":len(workflow_fail),"root_paths_tested":len(samples),
        "canonical_order_sha":consistency["sha256_owner_instruction"],
        "legacy_order_last_id":old_last,
        "virtual_roles":GRAND_TOTAL,
        "live_11T_verified":False,
        "enigma_execute_skipped_on_normal_push":bool(enigma and enigma["skip_execute_on_push"])
    },sort_keys=True))
    # The script provides an audit even when old unrelated sources fail syntax.
    return 0 if not bad_routes and not workflow_fail and not json_fail else 1

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--run",action="store_true")
    x=p.parse_args()
    if not x.run:p.error("Use --run")
    sys.exit(main())
