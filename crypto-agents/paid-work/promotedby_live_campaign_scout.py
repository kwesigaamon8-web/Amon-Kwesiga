"""Read-only sponsor market scan for actually available Base-USDC campaigns.

Do not assume a campaign is claimable merely because it has funds.
No posts, applications, signatures, messages, purchases or submissions.
"""
import datetime as dt
import json
import pathlib
import re
import urllib.error
import urllib.request

SOURCE = "https://promotedby.ai/api/v1/opportunities"
OUT = pathlib.Path("paid-opportunity-reports/promotedby-live-campaigns.json")
CLEAN = re.compile(r"[^a-zA-Z0-9 _.,:/#()-]")
def short(x, limit=180):
    return CLEAN.sub("", str(x or ""))[:limit]

def scan(payload, now=None):
    if not isinstance(payload, dict) or not isinstance(payload.get("opportunities"), list):
        raise ValueError("SOURCE_FORMAT_ERROR")
    campaigns = []
    for x in payload["opportunities"]:
        if not isinstance(x, dict):
            continue
        cents = x.get("available_cents", 0)
        if isinstance(cents, bool) or not isinstance(cents, (int, float)) or cents < 0:
            cents = 0
        acts = x.get("allowed_activities", [])
        keys = [short(a.get("key"), 40) for a in acts if isinstance(a, dict)] if isinstance(acts, list) else []
        active = x.get("status") == "live" and cents >= 100
        campaigns.append({
            "id": short(x.get("id"), 72),
            "name": short(x.get("name") or x.get("title"), 160),
            "status": short(x.get("status"), 48),
            "advertised_available_usdc": round(cents / 100, 2),
            "allowed_activity_keys": keys,
            "campaign_link": short(x.get("url") or x.get("link"), 240),
            "source_advertises_live_funds": active,
            "submission_authorized": False,
            "eligibility_verified": False,
            "payout_verified": False
        })
    campaigns.sort(key=lambda x:(x["source_advertises_live_funds"],x["advertised_available_usdc"]),reverse=True)
    return campaigns

def self_test():
    demo = {"opportunities":[
       {"id":"a", "title":"Sponsor brief", "status":"live","available_cents":1000,
        "allowed_activities":[{"key":"other"}]},
       {"id":"b", "status":"closed", "available_cents":10000},
       {"id":"c", "status":"live", "available_cents":0}
    ]}
    res=scan(demo)
    assert len(res)==3
    assert [x["id"] for x in res if x["source_advertises_live_funds"]]==["a"]
    assert res[0]["advertised_available_usdc"]==10
    assert not res[0]["eligibility_verified"] and not res[0]["submission_authorized"]
    try: scan({"not_the_feed": []})
    except ValueError: pass
    else: raise AssertionError("Bad feed must not be reported as empty")
    print("SPONSOR_CAMPAIGN_READ_ONLY_FILTER_TEST_PASS")

def main():
    self_test()
    output={"checked_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "source":SOURCE,"read_only":True,"claim_submissions":0,
            "earned_usdc":0,"status":"SOURCE_NOT_CHECKED","campaigns":[]}
    try:
        req=urllib.request.Request(SOURCE,headers={
           "Accept":"application/json","User-Agent":"B1B2-Owner-ReadOnlySponsorScout/1.0"})
        with urllib.request.urlopen(req,timeout=15) as response:
            raw=json.load(response)
        output["campaigns"]=scan(raw)
        output["status"]="SOURCE_CHECKED_NOT_ELIGIBILITY_PROVEN"
        live=[x for x in output["campaigns"] if x["source_advertises_live_funds"]]
        output["source_live_count"]=len(live)
        output["action"]="Review original terms, placement rules, owner access and dry_run before any paid work"
        print("SPONSOR_LIVE_FUNDING_NOT_EARNINGS",json.dumps(live[:30],ensure_ascii=False))
    except Exception as e:
        output["status"]="SOURCE_ERROR_NO_EMPTY_MARKET_CLAIM"
        output["source_error"]=type(e).__name__+":"+short(e,150)
        print("SPONSOR_SOURCE_ERROR",output["source_error"])
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n")
if __name__=="__main__": main()
