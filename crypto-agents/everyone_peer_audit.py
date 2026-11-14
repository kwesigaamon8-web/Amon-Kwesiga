"""100% deterministic, reciprocal checks of all ACTUALLY invoked workers.

Compares each real attempted worker report with every *other* attempted
worker report in the SAME company. This does NOT claim that one model
understood or reviewed another model's work. The engine performs the
pairwise comparisons; independent model peer reviews need separately
verified inference evidence. No client secrets or wallets are transferred.
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter,defaultdict
from datetime import datetime, timezone
from pathlib import Path

FLEET=os.environ.get("WORKFORCE_ID","")
assert FLEET in ("transferexperiment","BountyScoutAI")
SOURCE=Path("strict-worker-accountability")/("strict-"+FLEET+".json")
R=json.loads(SOURCE.read_text(encoding="utf-8"))
OUT=Path("peer-accountability")
OUT.mkdir(exist_ok=True)
rows=[r for r in R["individual_results"] if
      r["id"].startswith(FLEET+"/D") and r["id"].count("-")>=1]
ids=[r["id"] for r in rows]
if len(ids)!=len(set(ids)):
    raise ValueError("Duplicated attempted worker identities; cannot prove reciprocal coverage")
assert all(r.get("director") in [f"D{i:02d}" for i in range(1,11)] for r in rows)
n=len(rows)
assert n<=500, "Audit budget safety: no uncontrolled O(N²) job"
checks=Counter()
supervisors=defaultdict(list)
directors=defaultdict(list)
individual=[]
top_errors=[]

def words(text):
    return set(re.findall(r"[a-z0-9]{3,}",str(text or "").lower()))
def normalized(text):
    return re.sub(r"\s+"," ",str(text or "").lower()).strip()

tokens={r["id"]:words(r.get("independent_model_excerpt","")) for r in rows}
output={r["id"]:normalized(r.get("independent_model_excerpt","")) for r in rows}
for index,r in enumerate(rows):
    id=r["id"]
    p=r.get("parent")
    d=r["director"]
    if p:
        supervisors[p].append(id)
    directors[d].append(id)
    peer_ids=[]
    pair_flags=[]
    for other in rows:
        if other["id"]==id:
            continue
        checks["ordered_pairwise_comparisons"]+=1
        # Public-source similarity is not proof of copied work or payment.
        same_output=bool(output[id] and output[id]==output[other["id"]])
        a,b=tokens[id],tokens[other["id"]]
        score=(len(a&b)/len(a|b)) if a and b else 0
        if same_output:
            checks["identical_response_pairs"]+=1
            pair_flags.append({"with":other["id"],"type":"IDENTICAL_MODEL_TEXT"})
        elif score>=0.90 and min(len(a),len(b))>=15:
            checks["very_similar_response_pairs"]+=1
            if len(pair_flags)<7:
                pair_flags.append({"with":other["id"],"type":"SIMILARITY_REQUIRES_REVIEW"})
        if other.get("source_urls") and r.get("source_urls"):
            if r["source_urls"][0]==other["source_urls"][0]:
                checks["overlapping_first_source_pairs"]+=1
        peer_ids.append(other["id"])
    hard=set(r.get("defects") or [])
    grade=r.get("grade","NOT_QUALIFIED")
    base=100 if grade=="QUALIFIED_SOURCE_BACKED_AI_RESEARCH" else (
        65 if grade=="REVIEW_MODEL_OUTPUT_NOT_SOURCE_BACKED" else 20)
    score=max(0,base-20*any(v["type"]=="IDENTICAL_MODEL_TEXT" for v in pair_flags)
                  -10*any(v["type"]=="SIMILARITY_REQUIRES_REVIEW" for v in pair_flags))
    required_fixes=sorted(hard)
    if any(v["type"]=="IDENTICAL_MODEL_TEXT" for v in pair_flags):
        required_fixes.append("Repeated model response: do fresh independent source research")
    # Only assign a genuine worker as a reviewer if it exists in this run.
    # Assignment != peer review performed.
    proposed_peer=ids[(index+1)%n] if n>=2 else None
    individual.append({
        "actual_worker_id":id,
        "independently_launched_process_status":r["grade"],
        "engine_checks_against_distinct_other_workers":len(peer_ids),
        "automated_pairwise_comparison_completed":True,
        "all_to_all_model_generated_peer_reviews_completed":0,
        "separate_AI_peer_review_status":"NOT_RUN",
        "assigned_peer_reviewer_for_next_authorized_execution":proposed_peer,
        "peer_model_assignment_status":"QUEUED_NOT_EXECUTED" if proposed_peer else "NO_PEER_AVAILABLE",
        "direct_supervisor":p or "UNVERIFIED",
        "director":FLEET+"/"+d,
        "supervisor_verification":"AUTOMATED_EVIDENCE_CHECK_ONLY",
        "supervisor_model_review":"NOT_PROVEN",
        "score_out_of_100":score,
        "distinct_work_result":r["independent_model_excerpt"][:240],
        "checked_external_source_urls":r.get("source_urls",[])[:2],
        "verified_payer_and_payment_status":"NOT_ESTABLISHED",
        "caution_flags":pair_flags[:7],
        "needed_corrections":required_fixes[:10],
        "next_legal_action":r.get("next_action","")[:300],
        "source_visibility":"public_non_sensitive_evidence_only"
    })
    checks["workers_with_pairwise_automated_audits"]+=1
    checks["workers_with_peers_assigned"]+=int(bool(proposed_peer))
    checks["workers_with_any_corrective_action"]+=int(bool(required_fixes))
    if score<70:
        checks["low_scoring_actual_workers"]+=1

director_matrix={}
for i in range(1,11):
    director=f"D{i:02d}"
    direct=directors.get(director,[])
    review_target=f"D{(i%10)+1:02d}"
    director_matrix[FLEET+"/"+director]={
        "actually_attempted_worker_reports":len(direct),
        "own_direct_reports_reviewed_by_deterministic_audit":len(direct),
        "own_direct_reports_all_qualified":all(
            x["score_out_of_100"]>=90 for x in individual if x["director"]==FLEET+"/"+director
        ) if direct else False,
        "assigned_cross_director_to_review":FLEET+"/"+review_target,
        "cross_director_model_review_status":"NOT_EXECUTED_BY_THIS_ENGINE",
        "cross_director_summary_check_status":"ASSIGNMENT_ONLY",
        "followup_needed":sum(
            x["score_out_of_100"]<90 for x in individual if x["director"]==FLEET+"/"+director
        ),
        "reports_to":"D"
    }

management={
    "generated_utc":datetime.now(timezone.utc).isoformat(),
    "owner_order":"OWNER-20261114-072052",
    "information_share_order":"OWNER-20261114-072113",
    "fleet":FLEET,
    "attempted_actual_worker_reports":n,
    "number_of_directors_in_company":10,
    "supervisors_with_actual_worker_results":len(supervisors),
    "total_deterministic_ordered_worker_vs_worker_comparisons":checks["ordered_pairwise_comparisons"],
    "expected_all_to_all_ordered_comparisons":n*(n-1),
    "engine_did_an_automated_check_on_every_distinct_pair":checks["ordered_pairwise_comparisons"]==n*(n-1),
    "actual_separate_model_generated_peer_reviews":0,
    "actual_authenticated_parent_model_reviews":0,
    "per_worker":individual,
    "per_director":director_matrix,
    "supervisor_loads":[{"supervisor":FLEET+"/"+p,"attempted_children":len(x),
                         "automated_child_reviews":len(x),
                         "parent_AI_review_evidenced":False} for p,x in sorted(supervisors.items())],
    "automated_checks":dict(checks),
    "global_chief_director":"D",
    "chief_decision":"Strict model-generated peer and direct-parent reviews remain unverified. Each ACTUALLY attempted output has deterministic cross-check and follow-up; all dormant roles have no artificial review.",
    "external_payments_verified":False,
    "review_limit":"Automated pairwise review tests reported identity, source/response similarity and prior strict grades. It is NOT a completed independent AI peer critique of each other worker's work or factual verification of the payer. No PII, private keys, passwords, private customer files or payments are published.",
}
assert management["engine_did_an_automated_check_on_every_distinct_pair"]
assert len(individual)==n
(OUT/("peer-everyone-"+FLEET+".json")).write_text(
    json.dumps(management,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
lines=[
 "# Everyone audits everyone — "+FLEET,
 "",
 "Report date: "+management["generated_utc"],
 "",
 "**Actual attempted workers with strict audit rows:** "+str(n),
 "**Automated unique ordered worker-to-worker comparisons:** "+f"{checks['ordered_pairwise_comparisons']:,}",
 "**Expected full pairwise checks:** "+f"{n*(n-1):,}",
 "**Workers with distinct-peer review assignment:** "+str(checks["workers_with_peers_assigned"]),
 "**Workers needing correction:** "+str(checks["workers_with_any_corrective_action"]),
 "**Verified actual independent peer-model reviews:** 0 (NOT run by this auditor)",
 "**Director/supervisor assessment:** automated only, no invented executed manager AI review.",
 "",
 "## Every company's director evaluates actual worker evidence",
]
for director,values in director_matrix.items():
    lines.append("- "+director+": "+str(values["actually_attempted_worker_reports"])+
        " attempted workers, "+str(values["followup_needed"])+" with grade below 90; "+
        "other-director peer reviewer assignment "+values["assigned_cross_director_to_review"])
lines += [
 "",
 "## Chief D evaluation",
 "Both independent company directors and all actual workers get deterministic peer evidence checks; subsequent real AI peer critique is explicitly NOT YET EXECUTED unless a separately logged model process later proves it.",
 "Both companies may share public, non-sensitive research and audit lessons freely. Never share credentials, private client information or wallet secrets.",
 "Current payment verified by this audit: NOT ASSESSED. Confirm genuine client acceptance and blockchain transactions separately."
]
(OUT/("peer-everyone-"+FLEET+".md")).write_text("\n".join(lines)+"\n",encoding="utf-8")
print("EVERYONE_PEER_AUDIT",json.dumps({
 "fleet":FLEET,"actual_workers":n,
 "comparisons":checks["ordered_pairwise_comparisons"],
 "coverage":"PASS" if management["engine_did_an_automated_check_on_every_distinct_pair"] else "FAIL",
 "corrective_cases":checks["workers_with_any_corrective_action"],
 "actual_AI_peer_reviews":0,
 "external_payments_verified":"not_assessed"
}))
