"""Country allocation of ALL 30 original/Enigma B1/B2 systems by internet users.

This is public-data planning, never Bitcoin mining on GitHub Actions.
No virtual role means real hardware, hash-rate, internet user or payment.
"""
from __future__ import annotations
import csv,json,urllib.request,urllib.error
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from datetime import datetime,timezone

ROOT=Path("crypto-agents")
OUT=Path("btc-country-mining-plan")
ROLE_SYSTEMS=30
ROLES_PER_SYSTEM=375_188_632_680
TOTAL=ROLE_SYSTEMS*ROLES_PER_SYSTEM
YEARS=("2024","2023","2022","2021")
COUNTRY_API="https://api.worldbank.org/v2/country?format=json&per_page=500"
BASE="https://api.worldbank.org/v2/country/all/indicator/"
POP="SP.POP.TOTL"
PEN="IT.NET.USER.ZS"
SOURCES={
 "population":"https://data.worldbank.org/indicator/SP.POP.TOTL",
 "internet_percentage":"https://data.worldbank.org/indicator/IT.NET.USER.ZS",
 "metadata":COUNTRY_API,
}
ROUTES={
 "B1":"bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z",
 "B2":"bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9",
}
def read_api(url):
    req=urllib.request.Request(url,headers={
      "User-Agent":"EnigmaCountryInternetAllocation/1.0 (public statistical download)",
      "Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=25) as r:
        raw=r.read(2300000)
    obj=json.loads(raw)
    if not isinstance(obj,list) or len(obj)!=2 or not isinstance(obj[1],list):
        raise ValueError("Unexpected World Bank API response")
    return obj[1]

def get_ind(code):
    url=BASE+code+"?format=json&per_page=30000&date=2021:2024"
    docs=read_api(url)
    data={}
    for x in docs:
        if not isinstance(x,dict) or x.get("value") is None:continue
        country=(x.get("country") or {}).get("id")
        year=x.get("date")
        if not isinstance(country,str) or year not in YEARS:continue
        try: val=Decimal(str(x["value"]))
        except Exception:continue
        if val.is_finite():data[(country,year)]=val
    return data

def allocate_exact(amount, weights):
    """Hamilton largest-remainder, exact integer totals and stable ISO3 tie breaks."""
    assert type(amount)==int and amount>0
    total=sum(weights.values(),0)
    if total<=0:raise ValueError("No usable internet counts")
    floors={k:amount*v//total for k,v in weights.items()}
    leftover=amount-sum(floors.values())
    ranked=sorted(weights,key=lambda k:(-((amount*weights[k])%total),k))
    for k in ranked[:leftover]:floors[k]+=1
    assert sum(floors.values())==amount
    return floors

def build():
    countries=read_api(COUNTRY_API)
    pops=get_ind(POP)
    internet=get_ind(PEN)
    rows=[]
    for c in countries:
        if not isinstance(c,dict):continue
        region=(c.get("region") or {})
        if region.get("id")=="NA":continue # WB aggregate, not economy
        id3=c.get("id");iso2=c.get("iso2Code");name=c.get("name")
        if not isinstance(id3,str) or len(id3)!=3 or not isinstance(name,str):continue
        estimate=0;year="";pct=None;pop=None
        for y in YEARS:
            a=pops.get((iso2,y));b=internet.get((iso2,y))
            if a is None or b is None or a<0 or not (Decimal(0)<=b<=Decimal(100)):
                continue
            pop=int(a)
            pct=b
            estimate=int((a*b/Decimal(100)).quantize(Decimal(1),rounding=ROUND_HALF_UP))
            year=y
            break
        rows.append({
            "ISO3":id3,"ISO2":iso2,"Country or economy":name,
            "WB Region":region.get("value"),"Data year":year or "NO_MATCHING_DATA",
            "Population":pop,"Internet use (%)":float(pct) if pct is not None else None,
            "Estimated internet users":estimate,"Data available":bool(year),
        })
    rows.sort(key=lambda r:(-r["Estimated internet users"],r["ISO3"]))
    usable={r["ISO3"]:r["Estimated internet users"] for r in rows if r["Data available"] and r["Estimated internet users"]>0}
    assigned=allocate_exact(ROLES_PER_SYSTEM,usable)
    first=0
    for r in rows:
        n=assigned.get(r["ISO3"],0)
        r["Virtual roles per B system"]=n
        r["B1 total virtual allocation (15 systems)"]=n*15
        r["B2 total virtual allocation (15 systems)"]=n*15
        r["Total virtual role allocation (30 systems)"]=n*30
        r["Per-system role start"]=first if n else ""
        r["Per-system role end inclusive"]=first+n-1 if n else ""
        first+=n
        r["Actual miners deployed"]=0
        r["Verified hashrate H/s"]=0
        r["Bitcoin mined BTC"]=0
        r["Deployment status"]="NO AUTHORIZED COUNTRY MINING HOST VERIFIED"
        r["Mining task"]="Bitcoin SHA-256 only on owner-authorized devices"
    assert first==ROLES_PER_SYSTEM
    assert sum(r["Total virtual role allocation (30 systems)"] for r in rows)==TOTAL
    OUT.mkdir(parents=True,exist_ok=True)
    head=list(rows[0].keys())
    with (OUT/"country_allocations.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=head);w.writeheader();w.writerows(rows)
    summary={
      "generated_utc":datetime.now(timezone.utc).isoformat(),
      "purpose":"BTC mining country planning ONLY, not real miner deployment",
      "country_and_economy_rows":len(rows),
      "economies_with_matching_internet_data":sum(r["Data available"] for r in rows),
      "missing_data_rows":sum(not r["Data available"] for r in rows),
      "reference_years":YEARS,
      "weight": "Population in year * internet-use percentage in same year; estimated number of internet users",
      "role_systems":ROLE_SYSTEMS,"virtual_roles_per_system":ROLES_PER_SYSTEM,
      "virtual_role_slots_assigned":TOTAL,
      "original_two_b_systems_plus_28_enigma":True,
      "actual_mining_workers_deployed":0,
      "confirmed_live_country_mining_hashrate":0,
      "bitcoin_receipts_verified":0,
      "bitcoin_payment_routes":ROUTES,
      "data_sources":SOURCES,
      "limits":[
       "No GH Actions mining: GitHub Terms prohibit cryptomining",
       "No mining on third-party devices or networks without owner/operator consent",
       "Internet users are a proxy for distribution, NOT available mining hardware or electricity",
       "No data yields zero unallocated roles, not a claim of zero internet users",
       "Assigned B worker roles are virtual addresses, not activated processes",
       "Profitability depends on ASIC hashrate, power cost, BTC difficulty and payout fees",
      ]
    }
    (OUT/"country_summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf8")
    with (OUT/"COUNTRY_MINING_STATUS.txt").open("w",encoding="utf8") as f:
        f.write("BITCOIN MINING COUNTRY ALLOCATION — VIRTUAL TASK ROSTER\n")
        f.write(f"Rows: {len(rows)} countries/economies. Internet-data rows: {summary['economies_with_matching_internet_data']}.\n")
        f.write(f"TOTAL VIRTUAL ROLE SLOTS: {TOTAL:,}. ACTUALLY RUNNING MINERS VERIFIED: 0.\n")
        f.write("This is a mathematical deployment plan, NOT real miners installed worldwide.\n")
        f.write(f"B1 Bitcoin mainnet receiver: {ROUTES['B1']}\n")
        f.write(f"B2 Bitcoin mainnet receiver: {ROUTES['B2']}\n")
        f.write("Sources: "+json.dumps(SOURCES)+"\n")
    print("ENIGMA_COUNTRY_PLAN_COMPLETED "+json.dumps({
        "rows":len(rows),"with_data":summary["economies_with_matching_internet_data"],
        "virtual_roles":TOTAL,"active_miners":0,
        "top5":[[r["Country or economy"],r["Total virtual role allocation (30 systems)"]] for r in rows[:5]]
        }))
    return rows,summary

if __name__=="__main__":build()
