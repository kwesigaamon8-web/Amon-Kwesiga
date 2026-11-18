"""Read-only SwarmMemo USDC task scout for B1/B2.

Never mistakes transferable platform credits for actual USDC. Does NOT register
agents, post/reply/claim, sign with any key, modify wallets or fabricate receipts.
"""
from __future__ import annotations
import argparse
import datetime as dt
import decimal
import json
import urllib.request
from pathlib import Path

API = "https://swarmmemo.com/api/works?kind=rewarded&limit=80"
OUT = Path("paid-opportunity-reports") / "swarmmemo-usdc.json"

def parse_works(payload):
    if isinstance(payload, list):
        return payload
    if not isinstance(payload, dict):
        return []
    data = payload.get("data", payload)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("works", "items", "results", "tasks"):
            if isinstance(data.get(key), list):
                return data[key]
    return []

def _usdc(work):
    # Public API uses reward={amount, unit:"credit"} plus
    # standing.tiers=[{name, credits, usdc}], not the marketing-page format.
    reward=work.get("reward") or {}
    standing=work.get("standing") or {}
    if not isinstance(reward,dict):reward={}
    if not isinstance(standing,dict):standing={}
    candidates=[reward.get("usdc"),reward.get("usdc_amount")]
    if str(reward.get("unit") or "").lower()=="usdc":
        candidates.append(reward.get("amount"))
    for tier in standing.get("tiers") or []:
        if isinstance(tier,dict):candidates.append(tier.get("usdc"))
    direct=work.get("reward_usdc")
    if isinstance(direct,dict):candidates.append(direct.get("amount"))
    elif isinstance(direct,(str,int,float)):candidates.append(direct)
    amounts=[]
    for v in candidates:
        try:
            n=decimal.Decimal(str(v if v is not None else "0"))
            if n.is_finite() and n>0:amounts.append(n)
        except decimal.InvalidOperation:
            pass
    return max(amounts,default=decimal.Decimal(0))

def screen(payload, when=None):
    when=when or dt.datetime.now(dt.timezone.utc)
    listed=parse_works(payload)
    reviewed=[]
    for w in listed:
        if not isinstance(w, dict):continue
        amount=_usdc(w)
        if amount<=0:continue
        state=str(w.get("state") or w.get("status") or "").lower()
        standing=w.get("standing") or {}
        if not isinstance(standing, dict):standing={}
        available=standing.get("open")
        if type(available)!=int: available=None
        deadline=w.get("deadline") or w.get("expires_at")
        if deadline:
            try:
                if isinstance(deadline,(int,float)):
                    ending=dt.datetime.fromtimestamp(deadline,tz=dt.timezone.utc)
                else:
                    ending=dt.datetime.fromisoformat(str(deadline).replace("Z","+00:00"))
                    if ending.tzinfo is None:ending=ending.replace(tzinfo=dt.timezone.utc)
            except (ValueError,OverflowError,OSError):
                ending=None
        else:
            ending=None
        if state in {"cancelled","expired","closed","accepted","completed","paid"}:
            status="REJECT_CLOSED"
        elif ending is not None and ending < when:
            status="REJECT_DEADLINE_PASSED"
        elif available is None:
            status="HOLD_SEAT_AVAILABILITY_UNVERIFIED"
        elif available <= 0:
            status="HOLD_NO_OPEN_SEATS"
        elif state not in ("open", "submitted"):
            status="HOLD_OPEN_STATUS_UNVERIFIED"
        else:
            status="POSSIBLE_USDC_TASK_UNVERIFIED_PAYER_AND_SUBMISSION"
        reviewed.append({
            "id":str(w.get("id") or w.get("message_id") or "")[:80],
            "title":str(w.get("title") or "")[:180],
            "usdc_reward_advertised":str(amount),
            "asset":"USDC","network":"Base",
            "credit_reward_excluded_from_crypto_income":True,
            "seats_stated_available":available,
            "status":status,
            "requires_free_signed_agent_key":True,
            "authenticated_worker_account_connected":False,
            "recipient_ownership_and_token_compatibility_confirmed":False,
            "requester_payment_acceptance_verified":False,
            "actual_usdc_received":False,
            "next_action":"Verify original task and claim eligibility; use only authorized agent identity and owner-approved Base USDC recipient. Never count credits or advertised amounts as earnings.",
        })
    return {
        "source":API,"checked_utc":when.isoformat(),
        "candidate_usdc_rows":len(reviewed),
        "possible_nonzero_usdc_tasks":[x for x in reviewed if x["status"].startswith("POSSIBLE_")],
        "blocked_or_unknown_usdc_tasks":[x for x in reviewed if not x["status"].startswith("POSSIBLE_")],
        "read_only":True,"external_identity_created":False,
        "external_message_or_claim_sent":False,
        "wallet_signing_or_spending":False,
        "paid_receipts_independently_verified":0,
        "limitations":"Site's own tasks API is a discovery source only. Even positive USDC row requires requester, account eligibility, verified owner receiving address, actual acceptance and independent Base USDC TXID.",
    }

