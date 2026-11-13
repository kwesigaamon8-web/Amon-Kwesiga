"""Run genuine opening introductions for 80 sampled research agents: 10 D, 20 A,
10 M, 10 W, 10 S, 10 G and 10 H. Every role gets a separate actual model
invocation. No fictional speeches for 375 billion dormant software identities.
"""
import csv,json,os,time,urllib.request,urllib.parse
from pathlib import Path
from datetime import datetime,timezone
from subagent_factory import describe_child
from microcompany_factory import describe_micro_worker
from mega_branch_factory import describe_branch_worker
from understanding_response import understanding_report,BRIEF

OUT=Path("system-introductions")
OUT.mkdir(exist_ok=True)
SOURCE=Path("crypto-agents")
ROLES=json.loads((SOURCE/"roles.json").read_text(encoding="utf-8"))
REG={v["id"]:v for v in csv.DictReader((SOURCE/"agent_registry.csv").open(encoding="utf-8"))}
PUBLIC=json.loads((SOURCE/"branch_brief.json").read_text(encoding="utf-8"))["public_payment_routes"]
REPONAME="kwesigaamon8-web/Amon-Kwesiga"
EXPECTED=375188632680

def roster():
    result=[]
    for i in range(1,11):
        d=f"D{i:02d}"
        for rid in (d,d+"-A",d+"-B"):
            v=next(x for x in ROLES if x["id"]==rid)
            result.append({"id":rid,"name":v["name"],"parent":"OWNER" if rid==d else d,
                "level":"director" if rid==d else "independent_assistant","task":v["mission"]})
        m=d+"-M01"
        w=m+"-W01"
        result.append({"id":m,"name":REG[m]["agent_name"],"parent":d,
                "level":"manager","task":"Supervise and independently challenge 50 workers"})
        result.append({"id":w,"name":REG[w]["agent_name"],"parent":m,
                "level":"worker","task":REG[w]["assignment"]})
        s=describe_child(w,REG[w]["agent_name"],1)
        result.append({"id":s["id"],"name":s["agent_name"],"parent":w,
                "level":"delegated_subagent","task":s["objective"]})
        g=describe_micro_worker(s["id"],s["agent_name"],1)
        result.append({"id":g["id"],"name":g["name"],"parent":s["id"],
                "level":"microcompany_worker","task":g["independent_research_objective"]})
        h=describe_branch_worker(g["id"],g["name"],1)
        result.append({"id":h["id"],"name":h["name"],"parent":g["id"],
                "level":"mega_branch_worker","task":h["mission"]})
    assert len(result)==80 and len({x["id"] for x in result})==80
    return result

def infer(model,x):
    if model is None:return {"status":"llm_unavailable","analysis":""}
    prompt={"my_id":x["id"],"my_name":x["name"],"single_reporting_parent":x["parent"],
        "my_role":x["level"],"my_task":x["task"][:130],
        "owner_profession":BRIEF["whom_you_work_for"]["description"],
        "owner_goal":BRIEF["owner_instructions"]["single_success_condition"],
        "instruction":"Introduce yourself beginning Hello, I am; in your own words identify your one supervisor, explain a practical specific paid crypto research task, and distinguish a real payment from a lead. No made-up accomplishments."}
    try:
        messages=[{"role":"system","content":"You are an assigned AI research role, not human. Speak in first person, under 80 words. No claims of actual money, signed contracts or sent posts."},
                  {"role":"user","content":json.dumps(prompt,ensure_ascii=False)[:1300]}]
        value=model(messages,max_new_tokens=85,do_sample=False,return_full_text=False)[0]["generated_text"]
        if isinstance(value,list):value=value[-1].get("content","")
        if isinstance(value,dict):value=value.get("content","")
        return {"status":"model_completed","analysis":str(value)[:850],"parent_id":x["parent"]}
    except Exception as exc:
        return {"status":"llm_execution_failed","analysis":"","error":str(exc)[:130],"parent_id":x["parent"]}

