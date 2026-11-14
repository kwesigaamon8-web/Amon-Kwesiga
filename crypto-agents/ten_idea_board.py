"""One Chief D view of the 10-idea exercise assignment across both boards.

This is an immediately actionable *assignment* for 20 company-local director
roles, not 200 separate model-generated brainstorms. Actual worker model
brainstorming appears later in independently logged daily process artifacts.
"""
from __future__ import annotations
import json
from datetime import datetime,timezone
from pathlib import Path
from ten_ideas_exercise import role_menu,self_test

R=Path("crypto-agents")
OUT=Path("chief-D-reports")
OUT.mkdir(exist_ok=True)
cfg=json.loads((R/"b_collection_assignments.json").read_text(encoding="utf-8"))
owner=json.loads((R/"chief_D_owner_orders.json").read_text(encoding="utf-8"))
assert owner["current_owner_order_id"]=="OWNER-20261114-075553"
assert self_test()["status"]=="PASS"
report={
 "as_of_utc":datetime.now(timezone.utc).isoformat(),
 "chief_director":"D",
 "owner_order":"OWNER-20261114-075553",
 "scope":"Two independent companies, ten actual director role definitions each, one Chief D",
 "director_exercise_assignments":{},
 "director_models_which_independently_proposed_10_ideas_in_this_job":0,
 "active_workers_independently_proposing_ten_in_this_job":0,
 "actual_payable_jobs_confirmed_in_this_job":0,
 "on_chain_crypto_receipts_confirmed_in_this_job":0,
 "definitions_are_not_executing_models":True,
}
for fleet in ("transferexperiment","BountyScoutAI"):
    board=cfg["hierarchy"]["companies"][fleet]
    for director in board["local_director_ids"]:
        local=director.split("/")[-1]
        specialty=("Independently verify accepted unpaid customer payments"
                   if local=="D10" else "Find and deliver source-confirmed lawful crypto-paid work")
        m=role_menu(fleet,local,"D",specialty)
        report["director_exercise_assignments"][director]={
            "company_wallet":cfg["fleets"][fleet]["address"],
            "direct_parent":"D",
            "idea_options":m["candidate_ideas"],
            "distinct_idea_options_assigned":m["count"],
            "requested_model_generated_ideas":"10 per future ACTUALLY executing B worker",
            "director_AI_model_completed":"NOT_EVIDENCED",
            "director_follow_up":"Validate top opportunity with genuine sponsor and payout rules, reject nonpayable schemes; present useful work plan to Chief D.",
            "payment_recovery_boundary":"Only original sponsor acceptance and proof of payment due may go to local D10.",
        }
assert len(report["director_exercise_assignments"])==20
assert all(x["distinct_idea_options_assigned"]==10 for x in report["director_exercise_assignments"].values())
(OUT/"CHIEF_D_TEN_IDEA_BOARD.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
lines=["# Chief D — ten-idea exercise for both B companies","",
    "Order: "+report["owner_order"],
    "",
    "**Two independent companies; 20 separate company director role assignments × 10 = 200 assigned testable idea hypotheses.**",
    "**AI-generated ten-idea replies confirmed by this script: 0.**",
    "**New paid contracts confirmed: 0; new cryptocurrency deposits verified: 0.**",
    "Assignments are evidence-gated research possibilities, NOT completed work.",
    ""]
for fleet in ("transferexperiment","BountyScoutAI"):
    lines+=["## "+fleet]
    for director in cfg["hierarchy"]["companies"][fleet]["local_director_ids"]:
        m=report["director_exercise_assignments"][director]
        titles=", ".join(x["idea_title"] for x in m["idea_options"][:3])
        lines.append("- "+director+": 10 options assigned; initial research angles: "+titles)
    lines.append("")
lines+=["## Chief D's evaluation rule",
    "When an actual B worker's model runs, require ten numbered DISTINCT ideas; verify payer, deliverable, accepted terms, eligibility and correct-network address before claiming a real earning.",
    "D01–D09 scout and implement legitimate paid work, each company's D10 checks only its own accepted/unpaid receivables.",
    "Shared public evidence may circulate across companies; no wallet keys, password, confidential client data or invented miner contact."]
(OUT/"CHIEF_D_TEN_IDEA_BOARD.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("CHIEF_D_TEN_IDEA_BOARD",json.dumps({
 "boards":2,
 "separate_director_roles":20,
 "distinct_menu_ideas_per_director":10,
 "total_idea_assignments":200,
 "actual_independent_B_model_ten_idea_responses":0,
 "confirmed_new_earnings":0
}))
