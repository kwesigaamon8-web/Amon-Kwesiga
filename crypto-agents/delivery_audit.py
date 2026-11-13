"""ORD-024: Cross-company audit of per-agent deliverable documents.

Never synthesizes completed research for absent or inactive role identities.
Documents are evidence files, not money or contracts.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse
import json
import re

P = argparse.ArgumentParser()
P.add_argument("--reports", default="combined-reports")
P.add_argument("--output", default="delivery-audit")
args = P.parse_args()
base = Path(args.reports)
out = Path(args.output)
out.mkdir(parents=True, exist_ok=True)

ids = [f"D{d:02d}{suffix}" for d in range(1,11) for suffix in ("", "-A", "-B")]
manifests = {}
errors = []
for file in sorted(base.rglob("manifest-D*.json")) if base.exists() else []:
    try:
        obj = json.loads(file.read_text(encoding="utf-8"))
        role = obj.get("main_role")
        if role in ids:
            if role in manifests:
                errors.append("Duplicate manifest for " + role)
            manifests[role] = obj
    except (ValueError, OSError) as e:
        errors.append(str(file) + ": " + str(e)[:120])

levels = Counter()
statuses = Counter()
model_completed = 0
verified_doc_files = 0
missing_documents = []
expected_unreported = []
per_job = []
for role in ids:
    manifest = manifests.get(role)
    if not manifest:
        per_job.append({"role": role, "status": "missing_manifest_no_claim_of_agent_execution",
                        "documents": 0, "missing_expected": None})
        continue
    records = manifest.get("documents", [])
    valid = 0
    for agent in records:
        ident = agent.get("id")
        # Agents write agent-deliverables/<ID>.md inside per-job upload.
        if not isinstance(ident, str) or not re.fullmatch(r"D(?:0[1-9]|10)(?:-[AB]|(?:-M\d\d(?:-W\d\d(?:-S\d\d\d(?:-G\d\d\d(?:-H\d\d\d)?)?)?)?)?)?", ident):
            errors.append("Unexpected role ID in manifest " + str(role) + ": " + str(ident)[:90])
            continue
        paths = list(base.rglob("agent-deliverables/" + ident + ".md"))
        if len(paths) != 1:
            missing_documents.append(ident)
            continue
        content = paths[0].read_text(encoding="utf-8", errors="replace")
        if "## Actual work and result" not in content or "## Verified cryptocurrency receipts" not in content or "## Next permitted action" not in content:
            errors.append("Malformed deliverable sections: " + ident)
            continue
        valid += 1
        levels[agent.get("level", "unknown")] += 1
        statuses[agent.get("status", "unknown")] += 1
        if agent.get("model_completed") is True:
            model_completed += 1
    verified_doc_files += valid
    expected_unreported.extend(manifest.get("missing_expected_ids", []))
    per_job.append({"role": role, "status": "manifest_present",
                    "documents": valid,
                    "model_completed": sum(1 for x in records if x.get("model_completed")),
                    "missing_expected": len(manifest.get("missing_expected_ids", []))})

missing_primary = [x for x in ids if x not in manifests]
results = {
    "order_id": "ORD-024",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "main_research_jobs_expected": 30,
    "main_research_jobs_with_manifest": len(manifests),
    "main_research_jobs_missing_manifests": missing_primary,
    "individual_deliverables_verified_present": verified_doc_files,
    "per_level_deliverables": dict(levels),
    "per_status_deliverables": dict(statuses),
    "model_completed_from_role_reports_not_chain_receipts": model_completed,
    "scheduled_role_ids_with_missing_report": len(expected_unreported),
    "missing_report_sample": expected_unreported[:60],
    "individual_manifest_entries_missing_actual_document": missing_documents,
    "issues": errors,
    "job_reports": per_job,
    "result": "reports_present_with_gaps" if (missing_primary or expected_unreported or missing_documents or errors) else "all_reported_scheduled_roles_have_documents",
    "NOT_a_claim_all_defined_agents_are_working": True,
    "defined_roles_are_not_all_active": True,
    "payments_verified_by_this_audit": [],
    "verified_receipts_count_claim": "not assessed; a document is not proof of deposit"
}
(out / "REPORT.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
lines = [
    "# ORD-024 — Agent delivery accountability audit", "",
    f"Generated UTC: {results['generated_at_utc']}",
    f"Primary research jobs reporting: **{len(manifests)}/30**",
    f"Individually documented agent reports: **{verified_doc_files}**",
    f"Role reports explicitly marking completed model inference: **{model_completed}**",
    f"Expected scheduled role reports missing: **{len(expected_unreported)}**",
    f"Missing/corrupt written deliverables: **{len(missing_documents)}**",
    "", "## Documents by role level"
]
for level, value in sorted(levels.items()):
    lines.append(f"- {level}: {value}")
lines += ["", "## 30 jobs — report completeness"]
for item in per_job:
    lines.append(f"- {item['role']}: {item['status']} — {item['documents']} documents; missing scheduled: {item['missing_expected']}")
lines += ["", "## Execution distinction",
    "The hundreds of billions of defined role identifiers are not running independently. "
    "Only documented actually scheduled roles can be considered attempted; "
    "only a successful model-completed status is recorded as completed independent inference.",
    "This report audits documents, not blockchain payments or contracts.",
    "", "## Issues"]
if missing_primary:
    lines.append("- Missing primary job manifests: " + ", ".join(missing_primary))
if expected_unreported:
    lines.append("- Missing scheduled role reports include: " + ", ".join(expected_unreported[:25]))
if missing_documents:
    lines.append("- Missing Markdown documents: " + ", ".join(missing_documents[:25]))
if errors:
    lines.extend("- " + x for x in errors[:15])
if not (missing_primary or expected_unreported or missing_documents or errors):
    lines.append("- No missing documents detected among the actually reported scheduled roles.")
(out / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("ORD024_AUDIT", "primary", len(manifests), "docs", verified_doc_files,
      "model_completed", model_completed, "missing_expected", len(expected_unreported),
      "missing_documents", len(missing_documents))
