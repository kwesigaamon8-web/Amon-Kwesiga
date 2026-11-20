"""World OSINT: 249 country and territory codes, 30 finite worker processes.

Public World Bank V2 metadata, public Internet-use/population indicators,
public GitHub original issue index. No private-person profiling or contact,
emails, hidden networks, unauthorized login, wallet signing or mining.
One order can be lazily accessed by all virtual B1/B2 role identifiers,
but only actual processes create OSINT evidence.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=ROOT/"world-osint-evidence"
COUNT=30
WB_ROOT="https://api.worldbank.org/v2/"
WB_COUNTRY=WB_ROOT+"country?format=json&per_page=400"
INDICATORS=("IT.NET.USER.ZS","SP.POP.TOTL")
QUERIES=('is:issue is:open "bitcoin" "bounty" created:>=2026-11-01',
         'is:issue is:open "python" "paid" created:>=2026-11-01',
         'is:issue is:open "documentation" "bounty" created:>=2026-11-01')

def canonical():
    sys.path.insert(0,str(HERE))
    from directive_cascade import read_owner
    from enigma_universal_owner_order import GRAND_TOTAL
    d=read_owner()
    assert GRAND_TOTAL==11_255_658_980_400
    return {"order_id":d["owner_order_id"],"owner_sha256":d["owner_sha256"],
            "standing_sha256":d["standard_sha256"],"configured_roles":GRAND_TOTAL}

def codes():
    sys.path.insert(0,str(HERE/"marketing"))
    from country_market_research import COUNTRY_CODES
    assert len(COUNTRY_CODES)==249 and len(set(COUNTRY_CODES))==249
    return COUNTRY_CODES

def for_shard(i):
    if type(i)!=int or not 0<=i<COUNT:raise ValueError("OSINT_INVALID_SHARD")
    return codes()[i::COUNT]

def get_json(url):
    u=urllib.parse.urlsplit(url)
    if u.scheme!="https" or u.hostname not in ("api.worldbank.org","api.github.com"):
        raise ValueError("OSINT_NON_ALLOWLISTED_SOURCE")
    headers={"User-Agent":"B1B2-WorldOSINT-ReadOnly/1.0","Accept":"application/json"}
    if u.hostname=="api.github.com" and os.getenv("GH_TOKEN"):
        headers["Authorization"]="Bearer "+os.environ["GH_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=22) as r:
        raw=r.read(3_000_001)
        if r.status!=200 or len(raw)>3_000_000:raise ValueError("OSINT_BAD_SOURCE_RESPONSE")
    return json.loads(raw)

def wb_rows(value):
    if not isinstance(value,list) or len(value)!=2 or not isinstance(value[0],dict) or not isinstance(value[1],list):
        raise ValueError("OSINT_BAD_WB_SCHEMA")
    if value[0].get("pages")!=1 or value[0].get("total")!=len(value[1]):
        raise ValueError("OSINT_INCOMPLETE_WB_PAGE")
    return value[1]

def gather(fetch=get_json):
    owner=canonical()
    rows={k:{"country_or_territory_iso2":k,"source_status":"UNAVAILABLE",
             "observations":{},"citations":[]} for k in codes()}
    snapshot={"schema":"B1B2_WORLD_OSINT_V1","as_of_utc":datetime.now(timezone.utc).isoformat(),
              "owner":owner,"countries":rows,"worldbank_metadata":"UNAVAILABLE",
              "indicators":{},"github_issue_search":"UNAVAILABLE",
              "unverified_public_issue_candidates":[],
              "verified_buyer_contracts":0,"verified_incoming_btc":0}
    try:
        data=wb_rows(fetch(WB_COUNTRY))
        for d in data:
            if not isinstance(d,dict):continue
            iso=str(d.get("iso2Code") or "").upper()
            region=(d.get("region") or {}).get("value")
            if iso not in rows or not region or region=="Aggregates":continue
            rows[iso]["observations"]["official_country_metadata"]={
                "worldbank_name":d.get("name"),"region":region,
                "income_level":(d.get("incomeLevel") or {}).get("value")}
            rows[iso]["citations"].append(WB_COUNTRY)
            rows[iso]["source_status"]="METADATA_OBSERVED"
        snapshot["worldbank_metadata"]="AVAILABLE"
    except (ValueError,KeyError,TypeError,OSError,TimeoutError) as e:
        snapshot["worldbank_metadata"]="UNAVAILABLE_"+type(e).__name__
    for indicator in INDICATORS:
        url=WB_ROOT+"country/all/indicator/"+indicator+"?format=json&mrnev=1&per_page=500"
        n=0
        try:
            data=wb_rows(fetch(url))
            seen=set()
            for d in data:
                if not isinstance(d,dict):continue
                iso=str((d.get("country") or {}).get("id") or "").upper()
                year=str(d.get("date") or "")
                v=d.get("value")
                if iso not in rows or iso in seen or not re.fullmatch(r"\d{4}",year):continue
                if isinstance(v,bool) or not isinstance(v,(int,float)):continue
                if indicator=="IT.NET.USER.ZS" and not 0<=v<=100:continue
                if indicator=="SP.POP.TOTL" and v<0:continue
                seen.add(iso)
                rows[iso]["observations"][indicator]={"value":v,"observation_year":int(year)}
                rows[iso]["citations"].append(url)
                rows[iso]["source_status"]="INDICATOR_OBSERVED"
                n+=1
            snapshot["indicators"][indicator]={"status":"AVAILABLE","matched_countries":n}
        except (ValueError,KeyError,TypeError,OSError,TimeoutError) as e:
            snapshot["indicators"][indicator]={"status":"UNAVAILABLE_"+type(e).__name__,"matched_countries":0}
    found={}
    checked=0
    for term in QUERIES:
        url="https://api.github.com/search/issues?"+urllib.parse.urlencode(
            {"q":term,"sort":"updated","order":"desc","per_page":"12"})
        try:
            doc=fetch(url)
            if not isinstance(doc,dict) or not isinstance(doc.get("items"),list):
                raise ValueError("OSINT_GH_BAD_SCHEMA")
            checked+=1
            for d in doc["items"][:12]:
                if not isinstance(d,dict) or d.get("state")!="open" or d.get("pull_request"):continue
                url=str(d.get("html_url") or "")
                if not url.startswith("https://github.com/") or "kwesigaamon8-web/Amon-Kwesiga" in url:continue
                found[url]={"original_issue_url":url,"title":str(d.get("title") or "")[:160],
                            "source_updated_at":d.get("updated_at"),
                            "funded_bounty_unverified":True,"buyer_and_eligibility_unverified":True,
                            "native_btc_payout_unverified":True,"external_application_sent":False,
                            "earned_payment_verified":False}
        except (ValueError,KeyError,TypeError,OSError,TimeoutError):
            continue
    snapshot["github_issue_search"]=str(checked)+"_OF_"+str(len(QUERIES))+"_SOURCE_QUERIES"
    snapshot["unverified_public_issue_candidates"]=list(found.values())[:30]
    return snapshot

def shard(i,snapshot):
    owner=canonical()
    if (snapshot.get("schema")!="B1B2_WORLD_OSINT_V1" or
        snapshot.get("owner",{}).get("owner_sha256")!=owner["owner_sha256"] or
        snapshot["owner"]["order_id"]!=owner["order_id"]):
        raise ValueError("OSINT_STALE_OWNER_OR_SNAPSHOT")
    subjects=[]
    for iso in for_shard(i):
        item=snapshot.get("countries",{}).get(iso)
        if not isinstance(item,dict) or item.get("country_or_territory_iso2")!=iso:
            raise ValueError("OSINT_MISSING_COUNTRY_IN_SOURCE")
        subjects.append({
            "country_or_territory":iso,
            "original_sources":item.get("citations",[]),
            "source_status":item.get("source_status"),
            "official_observations":item.get("observations",{}),
            "research_action":"Assess public market context, find one authorized original paid digital-work brief and verify eligibility, budget, acceptance and payout source",
            "actual_client_verified":False,"individuals_profiled":0,
            "btc_payment_received":False,
        })
    checksum=hashlib.sha256(json.dumps(subjects,sort_keys=True).encode()).hexdigest()
    return {"schema":"B1B2_REAL_OSINT_SHARD_V1",
            "shard":i,"pid":os.getpid(),"owner":owner,
            "country_count":len(subjects),"observed_metadata":sum("official_country_metadata" in x["official_observations"] for x in subjects),
            "observed_indicators":sum(sum(k in x["official_observations"] for k in INDICATORS) for x in subjects),
            "country_codes":list(for_shard(i)),"report_sha256":checksum,"findings":subjects,
            "real_python_process":True,"independent_ai_model_calls":0,
            "other_virtual_roles_notified":False,"external_outreach":False,
            "verified_new_earned_btc":0}

def tests():
    assert len(codes())==249
    blocks=[for_shard(i) for i in range(COUNT)]
    assert len([x for b in blocks for x in b])==249
    assert set(x for b in blocks for x in b)==set(codes())
    assert all(len(b) in (8,9) for b in blocks)
    for bad in (-1,30,True,0.5,"30"):
        try:for_shard(bad)
        except ValueError:pass
        else:raise AssertionError("Bad shard accepted")
    try:wb_rows([{"pages":2,"total":1},[{"a":1}]])
    except ValueError:pass
    else:raise AssertionError("Partial WB source accepted")
    assert len(wb_rows([{"pages":1,"total":1},[{"a":1}]]))==1
    print("B1B2_249_COUNTRY_OSINT_DISPATCH_TEST_PASS")

def summary(snapshot):
    receipts=[json.loads(x.read_text()) for x in sorted((OUT/"shards").glob("part-*.json"))]
    assert len(receipts)==COUNT and len({r["pid"] for r in receipts})==COUNT
    assert set(r["shard"] for r in receipts)==set(range(COUNT))
    union=[x for r in receipts for x in r["country_codes"]]
    assert len(union)==249 and set(union)==set(codes())
    assert all(r["owner"]["owner_sha256"]==snapshot["owner"]["owner_sha256"] for r in receipts)
    s={"schema":"B1B2_FULL_WORLD_OSINT_ACTUAL_WORK_V1",
       "source_timestamp":snapshot["as_of_utc"],
       "owner_order_id":snapshot["owner"]["order_id"],
       "virtual_roles_addressable_not_live":snapshot["owner"]["configured_roles"],
       "real_python_osint_subprocesses_executed":COUNT,
       "distinct_country_territory_briefs_completed":len(union),
       "worldbank_metadata_observed":sum(r["observed_metadata"] for r in receipts),
       "worldbank_indicator_observations":sum(r["observed_indicators"] for r in receipts),
       "unverified_original_github_issue_candidates":len(snapshot["unverified_public_issue_candidates"]),
       "github_issue_search_source_status":snapshot["github_issue_search"],
       "worldbank_metadata_source_status":snapshot["worldbank_metadata"],
       "indicator_source_status":snapshot["indicators"],
       "actual_llm_calls_verified":0,"genuine_buyer_contracts_verified":0,
       "new_earned_btc_payouts_verified":0,
       "personal_profiles_or_outreach_created":0}
    (OUT/"RESULT.json").write_text(json.dumps(s,indent=2)+"\n")
    lines=["# Worldwide open-source intelligence result",
           "", "Current authorized order: "+s["owner_order_id"],
           "", "249 countries and territories covered by 30 distinct finite Python OS processes.",
           "Not 249 separate LLM calls, 249 local humans or 11T live workers.",
           "", "Official World Bank country metadata observed: "+str(s["worldbank_metadata_observed"]),
           "World Bank dated indicator observations: "+str(s["worldbank_indicator_observations"]),
           "Public GitHub issue prospects (unverified): "+str(s["unverified_original_github_issue_candidates"]),
           "Verified client contracts: 0; Verified incoming BTC attributable to this research: 0.",
           "", "Source: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392",
           "Every shard receipt contains individual country sources and explicit unknowns.",
           "No emails, payments, login, anonymous networking, private person profiling, mass web scanning or outreach."]
    (OUT/"REPORT.md").write_text("\n".join(lines)+"\n")
    print("B1B2_WORLDWIDE_OSINT_249_30_REAL_PROCESS_RESULT "+json.dumps(s))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--collect",action="store_true")
    p.add_argument("--shard",type=int)
    p.add_argument("--summarize",action="store_true")
    a=p.parse_args()
    tests()
    if a.self_test:return
    OUT.mkdir(parents=True,exist_ok=True)
    file=OUT/"snapshot.json"
    if a.collect:
        d=gather()
        file.write_text(json.dumps(d,indent=2)+"\n")
        print("B1B2_WORLD_PUBLIC_OSINT_FETCH "+json.dumps({
            "countries":len(d["countries"]),
            "metadata":d["worldbank_metadata"],
            "indicators":d["indicators"],
            "public_github_issue_candidates_unverified":len(d["unverified_public_issue_candidates"]),
            "search_status":d["github_issue_search"],
            "contacts_sent":0,"new_paid_btc":0}))
        return
    if not file.exists():raise ValueError("OSINT_NO_SOURCE_SNAPSHOT")
    snapshot=json.loads(file.read_text())
    if a.shard is not None:
        result=shard(a.shard,snapshot)
        folder=OUT/"shards";folder.mkdir(parents=True,exist_ok=True)
        (folder/("part-%02d.json"%a.shard)).write_text(json.dumps(result,indent=2)+"\n")
        print("B1B2_WORLD_OSINT_REAL_PROCESS "+json.dumps({
            "shard":a.shard,"pid":result["pid"],"countries":result["country_count"],
            "official_metadata":result["observed_metadata"],"official_indicators":result["observed_indicators"],
            "funded_clients_verified":0}))
    elif a.summarize:summary(snapshot)
    else:p.error("Choose --collect, --shard N, --summarize or --self-test")
if __name__=="__main__":main()
