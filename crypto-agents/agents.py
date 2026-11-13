"""Thirty independent research roles. Public-source, read-only. No money movement."""
import json, os, sys, time, urllib.request, urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from social_scan import scan_social
from deep_research import due_diligence
from director_inbox import read_inbox
from wallet_routes import private_directory_status
from friendly_pitch import warm_pitch
from understanding_response import understanding_report, BRIEF

role_id=os.environ.get("ROLE_ID") or (sys.argv[1] if len(sys.argv)>1 else "D01")
role=next((r for r in json.loads(Path("crypto-agents/roles.json").read_text()) if r["id"]==role_id), None)
if role is None: raise SystemExit("Unknown role")
owner_brief=json.loads(Path("crypto-agents/owner_brief.json").read_text(encoding="utf-8"))
owner_context=owner_brief["agent_prompt"]
AUTONOMY=json.loads(Path("crypto-agents/autonomy_policy.json").read_text(encoding="utf-8"))
EARNINGS=json.loads(Path("crypto-agents/earnings_playbook.json").read_text(encoding="utf-8"))
EARNING_PATHS=list(EARNINGS["where_to_find_pay"].keys())
FRIENDLY=json.loads(Path("crypto-agents/friendly_earnings_directive.json").read_text(encoding="utf-8"))
SHARED=json.loads(Path("crypto-agents/shared_understanding.json").read_text(encoding="utf-8"))
directors_goal=SHARED["director_mandates"].get(role["director"],"Earn genuine cryptocurrency via lawful paid work")

coordination_inbox=read_inbox(role_id)
wallet_directory_status=private_directory_status()


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
def analyze(leads, research, branch_summary):
    if not leads:return {"status":"no_leads","review":"","critical_challenge":""}
    try:
        import torch
        from transformers import pipeline
        model=pipeline("text-generation",model="HuggingFaceTB/SmolLM2-135M-Instruct",device=-1)
        info=[{"title":x["title"],"url":x["url"],"excerpt":x["excerpt"][:120]} for x in leads[:3]]
        checked=research.get("dossiers",[])[:2]
        compact_checks=[{"title":x["title"],"source_status":x["source_status"],"score":x["score_for_followup_not_payment_probability"],"risks":x["counter_evidence_and_risks"][:3],"unknowns":x["unknowns"][:3]} for x in checked]
        subordinate_findings=[{"agent":x.get("discovered_by"),"title":x.get("title"),"url":x.get("url")} for x in branch_summary.get("sample_unverified_leads", [])[:3]]
        prompt=[
          {"role":"system","content":"You are a director or independently thinking assistant using an evidence-first ChatGPT-style method. Your ONLY success condition is legally earned cryptocurrency actually received by the owner's approved address on the correct chain; no fiat-only payment, unclaimed points, testnet tokens, or promises. Use sources skeptically and do not fabricate earnings."},
          {"role":"user","content":json.dumps({
            "owner_professional_context":BRIEF["whom_you_work_for"]["description"],
            "professional_strengths":BRIEF["whom_you_work_for"]["strengths"][:5],
            "must_answer_in_own_words":"Explain whose legitimate professional work we support, your distinct role and single director boss, your next original-source check and exact proof of real crypto received.",
            "owner_real_goal":SHARED["owner_intent"]["real_goal"],
            "director_strategy":directors_goal,
            "coordinator_reasoning_method":SHARED["assistant_method_the_directors_should_understand"]["reasoning"],
            "coordinator_execution_limit":SHARED["assistant_method_the_directors_should_understand"]["execution"],
            "role":role_id,
            "handoff_urls_unverified":coordination_inbox.get("handoff_urls",[])[:2],
            "leads":info[:2],
            "checks":compact_checks[:2],
            "subordinate_findings":subordinate_findings[:2],
            "request":"Independently find the best credible opportunity to earn cryptocurrency paid to a correct owner-approved address. State verified facts, unknowns, risks, and the next genuinely executable action. Reject unverified offers."
          },ensure_ascii=False)[:2900]}
        ]
        response=model(prompt,max_new_tokens=120,do_sample=False,return_full_text=False)
        result=response[0]["generated_text"]
        if isinstance(result,list):result=result[-1].get("content","")
        # Separate adversarial pass challenges the initial recommendation.
        challenge=[
            {"role":"system","content":"You are a skeptical second reviewer. Do not claim any payment, opportunity, eligibility or promise is verified unless the supplied independent evidence establishes it. You may recommend rejecting everything."},
            {"role":"user","content":"Critique this first-pass paid-opportunity recommendation, looking for missing payer evidence, scams, false amounts, country restrictions, closed issues and unsuitable work. Source records and unknowns: "+json.dumps(compact_checks,ensure_ascii=False)[:2500]+" First pass: "+str(result)[:650]+" Give no more than 100 words and one clear next action."}
        ]
        try:
            response2=model(challenge,max_new_tokens=120,do_sample=False,return_full_text=False)
            result2=response2[0]["generated_text"]
            if isinstance(result2,list): result2=result2[-1].get("content","")
            critical=str(result2)[:900]
            crit_status="completed"
        except Exception as critique_error:
            critical="Separate model challenge unavailable: "+str(critique_error)[:130]
            crit_status="unavailable"
        return {"status":"llm_completed","review":str(result)[:900],
                "critical_challenge":critical,"critical_challenge_status":crit_status}
    except Exception as e: return {"status":"llm_unavailable","review":"Source discovery only; AI analysis not run.","error":str(e)[:180]}
