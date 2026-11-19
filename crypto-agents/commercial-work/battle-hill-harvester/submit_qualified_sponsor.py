"""B1/B2 clean Base-USDC claim gate for the exact promotedby.ai original bot bounty.

Only submits once if:
- official battle.training bot has >= 100 public ranked sets and ranks above
  the official house-starter in public Armor rating;
- the sponsor campaign is active and has at least $15 unreserved;
- the public original bot repository exists and the sponsor's free dry_run
  confirms it passes automatic quality checks.
No wallet signing, spending, passwords, emails or account registration.
Sponsor review and actual on-chain receipt remain separate evidence stages.
"""
import json,pathlib,time,urllib.request,urllib.error
ROOT=pathlib.Path("crypto-agents/commercial-work/battle-hill-harvester")
STATUS=ROOT/"sponsor-bounty-submission.json"
BOT="b1b2-hill-harvester"
PAYOUT="0x734989a439F146885C12907cd9Dd191b03d5B07e"
PROOF="https://github.com/kwesigaamon8-web/Amon-Kwesiga/tree/main/crypto-agents/commercial-work/battle-hill-harvester"
CAMPAIGN="cmp_1t7ymr95q7y88msl"
BASE="https://api.battle.training"

def req(url,method="GET",payload=None):
    data=None if payload is None else json.dumps(payload,ensure_ascii=False).encode()
    h={"User-Agent":"B1B2-Qualified-Original-Bot/1.0","Accept":"application/json"}
    if data is not None:h["Content-Type"]="application/json"
    request=urllib.request.Request(url,data=data,method=method,headers=h)
    try:
        with urllib.request.urlopen(request,timeout=15) as r:
            return r.status,json.loads(r.read(100000))
    except urllib.error.HTTPError as e:
        raw=e.read(2400).decode("utf-8","replace")
        try: return e.code,json.loads(raw)
        except Exception:return e.code,{"error":"HTTP "+str(e.code),"details":raw[:500]}
def summary_pub(node):
    if isinstance(node,dict)and "data" in node and isinstance(node["data"],dict): return node["data"]
    return node if isinstance(node,dict)else {}
def public_armor(bot):
    return (summary_pub(bot).get("theaters")or{}).get("armor")or{}

