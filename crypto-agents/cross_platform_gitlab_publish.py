#!/usr/bin/env python3
"""One-owner-order GitLab Pages publisher for the B1/B2 public worker hub.

VALIDATE mode is offline and never needs GitLab credentials.
PUBLISH mode requires GITLAB_TOKEN in CI environment; never enter credentials
in HTML, GitHub source code, workflow logs or a public web form.

This replicates a static interface with 11.26T mathematically addressable
virtual roles, not 11.26T online accounts, agents, devices or paid outputs.
It never performs mining, any wallet transfer, or an external bug bounty submission.
"""
from __future__ import annotations
import argparse
import base64
import csv
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "docs/b1b2-worker-hub/hf-worker-hub.html"
COUNTRIES = ROOT / "crypto-agents/data/bitcoin_country_allocations.csv"
ADDRESSES = ROOT / "crypto-agents/public_payment_routes.json"
VIRTUAL_COUNT = 11_255_658_980_400
PER_DIVISION = 375_188_632_680
BTC = {
  "BTC-01": "bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z",
  "BTC-02": "bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9",
}
MANAGED = {"managed_by": "kwesigaamon8-web/Amon-Kwesiga",
           "kind": "B1B2_PORTABLE_PUBLIC_STATIC_WORKER_HUB",
           "synchronization": "Canonical owner commands originate in ChatGPT; read-only GitHub references.",
           "configured_virtual_roles": VIRTUAL_COUNT,
           "real_independent_ai_workers_created_by_mirror": 0}
CI = """stages:
  - deploy
publish-hub:
  stage: deploy
  image: alpine:3.20
  script:
    - test -s public/index.html
    - test -s public/country-allocations.json
    - test -s public/wallet-routes.json
    - echo "Publishing static B1/B2 worker role lookup; no mining or AI model execution."
  pages: true
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
"""
README = """# B1/B2 Worker Hub — GitLab mirror

This GitLab project is a static, source-verified public mirror of the owner-controlled
B1/B2 organization on GitHub. All instructions originate from the owner's ChatGPT
conversation and the owner's authenticated canonical GitHub order file.

This site supports 11,255,658,980,400 mathematically configured role ID lookups
in 30 systems. They are not independent AI accounts, funded tasks, physical miners,
verified posts, real-country presences or cryptocurrency earnings.

- Master order: https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/chief_D_owner_orders.json
- Human/owner public wallets: https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/PUBLIC_RECEIVING_ADDRESSES.md
- Hugging Face existing Space: https://huggingface.co/spaces/Amonkkkk/b1b2-superworker-assembly
- Source and validation: https://github.com/kwesigaamon8-web/Amon-Kwesiga

Never post unapproved messages, mine on third-party devices, spend/sign wallets,
claim paid receipts without a correct-chain TXID, or send/read Gmail.
"""

def build():
    html = HTML.read_text(encoding="utf8")
    assert "<!doctype html>" in html.lower()
    assert "11,255,658,980,400" in html
    assert all(address in html for address in BTC.values())
    assert "country-allocations.json" in html and "wallet-routes.json" in html
    with COUNTRIES.open(newline="", encoding="utf-8-sig") as f:
        country=[]
        last=-1
        for r in csv.DictReader(f):
            count=int(r["Virtual roles per B system"])
            if count <= 0: continue
            start=int(r["Per-system role start"])
            end=int(r["Per-system role end inclusive"])
            assert start == last+1 and end-start+1 == count, (r["ISO3"],start,end)
            country.append({"iso3":r["ISO3"],"country":r["Country or economy"],
                            "start":str(start),"end":str(end)})
            last=end
    assert last == PER_DIVISION-1 and len(country)>100
    routes=json.loads(ADDRESSES.read_text(encoding="utf8"))["self_custody_candidate_routes"]
    assert len(routes)==10
    as_map={r["route_id"]:r["receiving_address"] for r in routes}
    for name,address in BTC.items():assert as_map[name]==address
    assert all(r["payment_status"].startswith("HOLD") for r in routes if r["route_id"] not in BTC)
    build_map={
       "public/index.html":html,
       "public/country-allocations.json":json.dumps(
           {"version":1,"country_allocations_not_actual_deployments":True,"countries":country},separators=(",",":")),
       "public/wallet-routes.json":json.dumps(
           {"schema":"B1B2_PUBLISHED_SELF_CUSTODY_ROUTES","self_custody_candidate_routes":routes},separators=(",",":")),
       ".gitlab-ci.yml":CI,
       "README.md":README,
       ".b1b2-managed-project.json":json.dumps(MANAGED,sort_keys=True,indent=2)+"\n",
    }
    assert len(build_map)==6
    return build_map,len(country)