company_summary_file=Path("company-reports")/(role_id+"-COMPANY-SUMMARY.json")
company_summary=json.loads(company_summary_file.read_text(encoding="utf-8")) if company_summary_file.exists() else {
    "director_id":role_id,"configured_managers":0,"configured_workers":0,
    "status":"independent_assistant_not_company_supervisor"}
branch_summary={
    "manager":role_id, "subagent_count":company_summary.get("workers_attempted_this_cycle",0),
    "sample_unverified_leads":company_summary.get("manager_findings",[])[:6]
}
leads,errors=collect()
research=due_diligence(leads,max_items=5)
analysis=analyze(leads,research,branch_summary)
out={"role":role["id"],"name":role["name"],"director":role["director"],"mission":role["mission"],
     "checked_at_utc":datetime.now(timezone.utc).isoformat(),"verified_paid_receipts":[],
     "warning":"All found items are UNVERIFIED leads, not payments, offers, or confirmed jobs. Never pay application fees or connect wallets.",
     "leads":leads,"ai_analysis":analysis,"deep_research":research,"source_errors":errors,
     "understanding_response":understanding_report(role_id,role["name"],"OWNER" if role_id==role["director"] else role["director"],
         role["mission"],analysis,[x.get("url") for x in leads[:2]]),
     "owner_professional_brief_version":BRIEF["version"],
     "friendly_outreach_drafts":[warm_pitch(x,role=role["mission"],writer_id=role_id) for x in leads[:3]],
     "friendly_earning_directive":FRIENDLY["version"],
     "communication_activity":"Drafted only; not yet sent externally.",
     "share_evidence_with_director":role["director"],
     "company_supervision":company_summary,"delegated_research_sample":branch_summary,
     "owner_brief_version":owner_brief["version"],
     "autonomy_policy_version":AUTONOMY["version"],
     "earnings_playbook_version":EARNINGS["version"],
     "source_code_earning_channels":EARNING_PATHS,
     "owner_wallet_directory_access":wallet_directory_status["status"],
     "owner_payment_route_ids_available":wallet_directory_status["route_ids"],
     "owner_understanding":SHARED["owner_intent"]["real_goal"],
     "coordinator_reasoning_method":SHARED["assistant_method_the_directors_should_understand"]["reasoning"],
     "director_priority_understood":directors_goal,
     "shared_understanding_version":SHARED["version"],
     "owner_authorization":role.get("owner_authorization",""),
     "payment_priority":role.get("payment_priority",""),
     "cross_domain_authority":role.get("cross_domain_authority",""),
     "meeting_url":role.get("meeting_url",""),
     "director_coordination_inbox":coordination_inbox,
     "director_teamwork_contract":role.get("teamwork_contract",{}),
     "meeting_instruction":role.get("meeting_instruction",""),
     "execution_intent":role.get("execution_intent",""),
     "independent_action_status":"Research and proposal preparation permitted; public posting, job applications, negotiations and payment collection not available in this workflow.",
     "crypto_only_success_condition":"Genuine cryptocurrency received at approved correct-network wallet route; not fiat, platform points or claimed offers.",
     "payout_request_policy":"Use owner-approved route on exact supported chain only when there is a real payer. Do not publish full user wallet mappings into public research artifacts."}
Path("reports").mkdir(exist_ok=True)
Path("reports",role_id+".json").write_text(json.dumps(out,indent=2))
print(role_id,"leads",len(leads),"AI",analysis["status"],"errors",len(errors))
