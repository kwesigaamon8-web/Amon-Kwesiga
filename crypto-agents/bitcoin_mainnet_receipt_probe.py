"""Read-only Bitcoin mainnet output verification using independent public APIs.

Never interpret unavailable API as zero balance. Inbound chain output is NOT
automatically real customer earnings or a new voluntary donation.
"""
import datetime as dt
import json
import urllib.error
import urllib.request
from pathlib import Path

ACCOUNTS={
 "transferexperiment":"bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z",
 "BountyScoutAI":"bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9",
}
CUTOFF=dt.datetime.fromisoformat("2026-11-13T00:00:00+00:00")
SOURCES={
 "mempool.space":"https://mempool.space/api/address/{address}/txs",
 "blockstream.info":"https://blockstream.info/api/address/{address}/txs",
}
OUT=Path("bitcoin-receipt-probe")
OUT.mkdir(exist_ok=True)

def check(address,source):
    url=SOURCES[source].format(address=address)
    try:
        req=urllib.request.Request(url,headers={
            "Accept":"application/json","User-Agent":"NoncustodialReadOnlyBTCProof/1.0"})
        with urllib.request.urlopen(req,timeout=14) as response:
            data=json.loads(response.read(2_000_000))
        if not isinstance(data,list):raise ValueError("Expected transactions list")
        found=[]
        for tx in data[:25]:
            txid=tx.get("txid")
            if not isinstance(txid,str) or len(txid)!=64:continue
            status=tx.get("status") or {}
            timestamp=status.get("block_time")
            iso=(dt.datetime.fromtimestamp(timestamp,dt.timezone.utc).isoformat()
                 if isinstance(timestamp,(int,float)) else None)
            for index,output in enumerate(tx.get("vout") or []):
                if output.get("scriptpubkey_address")==address and isinstance(output.get("value"),int) and output["value"]>0:
                    found.append({"txid":txid,"vout":index,"satoshi":output["value"],
                                  "btc":round(output["value"]/1e8,8),
                                  "confirmed":bool(status.get("confirmed")),
                                  "time_utc":iso,"payer_origin":"NOT_PROVEN"})
        return {"source":source,"url":url,"status":"AVAILABLE","tx_rows":len(data),
                "receiving_outputs":found}
    except (urllib.error.URLError,TimeoutError,ValueError,OSError) as exc:
        return {"source":source,"url":url,"status":"UNAVAILABLE",
                "error":type(exc).__name__+":"+str(exc)[:180],
                "receiving_outputs":[]}

def run():
    outcome={"as_of_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
             "since_utc":CUTOFF.isoformat(),
             "receipts_are_not_automatically_income":True,"accounts":{}}
    for fleet,address in ACCOUNTS.items():
        per=[check(address,src) for src in SOURCES]
        pairs={}
        for r in per:
            if r["status"]!="AVAILABLE":continue
            for v in r["receiving_outputs"]:
                key=(v["txid"],v["vout"],v["satoshi"])
                if key not in pairs:pairs[key]={**v,"sources":[]}
                pairs[key]["sources"].append(r["source"])
        recent=[x for x in pairs.values() if x["time_utc"] and
                dt.datetime.fromisoformat(x["time_utc"])>=CUTOFF]
        live=sum(x["status"]=="AVAILABLE" for x in per)
        outcome["accounts"][fleet]={
            "address":address,"network":"BTC Bitcoin mainnet",
            "explorers_available":live,
            "status":"NOT_VERIFIABLE_EXPLORERS_UNREACHABLE" if live==0 else
                     "RECENT_CONFIRMED_RECEIVING_OUTPUTS_FOUND" if recent else
                     "NO_RECENT_OUTPUTS_IN_LATEST_PAGE_NOT_EXHAUSTIVE",
            "recent_outputs":recent,
            "sources":per,
            "external_payment_or_donation_proven":False,
            "full_transaction_history_checked":False,
        }
    (OUT/"BTC_PUBLIC_RECEIPTS.json").write_text(json.dumps(outcome,indent=2)+"\n")
    lines=["# Read-only Bitcoin mainnet receipt probe","",
           "Time: "+outcome["as_of_utc"],""]
    for fleet,d in outcome["accounts"].items():
        lines+=["## "+fleet,d["address"],"Explorer responses: "+str(d["explorers_available"])+"/2",
                "Status: "+d["status"],""]
        for t in d["recent_outputs"]:
            lines.append("BTC "+str(t["btc"])+" | txid "+t["txid"]+" | vout "+str(t["vout"])+
                         " | independent sources "+", ".join(t["sources"])+" | payer unknown")
    lines+=["","Any confirmed on-chain transfer requires an independent payer or work-acceptance check before classifying as earnings.",
            "If explorers are unreachable, NO BALANCE CONCLUSION IS POSSIBLE."]
    (OUT/"BTC_PUBLIC_RECEIPTS.md").write_text("\n".join(lines)+"\n")
    print("MAINNET_RECEIPT_CHECK",json.dumps({
      fleet:{"status":d["status"],"explorers_available":d["explorers_available"],
             "recent_outputs":len(d["recent_outputs"])}
      for fleet,d in outcome["accounts"].items()}))
if __name__=="__main__":
    assert len(ACCOUNTS)==2 and len(set(ACCOUNTS.values()))==2
    assert all(len(x)==42 and x.startswith("bc1q") for x in ACCOUNTS.values())
    run()