def request(method,path,token,payload=None,optional=False):
    url="https://gitlab.com/api/v4/"+path.lstrip("/")
    data=None if payload is None else json.dumps(payload).encode()
    req=urllib.request.Request(url,data=data,method=method,headers={
       "PRIVATE-TOKEN":token,
       "Accept":"application/json",
       **({"Content-Type":"application/json"} if payload is not None else {})
    })
    try:
        with urllib.request.urlopen(req,timeout=30) as res:
            body=res.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        if optional and e.code==404:return None
        # Do not print any authorization headers or URL params.
        msg=e.read(700).decode(errors="replace").replace(token,"[REDACTED]")
        raise RuntimeError(f"GitLab {method} {path.split('?')[0]} HTTP {e.code}: {msg[:360]}") from None

def publish(files):
    token=os.environ.get("GITLAB_TOKEN","")
    if not token:
        print("GITLAB_PUBLISH_NOT_AUTHORIZED: missing GitHub Actions secret GITLAB_TOKEN; offline source validation passed.")
        return {"status":"AUTHORIZATION_REQUIRED"}
    specified=os.environ.get("GITLAB_PROJECT_ID","").strip()
    if specified:
        project=request("GET",f"projects/{urllib.parse.quote(specified,safe='')}",token)
        if project.get("path")!="b1b2-worker-hub":
            raise RuntimeError("Refusing to overwrite unrelated GitLab project: expected slug b1b2-worker-hub")
    else:
        user=request("GET","user",token)
        username=user["username"]
        canonical=urllib.parse.quote(username+"/b1b2-worker-hub",safe="")
        project=request("GET",f"projects/{canonical}",token,optional=True)
        if project is None:
            project=request("POST","projects",token,{"name":"B1B2 Worker Hub",
                 "path":"b1b2-worker-hub","visibility":"public","initialize_with_readme":True,
                 "description":"Static public mirror of B1/B2 virtual role lookup and owner receive-only wallet references"})
    if project.get("visibility")!="public":
        raise RuntimeError("Target project must be publicly visible: static public wallet dashboard")
    project_id=project["id"]
    branch=project.get("default_branch") or "main"
    # A previous project may be edited ONLY when it has our exact managed marker.
    marker_id=urllib.parse.quote(".b1b2-managed-project.json",safe="")
    marker_doc=request("GET",f"projects/{project_id}/repository/files/{marker_id}?ref={urllib.parse.quote(branch,safe='')}",token,optional=True)
    if marker_doc is not None:
        try:
            existing=json.loads(base64.b64decode(marker_doc["content"]).decode())
        except (KeyError,ValueError,UnicodeDecodeError) as exc:
            raise RuntimeError("Invalid GitLab project ownership marker") from exc
        if existing.get("kind")!=MANAGED["kind"] or existing.get("managed_by")!=MANAGED["managed_by"]:
            raise RuntimeError("GitLab project does not match B1/B2 owner-managed marker")
    else:
        # Only a new README-only project can be bootstrapped safely.
        tree=request("GET",f"projects/{project_id}/repository/tree?ref={urllib.parse.quote(branch,safe='')}&per_page=20",token)
        if any(obj.get("path")!="README.md" for obj in tree):
            raise RuntimeError("Existing GitLab project lacks our marker; refusing to overwrite its source")
    existing_actions=[]
    for filename,value in files.items():
        encoded=urllib.parse.quote(filename,safe="")
        url=f"projects/{project_id}/repository/files/{encoded}?ref={urllib.parse.quote(branch,safe='')}"
        old=request("GET",url,token,optional=True)
        existing_actions.append({"action":"update" if old is not None else "create",
                                "file_path":filename,"content":value,"encoding":"text"})
    result=request("POST",f"projects/{project_id}/repository/commits",token,{
        "branch":branch,"commit_message":"Sync original B1/B2 country-assigned worker lookup and public receiving routes",
        "actions":existing_actions})
    url=project.get("web_url","")
    print("GITLAB_PUBLIC_HUB_COMMIT_CREATED",json.dumps({
        "project":url,"commit":result.get("id"),"files":len(existing_actions),
        "virtual_role_count":VIRTUAL_COUNT,
        "verified_running_agents_by_this_sync":0,
        "verified_payments_by_this_sync":0}))
    print("GITLAB_PAGES_PENDING_GITLAB_PIPELINE; verify Deploy > Pages for the actual public URL")
    return {"status":"COMMIT_CREATED","project":url,"commit":result.get("id")}

def main():
    p=argparse.ArgumentParser()
    x=p.add_mutually_exclusive_group(required=True)
    x.add_argument("--validate",action="store_true")
    x.add_argument("--publish",action="store_true")
    a=p.parse_args()
    docs,regions=build()
    print("GITLAB_B1B2_SOURCE_VALIDATED",json.dumps({
      "files":len(docs),"country_or_economy_allocations":regions,
      "logical_divisions":30,"virtual_role_slots":VIRTUAL_COUNT,
      "public_self_custody_routes":10,
      "real_agents_started":0,"mining_started":0,"crypto_received":0}))
    if a.publish:publish(docs)

if __name__=="__main__":main()
