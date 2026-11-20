"""28 B1/B2 subdivisions for the 14 Enigma GitHub agents.

Original 750,377,265,360-role *logical namespace* cloned per Enigma agent.
28 bounded OS/model tasks on launch, never 10.5 trillion running workers.
Existing verified Moltbook identities only; no new logins, emails or transfers.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, sys, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from b_registered_account_worker_map import (
    ROLES_PER_ACCOUNT, TOTAL_ROLES, role_at_global_index, packet
)
from b_certified_agent_service_router import role_index

AGENTS = tuple(f"ENIGMA-G{i:02d}-{a}" for i in range(1,8) for a in "AB")
PARENTS = {"B1":"transferexperiment","B2":"BountyScoutAI"}
PER_AGENT_ROLES = TOTAL_ROLES
ALL_ROLE_SLOTS = len(AGENTS)*PER_AGENT_ROLES
DIVISIONS = len(AGENTS)*len(PARENTS)
MODEL="HuggingFaceTB/SmolLM2-135M-Instruct"
SOURCES = {
 "G01":("worldwide useful software needs","original browser-tool defects"),
 "G02":("authentic market requirements","low-cost productivity tools"),
 "G03":("community and education needs","accessible offline software"),
 "G04":("open source permission and attribution","software safety and privacy"),
 "G05":("real public paid-task requirements","buyer-specific original service delivery"),
 "G06":("requirements for actual buyer acceptance","reproducible software testing"),
 "G07":("bitcoin payment and chain evidence","mining feasibility and SHA-256 work"),
}
RESTRICTIONS = [
 "Do not use Gmail; no emails, drafts or forwarding",
 "Do not share B1/B2 Moltbook tokens or impersonate verified accounts",
 "Do not register alternative accounts to bypass Moltbook restrictions",
 "No wallet signing, transfers, unsolicited promotion or unapproved spending",
 "All role slots are virtual until a specific independently logged model call",
 "Paid buyer, acceptance, invoice and receipt require original independent evidence",
]
assert ROLES_PER_ACCOUNT*2==TOTAL_ROLES==750_377_265_360

def utc():return datetime.now(timezone.utc).isoformat()

def role_at(global_index):
    """Invert every one of 10,505,281,715,040 logical role IDs on demand."""
    if type(global_index) is not int or global_index<0 or global_index>=ALL_ROLE_SLOTS:
        raise ValueError("Global role index out of bounds")
    agent_no,original_index=divmod(global_index,TOTAL_ROLES)
    agent=AGENTS[agent_no]
    original=role_at_global_index(original_index)
    fleet="B1" if original["company"]==PARENTS["B1"] else "B2"
    rel=role_index(original["company"],original["worker_role"])
    if rel!=original_index:raise AssertionError("Original B system mapping mismatch")
    return {"global_index":global_index,"enigma_agent":agent,"division":agent+"/"+fleet,
        "original_verified_moltbook_parent":PARENTS[fleet],
        "internal_worker_id":agent+"/"+fleet+"/"+original["worker_role"],
        "original_company_worker":original["company"]+"/"+original["worker_role"],
        "tier":original["tier"],"virtual_role_only":True,"live_model_completed":False}

def index_of(agent,fleet,original_role):
    if agent not in AGENTS or fleet not in PARENTS:raise ValueError("Wrong agent/fleet")
    return AGENTS.index(agent)*TOTAL_ROLES+role_index(PARENTS[fleet],original_role)

def hierarchy(agent,fleet):
    if agent not in AGENTS or fleet not in PARENTS:raise ValueError("Wrong division")
    return {
      "division":agent+"/"+fleet,"enigma_agent":agent,"parent_moltbook":PARENTS[fleet],
      "owner_to_worker_chain":["HUMAN_OWNER","CHIEF_D",PARENTS[fleet],agent,fleet,
                               "D01..D10","A/B + M01..M15","W01..W50","S/G/H descendants"],
      "ten_directors":[{"id":f"D{i:02d}","assistants":[f"D{i:02d}-A",f"D{i:02d}-B"],
          "managers":15,"initial_workers_per_manager":50,
          "d10_payment_evidence_only":i==10} for i in range(1,11)],
      "defined_virtual_roles":ROLES_PER_ACCOUNT,
      "original_subtree_per_director":ROLES_PER_ACCOUNT//10,
      "first_tier_worker_slots":10*15*50,
      "independent_moltbook_identity":False,
      "directors_does_not_mean_active":True,
      "reports_to":"CHIEF_D through verified "+PARENTS[fleet],
    }

def rotate(agent,fleet,cycle):
    if type(cycle)!=int or cycle<1:raise ValueError("Positive cycle required")
    seed=hashlib.sha256((agent+"/"+fleet+"/"+str(cycle)).encode()).digest()
    d=int.from_bytes(seed[0:4],"big")%9+1 # D01-D09 execute; D10 audit receipts
    m=int.from_bytes(seed[4:8],"big")%15+1
    w=int.from_bytes(seed[8:12],"big")%50+1
    role=f"D{d:02d}-M{m:02d}-W{w:02d}"
    ix=index_of(agent,fleet,role)
    selected=role_at(ix)
    selected["reports_via"]=[role,f"D{d:02d}-M{m:02d}",f"D{d:02d}",
                              agent,PARENTS[fleet],"CHIEF_D","HUMAN_OWNER"]
    selected["cycle"]=cycle
    return selected

def source_search(agent,fleet,reader=None):
    # Public GitHub issues are LEADS for human verification, not paid offers.
    topic=SOURCES[agent.split("-")[1]][0 if fleet=="B1" else 1]
    query=("is:issue is:open bounty " if fleet=="B1" else "is:issue is:open help wanted ") + (
       "software" if fleet=="B1" else "bug")
    url="https://api.github.com/search/issues?"+urllib.parse.urlencode({"q":query,"per_page":6})
    try:
        if reader is None:
            headers={"Accept":"application/vnd.github+json","User-Agent":"Enigma-B1B2-Worker/1.0"}
            if os.getenv("GITHUB_TOKEN"):headers["Authorization"]="Bearer "+os.environ["GITHUB_TOKEN"]
            req=urllib.request.Request(url,headers=headers)
            with urllib.request.urlopen(req,timeout=12) as resp:
                payload=resp.read(2_000_001)
            if len(payload)>2_000_000:
                raise ValueError("Original GitHub issue search result exceeds 2MB bound")
            doc=json.loads(payload)
        else:doc=reader(url)
        records=doc.get("items") if isinstance(doc,dict) else None
        if not isinstance(records,list):raise ValueError("No issue listing")
        issues=[]
        for it in records[:6]:
            if not isinstance(it,dict) or it.get("pull_request"):continue
            link=it.get("html_url")
            if isinstance(link,str) and link.startswith("https://github.com/"):
                issues.append({"title":str(it.get("title",""))[:140],
                    "url":link,"status":"UNVERIFIED_PUBLIC_ISSUE_NOT_PAID_JOB"})
        return {"topic":topic,"source_url":url,"status":"FETCHED_PUBLIC_CANDIDATES",
                "issues":issues,"payer_verified":False}
    except (ValueError,OSError,TimeoutError,urllib.error.URLError) as ex:
        return {"topic":topic,"source_url":url,"status":"SOURCE_UNAVAILABLE",
                "issues":[],"error_type":type(ex).__name__,"payer_verified":False}

def software_qa(agent,path="docs/global-1000-manifest.json"):
    """Actual manifest QA of distinct 40-tool tranche per Enigma agent."""
    p=Path(path)
    if not p.is_file():return {"status":"MISSING_MANIFEST","tests":{}}
    try:
        manifest=json.loads(p.read_text(encoding="utf8"))
        rows=manifest["items"]
        ix=AGENTS.index(agent)
        subset=rows[ix*40:(ix+1)*40]
        ids=[x.get("id") for x in subset if isinstance(x,dict)]
        tests={
         "release_total_equals_1000":len(rows)==1000,
         "tranche_has_40_tools":len(subset)==40,
         "ids_unique_in_tranche":len(set(ids))==40,
         "ids_form_expected_sequence":ids==[f"SW-{j:03d}" for j in range(ix*40+1,ix*40+41)],
         "all_tools_marked_free":all(x.get("free") is True for x in subset),
         "all_tools_have_url":all(isinstance(x.get("software_url"),str)
                                  and x["software_url"].startswith("global-1000.html")
                                  for x in subset),
        }
        return {"status":"TESTED" if all(tests.values()) else "ISSUES_FOUND",
                "tranche_first":ix*40+1,"tranche_last":ix*40+40,
                "tests":tests,"tests_passed":sum(tests.values())}
    except (ValueError,KeyError,TypeError,OSError) as ex:
        return {"status":"QA_ERROR_"+type(ex).__name__,"tests":{}}

def execute(agent,fleet,cycle,out,model_factory=None):
    from enigma_universal_owner_order import order as canonical_owner_order
    from directive_cascade import read_owner
    from hierarchy_command_core import task_context as centralized_role_task, ASSIGNED_CODES as ONE_CODE_PER_TIER
    from role_capability_audit import run_trial as test_actual_capability, audit as verify_capability
    from directive_understanding_gate import challenge as understanding_challenge, grade as understanding_grade
    live_owner_order=canonical_owner_order()
    full_cascade_order=read_owner()
    if full_cascade_order["owner_order_id"]!=live_owner_order["id"]:
        raise ValueError("Enigma actual model cannot run with stale owner cascade")
    div=hierarchy(agent,fleet)
    selected=rotate(agent,fleet,cycle)
    # The actual Enigma W-model uses the SAME central worker code/command
    # contract as every other B1/B2 original and Enigma root division.
    selected_original_role=selected["internal_worker_id"].split("/",2)[2]
    shared_index=TOTAL_ROLES+index_of(agent,fleet,selected_original_role)
    shared=centralized_role_task(shared_index,expected={"W"})
    if (shared["parent"]!=div["division"]+"/"+selected["reports_via"][1]
        or shared["owner_command"]["owner_order_id"]!=live_owner_order["id"]):
        raise ValueError("Enigma child role has stale command or incorrect supervisor")
    individual_capability=test_actual_capability(shared["tier"],shared["role_id"],
        shared["parent"],live_owner_order["id"])
    checked,failures=verify_capability(individual_capability,
        live_owner_order["id"],shared["parent"],shared["tier"])
    if not checked:
        raise ValueError("Enigma worker local task/capability proof failed: "+str(failures))
    research=source_search(agent,fleet)
    qa=software_qa(agent) if fleet=="B2" else None
    generator=None
    error=None
    try:
        if model_factory is not None:generator=model_factory()
        else:
            from transformers import pipeline
            generator=pipeline("text-generation",model=os.getenv("ENIGMA_MODEL_ID",MODEL),device=-1)
    except Exception as ex:
        error="MODEL_LOAD_ERROR_"+type(ex).__name__
    response=None
    if generator is not None:
        prompt=("You are an original AI worker subordinate to verified parent "+PARENTS[fleet]+
            ", division "+div["division"]+", role "+selected["internal_worker_id"]+
            ". Produce 3 specific small useful software improvements or legitimate paid-task "
            "qualification tests, with exact acceptance criteria. Public research is ONLY "
            "unverified issue data; do not claim real buyers, completed builds, approval, "
            "mining, crypto receipts, X/Moltbook posts or email. "
            "Full owner instruction digest "+full_cascade_order["owner_sha256"]+
            ". Standing owner prompt digest "+full_cascade_order["standard_sha256"]+
            ". One strict owner→Chief D→B1/B2→Enigma→director→manager→W/S/G/H path: "+str(selected["reports_via"])+
            ". Follow owner prompt protocol: preserve mission, identify exact role and parent, "
            "perform one genuine source-qualified customer task or report failure. "
            "NO EMAILS or unsolicited mass marketing, no unsupported paid receipts. "
            "This COMPLETE latest canonical human owner instruction applies: "+live_owner_order["text"]+
            " THE COMPLETE STANDING OWNER RESTRICTIONS AND REPORTING PROTOCOL ARE: "+
            full_cascade_order["standard_prompt"]+
            " Research (unverified source): "+json.dumps(research)[:850]+
            " Software QA (not customer acceptance): "+json.dumps(qa)[:400]+" Actions:")
        try:
            raw=generator(prompt,max_new_tokens=150,do_sample=False,return_full_text=False)
            response=str(raw[0].get("generated_text") or "").strip()
            if not response:raise ValueError("Empty model response")
        except Exception as ex:
            error="INFERENCE_ERROR_"+type(ex).__name__
            response=None
    # Separate model-produced answer, not proof from configured virtual roles.
    comprehension_reply=""
    comprehension_called=False
    comprehension_parent=div["division"]+"/"+selected["reports_via"][1]
    if generator is not None and response:
        try:
            raw_ack=generator(understanding_challenge(
                live_owner_order["id"],selected["internal_worker_id"],
                comprehension_parent,live_owner_order["text"]),
                max_new_tokens=245,do_sample=False,return_full_text=False)
            comprehension_reply=raw_ack[0].get("generated_text") or ""
            if isinstance(comprehension_reply,list):
                comprehension_reply=comprehension_reply[-1].get("content","")
            comprehension_reply=str(comprehension_reply).strip()
            comprehension_called=bool(comprehension_reply)
        except Exception as e:
            error=(error or "")+" COMPREHENSION_INFERENCE_ERROR_"+type(e).__name__
    comprehension_grade=understanding_grade(
        comprehension_reply,selected["internal_worker_id"],comprehension_parent,
        live_owner_order["id"],model_invocation_completed=comprehension_called,
        accepted_task_proof=False)
    state={
       "owner_order_capability_audit":individual_capability,
       "owner_order_capability_test_pass":checked,
       "central_hierarchy_role_engine":"crypto-agents/hierarchy_command_core.py",
       "one_shared_worker_program":ONE_CODE_PER_TIER[shared["tier"]],
       "centralized_owner_command_sha256":shared["owner_command"]["owner_sha256"],
       "centralized_immediate_parent":shared["parent"],
       "owner_instruction_comprehension_grade":comprehension_grade,
       "owner_directive_ack_not_assumed_for_virtual_roles":True,
       "run_utc":utc(),"agent_id":agent,"division_id":div["division"],
       "received_owner_order_id":live_owner_order["id"],
       "received_owner_order_sha256":live_owner_order["sha256"],
       "full_owner_instruction_sha256":full_cascade_order["owner_sha256"],
       "standing_prompt_sha256":full_cascade_order["standard_sha256"],
       "actual_process_received_full_owner_prompt":True,
       "model_prompt_includes_full_standing_protocol":True,
       "model_prompt_sha256":hashlib.sha256(prompt.encode("utf-8")).hexdigest() if generator is not None else None,
       "last_H_receipt_not_implied_unless_selected_is_H":True,
       "this_run_selected_role_parent_route":selected["reports_via"],
       "owner_instruction_in_prompt":True,
       "parent_moltbook_identity":div["parent_moltbook"],
       "logical_worker_capacity_per_division":ROLES_PER_ACCOUNT,
       "original_root_hierarchy":div["owner_to_worker_chain"],
       "selected_worker":selected,
       "os_pid":os.getpid(),"actual_model_completed":bool(response),
       "model_status":"COMPLETED_UNREVIEWED" if response else (error or "NOT_RUN"),
       "original_task_proposals_untrusted":response,
       "source_checks":research,"reproducible_software_qa":qa,
       "moltbook_accounts_created":0,"external_posts_sent":0,"emails_sent":0,
       "verified_earning":False,"confirmed_new_payments":0,
       "real_workers_completed_in_this_division":1 if response else 0,
       "individual_worker_textual_comprehension_candidate":comprehension_grade["textual_screen_pass"],
       "individual_worker_understanding_accepted_as_verified":False,
       "owner_receiving_wallets_unchanged":True,"safety":RESTRICTIONS,
    }
    target=Path(out)/agent
    target.mkdir(parents=True,exist_ok=True)
    file=target/(fleet+".json")
    file.write_text(json.dumps(state,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("ENIGMA_DIVISION_EXECUTION "+json.dumps({
       "division":div["division"],"os_pid":os.getpid(),
       "model_completed":bool(response),"qa_status":(qa or {}).get("status"),
       "virtual_capacity":ROLES_PER_ACCOUNT,
       "real_model_count":1 if response else 0,
       "emails":0,"posts":0,"verified_paid":0},sort_keys=True))
    return state

def summarize(root,out):
    root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for agent in AGENTS:
        for fleet in PARENTS:
            target=root/agent/(fleet+".json")
            obj=None
            try:
                if target.is_file():obj=json.loads(target.read_text(encoding="utf8"))
            except (ValueError,OSError):obj=None
            valid=isinstance(obj,dict) and obj.get("agent_id")==agent and obj.get("division_id")==agent+"/"+fleet
            done=bool(valid and obj.get("actual_model_completed") is True
                      and isinstance(obj.get("os_pid"),int) and
                      isinstance(obj.get("original_task_proposals_untrusted"),str)
                      and obj["original_task_proposals_untrusted"].strip())
            comprehension=(obj.get("owner_instruction_comprehension_grade") or {}) if valid else {}
            candidate=bool(done and comprehension.get("textual_screen_pass") is True)
            rows.append({"division":agent+"/"+fleet,"parent":PARENTS[fleet],
                "configured_virtual_roles":ROLES_PER_ACCOUNT,
                "real_model_inference_evidenced":done,
                "textual_comprehension_candidate":candidate,
                "accepted_real_customer_task_evidenced":False,
                "status":("MODEL_REPLY_COMPREHENSION_CANDIDATE_NEEDS_REAL_TASK" if candidate
                   else "MODEL_REPLY_FAILED_COMPREHENSION_SCREEN" if done
                   else "NO_VERIFIED_MODEL_RESULT")})
    report={"created_utc":utc(),"agents":len(AGENTS),"divisions":len(rows),
            "virtual_role_positions_total":ALL_ROLE_SLOTS,
            "virtual_positions_per_agent":PER_AGENT_ROLES,
            "actual_completed_inference_calls":sum(r["real_model_inference_evidenced"] for r in rows),
            "B1_results":sum(r["real_model_inference_evidenced"] for r in rows if r["parent"]==PARENTS["B1"]),
            "B2_results":sum(r["real_model_inference_evidenced"] for r in rows if r["parent"]==PARENTS["B2"]),
            "textual_comprehension_candidates":sum(r["textual_comprehension_candidate"] for r in rows),
            "independently_accepted_comprehension_and_task_proven":0,
            "individual_child_receipts_unavailable_are_not_understood":True,
            "new_moltbook_accounts":0,"emails_sent":0,"social_posts_sent":0,
            "verified_crypto_receipts":0,"hierarchies":rows}
    (out/"summary.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf8")
    md=["# Enigma fourteen-agent B1/B2 hierarchy","","System divisions: 28",
        "Virtual addressable positions: "+f"{ALL_ROLE_SLOTS:,}",
        "Actual model calls evidenced: "+str(report["actual_completed_inference_calls"])+"/28",
        "No verified customers, new deposits or 24/7 independent processes claimed.",""]
    md.extend("- "+r["division"]+" — "+r["status"] for r in rows)
    (out/"summary.md").write_text("\n".join(md)+"\n",encoding="utf8")
    print("ENIGMA_28_SYSTEM_SUMMARY "+json.dumps({
        "divisions":28,"virtual_roles":ALL_ROLE_SLOTS,
        "real_model_calls":report["actual_completed_inference_calls"],
        "B1":report["B1_results"],"B2":report["B2_results"],"paid_receipts":0}))
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--agent",choices=AGENTS)
    parser.add_argument("--fleet",choices=list(PARENTS))
    parser.add_argument("--cycle",type=int,default=1)
    parser.add_argument("--out",default="enigma-28-evidence")
    parser.add_argument("--aggregate",action="store_true")
    parser.add_argument("--input",default="enigma-28-evidence")
    args=parser.parse_args()
    if args.aggregate:summarize(args.input,args.out)
    elif args.agent and args.fleet:execute(args.agent,args.fleet,args.cycle,args.out)
    else:parser.error("Choose an agent and fleet, or --aggregate")