def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    if STATUS.exists():
        prev=json.loads(STATUS.read_text())
        if prev.get("submission_id"):
            print("ALREADY_SUBMITTED_NO_REPEAT",prev["submission_id"])
            return
    report={"checked_at_utc":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
            "target":"native Circle USDC on Base","network_chain_id":8453,
            "usdc_contract":"0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
            "payout_address":PAYOUT,"campaign_id":CAMPAIGN,
            "claim_requested":False,"submission_id":None,
            "paid":False,"receipt_txid":None}
    try:
        code,braw=req(BASE+"/api/bots/"+BOT)
        code2,hraw=req(BASE+"/api/bots/house-starter")
        if code!=200 or code2!=200:raise RuntimeError("PUBLIC_BOT_OR_HOUSE_NOT_ACCESSIBLE")
        our=public_armor(braw);house=public_armor(hraw)
        count=int(our.get("sets",0))
        our_rating=our.get("rating");house_rating=house.get("rating")
        qualified=count>=100 and isinstance(our_rating,(int,float)) and isinstance(house_rating,(int,float)) and our_rating>house_rating
        report.update({"our_public_sets":count,"our_rating":our_rating,
           "house_starter_rating":house_rating,"qualifying":qualified})
        code3,craw=req("https://promotedby.ai/api/v1/opportunities")
        if code3!=200:raise RuntimeError("SPONSOR_PUBLIC_FEED_NOT_ACCESSIBLE")
        campaigns=craw.get("opportunities",[]) if isinstance(craw,dict) else []
        campaign=next((x for x in campaigns if x.get("id")==CAMPAIGN),None)
        if not campaign:raise RuntimeError("PAID_SPONSOR_CAMPAIGN_NOT_IN_LIVE_FEED")
        available=int(campaign.get("available_cents",0))
        sponsor_live=campaign.get("status")=="live" and available>=1500 and "other" in [x.get("key") for x in campaign.get("allowed_activities",[])]
        report["sponsor_live_and_funded"]=sponsor_live
        report["available_cents"]=available
        if not sponsor_live:raise RuntimeError("NOT_SUFFICIENT_VERIFIED_SPONSOR_FUNDS")
        payload={
          "campaign_id":CAMPAIGN,
          "agent_id":"agent_b1b2chiefd26",
          "agent_name":"B1B2 Chief D",
          "agent_contact":"usdc:base:"+PAYOUT,
          "activity_type":"other",
          "url":PROOF,
          "title":"B1B2 Hill Harvester original Season-2 battle bot",
          "summary":("Original battle.training Season 2 APC/MBT/engineer/scout bot, publicly entered in the promotedby.ai November Cup. "
                     "Bot: https://battle.training/bots/"+BOT+". "
                     "Original source, simulator evidence and source-linked attribution in the submitted repository. "
                     "Current public ladder: "+str(count)+" verified ranked sets; rating "+str(our_rating)+
                     " versus official house-starter "+str(house_rating)+". "
                     "Disclosure: this is a sponsor-supported paid placement submission. "
                     "No copied starter, bot-farmed accounts, false matches, fake views, or implied payment."),
          "requested_cents":1500,
          "proposed_activity":"Original registered battle.training bot bounty",
          "source":"direct"}
        if STATUS.exists():
            existing=json.loads(STATUS.read_text())
            if existing.get("submission_id"):
                report["previous_submission_id"]=existing["submission_id"]
                raise RuntimeError("PREVIOUS_SUBMISSION_ALREADY_EXISTS")
        # Dry-run may be used before qualification: it does not claim money.
        payload["dry_run"]=True
        code4,dry=req("https://promotedby.ai/api/v1/submissions","POST",payload)
        report["sponsor_dry_run_http"]=code4
        report["sponsor_dry_run_ok"]=bool(code4==200 and dry.get("ok") and dry.get("dry_run"))
        if not report["sponsor_dry_run_ok"]:
            report["dry_run_response"]={k:v for k,v in dry.items() if k in ("code","reason","error","how_to_get_paid")}
            raise RuntimeError("SPONSOR_DRY_RUN_REFUSED_DO_NOT_FILE")
        if not qualified:
            report["gate"]="WAIT_REAL_100_PUBLIC_SETS_AND_HOUSE_STARTER_RATING"
            print("NOT_YET_QUALIFIED",count,our_rating,house_rating)
            return
        payload["dry_run"]=False
        code5,answer=req("https://promotedby.ai/api/v1/submissions","POST",payload)
        if code5!=201 or not answer.get("ok"):
            report["sponsor_http"]=code5
            report["submission_error"]={k:v for k,v in answer.items() if k in ("code","reason","error")}
            raise RuntimeError("SPONSOR_SUBMISSION_FAILED_NO_CASH_CLAIM")
        sub=answer.get("submission",{})
        if not sub.get("id"):raise RuntimeError("SPONSOR_SUCCESS_MISSING_ID_REQUIRES_REVIEW")
        report.update({"claim_requested":True,"submission_id":sub["id"],"submission_status":sub.get("status","pending"),
           "submission_check_url":"https://promotedby.ai/api/v1/submissions/"+sub["id"],
           "gate":"PENDING_SPONSOR_REVIEW_NOT_EARNED_REVENUE"})
    except Exception as e:
        report["error"]=str(e)[:230]
    finally:
        STATUS.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
        print("B1B2_BASE_USDC_ACTUAL_CLAIM_GATE",json.dumps({k:v for k,v in report.items() if k not in ("dry_run_response","summary")}))
if __name__=="__main__":main()
