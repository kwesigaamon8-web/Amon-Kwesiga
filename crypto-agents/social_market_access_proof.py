"""Finite, honest test of a worldwide social-media search order.
Virtual role addressability != executing 11.25 trillion workers.
Each actually launched child process performs exactly one *public endpoint availability*
probe; HTTPS status never means search results, account access, contacts or earnings.
Never logs in, scrapes private posts, or sends an outbound message.
"""
import argparse
import bisect
import csv
import json
import os
import random
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PLATFORMS = [
    ("Reddit","https://www.reddit.com/"),
    ("LinkedIn","https://www.linkedin.com/"),
    ("Facebook","https://www.facebook.com/"),
    ("Instagram","https://www.instagram.com/"),
    ("X","https://x.com/"),
    ("TikTok","https://www.tiktok.com/"),
    ("YouTube","https://www.youtube.com/"),
    ("Threads","https://www.threads.net/"),
    ("Bluesky","https://bsky.app/"),
    ("Pinterest","https://www.pinterest.com/"),
    ("Mastodon","https://mastodon.social/"),
    ("Telegram","https://web.telegram.org/"),
    ("Discord","https://discord.com/"),
    ("Snapchat","https://www.snapchat.com/"),
]
COUNTRIES = Path("crypto-agents/data/bitcoin_country_allocations.csv")
OUT = Path("social-platform-task-evidence")
SYSTEMS = 30
EXPECTED_VIRTUAL = 11_255_658_980_400

def now():
    return datetime.now(timezone.utc).isoformat()

