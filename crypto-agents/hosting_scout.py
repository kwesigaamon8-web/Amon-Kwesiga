"""One owner-requested hosting research assignment per actually running B worker.

The catalog lists OFFICIAL pages only. A free plan is not a deployed account,
a running model, or permission for cryptomining. A page probe proves only that
an official source responded at this instant; it does not verify all terms.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlparse

FLEETS=("transferexperiment","BountyScoutAI")
HOSTS=(
    {"id":"cloudflare-workers","name":"Cloudflare Workers Free","official_url":"https://developers.cloudflare.com/workers/platform/limits/","fit":"tiny authenticated event router, queue coordinator, HTTP API; not full LLM CPU","limit":"100000 requests/day and 10ms CPU/request; 5 cron triggers/account","risk":"Account not connected; no persistent long CPU model processing","account_status":"NOT_CONNECTED"},
    {"id":"oracle-always-free","name":"Oracle Cloud Always Free Compute","official_url":"https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm","fit":"limited actual CPU server or worker if owner tenancy is eligible and resources available","limit":"E2 micro or bounded A1 capacity; quota, home region and idleness reclamation apply","risk":"Account and region/capacity unverified; free tenancy may need payment method; no VM deployed","account_status":"NOT_CONNECTED"},
    {"id":"render-free","name":"Render Free Web Service","official_url":"https://render.com/docs/free","fit":"small Flask web app/dashboard, not continuous AI inference","limit":"750 workspace free instance hours/month; sleeps after 15 minutes idle; ephemeral disk","risk":"EXISTING service deploy FAILS; no healthy public deployment confirmed; possible bandwidth charges after included quotas","account_status":"EXISTING_SERVICE_DEPLOY_FAILED"},
    {"id":"koyeb-free","name":"Koyeb Free Instance","official_url":"https://www.koyeb.com/docs/reference/instances","fit":"small HTTP status service only; extremely limited AI inference","limit":"one web Free instance per organization, 0.1 vCPU, 512MB RAM, 2GB disk; sleep after 1h","risk":"Not usable as a background Worker Service; account and card/identity eligibility unverified","account_status":"NOT_CONNECTED"},
    {"id":"netlify-free","name":"Netlify Free","official_url":"https://www.netlify.com/pricing/","fit":"static status portal and bounded web functions, not always-on inference","limit":"free 300-credit monthly allowance; detailed billing and function usage must be checked","risk":"No connected site; functions and credit limit may constrain work","account_status":"NOT_CONNECTED"},
    {"id":"huggingface-static","name":"Hugging Face Static Spaces","official_url":"https://huggingface.co/docs/hub/spaces-overview","fit":"static public informational page, not running coding agents or live Python inference","limit":"Static Spaces free; current new Gradio/Docker compute Spaces require paid plan","risk":"Only read-only linked HF account; no free persistent compute deployment","account_status":"READ_ONLY_CONNECTION_NO_DEPLOY"},
    {"id":"github-pages","name":"GitHub Pages","official_url":"https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits","fit":"noncommercial static open-source project docs/status only","limit":"static frontend; no server runtime; cannot run commercial transaction/SaaS site on Pages","risk":"This public repo Pages not enabled; unsuitable for commercial earning host","account_status":"REPO_CONNECTED_PAGES_DISABLED"},
    {"id":"vercel-hobby","name":"Vercel Hobby","official_url":"https://vercel.com/docs/plans/hobby","fit":"personal NONCOMMERCIAL small app demos only","limit":"Hobby plan restricts to personal/noncommercial; function/runtime quotas","risk":"Not suitable for automated commercial worker operation; account unconnected","account_status":"NOT_CONNECTED"},
    {"id":"google-cloud-run","name":"Google Cloud Run Free Tier","official_url":"https://cloud.google.com/run/pricing","fit":"small serverless service if existing authorized billing project and free tier permits","limit":"free allowance by billing account; usage over threshold is billed","risk":"Billing account necessary; no authorized connected project or zero-charge guard verified","account_status":"NOT_CONNECTED_BILLING_REQUIRED"},
    {"id":"deno-deploy","name":"Deno Deploy","official_url":"https://docs.deno.com/deploy/pricing_and_limits/","fit":"short serverless functions; weak long-term option","limit":"public pricing/limits; docs warn Deno Deploy sunset April 2027","risk":"Platform retirement deadline; no connected account","account_status":"NOT_CONNECTED"},
)

def plan(fleet: str, worker_id: str) -> dict:
    if fleet not in FLEETS or not isinstance(worker_id,str) or not worker_id.strip():
        raise ValueError("Must supply an actual B fleet and nonempty role ID")
    # Stable source diversification without generating phantom active instances.
    number=int.from_bytes(hashlib.sha256((fleet+":"+worker_id).encode("utf-8")).digest()[:8],"big")
    primary=number%len(HOSTS)
    other=(primary+1+(number//len(HOSTS))%(len(HOSTS)-1))%len(HOSTS)
    if other==primary:
        raise AssertionError("hosting alternatives are not independent")
    return {"fleet":fleet,"worker_id":worker_id,
            "assigned":dict(HOSTS[primary]),
            "independent_alternative":dict(HOSTS[other]),
            "source_document":"crypto-agents/HOSTING_RESEARCH_FOR_ALL_WORKERS.md",
            "assignment":"SECONDARY_PARALLEL_TASK_NOT_REPLACING_PAID_WORK",
            "assignment_exists_not_deployed":True,
            "owner_spending_authorized":False,
            "registration_or_deployment_done":False,
            "real_source_proof_requires_probe":True,
            "real_worker_execution_proof_requires_model_run":True}

def probe(host: dict, timeout: float=4.0) -> dict:
    """GET one exact official documentation page. This is NOT provider account access."""
    url=host["official_url"]
    domain=urlparse(url).hostname
    if not domain or not url.startswith("https://"):
        raise ValueError("Official HTTPS source required")
    stamped=datetime.now(timezone.utc).isoformat()
    output={"url":url,"checked_utc":stamped,"status":"SOURCE_UNREACHABLE",
            "http_status":None,"bytes_sampled":0,
            "account_connected":False,"worker_host_deployed":False,
            "latest_terms_verified_by_probe":False}
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"OwnerBHostingScout/1.0",
                                                   "Accept":"text/html,text/plain"})
        with urllib.request.urlopen(req,timeout=timeout) as response:
            # Never read the whole site; never execute untrusted site content.
            chunk=response.read(1024)
            output.update(status="OFFICIAL_PAGE_REACHABLE_TERMS_STILL_REQUIRE_REVIEW",
                          http_status=int(response.status),bytes_sampled=len(chunk),
                          evidence_digest_sha256=hashlib.sha256(chunk).hexdigest())
    except (OSError,ValueError,urllib.error.URLError,TimeoutError) as e:
        output["error"]=type(e).__name__[:70]
    return output

def self_test() -> dict:
    assert len({h["id"] for h in HOSTS})==len(HOSTS)
    assert all(h["official_url"].startswith("https://") for h in HOSTS)
    assert all(h["account_status"]!="DEPLOYED" for h in HOSTS)
    examples=[plan(f,"D%02d-M%02d-W%02d"%(j%9+1,j%15+1,j%50+1))
              for f in FLEETS for j in range(1,201)]
    assert len({x["assigned"]["id"] for x in examples})>=8
    assert all(x["assigned"]["id"]!=x["independent_alternative"]["id"] for x in examples)
    assert all(x["registration_or_deployment_done"] is False for x in examples)
    assert plan(FLEETS[0],"D01-M01-W01")==plan(FLEETS[0],"D01-M01-W01")
    return {"result":"PASS","candidate_platforms":len(HOSTS),
            "sampled_logical_roles":len(examples),"accounts_created":0,
            "hosting_deployments_claimed":0,"models_started_by_test":0}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--fleet",choices=FLEETS)
    p.add_argument("--worker-id")
    a=p.parse_args()
    if a.self_test:
        print("B_HOSTING_SOURCE_ALLOCATION_TEST",json.dumps(self_test(),sort_keys=True))
    else:
        if not a.fleet or not a.worker_id:p.error("provide --fleet and --worker-id")
        print(json.dumps(plan(a.fleet,a.worker_id),indent=2))
