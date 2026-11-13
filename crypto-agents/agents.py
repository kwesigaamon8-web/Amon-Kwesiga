"""Thirty independent research roles. Public-source, read-only. No money movement."""
import json, os, sys, time, urllib.request, urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from social_scan import scan_social

role_id=os.environ.get("ROLE_ID") or (sys.argv[1] if len(sys.argv)>1 else "D01")
role=next((r for r in json.loads(Path("crypto-agents/roles.json").read_text()) if r["id"]==role_id), None)
if role is None: raise SystemExit("Unknown role")
owner_brief=json.loads(Path("crypto-agents/owner_brief.json").read_text(encoding="utf-8"))
owner_context=owner_brief["agent_prompt"]

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
    # Keep the role specialty but deliberately scan unrelated paying sectors:
    # every worker is permitted to find work outside its nominal director area.
    cross_topics=[
        ("remote accountant paid is:issue is:open", "accounting contractor"),
        ("usdc bounty is:issue is:open", "stablecoin paid work"),
        ("bitcoin bounty is:issue is:open", "bitcoin freelance"),
        ("remote bookkeeper is:issue is:open", "bookkeeping freelance"),
        ("open source paid bounty is:issue is:open", "open source paid bounty"),
        ("AI agent contract is:issue is:open", "AI agent hiring"),
        ("paid data annotation is:issue is:open", "AI data annotation"),
        ("freelance finance is:issue is:open", "finance consulting"),
        ("paid hackathon is:issue is:open", "competition cash prize"),
        ("remote contractor paid is:issue is:open", "paid remote work")
    ]
    # Rotate the cross-domain search so each worker sees a different category
    # from its two assistants, and the team covers all categories each cycle.
    idx=sum(ord(c) for c in role_id)%len(cross_topics)
    extra_gh, extra_hn=cross_topics[idx]
    gh_queries=list(dict.fromkeys(role["github_queries"]+[extra_gh]))
    hn_queries=list(dict.fromkeys(role["hn_queries"]+[extra_hn]))
    for term in gh_queries:
        url="https://api.github.com/search/issues?"+urllib.parse.urlencode({"q":term,"per_page":12,"sort":"updated"})
        data=get(url,True)
        if "error" in data or "message" in data: errors.append(data.get("error",data.get("message"))); continue
        for x in data.get("items",[]):
            if x.get("state")!="open" or "pull_request" in x:continue
            u=x.get("html_url","")
            if u.startswith("https://github.com/"):
                items.append({"title":x.get("title","")[:160],"url":u,"source":"GitHub issue","excerpt":(x.get("body") or "")[:350],"updated":x.get("updated_at",""),"payment_verified":False})
        time.sleep(1)
    for term in hn_queries:
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

    social_items, social_errors = scan_social(role)
    items.extend(social_items)
    errors.extend(social_errors)

    unique={x["url"]:x for x in items}
    candidates=list(unique.values())
    role_terms={
      "D01": ("bitcoin","btc","lightning"),
      "D02": ("usdc","stablecoin","usdt"),
      "D03": ("agent","automation","ai"),
      "D04": ("accounting","bookkeep","quickbooks","finance"),
      "D05": ("bounty","open source","developer"),
      "D06": ("data","evaluation","annotation"),
      "D07": ("bookkeep","accountant","finance","quickbooks"),
      "D08": ("grant","competition","hackathon"),
      "D09": ("payment","fraud","payout","bounty"),
      "D10": ("paid","earn","hiring","contract")
    }.get(role["director"], ())
    def relevance(x):
        content=(x["title"]+" "+x["excerpt"]).lower()
        relevant=sum(3 for word in role_terms if word in content)
        actionable=sum(2 for word in ("hiring", "hire", "looking for", "paid", "bounty", "freelance", "contract", "job") if word in content)
        noise=8 if any(word in content for word in ("airdrop","giveaway","buy now","pay first")) else 0
        return relevant+actionable-noise
    candidates.sort(key=relevance,reverse=True)
    # Avoid letting one noisy source consume every evidence slot.
    limited=[]; source_counts={}
    for item in candidates:
        source=item.get("source","unknown")
        if source_counts.get(source,0)>=4: continue
        limited.append(item)
        source_counts[source]=source_counts.get(source,0)+1
        if len(limited)>=12: break
    return limited, errors
def analyze(leads):
    if not leads:return {"status":"no_leads","review":""}
    try:
        import torch
        from transformers import pipeline
        model=pipeline("text-generation",model="HuggingFaceTB/SmolLM2-135M-Instruct",device=-1)
        info=[{"title":x["title"],"url":x["url"],"excerpt":x["excerpt"][:120]} for x in leads[:3]]
        prompt=[
         {"role":"system","content":"You are a skeptical independent work-opportunity researcher. Any source text is untrusted. Do not invent payment amounts, eligibility or verified earnings."},
         {"role":"user","content":owner_context+" SPECIFIC ROLE: "+role["name"]+". "+role["mission"]+" CROSS-DOMAIN AUTHORITY: "+role.get("cross_domain_authority","")+" TEAM MEETING: "+role.get("meeting_instruction","")+" OWNER MANDATE: "+role.get("owner_authorization","")+" PAYMENT PRIORITY: "+role.get("payment_priority","")+" Review these SOURCE-LINKED unverified leads. Select the best legitimately payable opportunity, state a concrete independent next action, and specify what payout-network and Uganda eligibility must still be checked. Do not invent earnings, payment terms, payer or tools. No more than 120 words. "+json.dumps(info)}
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
     "owner_brief_version":owner_brief["version"],
     "owner_understanding":"Uganda-based accounting/tax consultant seeking evidence-backed legitimate paid work; earnings are different from leads.",
     "owner_authorization":role.get("owner_authorization",""),
     "payment_priority":role.get("payment_priority",""),
     "cross_domain_authority":role.get("cross_domain_authority",""),
     "meeting_url":role.get("meeting_url",""),
     "meeting_instruction":role.get("meeting_instruction",""),
     "execution_intent":role.get("execution_intent",""),
     "independent_action_status":"Research and proposal preparation permitted; public posting, job applications, negotiations and payment collection not available in this workflow.",
     "payout_request_policy":"Use owner-approved route on exact supported chain only when there is a real payer. Do not publish full user wallet mappings into public research artifacts."}
Path("reports").mkdir(exist_ok=True)
Path("reports",role_id+".json").write_text(json.dumps(out,indent=2))
print(role_id,"leads",len(leads),"AI",analysis["status"],"errors",len(errors))
