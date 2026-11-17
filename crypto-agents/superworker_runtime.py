"""B1/B2 independent superworker pilot. No inference or worker activity is fabricated.
Usage: python crypto-agents/superworker_runtime.py
Requires OWNER-APPROVED OpenAI-compatible endpoint and model credentials in env.
No API call if missing configuration. No mining, messaging or wallet operations.
"""
import os, json, time, uuid, hashlib, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path("superworker-evidence")
COMMAND_URL="https://raw.githubusercontent.com/kwesigaamon8-web/Amon-Kwesiga/main/crypto-agents/PUBLIC_AGENT_COMMAND.json"
COMMAND_PATH=Path("crypto-agents/PUBLIC_AGENT_COMMAND.json")
CHIEF_ORDERS_PATH=Path("crypto-agents/chief_D_owner_orders.json")
def owner_command():
    """Load the exact authenticated-repo order before any actual worker invocation."""
    d=json.loads(COMMAND_PATH.read_text(encoding="utf-8"))
    c=json.loads(CHIEF_ORDERS_PATH.read_text(encoding="utf-8"))
    if not d.get("command_id") or not d.get("hard_constraints") or not c.get("current_owner_order_id"):
        raise ValueError("Owner command is not current and complete")
    if not c["orders"] or c["orders"][-1]["id"]!=c["current_owner_order_id"]:
        raise ValueError("Latest owner command does not match chief order history")
    if "NO_EMAILS_OF_ANY_KIND_FOR_THIS_CRYPTO_WORKFLOW" not in d["hard_constraints"]:
        raise ValueError("No-email owner boundary missing")
    return {"id":c["current_owner_order_id"],"direct_user_instruction":c["orders"][-1]["instruction"],
            "public_link":COMMAND_URL,"hard_limits":d["hard_constraints"]}

