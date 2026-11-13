"""Director D's deterministic real-results scorecard for genuine AI worker runs.

Never count role definitions, LLM text, source-only research, or unverified
payment promises as income. Input: real GitHub Actions worker report artifacts.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("combined-ai-processes/ai-process-reports")
OUT = Path("director-D-results")
OUT.mkdir(exist_ok=True)
DIRECTORS = [f"D{i:02d}" for i in range(1, 11)]

def read_json(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None

def valid_link(url):
    return isinstance(url, str) and url.startswith("https://") and len(url) <= 1024

result = {
    "report_type": "Director D — execution-based results, not agent claims",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "standing_order": "ORD-040",
    "defined_role_identities_not_active_models": 375188632680,
    "directors_expected": 10,
    "directors_with_manifests": 0,
    "actual_model_completions_confirmed": 0,
    "workers_with_public_source_links": 0,
    "workers_with_specific_next_action": 0,
    "workers_with_model_critic_completed": 0,
    "payer_and_compensation_verified_by_this_audit": 0,
    "confirmed_owner_crypto_receipts_by_this_audit": 0,
    "workers_sampled": 0,
    "failure_and_missing_count": 0,
    "directors": [],
    "audit_limit": "No external payer, chain or exchange queries in this audit; source URLs are research, not payer verification.",
    "verified_earnings": "none_established_by_this_worker_evidence",
    "all_roles_running_concurrently": False,
}
seen = set()
for d in DIRECTORS:
    m = read_json(ROOT / f"manifest-{d}.json")
    row = {
        "director": d, "status": "MISSING_MANIFEST",
        "os_processes_invoked_from_manifest": 0,
        "individual_model_completions_checked": 0,
        "original_source_linked_reports": 0,
        "individual_action_checkpoints": 0,
        "verified_real_paid_opportunities": 0,
        "verified_crypto_receipts": 0,
        "missing_or_failed_worker_reports": 0,
        "first_source_backed_examples": [],
        "next_required_action": "Run actual agent model processes and upload each worker's report.",
    }
    if not isinstance(m, dict):
        result["directors"].append(row)
        result["failure_and_missing_count"] += 1
        continue
    result["directors_with_manifests"] += 1
    row["status"] = "MANIFEST_PRESENT"
    row["os_processes_invoked_from_manifest"] = int(m.get("subprocesses_invoked", 0))
    for wid in m.get("worker_processes_selected", [])[:50]:
        if wid in seen:
            row["missing_or_failed_worker_reports"] += 1
            continue
        seen.add(wid)
        agent = read_json(ROOT / f"{wid}.json")
        result["workers_sampled"] += 1
        if not isinstance(agent, dict) or agent.get("worker_id") != wid:
            row["missing_or_failed_worker_reports"] += 1
            continue
        if not (agent.get("inference_status") == "model_completed"
                and agent.get("os_process_pid") and str(agent.get("model_response") or "").strip()):
            row["missing_or_failed_worker_reports"] += 1
            continue
        row["individual_model_completions_checked"] += 1
        result["actual_model_completions_confirmed"] += 1
        evidence = agent.get("source_items") or []
        links = [x["url"] for x in evidence if isinstance(x, dict) and valid_link(x.get("url"))]
        # Source checked means a public search was attempted, not sponsor verification.
        source_backed = bool(links) and agent.get("source_check_status") == "source_checked"
        if source_backed:
            row["original_source_linked_reports"] += 1
            result["workers_with_public_source_links"] += 1
        checkpoint = agent.get("cognitive_checkpoint") or {}
        activation = agent.get("activation_evidence") or {}
        action = str(checkpoint.get("next_action") or activation.get("next_step_checkpoint") or "").strip()
        if action:
            row["individual_action_checkpoints"] += 1
            result["workers_with_specific_next_action"] += 1
        critic = agent.get("cognitive_critical_review") or {}
        if critic.get("status") == "model_completed" and critic.get("actually_second_inference"):
            result["workers_with_model_critic_completed"] += 1
        if source_backed and len(row["first_source_backed_examples"]) < 2:
            row["first_source_backed_examples"].append({
                "worker": wid, "public_source": links[0],
                "result_status": "source_researched_not_paid_work_verified",
                "next_action": action[:300] or "Confirm payer, eligibility and accepted payout network.",
            })
    result["failure_and_missing_count"] += row["missing_or_failed_worker_reports"]
    row["status"] = ("AI_RESEARCH_AND_REPORTS_PRESENT" if
                     row["individual_model_completions_checked"] else "NO_COMPLETED_AI_REPORTS")
    row["next_required_action"] = (
        "Validate a real sponsor and explicit payment terms for an evidenced source; prepare permitted work."
        if row["original_source_linked_reports"] else
        "Improve public-source checks; rerun failed or incomplete agents."
    )
    result["directors"].append(row)

(OUT / "DIRECTOR_D_RESULTS.json").write_text(
    json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
lines = [
    "# Director D — Real B Worker Results",
    "", "Date: " + result["generated_utc"], "",
    "**Defined roles:** 375,188,632,680 (NOT continuously active models)",
    "**Directors with actual process manifests:** " + str(result["directors_with_manifests"]) + "/10",
    "**Real worker model completions backed by individual files:** " +
        str(result["actual_model_completions_confirmed"]),
    "**Reports with actual public source URLs:** " + str(result["workers_with_public_source_links"]),
    "**Reports with specific next actions:** " + str(result["workers_with_specific_next_action"]),
    "**Completed independent critical-review model calls:** " +
        str(result["workers_with_model_critic_completed"]),
    "**Payer-and-compensation combinations verified here:** 0",
    "**Owner crypto receipts confirmed here:** 0", "",
    "## Individual director results", "",
]
for row in result["directors"]:
    lines += [
        f"### {row['director']} — {row['status']}",
        f"Individual model completions: {row['individual_model_completions_checked']}",
        f"Source-linked reports: {row['original_source_linked_reports']}",
        f"Action checkpoints: {row['individual_action_checkpoints']}",
        f"Missing/failed/duplicate evidence: {row['missing_or_failed_worker_reports']}",
        "Next action: " + row["next_required_action"],
    ]
    for example in row["first_source_backed_examples"]:
        lines.append("- Source investigated (not verified paid work): " + example["public_source"])
    lines.append("")
lines += [
    "## Director D's conclusion",
    "Every genuinely executed worker owes a real, source-backed result and next action.",
    "Configured role identities and unverified search links are not completed paying work.",
    "Only distinct model-process proofs are counted. No cryptocurrency earnings were verified by this audit.",
]
(OUT / "DIRECTOR_D_RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("DIRECTOR_D_RESULTS", json.dumps({
    "directors": result["directors_with_manifests"],
    "completed_models": result["actual_model_completions_confirmed"],
    "source_linked": result["workers_with_public_source_links"],
    "next_actions": result["workers_with_specific_next_action"],
    "critical_reviews": result["workers_with_model_critic_completed"],
    "verified_crypto_receipts": 0,
}))
