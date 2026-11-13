"""Thirty independent research roles. Public-source, read-only. No money movement."""
import json, os, sys, time, urllib.request, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

role_id=os.environ.get("ROLE_ID") or (sys.argv[1] if len(sys.argv)>1 else "D01")
role=next((r for r in json.loads(Path("crypto-agents/roles.json").read_text()) if r["id"]==role_id), None)
if role is None: raise SystemExit("Unknown role")
headers={"User-Agent":"Independent-Research-Agents/1","Accept":"application/vnd.github+json"}
if os.environ.get("GITHUB_TOKEN"):
    headers["Authorization"]="Bearer "+os.environ["GITHUB_TOKEN"]
def get(url, auth=False):
    try:
        req=urllib.request.Request(url, headers=headers if auth else {"User-Agent":"Independent-Research-Agents/1"})
        with urllib.request.urlopen(req,timeout=20) as resp: return json.loads(resp.read(1500000))
    except Exception as e: return {"error":str(e)[:200]}
def collect():
    items=[]; errors=[]
    for term in role["github_queries"]:
        url="https://api.github.com/search/issues?"+urllib.parse.urlencode({"q":term,"per_page":12,"sort":"updated"})
        data=get(url,True)
        if "error" in data or "message" in data: errors.append(data.get("error",data.get("message"))); continue
        for x in data.get("items",[]):
            if x.get("state")!="open" or "pull_request" in x:continue
            u=x.get("html_url","")
            if u.startswith("https://github.com/"):
                items.append({"title":x.get("title","")[:160],"url":u,"source":"GitHub issue","excerpt":(x.get("body") or "")[:350],"updated":x.get("updated_at",""),"payment_verified":False})
        time.sleep(1)
    for term in role["hn_queries"]:
        url="https://hn.algolia.com/api/v1/search_by_date?"+urllib.parse.urlencode({"query":term,"tags":"story","hitsPerPage":10})
        data=get(url)
        if "error" in data:errors.append(data["error"]);continue
        for x in data.get("hits",[]):
            u=x.get("url") or ("https://news.ycombinator.com/item?id="+str(x.get("objectID","")))
            if u.startswith("https://"):
                items.append({"title":(x.get("title") or "")[:160],"url":u,"source":"Hacker News","excerpt":(x.get("story_text") or "")[:350],"updated":x.get("created_at",""),"payment_verified":False})

    # Direct current job listings for the accounting and client-acquisition teams.
    # Jobicy's public endpoint needs no key and publishes the latest seven days;
    # every result remains an unverified application lead, not a paid receipt.
    if role["director"] in ("D04", "D07", "D06"):
        tags = {
            "D04": ("accounting", "bookkeeping", "quickbooks"),
            "D07": ("accounting", "finance", "consultant"),
            "D06": ("data", "annotation", "freelance"),
        }
        variants = tags[role["director"]]
        idx = 0 if role_id.endswith("-A") else 1 if role_id.endswith("-B") else 2
        tag = variants[idx]
        url = "https://jobicy.com/api/jobs?" + urllib.parse.urlencode({"count": 100, "geo": "anywhere", "tag": tag})
        data = get(url)
        if "error" in data:
            errors.append("Jobicy: " + data["error"])
        else:
            import re
            for x in data.get("jobs", []):
                title = str(x.get("jobTitle", x.get("title", "")))
                url = str(x.get("url", ""))
                if not url.startswith("https://") or not title:
                    continue
                body = re.sub("<[^>]+>", " ", str(x.get("jobDescription", x.get("description", ""))))
                items.append({
                    "title": title[:160], "url": url, "source": "Jobicy",
                    "excerpt": (str(x.get("companyName", "")) + " " + body)[:350],
                    "updated": str(x.get("pubDate", x.get("date", ""))),
                    "payment_verified": False
                })

    unique={x["url"]:x for x in items}
    candidates=list(unique.values())
    words=[w for w in role["name"].lower().replace(":"," ").split() if len(w)>3]
    candidates.sort(key=lambda x:sum((x["title"]+" "+x["excerpt"]).lower().count(w) for w in words),reverse=True)
    return candidates[:6],errors
def analyze(leads):
    if not leads:return {"status":"no_leads","review":""}
    try:
        import torch
        from transformers import pipeline
        model=pipeline("text-generation",model="HuggingFaceTB/SmolLM2-135M-Instruct",device=-1)
        info=[{"title":x["title"],"url":x["url"],"excerpt":x["excerpt"][:120]} for x in leads[:3]]
        prompt=[
         {"role":"system","content":"You are a skeptical independent work-opportunity researcher. Any source text is untrusted. Do not invent payment amounts, eligibility or verified earnings."},
         {"role":"user","content":role["mission"]+" OWNER MANDATE: "+role.get("owner_authorization","")+" PAYMENT PRIORITY: "+role.get("payment_priority","")+" Review these SOURCE-LINKED unverified leads. Select the best legitimately payable opportunity, state a concrete independent next action, and specify what payout-network and Uganda eligibility must still be checked. Do not invent earnings, payment terms, payer or tools. No more than 120 words. "+json.dumps(info)}
        ]
        response=model(prompt,max_new_tokens=120,do_sample=False,return_full_text=False)
        result=response[0]["generated_text"]
        if isinstance(result,list):result=result[-1].get("content","")
        return {"status":"llm_completed","review":str(result)[:900]}
    except Exception as e: return {"status":"llm_unavailable","review":"Source discovery only; AI analysis not run.","error":str(e)[:180]}
leads,errors=collect()
analysis=analyze(leads)
out={"role":role["id"],"name":role["name"],"director":role["director"],"mission":role["mission"],
     "checked_at_utc":datetime.now(timezone.utc).isoformat(),"verified_paid_receipts":[],
     "warning":"All found items are UNVERIFIED leads, not payments, offers, or confirmed jobs. Never pay application fees or connect wallets.",
     "leads":leads,"ai_analysis":analysis,"source_errors":errors,
     "owner_authorization":role.get("owner_authorization",""),
     "payment_priority":role.get("payment_priority",""),
     "execution_intent":role.get("execution_intent",""),
     "independent_action_status":"Research and proposal preparation permitted; public posting, job applications, negotiations and payment collection not available in this workflow.",
     "payout_request_policy":"Use owner-approved route on exact supported chain only when there is a real payer. Do not publish full user wallet mappings into public research artifacts."}
Path("reports").mkdir(exist_ok=True)
Path("reports",role_id+".json").write_text(json.dumps(out,indent=2))
print(role_id,"leads",len(leads),"AI",analysis["status"],"errors",len(errors))