def load_countries():
    with COUNTRIES.open(encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    positive=[]
    for r in rows:
        n=int(r["Virtual roles per B system"])
        if n>0:
            positive.append((r["ISO2"],r["Country or economy"],n))
    assert len(rows)==217 and len(positive)==186
    assert sum(n for _,_,n in positive)*SYSTEMS==EXPECTED_VIRTUAL
    return rows,positive

def assign(index,positive):
    if type(index) is not int or index<0 or index>=EXPECTED_VIRTUAL:
        raise ValueError("Outside available virtual namespace")
    per=EXPECTED_VIRTUAL//SYSTEMS
    system= index//per
    local=index%per
    starts=[0]
    for _,_,n in positive:
        starts.append(starts[-1]+n)
    n=bisect.bisect_right(starts,local)-1
    if not 0<=n<len(positive):
        raise AssertionError("Invalid country assignment")
    return {"virtual_role_index":str(index),"system":f"{'B1' if system<15 else 'B2'}-S{system%15+1:02d}",
            "country_iso2":positive[n][0],"country":positive[n][1],
            "platform_task":PLATFORMS[index%len(PLATFORMS)][0],
            "virtual_role_is_live":False,"independently_executed":False}

def self_test():
    rows,pos=load_countries()
    per=EXPECTED_VIRTUAL//SYSTEMS
    sample={0,EXPECTED_VIRTUAL-1}
    for s in range(SYSTEMS):
        sample.add(s*per);sample.add((s+1)*per-1)
    rng=random.Random(20261120)
    sample.update(rng.randrange(EXPECTED_VIRTUAL) for _ in range(10000))
    mapped=[assign(i,pos) for i in sorted(sample)]
    assert len({i["virtual_role_index"] for i in mapped})==len(sample)
    assert len({i["system"] for i in mapped})==30
    result={"test":"VIRTUAL_ROLE_ADDRESSABILITY_ONLY",
            "virtual_positions_mathematically_mapped":EXPECTED_VIRTUAL,
            "country_rows":len(rows),"positive_allocation_countries":len(pos),
            "system_count":SYSTEMS,"boundary_and_random_samples_verified":len(sample),
            "real_models_invoked":0,"virtual_roles_actually_launched":0,
            "social_accounts_accessed":0,"verified_customers":0}
    print("SOCIAL_DISPATCH_ADDRESSABILITY_TEST "+json.dumps(result))
    return result

def probe_one(index):
    name,url=PLATFORMS[index]
    evidence={"platform":name,"url":url,"role":"FINITE_SOCIAL_ACCESS_PROBE-"+str(index+1).zfill(2),
              "actual_os_pid":os.getpid(),"instruction_received":"HEAD_ONLY_PUBLIC_PLATFORM_ACCESS_CHECK",
              "task_attempted":True,"timestamp_utc":now(),"account_authenticated":False,
              "social_search_performed":False,"social_posts_read":0,"buyers_verified":0,
              "messages_sent":0,"contacted_customers":0,"payment_verified":False}
    try:
        req=urllib.request.Request(url,method="HEAD",
          headers={"User-Agent":"B1B2-social-platform-access-audit/1.0"})
        with urllib.request.urlopen(req,timeout=8) as resp:
            evidence["public_https_status"]=resp.status
            evidence["endpoint_reachable"]=200<=resp.status<400
            evidence["result"]="PUBLIC_ROOT_HTTP_REACHABLE_NOT_SEARCH_AUTHORIZED"
    except urllib.error.HTTPError as err:
        evidence["public_https_status"]=err.code
        evidence["endpoint_reachable"]=False
        evidence["result"]="PUBLIC_ENDPOINT_HTTP_REJECTED_NOT_SOCIAL_ACCOUNT_ACCESS"
    except Exception as err:
        evidence["endpoint_reachable"]=False
        evidence["error_type"]=type(err).__name__
        evidence["result"]="PUBLIC_ENDPOINT_UNAVAILABLE_NOT_SOCIAL_SEARCH"
    OUT.mkdir(exist_ok=True)
    (OUT/f"platform-{index+1:02d}.json").write_text(
        json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    print("PUBLIC_PROBE "+json.dumps(evidence))
    return 0

def run_all():
    self_test()
    OUT.mkdir(exist_ok=True)
    launched=[]
    for i in range(len(PLATFORMS)):
        p=subprocess.run([sys.executable,str(Path(__file__).resolve()),
                          "--platform",str(i)],capture_output=True,text=True,timeout=15)
        launched.append({"platform":PLATFORMS[i][0],"exit_code":p.returncode,
                         "stderr":p.stderr[-400:]})
    reports=[]
    for i in range(len(PLATFORMS)):
        file=OUT/f"platform-{i+1:02d}.json"
        if file.exists():
            reports.append(json.loads(file.read_text(encoding="utf-8")))
    report={"as_of_utc":now(),"instruction":"Check whether finite workers can obey one per-platform public endpoint check",
            "eleven_trillion_roles_independently_activated":False,
            "virtual_role_positions":EXPECTED_VIRTUAL,
            "real_finite_os_processes_attempted":len(launched),
            "actual_platform_probe_records":len(reports),
            "platform_homepages_reachable":sum(x.get("endpoint_reachable",False) for x in reports),
            "platforms_with_authenticated_search_access":0,
            "public_social_media_searches_proven_by_this_code":0,
            "social_media_app_accounts_logged_into":0,"actual_customer_introductions_sent":0,
            "proof_level":"HEAD probes of root URLs only; NOT authenticated search or customer acquisition",
            "worker_runs":launched,"platforms":reports}
    (OUT/"SUMMARY.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    lines=["# B1/B2 sample social-platform task execution: verified scope","",
           "**Mathematical role namespace:** 11,255,658,980,400 addressable virtual positions, 30 systems, 186 countries. **Not 11 trillion executing workers.**","",
           "**Actual subprocess attempts:** "+str(len(launched))+
           ". These only test public site responsiveness, NOT platform search permission.","",
           "| Platform | HTTP status | Probe status | Actual authenticated search |",
           "|---|---|---|---|"]
    for p in reports:
        lines.append("| "+p["platform"]+" | "+str(p.get("public_https_status","network error"))+
                     " | "+p["result"]+" | No |")
    lines.extend(["","**Customer replies:** none. **Real payments:** none.","",
       "Each subprocess left an individual machine-readable evidence record. A public",
       "homepage responding does not mean the platform lets a bot read private accounts,",
       "send messages, search its entire database, or conduct sales."])
    (OUT/"REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("SOCIAL_FINITE_TASK_PILOT_SUMMARY "+json.dumps({
        "attempts":len(launched),"records":len(reports),
        "public_roots_reachable":report["platform_homepages_reachable"],
        "authenticated_platform_searches":0,"true_11T_worker_processes":0
    }))
    return 0 if len(reports)==len(PLATFORMS) and all(x["exit_code"]==0 for x in launched) else 1

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--run",action="store_true")
    parser.add_argument("--platform",type=int)
    args=parser.parse_args()
    if args.self_test:self_test()
    elif args.run:sys.exit(run_all())
    elif args.platform is not None:sys.exit(probe_one(args.platform))
    else:parser.error("Supply --self-test, --run or --platform N")
