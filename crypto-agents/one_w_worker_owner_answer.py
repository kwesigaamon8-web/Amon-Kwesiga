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
    question=(
      "I am the owner. Tell me what you, one W-level worker, can actually do "
      "within a GitHub Actions computer process right now. "
      "You are worker D01-M01-W01, not a director and not a Moltbook agent. "
      "Respond in the FIRST PERSON with 3 brief numbered sentences and one limitation. "
      "Your abilities: inspect publicly available software issues, evaluate whether "
      "paid opportunities are genuine (not guarantee payment), create and test small "
      "original scripts and proposals, save results and evidence, report to D01-M01. "
      "Limitations: you cannot independently use email, post on Moltbook, sign wallets, "
      "guarantee paying customers or claims of received Bitcoin. "
      "Only claim things your single currently running process can perform. "
      "Do not ask me a question. Do not mention billions of active agents."
    )
    error=None
    answer=None
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        torch.set_num_threads(2)
        model_id=os.getenv("ENIGMA_MODEL_ID","Qwen/Qwen2.5-0.5B-Instruct")
        tok=AutoTokenizer.from_pretrained(model_id,trust_remote_code=False)
        model=AutoModelForCausalLM.from_pretrained(model_id,trust_remote_code=False)
        msgs=[
            {"role":"system","content":"You are a bounded software research W-worker answering a direct question from your human owner. Be concise, accurate and never claim unperformed work."},
            {"role":"user","content":question}
        ]
        prompt_ids=tok.apply_chat_template(msgs,tokenize=True,add_generation_prompt=True,return_tensors="pt")
        with torch.no_grad():
            output=model.generate(prompt_ids,max_new_tokens=190,do_sample=False,
                                  pad_token_id=tok.eos_token_id)
        answer=tok.decode(output[0][prompt_ids.shape[-1]:],skip_special_tokens=True).strip()
        if not answer or len(answer)<55:
            raise ValueError("Too little substantive worker response")
    except Exception as ex:
        error="MODEL_EXECUTION_"+type(ex).__name__
        answer=None

    report={
        "worker_id":WORKER_ID,
        "worker_kind":"INDIVIDUAL_W_LEVEL_NOT_AGENT",
        "global_original_role_index":ROLE_GLOBAL_INDEX,
        "reporting_parent":parent,
        "owner_order_id":env["owner_order_id"],
        "owner_order_sha256":env["owner_order_sha256"],
        "asked_by_owner":"Tell me, one W worker, what you can do",
        "os_process_pid":os.getpid(),
        "model_id":os.getenv("ENIGMA_MODEL_ID","Qwen/Qwen2.5-0.5B-Instruct"),
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
