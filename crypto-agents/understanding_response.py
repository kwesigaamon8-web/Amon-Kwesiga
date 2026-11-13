"""Record an actual role's independent understanding reply without fabricating it.

Only evidence from a successful per-role model inference qualifies as a reply.
The heuristic checks are NOT proof of humanlike comprehension or correctness.
"""
import json
import re
from pathlib import Path

BRIEF=json.loads(Path("crypto-agents/professional_owner_context.json").read_text(encoding="utf-8"))

def understanding_report(agent_id, agent_name, parent_id, assigned_role, model_result, evidence_urls=None):
    if not isinstance(model_result,dict):
        model_result={}
    response=str(model_result.get("analysis") or model_result.get("review") or "").strip()[:1200]
    actually_generated=model_result.get("status") in ("model_completed","llm_completed") and len(response)>0
    lower=response.lower()
    has_coin=bool(re.search(r"\b(bitcoin|btc|usdc|crypto(?:currency)?|coins?|wallet|token)\b",lower))
    has_work=bool(re.search(r"\b(task|work|job|lead|client|bount|source|payer|contract|verif|research|check|find|review|deliver)\w*\b",lower))
    evidence=[u for u in (evidence_urls or []) if isinstance(u,str) and u.startswith("https://")][:3]
    if actually_generated and has_coin and has_work:
        status="model_response_contains_key_goal_and_action"
    elif actually_generated:
        status="model_response_recorded_unverified_comprehension"
    else:
        status="missing_or_failed_model_response"
    return {
       "agent_id":agent_id,
       "agent_name":agent_name,
       "reports_only_to":parent_id,
       "assigned_role":str(assigned_role)[:300],
       "professional_context_received":BRIEF["version"],
       "owner_professional_context":"Independent accounting/tax consultant with Commerce degree and CPA studies; bookkeeping, QuickBooks, reconciliations, reporting and spreadsheet skills.",
       "owner_goal":"Legitimate transferable cryptocurrency actually received at owner-approved correct-network address, independently verified.",
       "response_in_own_generated_words":response if actually_generated else "",
       "actual_model_result_status":model_result.get("status","not_run"),
       "understanding_check_status":status,
       "review_required":status!="model_response_contains_key_goal_and_action",
       "source_urls_behind_response":evidence,
       "verified_paid_work":False,
       "verified_received_coins":[],
       "truth_note":"This is the actual recorded text from a per-role model call, not a personal response from a human or separate account. Rule-of-thumb checks can reject weak answers but do not prove full understanding."
    }
