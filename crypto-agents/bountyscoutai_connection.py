"""Read-only Moltbook account verification for BountyScoutAI.
Requires MOLTBOOK_BOUNTYSCOUTAI_API_KEY as a GitHub Actions secret.
Never prints the credential or publishes posts.
"""
import json, os, urllib.request, urllib.error
from pathlib import Path

def main():
    token = os.environ.get("MOLTBOOK_BOUNTYSCOUTAI_API_KEY", "").strip()
    out = Path("reports/bountyscoutai-connection.json")
    out.parent.mkdir(exist_ok=True)
    result = {"account": "BountyScoutAI", "connected": False, "reason": "missing GitHub Actions secret"}
    if token:
        req = urllib.request.Request("https://www.moltbook.com/api/v1/agents/me",
            headers={"Authorization": "Bearer " + token, "Accept": "application/json",
                     "User-Agent": "BountyScoutAI-workforce-connector/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                obj = json.load(response)
            agent = obj.get("agent", obj) if isinstance(obj, dict) else {}
            name = agent.get("name", "") if isinstance(agent, dict) else ""
            result = {"account": "BountyScoutAI", "connected": name.lower() == "bountyscoutai",
                      "reported_name": name, "reason": "identity verified" if name.lower() == "bountyscoutai" else "unexpected identity"}
        except (urllib.error.URLError, ValueError, TimeoutError) as exc:
            result["reason"] = "API request failed: " + type(exc).__name__
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    if token and not result["connected"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
