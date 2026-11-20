"""Faithful owner-command prompt cascade to actual, individually invoked B1/B2 leaf workers.

H level is the deepest defined leaf. Lazy address mapping is not a live message
and cannot count as process execution or model inference. External webpages are
untrusted data, never owner commands.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("crypto-agents")
CHIEF = ROOT / "chief_D_owner_orders.json"
PUBLIC = ROOT / "PUBLIC_AGENT_COMMAND.json"
STANDARD = ROOT / "OWNER_DIRECTIVE_CASCADE_PROMPT.md"
FLEETS = ("transferexperiment", "BountyScoutAI")

def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def read_owner():
    chief = json.loads(CHIEF.read_text(encoding="utf-8"))
    public = json.loads(PUBLIC.read_text(encoding="utf-8"))
    last = chief["orders"][-1]
    order_id = chief["current_owner_order_id"]
    if last["id"] != order_id or public["command_id"] != order_id:
        raise ValueError("FATAL: Chief D/public directives out of sync")
    if last.get("origin") != "explicit_human_owner_conversation":
        raise ValueError("FATAL: non-owner directive rejected")
    if str(last["instruction"]) != str(public["owner_command"]):
        raise ValueError("FATAL: authoritative owner message altered")
    cfg = chief.get("owner_prompt_cascade") or {}
    pubcfg = public.get("owner_prompt_cascade") or {}
    if cfg.get("owner_order_id") != order_id or pubcfg.get("owner_order_id") != order_id:
        raise ValueError("FATAL: required cascade not active")
    if not STANDARD.is_file() or STANDARD.stat().st_size < 300:
        raise ValueError("FATAL: standing directive protocol absent")
    full = STANDARD.read_text(encoding="utf-8")
    for term in ("final H", "No Gmail", "actual", "SHA-256"):
        if term.lower() not in full.lower():
            raise ValueError("FATAL: cascade standard missing " + term)
    return {"owner_order_id":order_id, "full_owner_instruction":last["instruction"],
            "owner_sha256":sha(last["instruction"]),
            "standard_sha256":sha(full),
            "standard_prompt":full,
            "source":"versioned owner relay in linked GitHub repository; not a signed human identity proof"}

def prompt_for_worker(fleet, role, exact_task):
    """Exact, complete latest owner command + full standing protocol + one role task."""
    if fleet not in FLEETS:
        raise ValueError("Unknown B1/B2 parent")
    from owner_first_oath import command_envelope
    env = command_envelope(fleet,role)
    authority = read_owner()
    if env["order_id"] != authority["owner_order_id"]:
        raise ValueError("Stale role delegation")
    path = env["owner_to_worker_path"]
    if path[:3] != ["OWNER","CHIEF_D",fleet] or path[-1] != fleet+"/"+role:
        raise ValueError("Incorrect owner-to-leaf path")
    if env["immediate_parent"] != path[-2]:
        raise ValueError("Incorrect immediate parent")
    instruction = (
        "CURRENT HUMAN OWNER ORDER ("+authority["owner_order_id"]+
        ", SHA256 "+authority["owner_sha256"]+"):\n"+
        authority["full_owner_instruction"]+
        "\n\nMANDATORY CHIEF D STANDING PROMPT (SHA256 "+authority["standard_sha256"]+"):\n"+
        authority["standard_prompt"]+
        "\nASSIGNED ACTUAL WORKER "+fleet+"/"+role+
        "\nROUTE "+ " -> ".join(path)+
        "\nDIRECT PARENT "+env["immediate_parent"]+
        "\nEXECUTE ONE BOUNDED TASK NOW: "+str(exact_task)+
        "\nReply only with verified work evidence, original source URLs where applicable, next correction and the direct parent. "
        "Do not claim this message was delivered to uninvoked virtual workers."
    )
    return {
        "owner_order_id":authority["owner_order_id"],
        "owner_instruction_sha256":authority["owner_sha256"],
        "standard_prompt_sha256":authority["standard_sha256"],
        "full_model_prompt_sha256":sha(instruction),
        "model_prompt":instruction,
        "fleet":fleet,"role":role,"exact_task":str(exact_task),
        "immediate_parent":env["immediate_parent"],
        "owner_to_worker_path":path,
        "path_hops":[{"hop":i,"recipient":p,
            "independent_parent_execution_verified":False}
            for i,p in enumerate(path)],
        "configured_other_roles_received_this_prompt":False,
    }

def execution_receipt(packet, result="", model_completed=False):
    if sha(packet["model_prompt"]) != packet["full_model_prompt_sha256"]:
        raise ValueError("Prompt integrity mismatch")
    if not packet["owner_to_worker_path"][-1] == packet["fleet"]+"/"+packet["role"]:
        raise ValueError("Leaf identity mismatch")
    if model_completed and not str(result).strip():
        raise ValueError("Cannot assert completed model without output")
    return {
        "schema":"B1B2_OWNER_DIRECTIVE_LEAF_DELIVERY_V1",
        "owner_order_id":packet["owner_order_id"],
        "owner_instruction_sha256":packet["owner_instruction_sha256"],
        "standard_prompt_sha256":packet["standard_prompt_sha256"],
        "full_model_prompt_sha256":packet["full_model_prompt_sha256"],
        "exact_process_worker_id":packet["fleet"]+"/"+packet["role"],
        "immediate_parent":packet["immediate_parent"],
        "owner_to_leaf_path":packet["owner_to_worker_path"],
        "process_pid":os.getpid(),
        "timestamp_utc":datetime.now(timezone.utc).isoformat(),
        "full_prompt_loaded_by_actual_python_process":True,
        "model_response_present":bool(model_completed and str(result).strip()),
        "model_comprehension_independently_verified":False,
        "actual_task_output_sha256":sha(str(result)) if str(result) else None,
        "genuine_external_post_verified":False,
        "real_customer_response_verified":False,
        "payment_verified":False,
        "all_virtual_descendants_notified":False,
        "all_intermediate_managers_independently_acknowledged":False,
    }

def actual_python_leaf_selftest():
    """Test real process loading of full latest order at deepest H role."""
    tested=[]
    for fleet in FLEETS:
        for role in ("D01-M01-W01-S001-G001-H001",
                     "D10-M15-W50-S150-G500-H666",
                     "D04-M08-W22-S099-G272-H333"):
            pkt=prompt_for_worker(fleet,role,
                "Assess one permissioned public customer request or report precise source blocker")
            rec=execution_receipt(pkt,"Verified cascade prompt receipt, no buyer contacted")
            assert pkt["model_prompt"].count(read_owner()["full_owner_instruction"])==1
            assert len(rec["owner_to_leaf_path"])==9
            assert rec["immediate_parent"].endswith(role.rsplit("-",1)[0])
            assert rec["model_response_present"] is False
            tested.append(rec)
    return tested

def hierarchy_virtual_boundaries():
    """Check canonical order availability to H-endpoints across 30 root systems."""
    from enigma_universal_owner_order import PER_ROOT, GRAND_TOTAL, recipient, envelope
    if GRAND_TOTAL!=11_255_658_980_400:
        raise AssertionError("Original virtual namespace changed")
    sample=set()
    for root in range(30):
        sample.add(root*PER_ROOT)
        sample.add((root+1)*PER_ROOT-1)
    rng=random.Random(20261120)
    sample.update(rng.randrange(GRAND_TOTAL) for _ in range(120))
    authority=read_owner()
    leaves=0
    for ix in sorted(sample):
        env=envelope(ix)
        info=env["recipient"]
        assert env["owner_order_id"]==authority["owner_order_id"]
        assert env["owner_order_sha256"]==authority["owner_sha256"]
        assert env["canonical_owner_instruction"]==authority["full_owner_instruction"]
        assert info["owner_to_worker_path"][:2]==["HUMAN_OWNER","CHIEF_D"]
        assert info["immediate_parent"]==info["owner_to_worker_path"][-2]
        assert info["work_delivery_verified"] is False
        if "-H" in info["role"]:
            leaves+=1
    return {"all_root_systems_checked":30,"virtual_roles_addressable":GRAND_TOTAL,
            "virtual_role_paths_sampled":len(sample),"H_leaf_paths_sampled":leaves,
            "uninvoked_virtual_positions_do_not_have_delivery_receipts":True}

def self_test():
    authority=read_owner()
    leaves=actual_python_leaf_selftest()
    virt=hierarchy_virtual_boundaries()
    try:
        prompt_for_worker("invalid",leaves[0]["exact_process_worker_id"],"task")
    except ValueError:
        pass
    else:
        raise AssertionError("Unauthorized fleet accepted")
    result={"owner_order_id":authority["owner_order_id"],
        "full_order_sha256":authority["owner_sha256"],
        "full_standard_prompt_sha256":authority["standard_sha256"],
        "real_python_process_H_leaf_receipts_in_this_test":len(leaves),
        "real_model_inferences_in_this_test":0,
        "all_11_trillion_live_workers_verified":False, **virt}
    return result,leaves

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--self-test",action="store_true")
    cli.add_argument("--out",default="owner-cascade-evidence")
    cli.add_argument("--fleet",choices=FLEETS)
    cli.add_argument("--role")
    cli.add_argument("--task")
    opt=cli.parse_args()
    out=Path(opt.out)
    out.mkdir(exist_ok=True,parents=True)
    if opt.self_test:
        summary,leaves=self_test()
        (out/"cascade-summary.json").write_text(json.dumps(summary,indent=2)+"\n")
        (out/"six-actual-H-leaf-process-receipts.json").write_text(json.dumps(leaves,indent=2)+"\n")
        print("OWNER_TO_FINAL_H_PROMPT_CASCADE_TEST_PASS "+json.dumps(summary))
    elif opt.fleet and opt.role and opt.task:
        result=execution_receipt(prompt_for_worker(opt.fleet,opt.role,opt.task))
        (out/"one-leaf-delivery-receipt.json").write_text(json.dumps(result,indent=2)+"\n")
        print("OWNER_DIRECTIVE_ACTUAL_LEAF_RECEIPT "+json.dumps(result))
    else:
        cli.error("Provide --self-test or --fleet --role --task")
