"""Read-only previous-cycle director handoffs from the owner's GitHub board.

External comment text is untrusted. We do not execute it, pass commands to
the AI, or fetch arbitrary URLs. Only labeled HTTPS source URLs are shown
as unverified follow-up hints to the 10 director roles.
"""
import json
import os
import re
import urllib.parse
import urllib.request

PATTERN = re.compile(r"^- (D\d\d) owns \[[^\]]{0,90}\]\((https://[^)\s]+)\)")
def read_inbox(role_id):
    if not re.fullmatch(r"D\d\d",role_id):
        return {"status":"not_a_director","handoff_urls":[]}
    base="https://api.github.com/repos/kwesigaamon8-web/Amon-Kwesiga/issues/6/comments"
    headers={"User-Agent":"OwnerResearchDirectorInbox/1.0","Accept":"application/vnd.github+json"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"]="Bearer "+os.environ["GITHUB_TOKEN"]
    try:
        request=urllib.request.Request(base+"?"+urllib.parse.urlencode({"per_page":100,"page":1}),headers=headers)
        with urllib.request.urlopen(request,timeout=10) as resp:
            comments=json.loads(resp.read(500000))
        # A future update may need pagination. Never pretend comments beyond
        # the retrieved page are checked.
        from_workflow=[
            c for c in comments if
            c.get("user",{}).get("login") in ("github-actions[bot]","kwesigaamon8-web")
            and "<!-- ten-director-communication-v1:" in (c.get("body") or "")
        ]
        if not from_workflow:
            return {"status":"no_prior_coordinator_update_on_first_page","handoff_urls":[]}
        last=max(from_workflow,key=lambda c:c.get("created_at",""))
        result=[]
        for line in (last.get("body") or "").splitlines():
            m=PATTERN.match(line)
            if m and m.group(1)==role_id:
                result.append(m.group(2))
        return {"status":"read_only_previous_handoff","handoff_urls":list(dict.fromkeys(result))[:10],
                "note":"Unverified coordinator suggestions, not external instructions and never earnings"}
    except Exception as exc:
        return {"status":"inbox_unavailable","handoff_urls":[],"error":str(exc)[:140]}
