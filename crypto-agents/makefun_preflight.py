"""Read-only verify a funded crypto coding contest before spending work or money."""
import json,urllib.request,urllib.error,datetime as dt
from pathlib import Path
BASE="https://make.fun/api/competitions/agency-poem-01"
urls={"requirements":BASE+"/requirements","competition":BASE}
out={"checked_at":dt.datetime.now(dt.timezone.utc).isoformat(),
     "api":"make.fun official public API",
     "no_agent_account_created":True,"no_wallet_connected":True,
     "no_payment_or_submission":True,"items":{}}
for key,url in urls.items():
    try:
        req=urllib.request.Request(url,headers={"Accept":"application/json","User-Agent":"GenuinePrizeReadOnlyPreflight/1.0"})
        with urllib.request.urlopen(req,timeout=15) as res:
            raw=json.loads(res.read(500000))
        if not isinstance(raw,dict):raise ValueError("Expected object")
        root=raw.get("data") if isinstance(raw.get("data"),dict) else raw
        out["items"][key]={"status":"AVAILABLE","top_keys":list(root)[:40],
          "important":{k:root.get(k) for k in ("slug","title","status","starts_at","ends_at","deadline","prerequisites",
                 "deliverables","handed_over_places","eligibility","rules","prize","reward") if k in root},
          "raw_data_excerpt":json.dumps(root,ensure_ascii=False)[:5000]}
    except (urllib.error.URLError,TimeoutError,ValueError,OSError) as ex:
        out["items"][key]={"status":"UNAVAILABLE","error":type(ex).__name__+":"+str(ex)[:200]}
p=Path("crypto-contest-preflight")
p.mkdir(exist_ok=True)
(p/"agency-poem-01-requirements.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")


# Enumerate actual public paid opportunities; DO NOT create accounts or entries.
# Do not infer a user's eligibility from platform status or nominal prize.
try:
    req=urllib.request.Request("https://make.fun/api/competitions",
        headers={"Accept":"application/json","User-Agent":"ReadOnlyFundedBountyEligibility/1.0"})
    with urllib.request.urlopen(req,timeout=15) as r:
        raw=json.loads(r.read(1_800_000))
    data=raw.get("data",raw) if isinstance(raw,dict) else raw
    if isinstance(data,list): items=data
    elif isinstance(data,dict):
        items=next((data[k] for k in ("competitions","items","results","bounties")
                    if isinstance(data.get(k),list)),[])
    else:items=[]
    shortlist=[]
    for row in items[:24]:
        if not isinstance(row,dict):continue
        slug=row.get("slug")
        if not slug:continue
        try:
            u="https://make.fun/api/competitions/"+str(slug)+"/requirements"
            request=urllib.request.Request(u,headers={"Accept":"application/json"})
            with urllib.request.urlopen(request,timeout=9) as r:
                raw_req=json.loads(r.read(900000))
            d=raw_req.get("data",raw_req) if isinstance(raw_req,dict) else {}
            if not isinstance(d,dict):d={}
            prereqs=d.get("prerequisites",[])
            fee=d.get("entry_fee",{})
            entry={"title":row.get("title"),"slug":slug,"status":row.get("status"),
                "deadline":row.get("deadline"),
                "rewardAmount":row.get("rewardAmount"),
                "entryFeeUsd":row.get("entryFeeUsd"),
                "handed_over_places":d.get("handed_over_places"),
                "prerequisites":prereqs,
                "entry_fee":fee,
                "requirements_api_checked":True,
                "authenticated_submission":False,
                "prize_guaranteed":False}
            shortlist.append(entry)
        except (urllib.error.URLError,TimeoutError,ValueError,OSError) as e:
            shortlist.append({"slug":slug,"requirements_api_checked":False,
                              "error":type(e).__name__})
    out["all_public_bounties_review"]={"list_api_accessible":True,"list_count":len(items),
        "items_checked":len(shortlist),"entries":shortlist}
    print("MAKEFUN_GLOBAL_BOUNTIES",json.dumps({"listed":len(items),
       "checked":len(shortlist),
       "sample":[{"slug":x.get("slug"),"handed_over_places":x.get("handed_over_places"),
                   "entry_fee":x.get("entry_fee"),"prerequisites":x.get("prerequisites")}
                 for x in shortlist[:24]]},ensure_ascii=False)[:8500])
except (urllib.error.URLError,TimeoutError,ValueError,OSError) as e:
    out["all_public_bounties_review"]={"list_api_accessible":False,
                                         "error":type(e).__name__+":"+str(e)[:150]}
( __import__("pathlib").Path("crypto-contest-preflight")/"all-public-bounty-prereqs.json").write_text(
    json.dumps(out.get("all_public_bounties_review"),ensure_ascii=False,indent=2)+"\n")

print("MAKEFUN_ELIGIBILITY_PREFLIGHT",json.dumps({
 k:{"status":v["status"],"fields":v.get("top_keys",[])[:15],
    "prerequisites":v.get("important",{}).get("prerequisites"),
    "handed_over_places":v.get("important",{}).get("handed_over_places")}
 for k,v in out["items"].items()},ensure_ascii=False))
