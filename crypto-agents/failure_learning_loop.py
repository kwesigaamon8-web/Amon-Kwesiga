"""Chief D feedback cycle: observe real failed jobs, classify cause, propose fix, re-test.

No auto-retry of paid jobs, no wallet activity, no external messages, and no
claims that an observed workflow run made or received money.
"""
from __future__ import annotations

import collections
import datetime as dt
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "kwesigaamon8-web/Amon-Kwesiga")
OUT = Path("failure-learning-reports")
TOKEN = os.environ.get("GH_TOKEN", os.environ.get("GITHUB_TOKEN", ""))
BASE = "https://api.github.com/repos/" + REPO
MAX_RUNS = 35
MAX_FAILED_RUNS_TO_EXPAND = 12

# Specific, evidence-based failure modes; mitigation is a suggested next
# engineering action, not a claim that the root cause is certainly fixed.
RULES = (
    ("OLD_SCHEMA_CONTRACT", re.compile(r"test[\s_-]+cash[\s_-]+first[\s_-]+priority|test[\s_-]+public[\s_-]+payment[\s_-]+routes|schema|route.contract", re.I),
     "Check manifest version and compare test expectations to public route safety invariants; keep exchange deposits blocked. Re-run exact tests."),
    ("PAYMENT_ROUTE_UNSAFE", re.compile(r"wallet|balance|receiv|memo|deposit|address|chain", re.I),
     "Check source token/network and beneficiary, require independent receipt proof; do not issue a payer instruction on an unverified exchange route."),
    ("ORIGINAL_BUYER_UNVERIFIED", re.compile(r"paid task|source|buyer|candidate|bounty|scout|eligibility", re.I),
     "Stop speculative production; verify one real payer, live amount, correct owner eligibility and authenticated submission route first."),
    ("AI_MODEL_EXECUTION", re.compile(r"model|inference|worker|cuda|torch|transformer", re.I),
     "Read exact model step logs and artifact; fix memory, download or timeout issue, retry a bounded model, verify output before counting execution."),
    ("INFRA_DEPLOYMENT", re.compile(r"deploy|render|gunicorn|health|boot", re.I),
     "Inspect actual Render deploy logs and compare declared build/start settings; GitHub runner smoke success is not proof of a Render deployment."),
    ("TEST_REGRESSION", re.compile(r"test|pytest|assert|compile|syntax", re.I),
     "Reproduce the failing assertion, fix implementation or stale expectation without weakening safeguards, then execute the same test."),
    ("EXTERNAL_PERMISSION", re.compile(r"permission|forbidden|access denied|403|unauthoriz", re.I),
     "Stop forbidden retries; require verified authorized integration or user-permitted authenticated browser submission."),
)
def triage(name: str, step: str) -> dict:
    combined = f"{name} {step}"
    for code, pattern, correction in RULES:
        if pattern.search(combined):
            return {"category": code, "corrective_action": correction}
    return {"category": "UNCLASSIFIED", "corrective_action": "Inspect actual failed job logs and attach reproducible cause before retry. Never infer earnings."}

def api(path: str) -> dict:
    req = urllib.request.Request(BASE + path, headers={
        "User-Agent": "B1B2ChiefDFailureLearning/1.0",
        "Accept": "application/vnd.github+json",
        **({"Authorization": "Bearer " + TOKEN} if TOKEN else {}),
    })
    with urllib.request.urlopen(req, timeout=14) as r:
        return json.loads(r.read(1_500_000))

def analyze_runs(runs: list[dict], jobs_by_run: dict[int, list[dict]]) -> dict:
    failure_rows = []
    by_name = collections.Counter()
    success_rows = []
    for run in runs:
        if not isinstance(run, dict) or run.get("id") is None:
            continue
        name = str(run.get("name") or "Unnamed workflow")
        status = str(run.get("conclusion") or "not_concluded")
        if status == "success":
            success_rows.append({"id": run["id"], "name": name})
        if status != "failure":
            continue
        by_name[name] += 1
        jobs = jobs_by_run.get(run["id"], [])
        failed_jobs = [j for j in jobs if j.get("conclusion") == "failure"]
        if not failed_jobs:
            failure_rows.append({
                "run_id": run["id"], "workflow": name, "job_name": "NO_JOB_DETAIL_AVAILABLE",
                "step_name": "UNKNOWN", "link": run.get("html_url"),
                "failure_evidence": "workflow failed, failed job details missing",
                **triage(name, "UNKNOWN")})
        for job in failed_jobs:
            bad_steps = [s for s in job.get("steps", []) if s.get("conclusion") == "failure"]
            for step in bad_steps or [{"name": "FAILED_STEP_UNKNOWN"}]:
                failure_rows.append({
                    "run_id": run["id"],
                    "workflow": name,
                    "job_name": job.get("name") or "Unknown",
                    "step_name": step.get("name") or "Unknown",
                    "link": job.get("html_url") or run.get("html_url"),
                    "failure_evidence": "GitHub Actions job/step conclusion was failure; exact traceback still requires logs",
                    **triage(name, str(step.get("name") or "")),
                })
    return {
        "schema": "B1_B2_VERIFIED_FAILURE_FEEDBACK_V1",
        "repo": REPO,
        "runs_observed": len(runs),
        "successful_run_count": len(success_rows),
        "failed_run_count": sum(by_name.values()),
        "failed_steps_observed": len(failure_rows),
        "repeating_failed_workflows": {
            k: v for k, v in sorted(by_name.items()) if v >= 2},
        "failed_steps": failure_rows,
        "all_failures_remediated": False if failure_rows else None,
        "confirmed_new_collected_revenue": "NOT_ASSESSED_BY_THIS_AUDIT",
        "principle": "OBSERVE -> REPRODUCE -> CORRECT -> RETEST -> VERIFY PAYER RESULT; never claim payment from a successful job",
    }