def post_conference(replies):
    token=os.environ.get("GH_TOKEN","")
    if not token or os.environ.get("GITHUB_REPOSITORY")!=REPONAME:
        return "GitHub conference posting unavailable; reports saved"
    good=[r for r in replies if r["model_status"]=="model_completed" and r["own_words"]]
    if not good:return "No completed model replies; no speech is fabricated"
    day=datetime.now(timezone.utc).strftime("%Y-%m-%d")
    marker="<!-- real-system-introductions:"+day+" -->"
    url=f"https://api.github.com/repos/{REPONAME}/issues/7/comments"
    headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json",
             "X-GitHub-Api-Version":"2022-11-28","User-Agent":"Real-AI-Team-Introduction/1"}
    def call(method="GET",payload=None,suffix=""):
        req=urllib.request.Request(url+suffix,headers=headers,method=method,
                    data=json.dumps(payload).encode("utf-8") if payload is not None else None)
        with urllib.request.urlopen(req,timeout=18) as res:
            return json.loads(res.read(450000))
    try:
        for page in range(1,4):
            chunks=call(suffix=f"?per_page=100&page={page}")
            if any(marker in (r.get("body") or "") for r in chunks):
                return "Already posted the system's introduction today"
            if len(chunks)<100:break
        lines=[marker,"## Verified system introductions — "+day,"",
            f"**Actually generated AI model introductions: {len(good)}/80 selected role identities.**",
            "The remaining defined identities have not spoken. These are separate model responses through the owner's ONE GitHub automation account, not individually logged-in social users.",""]
        for d in [f"D{i:02d}" for i in range(1,11)]:
            own=[x for x in good if x["id"][:3]==d]
            if not own:continue
            lines.append("### "+d)
            for level in ("director","independent_assistant","mega_branch_worker"):
                x=next((z for z in own if z["level"]==level),None)
                if x:
                    speech=x["own_words"].replace("\n"," ").replace(chr(96),"'")[:500]
                    lines.append("- **"+x["id"]+"**, parent **"+x["parent"]+"**; actual model reply: "+speech)
        lines+=["","### Already approved PUBLIC crypto receiving addresses"]
        for k,v in PUBLIC.items():
            lines.append("- "+v["asset"]+" on "+v["network"]+": "+v["address"])
        lines+=["","For actual agreed paid work only: reconfirm each asset, network and address with the owner before any payer sends. Binance memos/private routes and credentials are not distributed. **This meeting verifies no incoming coin payments.**",
            "","Individual response reports (including non-replies and failures) are archived at:",
            "https://github.com/"+REPONAME+"/actions/runs/"+os.environ.get("GITHUB_RUN_ID","")]
        result=call("POST",{"body":"\n".join(lines)})
        return result.get("html_url","GitHub posted")
    except Exception as exc:
        return "Conference post unavailable: "+str(exc)[:120]

def main():
    started=datetime.now(timezone.utc).isoformat()
    try:
        from transformers import pipeline
        model=pipeline("text-generation",model="HuggingFaceTB/SmolLM2-135M-Instruct",device=-1)
        load_error=None
    except Exception as exc:
        model=None;load_error=str(exc)[:150]
    reports=[]
    for i,x in enumerate(roster(),1):
        raw=infer(model,x)
        reply=understanding_report(x["id"],x["name"],x["parent"],x["task"],raw)
        record={"id":x["id"],"name":x["name"],"parent":x["parent"],"level":x["level"],
            "task":x["task"],"model_status":raw["status"],"own_words":reply["response_in_own_generated_words"],
            "understanding_status":reply["understanding_check_status"],"actual_model_generated":raw["status"]=="model_completed",
            "verified_coins_received":[]}
        reports.append(record)
        (OUT/(x["id"]+".json")).write_text(json.dumps(record,indent=2),encoding="utf-8")
        if i%10==0:print("INTRODUCTIONS_PROCESSED",i,"model_success",sum(r["actual_model_generated"] for r in reports),flush=True)
    publication=post_conference(reports)
    summary={"started_utc":started,"sampled_agents":len(reports),"defined_roles":EXPECTED,
      "actual_separate_model_introductions":sum(r["actual_model_generated"] for r in reports),
      "model_load_error":load_error,
      "conference_result":publication,"public_payment_routes":PUBLIC,
      "private_wallet_map_exposed":False,"verified_received_cryptocurrency":[],
      "truth":"Only individually recorded completed model responses count as introductions. The other defined identities did not speak."}
    (OUT/"SUMMARY.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    (OUT/"SUMMARY.md").write_text("# System-wide introduction report\n\n"+
         "Individually generated model replies: "+str(summary["actual_separate_model_introductions"])+"/80 selected roles.\n\n"+
         "Defined role identities: 375,188,632,680; these are not active agents.\n\n"+
         "GitHub conference: "+publication+"\n\n"+
         "See separate role JSON files for actual wording. No coins verified from these introductions.\n",encoding="utf-8")
    print("SYSTEM_INTRO_RESULT",json.dumps({"replies":summary["actual_separate_model_introductions"],"selected":80,
       "conference":publication}),flush=True)

if __name__=="__main__":main()
