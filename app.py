"""Read-only public status dashboard for the repository's existing GitHub Actions agents.

This is a small Render-compatible web service, not a claim that billions of
configured role IDs are running. No wallet keys, account secrets, privileged
GitHub scopes, external actions, or crypto transactions are required.
"""
from datetime import datetime, timezone
from html import escape
import json
import os
import threading
import time
import urllib.error
import urllib.request
from flask import Flask, Response, jsonify

app = Flask(__name__)
GITHUB_REPO = "kwesigaamon8-web/Amon-Kwesiga"
RUNS_API = f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs?per_page=12"
RUNS_PAGE = f"https://github.com/{GITHUB_REPO}/actions"
CACHE_TTL = 150
_cache = {"at": 0.0, "runs": [], "error": None}
_cache_lock = threading.Lock()


def fetch_run_status():
    now = time.time()
    with _cache_lock:
        if now - _cache["at"] < CACHE_TTL:
            return dict(_cache)
        request = urllib.request.Request(
            RUNS_API,
            headers={
                "User-Agent": "IndependentAgentStatus/1.0",
                "Accept": "application/vnd.github+json",
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=7) as response:
                payload = json.loads(response.read(140000))
            rows = []
            for run in payload.get("workflow_runs", [])[:12]:
                if not isinstance(run, dict):
                    continue
                rows.append({
                    "name": str(run.get("name") or "Unnamed workflow")[:110],
                    "run_id": run.get("id"),
                    "status": str(run.get("status") or "unknown")[:40],
                    "conclusion": str(run.get("conclusion") or "not finished")[:40],
                    "created_at": str(run.get("created_at") or "")[:35],
                    "url": str(run.get("html_url") or RUNS_PAGE),
                })
            _cache.update(at=now, runs=rows, error=None)
        except (ValueError, urllib.error.URLError, TimeoutError, OSError) as exc:
            _cache.update(at=now, error=f"GitHub status temporarily unavailable: {type(exc).__name__}")
        return dict(_cache)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "public-status-dashboard",
                    "running_agents_claim": False,
                    "note": "Health of dashboard only, not model or worker health."})


@app.get("/api/status")
def status():
    latest = fetch_run_status()
    return jsonify({
        "as_of_utc": datetime.now(timezone.utc).isoformat(),
        "source": "read-only public GitHub Actions run metadata",
        "repository": GITHUB_REPO,
        "runs": latest["runs"],
        "source_error": latest["error"],
        "real_agent_work_verified_by_dashboard": False,
        "cryptocurrency_received_verified_by_dashboard": False,
        "caveat": "A successful workflow may create agent artifacts; inspect them individually. No defined dormant role is counted as executing.",
    })


@app.get("/")
def index():
    data = fetch_run_status()
    out = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        "<title>Agent Operations — Status</title>",
        "<style>",
        "body{font:16px system-ui,Arial,sans-serif;max-width:960px;margin:30px auto;padding:0 18px;background:#f7f8fa;color:#222}",
        "h1{font-size:27px} h2{font-size:20px} a{color:#16589f}",
        "main{background:white;padding:20px 24px;border:1px solid #ddd;border-radius:12px}",
        "table{border-collapse:collapse;width:100%;font-size:14px} th,td{padding:10px 8px;text-align:left;border-bottom:1px solid #ddd}",
        "th{background:#f2f4f6} .note{color:#555} .tag{font-weight:600} .wrap{overflow-x:auto}",
        "</style></head><body><main>",
        "<h1>Independent Agent Operations</h1>",
        "<p class='note'>Public read-only dashboard for actual GitHub Actions research workflows.</p>",
        "<p><a href='" + escape(RUNS_PAGE, quote=True) + "'>Open full workflow results and agent artifacts</a></p>",
        "<h2>Recent workflow runs</h2>",
    ]
    if data["error"]:
        out.append("<p class='note'>" + escape(data["error"]) + "</p>")
    out.append("<div class='wrap'><table><thead><tr><th>Workflow</th><th>Status</th><th>Result</th><th>Created (UTC)</th></tr></thead><tbody>")
    for run in data["runs"]:
        url = run["url"] if run["url"].startswith("https://github.com/") else RUNS_PAGE
        out.append("<tr><td><a href='" + escape(url, quote=True) + "'>" + escape(run["name"]) + "</a></td>" +
                   "<td>" + escape(run["status"]) + "</td>" +
                   "<td class='tag'>" + escape(run["conclusion"]) + "</td>" +
                   "<td>" + escape(run["created_at"]) + "</td></tr>")
    if not data["runs"]:
        out.append("<tr><td colspan='4'>No runs currently available.</td></tr>")
    out.extend([
        "</tbody></table></div>",
        "<h2>Evidence standard</h2>",
        "<p class='note'>A scheduled or pending workflow is not an executed agent. Successful runs must be checked for individual agent documents and completed model/source checks. Defined role identities are not live instances. No cryptocurrency receipts are established by this page.</p>",
        "<p class='note'>This free Render web dashboard can sleep when idle. GitHub Actions remains responsible for scheduled research and evidence delivery.</p>",
        "<p><a href='/api/status'>Machine-readable status</a> · <a href='/health'>Service health</a></p>",
        "</main></body></html>",
    ])
    return Response("".join(out), content_type="text/html; charset=utf-8")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
