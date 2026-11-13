"""Director D: census every B role and report EACH genuinely executed worker.

A configured identity is not a currently running agent and does not get a
fabricated reply. Output lists every completed, attempted or missing report
available in THIS workflow, and covers the full role-space in aggregate.
"""
import csv
import json
from collections import Counter
from pathlib import Path
from datetime import datetime, timezone

OUT = Path("owner-B-reports")
LEVELS = [
    ("operating_directors", 10),
    ("director_assistants", 20),
    ("managers", 150),
    ("W", 7500),
    ("S", 1125000),
    ("G", 562500000),
    ("H", 374625000000),
]
TOTAL = sum(n for _,n in LEVELS)
assert TOTAL == 375188632680
COLUMNS = [
    "role_id", "director", "parent", "level", "model_status",
    "real_model_output_evidenced", "director_D_lesson_assessment",
    "director_D_lesson_model_evidence", "worker_reports_lesson_learned",
    "worker_lesson_answer", "model_response", "public_source_urls",
    "next_action", "failure_or_blocker"
]

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    src=OUT/"EVERY_ACTUAL_AGENT.json"
    try:
        data=json.loads(src.read_text(encoding="utf-8"))
        workers=data.get("individual_actual_agent_reports") or []
    except (ValueError,OSError,AttributeError):
        workers=[]
    if not isinstance(workers,list):
        workers=[]
    index={}
    for w in workers:
        if isinstance(w,dict) and isinstance(w.get("role_id"),str) and w["role_id"] not in index:
            index[w["role_id"]]=w
    workers=sorted(index.values(),key=lambda w:w["role_id"])
    output_csv=OUT/"EVERY_RECORDED_B_WORKER.csv"
    with output_csv.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=COLUMNS,extrasaction="ignore")
        writer.writeheader()
        for w in workers:
            row={k:w.get(k) for k in COLUMNS}
            row["public_source_urls"]=" ; ".join(
                x for x in (w.get("public_source_urls") or []) if isinstance(x,str)
            )
            writer.writerow(row)
    bydir={}
    for i in range(1,11):
        did=f"D{i:02d}"
        subset=[w for w in workers if w.get("director")==did]
        bydir[did]={
            "reports":len(subset),
            "completed_models":sum(w.get("real_model_output_evidenced") is True for w in subset),
            "lesson_answers":sum(w.get("director_D_lesson_model_evidence")=="model_completed" for w in subset),
            "lesson_passed":sum(w.get("worker_reports_lesson_learned") is True for w in subset),
            "lesson_needs_review":sum(w.get("director_D_lesson_assessment")=="needs_parent_review" for w in subset),
            "lesson_failed":sum(str(w.get("director_D_lesson_assessment","")).startswith("failed") for w in subset),
        }
    grades=Counter(str(w.get("director_D_lesson_assessment") or "not_run") for w in workers)
    levels=Counter(str(w.get("level") or "missing") for w in workers)
    result={
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "full_defined_software_role_count":TOTAL,
        "defined_roles_are_not_running_agents":True,
        "levels":dict(LEVELS),
        "evidenced_unique_worker_attempt_reports_this_batch":len(workers),
        "evidenced_successful_model_reports_this_batch":
            sum(w.get("real_model_output_evidenced") is True for w in workers),
        "evidenced_lesson_model_answers_this_batch":
            sum(w.get("director_D_lesson_model_evidence")=="model_completed" for w in workers),
        "evidenced_lesson_passes_this_batch":
            sum(w.get("worker_reports_lesson_learned") is True for w in workers),
        "not_evidenced_as_running_in_this_batch":TOTAL-len(workers),
        "lesson_grade_counts":dict(grades),
        "executed_worker_levels":dict(levels),
        "director_scorecards":bydir,
        "earned_crypto":"NOT ESTABLISHED by this census; blockchain/exchange validation separate",
        "individual_report_file":str(output_csv),
        "truth":"No invented responses. One row for each UNIQUE worker report found in this batch; billions of inactive role identities summarized, not enumerated.",
    }
    (OUT/"B_ALL_WORKERS_CENSUS.json").write_text(
        json.dumps(result,indent=2)+"\n",encoding="utf-8"
    )
    lines=[
        "# Director D — report for ALL B worker roles",
        "",
        "Generated (UTC): "+result["generated_at_utc"],
        "",
        "**Configured B role identities:** "+f"{TOTAL:,}"+". These are not all running AI models.",
        "**Individual unique attempted worker reports actually present:** "+str(len(workers)),
        "**Actually completed model reports evidenced:** "+str(result["evidenced_successful_model_reports_this_batch"]),
        "**Actual separate lesson-model answers recorded:** "+str(result["evidenced_lesson_model_answers_this_batch"]),
        "**Actual lesson passes:** "+str(result["evidenced_lesson_passes_this_batch"]),
        "**Configured role identities NOT represented by worker reports in this batch:** "+
            f"{result['not_evidenced_as_running_in_this_batch']:,}",
        "",
        "## Full hierarchy census (defined role IDs, not live participants)",
        "",
        "| Level | Defined roles |",
        "|---|---:|",
    ]
    lines.extend("| "+name+" | "+f"{n:,}"+" |" for name,n in LEVELS)
    lines.extend([
        "",
        "## Actual director/team execution evidence",
        "",
        "| Director | Worker report entries | Actual model completions | Lesson answers | Lesson passes |",
        "|---|---:|---:|---:|---:|"
    ])
    for did,item in bydir.items():
        lines.append("| "+did+" | "+str(item["reports"])+" | "+
            str(item["completed_models"])+" | "+str(item["lesson_answers"])+" | "+
            str(item["lesson_passed"])+" |")
    lines.extend([
        "",
        "## Individual replies",
        "",
        "Every recorded genuine worker answer is indexed, with its actual execution and lesson status, in `EVERY_RECORDED_B_WORKER.csv` and `EVERY_ACTUAL_AGENT.json`.",
        "Unexecuted role identities have no individual answers and cannot be called contacted or trained.",
        "This system report does not verify bank, blockchain or exchange deposits. Verified crypto income: **NOT ESTABLISHED**.",
    ])
    (OUT/"B_ALL_WORKERS_REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("B_ALL_WORKERS_REPORT",json.dumps({
        "role_ids":TOTAL, "individual_reports":len(workers),
        "completed_models":result["evidenced_successful_model_reports_this_batch"],
        "lesson_answers":result["evidenced_lesson_model_answers_this_batch"],
        "lesson_passes":result["evidenced_lesson_passes_this_batch"]
    }))
    return result

if __name__=="__main__":
    run()
