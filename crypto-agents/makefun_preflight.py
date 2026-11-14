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
print("MAKEFUN_ELIGIBILITY_PREFLIGHT",json.dumps({
 k:{"status":v["status"],"fields":v.get("top_keys",[])[:15],
    "prerequisites":v.get("important",{}).get("prerequisites"),
    "handed_over_places":v.get("important",{}).get("handed_over_places")}
 for k,v in out["items"].items()},ensure_ascii=False))