def self_test():
    now=dt.datetime(2026,11,18,tzinfo=dt.timezone.utc)
    cases=[
      {"id":"a","state":"open","title":"Usdc task","reward":{"credits":900,"usdc":"0.25"},"standing":{"open":1}},
      {"id":"b","state":"open","reward":{"credits":900},"standing":{"open":5}},
      {"id":"c","state":"open","reward":{"usdc":"1.0"},"standing":{"open":0}},
      {"id":"d","state":"closed","reward":{"usdc":"1.0"},"standing":{"open":2}},
      {"id":"e","state":"open","reward":{"usdc":"0.2"}},
      {"id":"f","state":"open","reward":{"usdc":"0.2"},"standing":{"open":1},"deadline":"2026-11-17T12:00:00Z"},
      {"id":"g","state":"open","reward":{"amount":500,"unit":"credit"},
       "standing":{"open":1,"tiers":[{"name":"notable","credits":80,"usdc":"0.10"}]}},
      {"id":"h","state":"open","reward":{"amount":300,"unit":"credit"},
       "standing":{"open":0,"tiers":[{"name":"brief","credits":30,"usdc":"0.02"}]}},
      {"id":"i","state":"open","reward":{"amount":300,"unit":"credit"},
       "standing":{"open":1,"tiers":[{"name":"brief","credits":30,"usdc":"0.02"}]},
       "deadline":1794900000},
    ]
    result=screen({"data":{"works":cases}},when=now)
    assert len(result["possible_nonzero_usdc_tasks"])==2
    assert result["possible_nonzero_usdc_tasks"][0]["id"]=="a"
    assert all(x["id"]!="b" for x in result["blocked_or_unknown_usdc_tasks"])
    assert len(result["blocked_or_unknown_usdc_tasks"])==6
    assert result["paid_receipts_independently_verified"]==0
    assert result["read_only"] and not result["external_identity_created"]
    assert parse_works({"data":{"items":cases}})==cases
    assert parse_works({"works":cases})==cases
    print("SWARMMEMO_USDC_SCOUT_TEST_PASS: cash-only, open-seat gate, expiry, no identity/wallet/write")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    opts=p.parse_args()
    if opts.self_test:
        self_test()
        return
    result=None
    try:
        request=urllib.request.Request(API,headers={
          "User-Agent":"B1B2-NoRegistration-ReadOnly-SourceCheck/1.0",
          "Accept":"application/json"})
        with urllib.request.urlopen(request,timeout=12) as r:
            raw=r.read(2_000_000)
        payload=json.loads(raw)
        result=screen(payload)
        result["api_status"]="RESPONSE_PARSED_OR_SOURCE_SCHEMA_UNKNOWN"
        result["response_root_keys"]=list(payload)[:15] if isinstance(payload,dict) else []
        result["response_row_count"]=len(parse_works(payload))
        result["sample_public_row_shapes"]=[
          {"keys":list(w)[:25],
           "id":str(w.get("id") or "")[:80],
           "title":str(w.get("title") or "")[:90],
           "reward":w.get("reward"),
           "state":w.get("state"),
           "standing":w.get("standing") if isinstance(w.get("standing"),dict) else None}
          for w in parse_works(payload)[:15] if isinstance(w,dict)
        ]
        if result["response_row_count"]==0:
            result["api_status"]="NO_RECOGNIZED_ROWS_DO_NOT_DECLARE_NO_USDC"
    except Exception as exc:
        result={"source":API,"api_status":"SOURCE_UNAVAILABLE",
                "error":type(exc).__name__,"read_only":True,
                "paid_receipts_independently_verified":0}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("SWARMMEMO_B1B2_USDC_CHECK",json.dumps(result)[:4500])

if __name__=="__main__":main()
