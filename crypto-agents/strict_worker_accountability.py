"""Strict evidence audit of each ACTUALLY invoked B worker process.

This does not execute dormant role definitions or imply external cryptocurrency
payments. Qualified independent output requires concrete evidence: a real
completed model, distinct response, direct parent, own source URL or explicit
source failure, and specific next action. All attempted workers get an outcome.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path("combined-ai-processes/ai-process-reports")
OUT=Path("strict-worker-accountability")
OUT.mkdir(exist_ok=True)
FLEET=os.getenv("WORKFORCE_ID","")
assert FLEET in ("transferexperiment","BountyScoutAI")
DIRECTORS=[f"D{i:02d}" for i in range(1,11)]
counts=Counter()
detail=[]
fingerprints={}
seen=set()

def own_evidence(items):
    return [str(x.get("url") or "") for x in items
            if isinstance(x,dict) and str(x.get("url") or "").startswith("https://")]

for director in DIRECTORS:
    manifest_path=ROOT/("manifest-"+director+".json")
    if not manifest_path.exists():
        counts["director_manifests_missing"]+=1
        detail.append({"id":FLEET+"/"+director,"director":director,"grade":"MISSING_DIRECTOR_MANIFEST",
                       "defects":["Director did not deliver process manifest"]})
        continue
    try:
        m=json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError,ValueError) as exc:
        counts["director_manifests_invalid"]+=1
        detail.append({"id":FLEET+"/"+director,"grade":"INVALID_DIRECTOR_MANIFEST",
                       "defects":[type(exc).__name__]})
        continue
    assert m.get("director_id")==director
    if m.get("workforce_namespace")!=FLEET:
        raise ValueError("WORKFORCE MIXUP in director manifest "+director)
    rows=m.get("worker_processes_selected",[])
    counts["actual_worker_process_attempts_from_manifests"]+=len(rows)
    for w in rows:
        id=FLEET+"/"+w
        defects=[]
        data={}
        if id in seen:
            defects.append("DUPLICATE_GLOBAL_WORKER_ID_THIS_RUN")
        seen.add(id)
        try:
            data=json.loads((ROOT/(w+".json")).read_text(encoding="utf-8"))
        except (OSError,ValueError):
            defects.append("MISSING_OR_INVALID_INDIVIDUAL_JSON")
        if data.get("globally_unique_agent_id")!=id:
            defects.append("IDENTITY_MISMATCH_OR_MISSING")
        if data.get("director_id")!=director:
            defects.append("WRONG_DIRECTOR")
        if data.get("workforce_namespace")!=FLEET:
            defects.append("WRONG_COMPANY")
        if data.get("os_process_pid") in (None,0,False):
            defects.append("OS_PROCESS_NOT_EVIDENCED")
        if data.get("inference_status")!="model_completed":
            defects.append("MODEL_INFERENCE_NOT_COMPLETED")
        answer=str(data.get("model_response") or "").strip()
        if len(answer)<18:
            defects.append("EMPTY_OR_TRIVIAL_MODEL_OUTPUT")
        elif data.get("inference_status")=="model_completed":
            normalized=re.sub(r"\s+"," ",answer.lower())
            fingerprint=hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            if fingerprint in fingerprints:
                defects.append("DUPLICATE_MODEL_OUTPUT_OF_"+fingerprints[fingerprint])
            else:
                fingerprints[fingerprint]=id
        if not data.get("parent_id"):
            defects.append("DIRECT_PARENT_MISSING")
        idea_menu=data.get("ten_idea_exercise") or {}
        generated_ideas=data.get("ten_idea_model_result") or {}
        if idea_menu.get("count")!=10:
            defects.append("TEN_CANDIDATE_IDEAS_NOT_ASSIGNED")
        if generated_ideas.get("status")!="TEN_MODEL_GENERATED_IDEAS_NEED_FACT_CHECK":
            defects.append("TEN_ORIGINAL_MODEL_IDEAS_MISSING_OR_REPETITIVE")
        ack=data.get("latest_command_model_acknowledgement") or {}
        if ack.get("status")!="MODEL_SELF_REPORTED_COMMAND_ACK":
            defects.append("LATEST_CHIEF_D_ORDER_NOT_ACKNOWLEDGED")
        if ack.get("chief_D_owner_order_id")!=data.get("strict_owner_order_id"):
            defects.append("CHIEF_D_ORDER_ACK_ID_MISMATCH")
        if not (ack.get("correct_direct_parent_in_model_reply") and
                ack.get("crypto_mission_stated") and
                ack.get("concrete_action_stated") and
                ack.get("source_or_payment_evidence_discussed")):
            defects.append("CHIEF_D_COMMAND_ACK_MISSING_REQUIRED_EVIDENCE")
        checkpoint=data.get("cognitive_checkpoint") or {}
        activate=data.get("activation_evidence") or {}
        next_action=str(checkpoint.get("next_action") or activate.get("next_step_checkpoint") or "")
        if len(next_action.strip())<20:
            defects.append("MISSING_SPECIFIC_NEXT_STEP")
        sources=own_evidence(data.get("source_items") or [])
        if not sources:
            defects.append("NO_ORIGINAL_JOB_SOURCE_LINK")
        if data.get("source_check_status") not in ("source_checked","source_failed"):
            defects.append("PUBLIC_SOURCE_CHECK_NOT_ATTEMPTED")
        if data.get("external_messages_sent"):
            # Worker code has no authenticated external poster. This would
            # require a separate direct external-message evidence audit.
            defects.append("UNVERIFIED_OUTREACH_CLAIM")
        if data.get("verified_wallet_receipts") or data.get("owner_verified_payment_receipts"):
            defects.append("CLAIMED_PAYMENT_REQUIRES_SEPARATE_CHAIN_PROOF")
        grade=("QUALIFIED_SOURCE_BACKED_AI_RESEARCH" if not defects
               else "REVIEW_MODEL_OUTPUT_NOT_SOURCE_BACKED" if defects==["NO_ORIGINAL_JOB_SOURCE_LINK"]
               else "NOT_QUALIFIED")
        counts["graded_"+grade]+=1
        if "MODEL_INFERENCE_NOT_COMPLETED" not in defects:
            counts["model_completions_evidenced"]+=1
        counts["unique_actual_ids_checked"]+=1
        detail.append({
            "id":id,"director":director,
            "role_level":data.get("agent_level","not_evidenced"),
            "parent":data.get("parent_id"),
            "grade":grade,"defects":defects,
            "latest_order_ack_status":ack.get("status","NO_MODEL_ACKNOWLEDGEMENT"),
            "ten_idea_menu_count":idea_menu.get("count",0),
            "model_generated_distinct_idea_count":generated_ideas.get("numbered_valid_unique_count",0),
            "ten_model_ideas_status":generated_ideas.get("status","NO_MODEL_IDEAS"),
            "latest_order_id_acknowledged":ack.get("chief_D_owner_order_id"),
            "seven_billion_campaign_target_index":data.get("seven_billion_campaign_target_index"),
            "source_urls":sources[:3],
            "independent_model_excerpt":answer[:300] or "NO_MODEL_OUTPUT",
            "next_action":next_action[:300] or "MISSING",
            "payer_accepted_work_verified":False,
            "payment_to_owner_verified":False,
            "external_outreach_sent_verified":False,
            "actual_source_check":data.get("source_check_status","missing"),
        })

res={
 "as_of_utc":datetime.now(timezone.utc).isoformat(),
 "fleet":FLEET,
 "owner_order":"OWNER-20261114-071710",
 "strict":True,
 "counts":dict(counts),
 "actual_workers_checked":sum(1 for x in detail if x.get("id","").startswith(FLEET+"/D") and
                               x.get("id","").count("-")>=1),
 "individual_results":detail,
 "qualified_results_not_paid_jobs":True,
 "acknowledgment_rule":"Genuine model-generated owner command receipt is required for a qualified research result, even though self-reported comprehension is not proof of competence.",
 "seven_billion_target_roles":7000000000,
 "ten_idea_owner_order":"OWNER-20261114-075553",
 "ten_ideas_are_not_verified_paid_jobs":True,
 "verified_new_income":"not_assessed",
 "dormant_defined_roles_are_not_running":True,
 "limitations":"Every attempt must have a grade. A validated model research result is not a verified paid job. Source links are untrusted until independently checked. Model output quality varies. Even QUALIFIED does not show payer acceptance, direct social posting, or cryptocurrency receipt."
}
(OUT/("strict-"+FLEET+".json")).write_text(json.dumps(res,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
lines=["# Strict worker results — "+FLEET,"",
       "Report date: "+res["as_of_utc"],
       "Only actual unique attempted workers can receive grades, not mathematically defined idle positions.",
       ""]
for k,v in sorted(counts.items()):
    lines.append(f"- **{k}:** {v:,}")
lines+=["","## Model output quality controls",
        "Workers lacking a genuine external source, unique model text, identity, supervisor or actionable next step do NOT count as qualified.",
        "Completed model inference, useful qualified research, accepted work, payer debt and actual receipt are separate categories.",
        "","## Selected work deficits"]
for x in detail:
    if x["grade"]=="QUALIFIED_SOURCE_BACKED_AI_RESEARCH":
        continue
    lines.append("- "+x["id"]+": "+", ".join(x["defects"][:5]))
    if len(lines)>90: break
lines+=["","**Coins independently received by this audit:** not assessed; inspect the wallet watches and accepted payer evidence."]
(OUT/("strict-"+FLEET+".md")).write_text("\n".join(lines)+"\n",encoding="utf-8")
print("STRICT_B_WORKER_AUDIT",json.dumps({
 "fleet":FLEET,
 "process_attempts":counts.get("actual_worker_process_attempts_from_manifests",0),
 "model_completions":counts.get("model_completions_evidenced",0),
 "source_backed_qualified":counts.get("graded_QUALIFIED_SOURCE_BACKED_AI_RESEARCH",0),
 "not_qualified":counts.get("graded_NOT_QUALIFIED",0),
 "source_not_backed":counts.get("graded_REVIEW_MODEL_OUTPUT_NOT_SOURCE_BACKED",0),
 "owner_wallet_receipts":"not_assessed",
}))
