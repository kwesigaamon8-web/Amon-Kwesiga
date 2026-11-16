"""B1/B2 independent superworker pilot. No inference or worker activity is fabricated.
Usage: python crypto-agents/superworker_runtime.py
Requires OWNER-APPROVED OpenAI-compatible endpoint and model credentials in env.
No API call if missing configuration. No mining, messaging or wallet operations.
"""
import os, json, time, uuid, hashlib, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path("superworker-evidence")
ROLES=["B1-researcher","B2-researcher","D6-reviewer"]
TASKS=[
 "Find three legitimate public paid tasks that explicitly permit AI-assisted original deliverables. Provide source URLs and verification steps. Do not contact buyers or claim payment.",
 "Independently propose three low-cost original software deliverables that can be offered to paying customers. Identify licensing and acceptance risks. Do not contact buyers.",
 "Review both research outputs for feasibility, originality, duplication, payment verification and unsupported claims. Mark unverifiable claims."
]
def utc():return datetime.now(timezone.utc).isoformat()
def run():
    endpoint=os.getenv("SUPERWORKER_API_URL","").rstrip("/")
    model=os.getenv("SUPERWORKER_MODEL","")
    key=os.getenv("SUPERWORKER_API_KEY","")
    if not (endpoint and model and key):
        print(json.dumps({"status":"NOT_DEPLOYED","reason":"No approved model endpoint/model/key configured","roles_defined":750377265361,"verified_active":0,"concurrent_verified":0}))
        return
    if not endpoint.startswith("https://"):
        raise ValueError("HTTPS model endpoint required")
    ROOT.mkdir(exist_ok=True)
    outputs=[]
    failures=0
    for i,(role,task) in enumerate(zip(ROLES,TASKS)):
        wid=f"pilot-{i+1}"
        start=utc()
        prompt=task
        if role=="D6-reviewer":
            prompt+="\nResearcher outputs to review:\n"+json.dumps(outputs,ensure_ascii=False)[:16000]
        body=json.dumps({"model":model,"messages":[{"role":"system","content":"You are an independent assistant. Do original useful work. Be truthful and cite evidence. Never claim a payment, active worker, or successful action without proof."},{"role":"user","content":prompt}],"temperature":0.3}).encode()
        request=urllib.request.Request(endpoint+"/chat/completions",data=body,headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
        record={"worker_id":wid,"role":role,"task":task,"start_utc":start,"status":"FAILED"}
        try:
            with urllib.request.urlopen(request,timeout=45) as response:
                data=json.loads(response.read(300000))
            output=data["choices"][0]["message"]["content"]
            record.update({"status":"COMPLETED","end_utc":utc(),"provider_response_id":data.get("id"),"model":data.get("model",model),"output":output,"output_sha256":hashlib.sha256(output.encode()).hexdigest()})
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