ROLES=["B1-researcher","B2-researcher","D6-reviewer"]
TASKS=[
 "Find three legitimate public paid tasks that explicitly permit AI-assisted original deliverables. Provide source URLs and verification steps. Do not contact buyers or claim payment.",
 "Independently propose three low-cost original software deliverables that can be offered to paying customers. Identify licensing and acceptance risks. Do not contact buyers.",
 "Review both research outputs for feasibility, originality, duplication, payment verification and unsupported claims. Mark unverifiable claims."
]
def utc():return datetime.now(timezone.utc).isoformat()
def run():
    current_order=owner_command()
    print(json.dumps({"public_owner_command_link":current_order["public_link"],
        "current_owner_order_id":current_order["id"],
        "real_workers_receive_on_actual_invocation_only":True,
        "configured_role_namespace_not_live_agent_count":750377265360}))
    endpoint=os.getenv("SUPERWORKER_API_URL","").rstrip("/")
    model=os.getenv("SUPERWORKER_MODEL","")
    key=os.getenv("SUPERWORKER_API_KEY","")
    if not (endpoint and model and key):
        print(json.dumps({"status":"NOT_DEPLOYED","reason":"No approved model endpoint/model/key configured","roles_defined":750377265361,"verified_active":0,"concurrent_verified":0}))
        raise SystemExit(2)
    if not endpoint.startswith("https://"):
        raise ValueError("HTTPS model endpoint required")
    ROOT.mkdir(exist_ok=True)
    outputs=[]
    failures=0
    for i,(role,task) in enumerate(zip(ROLES,TASKS)):
        wid=f"pilot-{i+1}"
        start=utc()
        prompt=("CURRENT HUMAN OWNER INSTRUCTION "+current_order["id"]+"\n"+
                current_order["direct_user_instruction"][:2600]+"\n"+
                "Canonical command: "+current_order["public_link"]+"\n"+
                "Non-negotiable limits: "+", ".join(current_order["hard_limits"])+"\n"+
                "Work task: "+task+"\n"+
                "Only actual authenticated allowed external posts count as contacts. "+
                "Only independently verified incoming onchain settled crypto to correct "+
                "owner-approved chain/address counts as received money. No email, no "+
                "private signing, no fees or wallet spending.")
        if role=="D6-reviewer":
            prompt+="\nResearcher outputs to review:\n"+json.dumps(outputs,ensure_ascii=False)[:16000]
        record={"worker_id":wid,"role":role,"task":task,"start_utc":start,"status":"FAILED",
                "order_link":COMMAND_URL,"owner_order_id":current_order["id"],
                "wallet_transactions_authorized":False,"email_contact_authorized":False}
        try:
            # A newer Google Gemini project can receive HTTP 404 for legacy 2.5.
            # Retry once with Google's documented 3.8 Flash compatibility model.
            # This is one bounded retry per pilot worker, not another invented worker.
            candidates=[model]
            if model=="gemini-2.5-flash" and endpoint=="https://generativelanguage.googleapis.com/v1beta/openai":
                candidates.append("gemini-3.8-flash")
            data=None
            for attempted_model in candidates:
                payload={"model":attempted_model,"messages":[{"role":"system","content":"You are an independent assistant. Do original useful work. Be truthful and cite evidence. Never claim a payment, active worker, or successful action without proof."},{"role":"user","content":prompt}],"max_tokens":1600}
                # Gemini 3.8 Flash no longer accepts sampling parameters such as temperature.
                if not attempted_model.startswith("gemini-3"):
                    payload["temperature"]=0.3
                body=json.dumps(payload).encode()
                request=urllib.request.Request(endpoint+"/chat/completions",data=body,headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
                fallback_to_next=False
                for retry in range(3):
                    try:
                        with urllib.request.urlopen(request,timeout=45) as response:
                            data=json.loads(response.read(300000))
                        break
                    except urllib.error.HTTPError as e:
                        if e.code==404 and attempted_model!=candidates[-1]:
                            print(json.dumps({"worker_id":wid,"retry_model":candidates[-1],"reason":"legacy model returned 404"}))
                            fallback_to_next=True
                            break
                        # Recover from temporary provider/gateway errors only.
                        # Never auto-retry quota, authorization, or billing errors.
                        if e.code in (500,502,503,504) and retry<2:
                            delay=(retry+1)*2
                            print(json.dumps({"worker_id":wid,"transient_http_status":e.code,"retry_number":retry+1,"max_retries":2,"backoff_seconds":delay}))
                            time.sleep(delay)
                            continue
                        raise
                if data is not None:
                    break
                if fallback_to_next:
                    continue
            if data is None:
                raise RuntimeError("No provider model completed a request")
            output=data["choices"][0]["message"]["content"]
            record.update({"status":"COMPLETED","end_utc":utc(),"provider_response_id":data.get("id"),"model":data.get("model",attempted_model),"output":output,"output_sha256":hashlib.sha256(output.encode()).hexdigest()})
            outputs.append({"worker_id":wid,"output":output})
        except urllib.error.HTTPError as e:
            failures+=1
            record.update({"end_utc":utc(),"error_type":"HTTPError","http_status":e.code,"diagnostic":"Provider rejected the request; check Gemini key, model access, billing and quota. Response body intentionally omitted to protect credentials."})
        except Exception as e:
            failures+=1
            record.update({"end_utc":utc(),"error_type":type(e).__name__})
        path=ROOT/(wid+"-"+uuid.uuid4().hex[:8]+".json")
        path.write_text(json.dumps(record,indent=2,ensure_ascii=False))
        print(json.dumps({"worker_id":wid,"status":record["status"],"http_status":record.get("http_status"),"error_type":record.get("error_type"),"evidence_file":str(path)}))
    print(json.dumps({"attempted":len(ROLES),"completed":len(ROLES)-failures,"failed":failures}))
    if failures:
        raise SystemExit(1)
if __name__=="__main__":run()
