"""Ask exactly one actual B1 W-tier worker what it can do.

A distinct OS job + original free small language-model inference, not a director,
not an agent account, not pretend 11T workers can hear messages.
"""
from __future__ import annotations
import argparse,hashlib,json,os,sys
from datetime import datetime,timezone
from pathlib import Path
from b_certified_agent_service_router import role_index
from enigma_universal_owner_order import envelope

WORKER="D01-M01-W01"
FLEET="transferexperiment"
WORKER_ID=FLEET+"/"+WORKER
ROLE_GLOBAL_INDEX=role_index(FLEET,WORKER)
OUT=Path("one-worker-own-answer")

def packet():
    """Check exact owner-to-W reporting path and one-worker target."""
    env=envelope(ROLE_GLOBAL_INDEX)
    r=env["recipient"]
    assert r["role"]=="ORIGINAL/"+WORKER_ID
    assert r["role"].endswith("-W01")
    assert r["immediate_parent"]=="ORIGINAL/transferexperiment/D01-M01"
    return env

def say(model=None):
    env=packet()
    parent=env["recipient"]["immediate_parent"]
    prompt=(
      "You are not an AI account, an agent, a director or a supervisor. "
      "You are just ONE genuine W-level worker, id "+WORKER_ID+". "
      "The human owner directly orders this worker: SAY WHAT YOU CAN DO. "
      "Answer in your own words, first person, as a specific worker. "
      "Explain five PRACTICAL actions you can do in this bounded GitHub worker shift. "
      "You can evaluate openly available software problems, identify source-backed "
      "potential paid jobs without assuming they pay, draft small original code and "
      "test suggestions, log your evidence, and report through your manager. "
      "Say what you CANNOT do: no personal login, no Gmail/email, no paid buyer "
      "guarantee, no automatic independent web posting or wallet transfer, no "
      "claims of millions of actual workers, real accepted jobs, or BTC earnings. "
      "Your immediate supervisor is "+parent+". "
      "No fake achievements. Avoid claiming you already completed work. "
      "Do not speak for Chief D or any other agents. "
      "Reply clearly, using numbered sentences, beginning 'I am worker D01-M01-W01'. "
      "Your answer:"
    )
    error=None
    if model is None:
        try:
            from transformers import pipeline
            model=pipeline("text-generation",
              model=os.getenv("ENIGMA_MODEL_ID","HuggingFaceTB/SmolLM2-135M-Instruct"),
              device=-1)
        except Exception as ex:
            error="MODEL_LOAD_"+type(ex).__name__
    answer=None
    if model is not None:
        try:
            result=model(prompt,max_new_tokens=235,do_sample=False,return_full_text=False)
            answer=str(result[0].get("generated_text") or "").strip()
            if not answer:raise ValueError("Empty real inference")
        except Exception as ex:
            error="MODEL_EXECUTION_"+type(ex).__name__
    report={
        "worker_id":WORKER_ID,
        "worker_kind":"INDIVIDUAL_W_LEVEL_NOT_AGENT",
        "global_original_role_index":ROLE_GLOBAL_INDEX,
        "reporting_parent":parent,
        "owner_order_id":env["owner_order_id"],
        "owner_order_sha256":env["owner_order_sha256"],
        "asked_by_owner":"Tell me, one W worker, what you can do",
        "os_process_pid":os.getpid(),
        "model_id":os.getenv("ENIGMA_MODEL_ID","HuggingFaceTB/SmolLM2-135M-Instruct"),
        "independent_model_call_completed":bool(answer),
        "raw_worker_answer":answer,
        "model_status":"MODEL_ANSWER_NEEDS_HUMAN_REVIEW" if answer else (error or "NO_RESPONSE"),
        "timestamp_utc":datetime.now(timezone.utc).isoformat(),
        "moltbook_accounts_created":0,"emails_sent":0,"social_posts_sent":0,
        "paid_customers_verified":0,"crypto_receipts_verified":0,
        "other_workers_claimed_active":0,
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"D01-M01-W01.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("WORKER_ID",WORKER_ID)
    print("PARENT",parent)
    print("REAL_MODEL_RESPONSE",bool(answer))
    if answer:
        print("WORKER_DIRECT_ANSWER_BEGIN")
        print(answer)
        print("WORKER_DIRECT_ANSWER_END")
    else:
        print("MODEL_ANSWER_UNAVAILABLE",report["model_status"])
    return report

def self_test():
    env=packet()
    assert env["recipient"]["role"]=="ORIGINAL/transferexperiment/D01-M01-W01"
    assert env["recipient"]["immediate_parent"]=="ORIGINAL/transferexperiment/D01-M01"
    assert env["verified_model_acknowledgement"] is False
    assert "OWNER-" in env["owner_order_id"]
    assert ROLE_GLOBAL_INDEX>=0
    print("ONE_W_WORKER_ROLE_MAPPING_TEST_PASS",WORKER_ID,"not an agent")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--answer",action="store_true")
    a=ap.parse_args()
    if a.self_test:self_test()
    elif a.answer:say()
    else:ap.error("Specify --answer or --self-test")
