"""Owner-facing joint D + B discussion, from real recorded agent outputs ONLY.

This is an asynchronous evidence-based roundtable, NOT billions of live AIs
simultaneously chatting. Do not call a synthetic/templated message a real model
response. Distinguish D as separately executed model only when evidence says so.
"""
import json
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone

OUT=Path("owner-B-reports")
DISC=Path("director-D-discussion/director-D-consensus.json")

def read(path):
    try:
        obj=json.loads(path.read_text(encoding="utf-8"))
        return obj if isinstance(obj,dict) else {}
    except (OSError,ValueError):
        return {}

def tidy(x,limit=1800):
    return str(x or "").replace("\r"," ").strip()[:limit]

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    owner=read(OUT/"EVERY_ACTUAL_AGENT.json")
    consensus=read(DISC)
    workers=owner.get("individual_actual_agent_reports") or []
    if not isinstance(workers,list): workers=[]
    contributions=[]
    for w in workers:
        if not isinstance(w,dict): continue
        actual=w.get("real_model_output_evidenced") is True
        learned=w.get("director_D_lesson_model_evidence")=="model_completed"
        contribution={
            "speaker":w.get("role_id"),
            "role":"B worker",
            "parent":w.get("parent"),
            "level":w.get("level"),
            "evidenced_actual_ai_model_response":actual,
            "model_response":w.get("model_response") if actual else None,
            "lesson_separate_model_response_evidenced":learned,
            "lesson_response":w.get("worker_lesson_answer") if learned else None,
            "lesson_grade":w.get("director_D_lesson_assessment","not_run"),
            "original_sources":w.get("public_source_urls") or [],
            "next_action":w.get("next_action"),
            "actual_external_contact_evidenced":False,
            "verified_crypto_income_from_discussion":None,
        }
        contributions.append(contribution)
    directors=[]
    rd1=consensus.get("round_one") or {}
    rd2=consensus.get("round_two") or {}
    for n in range(1,11):
        name=f"D{n:02d}"
        x=rd1.get(name) or {}
        y=rd2.get(name) or {}
        directors.append({
            "speaker":name,
            "first_round_model_status":x.get("status","not_run"),
            "first_round_response":x.get("response") if x.get("status")=="model_completed" else None,
            "cross_review_model_status":y.get("status","not_run"),
            "cross_review_response":y.get("response") if y.get("status")=="model_completed" else None,
        })
    teaching=consensus.get("director_D_teaching") or {}
    synthesis=consensus.get("director_D_response") or {}
    record={
        "title":"OWNER Joint D and B Evidence-Based Discussion",
        "mode":"asynchronous recorded model discussion; not simultaneous live group chat",
        "owner_order_ids":["ORD-047","ORD-048","ORD-049"],
        "created_at_utc":datetime.now(timezone.utc).isoformat(),
        "B_total_defined_role_identities":375188632680,
        "actually_attempted_B_worker_records_in_current_batch":len(contributions),
        "B_individual_research_model_responses":sum(c["evidenced_actual_ai_model_response"] for c in contributions),
        "B_individual_lesson_answers":sum(c["lesson_separate_model_response_evidenced"] for c in contributions),
        "B_actual_lesson_passes":sum(c["lesson_grade"]=="passed" for c in contributions),
        "B_unverified_or_not_run_worker_learner_claims":sum(c["lesson_grade"]!="passed" for c in contributions),
        "genuine_director_first_round_models":sum(d["first_round_model_status"]=="model_completed" for d in directors),
        "genuine_director_cross_review_models":sum(d["cross_review_model_status"]=="model_completed" for d in directors),
        "D_teacher_model_completed":teaching.get("status")=="model_completed",
        "D_teacher_actual_response":teaching.get("response") if teaching.get("status")=="model_completed" else None,
        "D_owner_synthesis_model_completed":synthesis.get("status")=="model_completed",
        "D_owner_actual_response":synthesis.get("response") if synthesis.get("status")=="model_completed" else None,
        "directors":directors,
        "individual_B_contributions":contributions,
        "joint_summary_limit":"D's roundtable only contains recorded independent model results and evidence; director synthesis may consider worker evidence. No new private or external group chat, genuine contracts or coin receipts are proven.",
        "verified_crypto_receipts":"NOT ESTABLISHED from this discussion evidence",
    }
    (OUT/"D_B_JOINT_DISCUSSION_ALL_AGENT_VOICES.json").write_text(
        json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    text=[
      "# Director D and B — joint workforce discussion (owner record)",
      "",
      "Date (UTC): "+record["created_at_utc"],
      "",
      "**Discussion format:** evidence-based asynchronous model cross-review, not billions of simultaneously speaking agents.",
      "**Defined role identities:** 375,188,632,680 (NOT 375 billion active participants).",
      "**Actual B worker report entries:** "+str(len(contributions)),
      "**Genuine worker research responses:** "+str(record["B_individual_research_model_responses"]),
      "**Genuine separate lesson answers:** "+str(record["B_individual_lesson_answers"]),
      "**Passed lesson checks:** "+str(record["B_actual_lesson_passes"]),
      "**Actual director first-round model replies:** "+str(record["genuine_director_first_round_models"])+"/10",
      "**Actual director cross-review model replies:** "+str(record["genuine_director_cross_review_models"])+"/10",
      "**Actual D teacher model reply:** "+("YES" if record["D_teacher_model_completed"] else "NOT VERIFIED"),
      "**Actual D owner-synthesis reply:** "+("YES" if record["D_owner_synthesis_model_completed"] else "NOT VERIFIED"),
      "",
      "## Agenda issued by OWNER",
      "",
      "1. Did you learn what Director D can genuinely do, and what D cannot do?",
      "2. What evidence-backed useful task has your real model done?",
      "3. What practical action could result in an actual paying client and real coins?",
      "4. What blockers or missing authorizations prevent useful work?",
      "5. How should D coordinate, challenge and report the next work?",
      "",
      "## Director D — teacher's ACTUAL recorded model answer",
      "",
      tidy(record["D_teacher_actual_response"]) if record["D_teacher_model_completed"] else
         "No real Director D teacher model response was evidenced in this run.",
      "",
      "## Individual B worker voices — first genuine response from each available director",
      "",
    ]
    for n in range(1,11):
        did=f"D{n:02d}"
        choices=[w for w in contributions if str(w.get("speaker") or "").startswith(did+"-")
                 and w.get("evidenced_actual_ai_model_response")]
        if not choices:
            text.extend(["### "+did,"No genuine executed B worker voice available in this run.",""])
            continue
        choice=sorted(choices,key=lambda z:z.get("speaker") or "")[0]
        text.extend([
           "### "+did+" — representative "+str(choice["speaker"]),
           "**Own research response:** "+tidy(choice["model_response"],1000),
           "**Own separate D lesson response:** "+(
                tidy(choice["lesson_response"],600) if choice["lesson_separate_model_response_evidenced"]
                else "NOT VERIFIED"
           ),
           "**Learning result:** "+str(choice["lesson_grade"]),
           "**Next real task:** "+tidy(choice["next_action"],260),
           "",
        ])
    text.extend(["","## Ten director discussion and actual cross-review answers",""])
    for d in directors:
        text.extend([
            "### "+d["speaker"],
            "**Actual round-one model:** "+d["first_round_model_status"],
            "**Actual cross-review model:** "+d["cross_review_model_status"],
            tidy(d["cross_review_response"],1000) if d["cross_review_response"]
              else "No genuine cross-review model output available.",
            "",
        ])
    text.extend([
       "",
       "## Director D — consolidated ACTUAL recorded model response",
       "",
       tidy(record["D_owner_actual_response"]) if record["D_owner_synthesis_model_completed"]
         else "No genuine D model synthesis completed in this run.",
       "",
       "## Open matters and earnings truth",
       "",
       "This report must not imply all defined roles were contacted, learned or attended.",
       "Exact all-worker response entries are in `D_B_JOINT_DISCUSSION_ALL_AGENT_VOICES.json` and `EVERY_RECORDED_B_WORKER.csv`.",
       "Public research links are not paying clients; no actual coin receipt is established by this discussion.",
    ])
    (OUT/"D_B_JOINT_DISCUSSION.md").write_text("\n".join(text)+"\n",encoding="utf-8")
    print("D_B_JOINT_DISCUSSION",json.dumps({
       "real_worker_voices":record["B_individual_research_model_responses"],
       "separate_training_replies":record["B_individual_lesson_answers"],
       "directors_cross_reviewed":record["genuine_director_cross_review_models"],
       "D_model_synthesis":record["D_owner_synthesis_model_completed"],
    }))
    return record

if __name__=="__main__":
    run()
