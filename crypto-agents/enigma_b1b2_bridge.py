"""Connect 14 GitHub AI workers to original Moltbook B1/B2 as INTERNAL work aides."""
import argparse,json,hashlib,subprocess
from pathlib import Path
from datetime import datetime,timezone
REPO="kwesigaamon8-web/Amon-Kwesiga"
PARENTS={"A":"transferexperiment","B":"BountyScoutAI"}
TASKS={
"G01":("World research, source checking","Useful original software engineering"),
"G02":("Verify market problems and buyer requirements","Software prototyping and QA"),
"G03":("Community services research","Low-data accessible software tests"),
"G04":("License and attribution research","Privacy/security code reviews"),
"G05":("Research real permitted buyer requests","Custom delivery and proposal QA"),
"G06":("Check customer acceptance requirements","Product implementation and tests"),
"G07":("Check Bitcoin transaction public evidence","Review mining economics and payment QA"),
}
EXPECTED={f"ENIGMA-{g}-{l}" for g in TASKS for l in PARENTS}
def one(agent,doc=None,url=None):
    if agent not in EXPECTED:raise ValueError("Unexpected worker identity")
    g,role=agent.split("-")[1:]
    result={"agent_id":agent,"verified_moltbook_supervisor":PARENTS[role],
        "assigned_task":TASKS[g][0 if role=="A" else 1],
        "github_support_only":True,"independent_moltbook_account":False,
        "real_model_call":False,"status":"NOT_PROVEN",
        "untrusted_model_notes":None,"evidence_run":url,"buyer_accepted":False,
        "crypto_receipt_verified":False}
    if not isinstance(doc,dict):return result
    if doc.get("agent_id")!=agent:result["status"]="SOURCE_ID_MISMATCH";return result
    notes=doc.get("generated_work_notes")
    if doc.get("actual_model_call_completed") is not True or not isinstance(notes,str) or not notes.strip():return result
    result.update({"real_model_call":True,"status":"REAL_MODEL_RESPONSE_AWAITING_FACT_CHECK",
        "untrusted_model_notes":notes.strip()[:1400],
        "notes_sha256":hashlib.sha256(notes.strip().encode()).hexdigest()})
    return result
def board_from(records):
    if len(records)!=14 or {r.get("agent_id") for r in records}!=EXPECTED:
        raise ValueError("14 unique worker records required")
    queues=[{"parent":p,"support_workers":sorted(
        [r for r in records if r["verified_moltbook_supervisor"]==p],key=lambda x:x["agent_id"])}
        for p in PARENTS.values()]
    assert all(len(q["support_workers"])==7 for q in queues)
    return {"created_utc":datetime.now(timezone.utc).isoformat(),
        "owner":"Enigma","connection":"Internal GitHub handoff, not shared Moltbook credentials",
        "registered_parent_handles":list(PARENTS.values()),
        "linked_internal_workers":14,"real_model_results":sum(x["real_model_call"] for x in records),
        "moltbook_accounts_created":0,"emails_sent":0,"external_posts":0,
        "paid_contracts_proven":0,"crypto_deposits_proven":0,"queues":queues}
def gh(*args):
    r=subprocess.run(["gh",*args],text=True,capture_output=True,timeout=35,check=False)
    if r.returncode:raise RuntimeError("GitHub read failed")
    return r.stdout
def fetch_existing(folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    outputs={}
    for g in TASKS:
        try:runs=json.loads(gh("run","list","--repo",REPO,"--workflow",f"enigma-{g.lower()}-pair.yml",
                                  "--limit","10","--json","databaseId,conclusion,status"))
        except (OSError,RuntimeError,ValueError,subprocess.TimeoutExpired):continue
        for run in runs:
            if run.get("status")!="completed" or run.get("conclusion")!="success":continue
            rid=str(run.get("databaseId",""))
            if not rid.isdecimal():continue
            pair={}
            for role in PARENTS:
                agent=f"ENIGMA-{g}-{role}"
                dest=folder/g/role;dest.mkdir(parents=True,exist_ok=True)
                try:
                    gh("run","download",rid,"--repo",REPO,"--name",
                       f"enigma-{g.lower()}-agent-{role}-evidence","--dir",str(dest))
                    obj=json.loads((dest/(agent+".json")).read_text(encoding="utf8"))
                    if obj.get("agent_id")!=agent:raise ValueError("Wrong source worker")
                    pair[agent]=(obj,f"https://github.com/{REPO}/actions/runs/{rid}")
                except (OSError,RuntimeError,ValueError,subprocess.TimeoutExpired):continue
            if len(pair)==2:
                outputs.update(pair);break
    return outputs
def main(folder,output,fetch=False):
    folder=Path(folder);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    evidence=fetch_existing(folder) if fetch else {}
    rows=[]
    for agent in sorted(EXPECTED):
        doc,url=evidence.get(agent,(None,None))
        if doc is None:
            g,role=agent.split("-")[1:]
            f=folder/g/role/(agent+".json")
            try:
                if f.is_file():doc=json.loads(f.read_text(encoding="utf8"))
            except (OSError,ValueError):doc=None
        rows.append(one(agent,doc,url))
    result=board_from(rows)
    (output/"bridge.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    lines=["# Enigma workers -> original verified B1/B2 identities",
       "","Real AI model responses from source artifacts: "+str(result["real_model_results"])+"/14",
       "New Moltbook accounts: 0; sent emails/posts: 0; proven payments: 0.",""]
    for queue in result["queues"]:
        lines.extend(["## "+queue["parent"],""])
        for r in queue["support_workers"]:
            lines.append(f"- {r['agent_id']} — {r['assigned_task']} — {r['status']}")
        lines.append("")
    (output/"bridge.md").write_text("\n".join(lines),encoding="utf8")
    print("ENIGMA_B1B2_INTERNAL_LINK",json.dumps({"B1":7,"B2":7,
       "real_model_results":result["real_model_results"],"external_posts":0,"emails_sent":0}))
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--folder",default="enigma-bridge-input")
    p.add_argument("--output",default="enigma-bridge-output")
    p.add_argument("--fetch",action="store_true")
    a=p.parse_args()
    main(a.folder,a.output,a.fetch)
