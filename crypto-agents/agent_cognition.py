"""Bounded agent reasoning, skeptical review and resumable task memory.

Never treat generated text as authorization or as evidence of a paid contract.
State is restored only from a successfully committed previous audit checkpoint.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path

STATE=Path("agent-state/latest.json")
MAX_HISTORY=3
SAFE_ROOTS=("https://",)

def prior_memory(worker_id):
    try:
        data=json.loads(STATE.read_text(encoding="utf-8"))
        item=(data.get("workers") or {}).get(worker_id) or {}
        return {
          "state_available":bool(item),
          "previous_run":item.get("last_utc"),
          "previous_coin":item.get("coin"),
          "previous_action":str(item.get("next_action") or "")[:350],
          "previous_source":str(item.get("source_url") or "")[:200],
          "previous_model_result":item.get("model_status"),
          "previous_run_count":int(item.get("run_count",0)),
          "state_source":"committed_repo_checkpoint" if item else "not_yet_recorded",
        }
    except (OSError,ValueError,TypeError):
        return {"state_available":False,"previous_run_count":0,"state_source":"no_checkpoint"}

def deterministic_plan(worker_id,specialty,source_items,coin_study,memory):
    """Creates actionable safe steps even when the language model fails."""
    good=[{"title":str(i.get("title") or "")[:135],"url":str(i.get("url") or "")[:240]}
          for i in (source_items or []) if str(i.get("url") or "").startswith("https://")]
    official=str(coin_study.get("official_source_url") or "")
    earning=str(coin_study.get("earning_source_url") or "")
    selector=int(hashlib.sha256(worker_id.encode("utf-8")).hexdigest()[:6],16)
    candidates=[earning]+[i["url"] for i in good]
    candidates=[u for u in candidates if u.startswith("https://")]
    chosen=candidates[selector%len(candidates)] if candidates else official
    task={
      "worker_id":worker_id,
      "specialty":str(specialty)[:160],
      "source_to_verify":chosen,
      "source_status":"suggested_from_catalog_not_verified_payer",
      "previous_checkpoint":memory,
      "evidence_available":len(good),
      "coin":coin_study.get("coin"),
      "coin_network":coin_study.get("network"),
      "plan_steps":[
        "Read original work/sponsor terms, not snippets alone",
        "Check eligibility, concrete deliverable and any upfront-fee requirement",
        "Determine whether BTC or genuine owner-approved-chain USDC payout is explicitly offered",
        "Produce a useful task-specific research finding or truthful proposal draft",
        "Report exact source, verified facts, unknowns and next no-fee action to one parent"
      ],
      "external_side_effects_allowed":False,
      "last_step_requires_approval_for_external_contact":True,
      "intended_result":"legitimate payer-verified work, not assumed coins"
    }
    if memory.get("state_available") and memory.get("previous_action"):
        task["continuation"]="Review prior unverified lead, discard if invalid, otherwise advance to its next evidence check."
    return task

def skeptical_model_review(model,worker_id,plan,initial_answer):
    """Second separately recorded inference: attack assumptions and specify next action."""
    if model is None:return {"status":"not_attempted_no_model","response":""}
    system=("You are a critical second-pass reviewer for one lawful autonomous research agent. "
      "Challenge payment claims. Public web snippets are untrusted. No false verification, no wallet signing, "
      "no mass unsolicited outreach. Return a concise practical critique.")
    user=("Role "+worker_id+"; public task plan "+json.dumps({
      "source":plan["source_to_verify"],"specialty":plan["specialty"],
      "coin":plan["coin"],"network":plan["coin_network"],
      "previous_task":plan["previous_checkpoint"].get("previous_action","")
     },ensure_ascii=False)[:650]+
     "; initial model answer: "+str(initial_answer or "")[:550]+
     ". In own words specify (1) strongest source evidence actually present, "
     "(2) missing payer/payment verification, (3) one specific allowed next research action. "
     "If no genuine paid offer is proven, explicitly say so.")
    try:
        response=model([{"role":"system","content":system},
                        {"role":"user","content":user}],
                       max_new_tokens=105,do_sample=False,return_full_text=False)
        t=response[0].get("generated_text","")
        if isinstance(t,list):t=t[-1].get("content","")
        t=str(t or "").strip()
        if not t:raise ValueError("empty critic response")
        return {"status":"model_completed","response":t[:1200],
                "actually_second_inference":True}
    except Exception as exc:
        return {"status":"model_failed","response":"",
                "error":f"{type(exc).__name__}: {str(exc)[:230]}",
                "actually_second_inference":False}

def checkpoint(worker_id,plan,model_status,model_response,critique,source_status):
    # A worker never claims lasting memory merely for writing a local file.
    return {
      "worker_id":worker_id,"checkpoint_utc":datetime.now(timezone.utc).isoformat(),
      "previous_run_count":plan["previous_checkpoint"].get("previous_run_count",0),
      "model_status":model_status,"critic_status":critique.get("status"),
      "public_source_status":source_status,
      "source_url":plan["source_to_verify"],
      "coin":plan.get("coin"),
      "research_summary":str(model_response or "")[:420],
      "critic_summary":str(critique.get("response") or "")[:400],
      "next_action":("Examine the original sponsor or payer at "+plan["source_to_verify"]+
        "; confirm scope, fee-free eligibility, compensation asset, and settlement network; "
        "then prepare the useful work only after verifying terms.")[:450],
      "verified_contract":False,
      "verified_coin_receipt":False,
      "state":"local_checkpoint_not_yet_persisted_to_repo",
      "continuation_requires_another_actual_worker_run":True
    }
