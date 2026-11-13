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
                    "source_linked": 0, "next_actions": 0}
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
            agents.append({
                "role_id": rid, "director": did, "parent": d.get("parent_id"),
                "level": d.get("agent_level"),
                "real_model_output_evidenced": bool(valid),
                "model_status": d.get("inference_status", "missing"),
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
             "Verified BTC income: NOT ASSESSED by this report.", "",
             "## Team accountability", "",
             "| Director | Attempts | Completed models | Evidence links | Next actions |",
             "|---|---:|---:|---:|---:|"]
    for x in directors:
        lines.append("| " + x["director"] + " | " + str(x["attempted"]) + " | " +
                     str(x["completed"]) + " | " + str(x["source_linked"]) + " | " +
                     str(x["next_actions"]) + " |")
    lines.extend(["", "## Individual evidence", "",
                  "Every actually attempted worker has its own evidence entry in EVERY_ACTUAL_AGENT.json.",
                  "Dormant role IDs have not generated actual model replies.",
                  "Director D must distinguish researched leads, delivered work, accepted contracts and independently verified payments."])
    (target / "DIRECTOR_D_TO_OWNER.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("DIRECTOR_D_OWNER_REPORT", json.dumps({"manifests": obj["directors_with_actual_worker_manifests"],
          "attempts": attempted, "completed": completed, "missing_or_failed": attempted - completed}))
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
