"""Choose a genuine single B worker to answer OWNER: Have you learned D's lesson?

Never fabricate workers' answers or award a pass to a worker that did not run
the curriculum with its own model.
"""
import json
from pathlib import Path

SRC=Path("owner-B-reports/EVERY_ACTUAL_AGENT.json")
OUT=Path("owner-B-reports/B_REPRESENTATIVE_TO_OWNER.md")
OUT.parent.mkdir(parents=True,exist_ok=True)

def load():
    try:
        return json.loads(SRC.read_text(encoding="utf-8"))
    except (FileNotFoundError,ValueError):
        return None

def summary(data):
    agents=(data or {}).get("individual_actual_agent_reports",[])
    usable=[w for w in agents if w.get("model_status")=="model_completed"
            and w.get("director_D_lesson_model_evidence")=="model_completed"
            and bool(w.get("worker_lesson_answer"))]
    passed=[w for w in usable if w.get("worker_reports_lesson_learned") is True
            and w.get("director_D_lesson_assessment")=="passed"]
    # Select first independently verified PASS if present, otherwise the first
    # actual trained worker that submitted a separately generated answer.
    winner=sorted(passed or usable,key=lambda w:w.get("role_id",""))[:1]
    lines=[
        "# Representative B worker — answer to OWNER",
        "",
        "Question: Have you learned Director D's lesson?",
        "",
    ]
    if not winner:
        lines.extend([
            "**Answer: NOT VERIFIED.**",
            "No actual B worker with an independently executed, recorded "
            "Director D lesson answer is available in this completed audit.",
            "I will not invent a worker's voice or say 'Yes, learned' for a dormant ID.",
            "",
            "Actual worker model records considered: "+str(len(agents)),
            "Curriculum: crypto-agents/DIRECTOR_D_LESSON_TO_B.md",
        ])
        return "\n".join(lines)+"\n"
    worker=winner[0]
    success=worker["worker_reports_lesson_learned"] is True
    lines.extend([
        "**Representative role:** "+str(worker["role_id"]),
        "**Immediate parent:** "+str(worker.get("parent") or "UNKNOWN"),
        "**Independent lesson model output recorded:** YES",
        "**Reported learned / passed check:** "+("YES, passed the automated knowledge check"
                                            if success else
                                            "NO — model answered, but knowledge check needs review"),
        "**Assessment:** "+str(worker.get("director_D_lesson_assessment") or "UNKNOWN"),
        "",
        "## Representative's actual model response",
        "",
        str(worker.get("worker_lesson_answer") or "NO RESPONSE").replace("\r"," ")[:900],
        "",
        "This is an actual saved model answer, not a statement that all B workers learned, "
        "a guarantee of human-like understanding or evidence of cryptocurrency earnings.",
    ])
    return "\n".join(lines)+"\n"

if __name__=="__main__":
    data=load()
    result=summary(data)
    OUT.write_text(result,encoding="utf-8")
    print("B_REPRESENTATIVE_STATUS", "real_model_response_selected"
          if "Independent lesson model output recorded:** YES" in result else "no_verified_learner")
    print(result)
