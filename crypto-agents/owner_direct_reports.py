"""One truthful owner report from Director D, with every executed worker as evidence."""
import json
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone

def read(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None

def tidy(s, size=650):
    return str(s or "").replace("\n", " ").replace("\r", " ").replace("|", "/")[:size]

def generate(root, target):
    target.mkdir(parents=True, exist_ok=True)
    agents = []
    directors = []
    seen = set()
    for n in range(1, 11):
        did = "D%02d" % n
        manifest = read(root / ("manifest-" + did + ".json"))
        director = {"director": did, "manifest_received": isinstance(manifest, dict),
                    "attempted": 0, "completed": 0, "failed_or_missing": 0,
                    "source_linked": 0, "next_actions": 0, "lesson_passed": 0,
                    "lesson_needs_review": 0, "lesson_failed": 0, "lesson_not_run": 0}
        ids = manifest.get("worker_processes_selected", []) if isinstance(manifest, dict) else []
        if not isinstance(ids, list):
            ids = []
        for rid in ids[:50]:
            if not isinstance(rid, str) or not rid.startswith(did + "-") or rid in seen:
                director["failed_or_missing"] += 1
                continue
            seen.add(rid)
            d = read(root / (rid + ".json"))
            d = d if isinstance(d, dict) else {}
            valid = (d.get("worker_id") == rid and
                     d.get("inference_status") == "model_completed" and
                     bool(d.get("os_process_pid")) and
                     bool(str(d.get("model_response") or "").strip()))
            original = d.get("source_items") or []
            original = [z.get("url") for z in original[:5] if isinstance(z, dict) and
                        isinstance(z.get("url"), str) and z["url"].startswith("https://")] if isinstance(original, list) else []
            checkpoint = d.get("cognitive_checkpoint") or {}
            activation = d.get("activation_evidence") or {}
            if not isinstance(checkpoint, dict):
                checkpoint = {}
            if not isinstance(activation, dict):
                activation = {}
            action = checkpoint.get("next_action") or activation.get("next_step_checkpoint")
            lesson = d.get("director_D_lesson_assessment") or {}
            if not isinstance(lesson, dict):
                lesson = {}
            lesson_status = str(lesson.get("assessment") or "not_run")
            lesson_pass = (
                lesson_status == "passed"
                and lesson.get("model_execution_status") == "model_completed"
                and lesson.get("lesson_accessible") is True
                and lesson.get("reported_learned") is True
                and bool(str(lesson.get("answer") or "").strip())
                and (lesson.get("knowledge_check") or {}).get("passed") is True
            )
            if lesson_pass:
                director["lesson_passed"] += 1
            elif lesson_status == "needs_parent_review":
                director["lesson_needs_review"] += 1
            elif lesson_status.startswith("failed"):
                director["lesson_failed"] += 1
            else:
                director["lesson_not_run"] += 1
            agents.append({
                "role_id": rid, "director": did, "parent": d.get("parent_id"),
                "level": d.get("agent_level"),
                "real_model_output_evidenced": bool(valid),
                "model_status": d.get("inference_status", "missing"),
                "director_D_lesson_assessment": "passed" if lesson_pass else lesson_status,
                "director_D_lesson_model_evidence": lesson.get("model_execution_status", "not_run"),
                "worker_reports_lesson_learned": bool(lesson_pass),
                "worker_lesson_answer": tidy(lesson.get("answer"), 900) if lesson.get("model_execution_status") == "model_completed" else None,
                "model_response": tidy(d.get("model_response"), 1100) if valid else None,
                "public_source_urls": original,
                "next_action": tidy(action, 400) if action else None,
                "failure_or_blocker": tidy(d.get("inference_error") or d.get("subprocess_error"), 300),
                "recipient": "OWNER via Director D",
                "actual_crypto_receipt_ascertained": None,
                "artifact_evidence_path": ("ai-process-reports/" + rid + ".json") if d else None
            })
            director["attempted"] += 1
            if valid:
                director["completed"] += 1
                director["source_linked"] += bool(original)
                director["next_actions"] += bool(action)
            else:
                director["failed_or_missing"] += 1
        directors.append(director)
    completed = sum(x["completed"] for x in directors)
    attempted = len(agents)
    obj = {
        "owner": "OWNER", "coordinator": "Director D",
        "order": "ORD-044",
        "reporting": "B worker -> parent -> manager -> D01-D10 -> Director D -> OWNER",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "software_defined_role_identities": 375188632680,
        "these_identities_are_not_all_active": True,
        "directors_with_actual_worker_manifests": sum(x["manifest_received"] for x in directors),
        "actual_agent_attempt_reports": attempted,
        "successful_individual_model_outputs": completed,
        "incomplete_individual_model_outputs": attempted - completed,
        "director_D_lesson_passed": sum(x["lesson_passed"] for x in directors),
        "director_D_lesson_needs_review": sum(x["lesson_needs_review"] for x in directors),
        "director_D_lesson_failed": sum(x["lesson_failed"] for x in directors),
        "director_D_lesson_not_run": sum(x["lesson_not_run"] for x in directors),
        "lesson_truth": "Only separately completed individual training model checks can report learned; dormant roles are not trained.",
        "verified_earned_crypto": None,
        "payment_limit": "No blockchain or exchange receipt verification in this audit.",
        "directors": directors, "individual_actual_agent_reports": agents
    }
    (target / "EVERY_ACTUAL_AGENT.json").write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = ["# Director D — Owner Report", "",
             "OWNER created B and directs its mission. Director D oversees reporting.",
             "Reporting: B worker > direct parent > director > Director D > OWNER.", "",
             "Actual director manifests: " + str(obj["directors_with_actual_worker_manifests"]) + "/10",
             "Actually attempted individual reports: " + str(attempted),
             "Successful actual AI model outputs: " + str(completed),
             "Failed or incomplete: " + str(attempted - completed), "",
             "Director D lesson — ACTUAL worker model learning reports: " + str(obj["director_D_lesson_passed"]) + " passed, " + str(obj["director_D_lesson_needs_review"]) + " needs parent review, " + str(obj["director_D_lesson_failed"]) + " failed, " + str(obj["director_D_lesson_not_run"]) + " not run.",
             "Dormant role identities trained: NOT CLAIMED.",
             "Verified BTC income: NOT ASSESSED by this report.", "",
             "## Team accountability", "",
             "| Director | Attempts | Completed models | Evidence links | Next actions |",
             "|---|---:|---:|---:|---:|"]
    for x in directors:
        lines.append("| " + x["director"] + " | " + str(x["attempted"]) + " | " +
                     str(x["completed"]) + " | " + str(x["source_linked"]) + " | " +
                     str(x["next_actions"]) + " |")
    lines.extend(["", "## Director D learner accountability",
                  "PASS requires a real separate model training answer, correct actual parent, accurate D capability and limit.",
                  "No response or missing model is never interpreted as learned.",
                  "", "## Individual evidence", "",
                  "Every actually attempted worker has its own evidence entry in EVERY_ACTUAL_AGENT.json.",
                  "Dormant role IDs have not generated actual model replies.",
                  "Director D must distinguish researched leads, delivered work, accepted contracts and independently verified payments."])
    (target / "DIRECTOR_D_TO_OWNER.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("DIRECTOR_D_OWNER_REPORT", json.dumps({"manifests": obj["directors_with_actual_worker_manifests"],
          "attempts": attempted, "completed": completed, "missing_or_failed": attempted - completed,
          "lesson_passed":obj["director_D_lesson_passed"],
          "lesson_needs_review":obj["director_D_lesson_needs_review"],
          "lesson_failed":obj["director_D_lesson_failed"],
          "lesson_not_run":obj["director_D_lesson_not_run"]}))
    return obj

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t) / "data"
            root.mkdir()
            rid = "D01-M01-W01"
            miss = "D01-M01-W02"
            (root / "manifest-D01.json").write_text(json.dumps({"worker_processes_selected": [rid, miss]}))
            (root / (rid + ".json")).write_text(json.dumps({
                "worker_id": rid, "parent_id": "D01-M01", "os_process_pid": 31,
                "inference_status": "model_completed", "model_response": "Source found, payer unknown",
                "source_items": [{"url": "https://example.org/offer"}],
                "cognitive_checkpoint": {"next_action": "Verify payer"}
            }))
            result = generate(root, Path(t) / "out")
            assert result["actual_agent_attempt_reports"] == 2
            assert result["successful_individual_model_outputs"] == 1
            assert result["incomplete_individual_model_outputs"] == 1
            assert result["individual_actual_agent_reports"][1]["model_response"] is None
            assert result["verified_earned_crypto"] is None
            print("DIRECTOR_D_OWNER_REPORT_SELF_TEST_PASS")
    else:
        generate(Path("combined-ai-processes/ai-process-reports"), Path("owner-B-reports"))