def selftest() -> None:
    runs = [
        {"id": 1, "name": "Paid Scout", "conclusion": "failure", "html_url": "https://github.com/example/runs/1"},
        {"id": 2, "name": "Paid Scout", "conclusion": "failure", "html_url": "https://github.com/example/runs/2"},
        {"id": 3, "name": "Real AI model", "conclusion": "success"},
        {"id": 4, "name": "in-progress", "conclusion": None}
    ]
    jobs = {
        1: [{"conclusion": "failure", "name": "check", "steps":[{"name": "test cash first priority", "conclusion": "failure"}]}],
        2: [{"conclusion": "failure", "name": "source scan", "steps":[{"name": "Verify buyer sources", "conclusion": "failure"}]}],
    }
    a = analyze_runs(runs, jobs)
    assert a["failed_run_count"] == 2 and a["successful_run_count"] == 1
    assert a["repeating_failed_workflows"] == {"Paid Scout": 2}
    assert a["failed_steps_observed"] == 2
    assert a["failed_steps"][0]["category"] == "OLD_SCHEMA_CONTRACT"
    assert a["failed_steps"][1]["category"] == "ORIGINAL_BUYER_UNVERIFIED"
    assert not a["all_failures_remediated"]
    assert analyze_runs([], {})["all_failures_remediated"] is None
    assert "confirmed_new_collected_revenue" in a
    print("CHIEF_D_FAILURE_LEARNING_SELFTEST_PASS")

def run() -> None:
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    errors = []
    try:
        data = api("/actions/runs?per_page=" + str(MAX_RUNS))
        runs = data.get("workflow_runs", [])
        if not isinstance(runs, list):
            raise ValueError("GitHub workflow_runs is not a list")
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as e:
        errors.append({"stage": "list_runs", "error": type(e).__name__ + ": " + str(e)[:150]})
        runs = []
    by_run = {}
    for run in [x for x in runs if x.get("conclusion") == "failure"][:MAX_FAILED_RUNS_TO_EXPAND]:
        try:
            jobs = api(f"/actions/runs/{int(run['id'])}/jobs?per_page=70")
            by_run[run["id"]] = jobs.get("jobs", [])
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as e:
            errors.append({"stage": f"jobs:{run.get('id')}", "error": type(e).__name__ + ": " + str(e)[:150]})
    result = analyze_runs(runs, by_run)
    result["observed_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    result["api_errors"] = errors
    result["source_status"] = "AVAILABLE" if runs and not errors else "PARTIAL_OR_UNAVAILABLE"
    (OUT / "failure-report.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = [
        "# Chief D: learn from actual failures",
        "",
        f"Observed at (UTC): {result['observed_at_utc']}",
        f"Source status: **{result['source_status']}**",
        f"Observed {result['runs_observed']} recent runs, {result['failed_run_count']} failed runs, {result['successful_run_count']} successful runs.",
        "",
        "## Repeated failed workflows",
    ]
    if result["repeating_failed_workflows"]:
        for name, count in result["repeating_failed_workflows"].items():
            lines.append(f"- {name}: {count} failures in observed window; stop unchanged retries, reproduce and fix")
    else:
        lines.append("- None established in observed window")
    lines.extend(["", "## Actionable failed steps"])
    if not result["failed_steps"]:
        lines.append("- No failed step details observed; missing access is UNKNOWN, not success")
    for x in result["failed_steps"][:24]:
        lines.extend([
            f"### {x['workflow']} — {x['step_name']}",
            f"- Evidence: {x['link'] or 'NOT_AVAILABLE'}",
            f"- Category: {x['category']}",
            f"- Required action: {x['corrective_action']}",
        ])
    lines.extend(["", "## Close-out requirements",
        "Every error needs actual log evidence, one owner for a change, a test that reproduced the failure and a passing re-test. A changed prompt is not a repaired external payment or deployment.",
        "Client money: check signed acceptance, beneficiary entitlement and settled account/chain receipt separately. No verified incoming funds were established by this audit.",
        f"API errors: {len(errors)}; do not silently classify missing data as zero failures."])
    (OUT / "CHIEF_D_FAILURE_REVIEW.md").write_text("\n".join(lines) + "\n")
    print("CHIEF_D_REAL_FAILURE_FEEDBACK", json.dumps({
        "observed_runs": len(runs), "failed_runs": result["failed_run_count"],
        "repeated_workflows": result["repeating_failed_workflows"],
        "api_errors": len(errors), "receipt_verified": False
    }))

if __name__ == "__main__":
    run()
