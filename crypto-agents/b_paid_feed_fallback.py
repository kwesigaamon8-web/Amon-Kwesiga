"""Backup public paid-task inventory if GitHub Search API returns HTTP 403.

This reads an existing public open-source bounty directory. The directory's
'verified payer' label is SECONDARY evidence only; it does not establish that
this agent is eligible or the money is escrowed, accepted or paid.
"""
import datetime as dt
import json
import re
import urllib.request

FEED="https://raw.githubusercontent.com/krishi-shah/dailybugbounties/main/data/bounties.json"
AGE_HOURS=72
MAX=32
REJECT_TITLE=re.compile(r"(?i)(?:\b(?:radar|digest|alert|mirror|test bounty|site credit|vote:)\b|\[\$0\]|bounty \$0)")
SKIP_REPOS=("bounty-plaza","bountyscout","bounty-bot")

def extract(payload,now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    try:
        last=dt.datetime.fromisoformat(payload["generated_at"].replace("Z","+00:00"))
        age=(now-last).total_seconds()/3600
        if age<0 or age>AGE_HOURS:
            return {"status":"STALE_OR_FUTURE_DIRECTORY","candidates":[],"age_hours":round(age,2)}
    except (KeyError,ValueError,TypeError):
        return {"status":"DIRECTORY_MISSING_VALID_TIMESTAMP","candidates":[]}
    items=[]
    for row in payload.get("bounties",[]):
        if not isinstance(row,dict):continue
        link=row.get("url")
        if not isinstance(link,str) or not re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+/issues/\d+",link):continue
        title=str(row.get("title") or "")
        repo=str(row.get("repo") or "").lower()
        if REJECT_TITLE.search(title) or any(w in repo for w in SKIP_REPOS):continue
        if row.get("state") not in ("OPEN","open") or row.get("archived") is True:continue
        pay=row.get("amount_usd")
        if not isinstance(pay,(float,int)) or pay<1:continue
        if row.get("verified_payer") is not True:continue
        # Source assertions remain unverified until we re-open original issue.
        items.append({
          "original_url":link,"title":title[:170],
          "status":"POSSIBLE_PAID_TASK_UNVERIFIED",
          "secondary_directory_url":FEED,
          "source":"third-party dated public inventory; original issue check pending",
          "secondary_payer_history_claim":True,
          "secondary_amount_usd_claim":pay,
          "secondary_payment_channel":str(row.get("payout") or "unknown"),
          "source_last_checked_utc":payload["generated_at"],
          "original_source_read_now":False,
          "reward_funded":False,
          "claim_eligible_for_owner":None,
          "payout_network_accepted":None,
          "work_completed":False,"external_payer_contact_sent":False,
          "verified_paid_receipt":False,
          "next_step":"Re-open original issue, comments and direct payout terms; confirm eligibility and real sponsor approval. No claim, message, work acceptance or payment established."
        })
    # Prefer accessible code/docs tasks; no hard exclusion of other claims.
    items.sort(key=lambda x:(-int(x["secondary_payer_history_claim"]),
       int(x["secondary_amount_usd_claim"]>=1000),x["original_url"]))
    return {"status":"FRESH_SECONDARY_DIRECTORY_ONLY","candidates":items[:MAX],
            "age_hours":round(age,2)}

def fetch():
    req=urllib.request.Request(FEED,headers={
      "User-Agent":"B1B2SourceQualityFallback/1.0",
      "Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=15) as r:
       data=json.loads(r.read(2_000_000))
    return extract(data)

def selftest():
    now=dt.datetime(2026,11,14,11,0,0,tzinfo=dt.timezone.utc)
    d={"generated_at":"2026-11-14T10:00:00+00:00","bounties":[
     {"title":"[$75] Fix concrete API endpoint 502 handling",
      "url":"https://github.com/real/project/issues/10","state":"OPEN",
      "amount_usd":75,"verified_payer":True,"payout":"crypto-wallet"},
     {"title":"[$600] mirror alert","url":"https://github.com/bounty-plaza/repo/issues/3",
      "state":"OPEN","amount_usd":600,"verified_payer":True},
     {"title":"[$250] legit but no payer history","url":"https://github.com/real/project/issues/7",
      "state":"OPEN","amount_usd":250,"verified_payer":False},
     {"title":"[$0] translate","url":"https://github.com/real/project/issues/12",
      "state":"OPEN","amount_usd":0,"verified_payer":True},
    ]}
    a=extract(d,now)
    assert len(a["candidates"])==1,a
    assert a["candidates"][0]["original_url"].endswith("/10")
    assert a["candidates"][0]["reward_funded"] is False
    assert extract(d,now+dt.timedelta(days=5))["status"]=="STALE_OR_FUTURE_DIRECTORY"
    print("SECONDARY_SOURCE_FALLBACK_TEST_PASS")
if __name__=="__main__":selftest()
