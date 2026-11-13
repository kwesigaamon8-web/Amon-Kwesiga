"""Owner-authorized public conference updates, one substantive reply per company/day.

This uses exactly one authenticated repository Actions identity. It does not
impersonate 7,680 social users or send unsolicited messages. Every claimed
activity is computed from actual downloaded worker, manager and AI reports.
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO="kwesigaamon8-web/Amon-Kwesiga"
TOKEN=os.environ.get("GH_TOKEN") or ""
RUN_ID=os.environ.get("GITHUB_RUN_ID","")
if not TOKEN or os.environ.get("GITHUB_REPOSITORY")!=REPO:
    raise SystemExit("No authenticated owner repository action available")
ROOT=Path("combined-reports")
hierarchy=json.loads(Path("crypto-agents/company_hierarchy.json").read_text(encoding="utf-8"))
url=f"https://api.github.com/repos/{REPO}/issues/7/comments"
headers={"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json",
 "X-GitHub-Api-Version":"2022-11-28","User-Agent":"OwnerTeamConference/1.0"}

def call(path,method="GET",payload=None):
    request=urllib.request.Request(path,headers=headers,method=method,
      data=json.dumps(payload).encode("utf-8") if payload is not None else None)
    with urllib.request.urlopen(request,timeout=20) as response:
        return json.loads(response.read(500000))

reports,companies,managers,workers={},{},{},{}
for path in ROOT.rglob("*.json"):
    try:
        item=json.loads(path.read_text(encoding="utf-8"))
    except (ValueError,OSError):
        continue
    if item.get("role") and isinstance(item.get("leads"),list):
        reports[item["role"]]=item
    elif item.get("configured_managers")==15 and item.get("director_id"):
        companies[item["director_id"]]=item
    elif item.get("workers_executed_this_cycle") is not None and item.get("manager_id"):
        managers[item["manager_id"]]=item
    elif item.get("worker_id") and item.get("manager_id"):
        workers[item["worker_id"]]=item

if not companies:
    raise SystemExit("No completed company worker reports: will not fake conference participation")
today=datetime.now(timezone.utc).strftime("%Y-%m-%d")
existing=[]
for page in range(1,5):
    chunk=call(url+"?"+urllib.parse.urlencode({"per_page":100,"page":page}))
    existing.extend(chunk)
    if len(chunk)<100:
        break
existing_text="\n".join(c.get("body") or "" for c in existing)

def safe(s,limit=100):
    return str(s or "").replace("\n"," ").replace("|","/").replace("[","(").replace("]",")")[:limit]

published=0
for comp in hierarchy["companies"]:
    director=comp["director_id"]
    c=companies.get(director)
    if c is None:
        print("No executed work for company",director,"- no reply asserted")
        continue
    marker=f"<!-- company-conference-activity:{today}:{director} -->"
    if marker in existing_text:
        print("Already posted company summary today",director)
        continue
    mgrs=[managers.get(m["id"]) for m in comp["managers"]]
    mgrs=[m for m in mgrs if m is not None]
    childs=[w for w in workers.values() if w.get("director_id")==director]
    live_workers=sum(w.get("model_inference",{}).get("status")=="model_completed" for w in childs)
    live_mgrs=sum(m.get("model_inference",{}).get("status")=="model_completed" for m in mgrs)
    searches=sum(w.get("execution_status")=="source_checked" for w in childs)
    failures=sum(w.get("execution_status")=="source_unavailable" for w in childs)
    drafts=sum(len(w.get("friendly_reply_drafts",[])) for w in childs)
    links=[]; seen=set()
    for w in childs:
        for lead in w.get("unverified_leads",[]):
            link=lead.get("url","")
            if link.startswith("https://") and link not in seen:
                links.append((safe(lead.get("title"),90),link))
                seen.add(link)
    name=comp.get("director_name",director)
    assistant_lines=[]
    for a in comp["assistant_ids"]:
        report=reports.get(a)
        if not report:
            assistant_lines.append(f"- {a}: no completed research report in this run")
        else:
            assistant_lines.append(f"- {a}: independently examined {len(report.get('leads',[]))} source-linked possibilities; AI review: {report.get('ai_analysis',{}).get('status','unknown')}")
    lines=[
       marker,
       f"## {safe(name)} — independent company conference reply · {today}",
       "",
       "**Speaking as one director-led company through the owner's GitHub automation, not as thousands of authenticated user accounts.**",
       "",
       f"Managers reporting: **{len(mgrs)}/15**; rotating worker reports: **{len(childs)}/30**; source searches completed: **{searches}**, errors: **{failures}**.",
       f"Independent AI model responses confirmed by role reports: workers **{live_workers}**, managers **{live_mgrs}**. Warm evidence-linked reply **drafts (not sent): {drafts}**.",
       "",
       "**My two independent assistants:**",*assistant_lines,
       "","**Unverified work leads our researchers want to investigate:**"
    ]
    if links:
        for title,link in links[:3]:
            lines.append(f"- [{title}]({link}) — source link only; payer, true compensation, country eligibility and scope must still be verified")
    else:
        lines.append("- No current lead justified a confident paid-work claim. We continue searching rather than making up a prospect.")
    lines.extend([
      "",
      "**Invitation:** If you are a genuine employer, client, agent or developer with a paying task, please share the original request, the expected deliverable, compensation, and how work would be accepted. We can consider BTC or genuine USDC on a mutually confirmed correct network for legitimately delivered work.",
      "[Owner-published public receiving-address directory](https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/PUBLIC_RECEIVING_ADDRESSES.md). Before paying, verify one exact owner-approved asset/address/network; Binance candidates are NOT payment-ready. The directory link is not evidence of a payment.",
      "",
      "Our managers independently evaluate specialist research and report to one director; each director shares evidence with the wider team. No employment, offer acceptance, public DM, transaction or income is claimed by this comment.",
      f"[Inspect the actual underlying run and its reports](https://github.com/{REPO}/actions/runs/{RUN_ID})."
    ])
    try:
        post=call(url,"POST",{"body":"\n".join(lines)})
        print("COMPANY_CONFERENCE_POSTED",director,post.get("html_url",post.get("id")))
        published+=1
        time.sleep(2)
    except urllib.error.HTTPError as exc:
        print("Conference posting halted by GitHub",exc.code,"after",published,"posts")
        if exc.code in (403,429):
            break
        raise
print("SUBSTANTIVE_COMPANY_REPLIES_PUBLISHED",published)
