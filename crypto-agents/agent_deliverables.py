"""ORD-024: Each actually attempted agent role gets an evidence-backed Markdown deliverable.

Does not invent research or fabricate AI execution for dormant role identifiers.
Runs once in each primary matrix GitHub job, even if a research step failed.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("agent-deliverables")
ROOT.mkdir(parents=True, exist_ok=True)
ROLE = os.getenv("ROLE_ID") or (sys.argv[1] if len(sys.argv) > 1 else "")
if not re.fullmatch(r"D(?:0[1-9]|10)(?:-[AB])?", ROLE):
    raise SystemExit("Expected one of the 30 scheduled role IDs")

def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

def clean(value, limit=500):
    s = str(value or "Unknown").replace("\r", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", s).strip()[:limit]

def links(record):
    seen = set()
    items = []
    for key in ("leads", "unverified_leads", "source_links", "source_evidence_urls",
                "research_source_urls", "source_linked_candidate_examples",
                "friendly_outreach_drafts"):
        value = record.get(key, [])
        if not isinstance(value, list):
            continue
        for obj in value:
            url = obj if isinstance(obj, str) else obj.get("url", "") if isinstance(obj, dict) else ""
            if isinstance(url, str) and url.startswith("https://") and url not in seen:
                seen.add(url)
                items.append(url)
                if len(items) >= 5:
                    return items
    return items

def get_identity(path, entry):
    if path.name.startswith("D") and path.parent.name == "reports":
        id_ = entry.get("role")
        return id_, "main_researcher"
    if "worker_id" in entry and "manager_id" in entry:
        return entry["worker_id"], "worker"
    if "manager_id" in entry and "workers_executed_this_cycle" in entry:
        return entry["manager_id"], "manager"
    if entry.get("level") in ("delegated_subagent", "microcompany_worker", "mega_branch_worker"):
        return entry.get("id"), entry["level"]
    return None, None

main = read_json(Path("reports") / (ROLE + ".json"))
tool = read_json(Path("tool-reports") / (ROLE + ".json"))
registry = {}
try:
    with Path("crypto-agents/agent_registry.csv").open(encoding="utf-8", newline="") as fh:
        registry = {x["id"]: x for x in csv.DictReader(fh)}
except OSError:
    pass

entries = []
if isinstance(main, dict) and main.get("role") == ROLE:
    entries.append((ROLE, "main_researcher", main))
for p in sorted(Path("company-reports").glob("*.json")):
    obj = read_json(p)
    if not isinstance(obj, dict):
        continue
    ident, level = get_identity(p, obj)
    if ident and level and ident.startswith(ROLE + "-"):
        entries.append((ident, level, obj))

# D01..D10 require a company summary, 15 manager outputs, 30 rotated workers
# unless earlier steps explicitly failed. Assistants have no manager workforce.
is_director = bool(re.fullmatch(r"D(?:0[1-9]|10)", ROLE))
company_summary = read_json(Path("company-reports") / (ROLE + "-COMPANY-SUMMARY.json"))
expected = {ROLE}
if is_director:
    for n in range(1, 16):
        mid = f"{ROLE}-M{n:02d}"
        expected.add(mid)
    if isinstance(company_summary, dict):
        for mid in company_summary.get("manager_report_ids", []):
            mgr = read_json(Path("company-reports") / (mid + ".json"))
            if isinstance(mgr, dict):
                expected.update(mgr.get("worker_ids_this_cycle", []))

created = []
for ident, level, obj in entries:
    if ident in {x["id"] for x in created}:
        continue
    parent = (obj.get("parent_id") or obj.get("manager_id") or obj.get("reports_to_one")
              or obj.get("reports_to_director") or obj.get("director"))
    if level == "main_researcher":
        parent = "OWNER" if ident == ROLE and is_director else ident[:3]
    if level == "manager":
        parent = ROLE
    if level == "delegated_subagent":
        parent = obj.get("parent_id")
    if level in ("microcompany_worker", "mega_branch_worker"):
        parent = obj.get("parent_id")
    name = obj.get("agent_name") or obj.get("name") or registry.get(ident, {}).get("agent_name") or ident
    task = (obj.get("assigned_role") or obj.get("objective") or obj.get("independent_research_objective")
            or obj.get("mission") or obj.get("manager_review") or "Independent worldwide research")
    model_state = (obj.get("model_inference") or {}).get("status") if isinstance(obj.get("model_inference"), dict) else None
    if not model_state:
        model_state = obj.get("source_model_status") or obj.get("actual_inference_status")
    if level == "main_researcher":
        model_state = (obj.get("ai_analysis") or {}).get("status", "not_assessed")
    src_state = obj.get("execution_status", "not_separately_recorded")
    sources = links(obj)
    errors = obj.get("source_error") or obj.get("source_errors") or []
    failures = []
    if errors:
        failures.append(clean(errors, 650))
    if model_state in ("llm_unavailable", "not_verified_active_AI", "model_unavailable"):
        failures.append("Model analysis unavailable or did not complete.")
    if level == "main_researcher":
        if obj.get("deep_research", {}).get("dossiers"):
            findings = "Independent source-check dossiers recorded."
        elif sources:
            findings = "Source-linked possible opportunities identified; not necessarily validated."
        else:
            findings = "No source-linked candidate established."
    else:
        leads = obj.get("unverified_leads")
        lead_titles = (
            "; ".join(clean(x.get("title", ""), 130) for x in leads[:3] if isinstance(x, dict))
            if isinstance(leads, list) else ""
        )
        inference = obj.get("model_inference") or {}
        model_summary = str(inference.get("analysis") or "").strip() if isinstance(inference, dict) else ""
        findings = lead_titles or model_summary or "No verified paid assignment recorded."
    completed = (model_state in ("model_completed", "llm_completed"))
    if completed:
        status = "model_completed"
    elif src_state == "source_checked":
        status = "source_checked_only"
    elif src_state == "source_unavailable":
        status = "source_failed"
    else:
        status = "attempted_unverified_model_execution"
    next_step = ("Recheck primary payer, deliverable, paid terms, eligibility and supported crypto route; "
                 "only pursue applications through authorized tools.")
    receipts = obj.get("verified_paid_receipts") or obj.get("verified_cryptocurrency_receipts") or obj.get("real_payments_verified") or []
    # No self-claimed receipt is considered independently confirmed by this script.
    document = [
        f"# Agent deliverable — {clean(ident)}",
        "",
        f"- **Agent:** {clean(name)}",
        f"- **Role:** {level}",
        f"- **Reports to:** {clean(parent)}",
        f"- **Cycle/document time (UTC):** {datetime.now(timezone.utc).isoformat()}",
        "- **Standing orders:** ORD-021, ORD-022, ORD-023, ORD-024",
        f"- **Execution status:** {status}",
        f"- **Model status:** {clean(model_state or 'not verified')}",
        f"- **Source-check status:** {clean(src_state)}",
        "",
        "## Assigned work",
        clean(task, 1100),
        "",
        "## Actual work and result",
        clean(findings, 950),
        "",
        "## Source evidence",
    ]
    document.extend(f"- {clean(u, 240)}" for u in sources)
    if not sources:
        document.append("- No independently source-linked finding was recorded.")
    document += ["", "## Tools and sites"]
    if ident == ROLE:
        if isinstance(tool, dict):
            document.append(f"- Public tool-discovery checks: {len(tool.get('sources_checked', []))}; candidates: {len(tool.get('new_tool_candidates', []))}.")
            for x in tool.get("new_tool_candidates", [])[:3]:
                document.append(f"- {clean(x.get('name'), 100)}: {clean(x.get('url'), 220)} (discovered, not installed)")
        else:
            document.append("- No tool-scout report available; tool discovery has not been verified.")
    else:
        document.append("- Descendant/manager access is limited to the actual recorded parent research and existing workflow tools. No new website account or software installation verified.")
    document += [
        "", "## Blockers and uncertainty",
    ]
    document.extend("- " + clean(e) for e in failures)
    if not failures:
        document.append("- Payer, eligibility, agreed paid work and payment route remain unverified unless supported by separate evidence.")
    document += ["", "## Next permitted action", next_step,
                 "", "## Verified cryptocurrency receipts",
                 "- No incoming deposit independently established by this document generator.",
                 "- Any reported amount remains unverified until separate blockchain/account-credit checks.",
                 "", "## Reporting integrity",
                 "- This is an inspectable record of an actual file produced by the configured workflow, not proof of a sent proposal, a contract, or a payment.",
                 "- Model completion is stated only if the source report explicitly records a successful inference."
                 ]
    out = ROOT / (ident + ".md")
    out.write_text("\n".join(document) + "\n", encoding="utf-8")
    created.append({"id": ident, "level": level, "parent": parent, "document": str(out),
                    "status": status, "model_completed": completed,
                    "source_count": len(sources), "verified_receipts_from_audit": 0})

created_ids = {x["id"] for x in created}
missing = sorted(expected - created_ids)
manifest = {
    "main_role": ROLE,
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "expected_scheduled_main_manager_worker_ids": len(expected),
    "individual_documents_generated": len(created),
    "documents": created,
    "missing_expected_ids": missing,
    "actual_model_completed": sum(x["model_completed"] for x in created),
    "documents_are_not_earnings": True,
    "verified_coin_receipts": [],
    "configured_but_unscheduled_H_roles_are_not_claimed_active": True,
}
(ROOT / ("manifest-" + ROLE + ".json")).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
index = [f"# Agent document index — {ROLE}", "", f"Generated files: {len(created)}",
         f"Model-completed reports: {manifest['actual_model_completed']}",
         f"Expected but missing scheduled identities: {len(missing)}", "",
         "## Delivered per-role documents"]
for x in created:
    index.append(f"- {x['id']}: {x['status']} — {x['document']}")
index += ["", "## Missing scheduled reports"]
index += [f"- {ident}: NOT REPORTED; no fabricated deliverable" for ident in missing] or ["- None"]
(ROOT / ("INDEX-" + ROLE + ".md")).write_text("\n".join(index) + "\n", encoding="utf-8")
print("ORD024_DELIVERABLES", ROLE, "created", len(created), "model_completed",
      manifest["actual_model_completed"], "missing", len(missing))
