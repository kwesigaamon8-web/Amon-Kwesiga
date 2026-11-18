"""Read-only Bitcoin mainnet output verification using independent public APIs.

Never interpret unavailable API as zero balance. Inbound chain output is NOT
automatically real customer earnings or a new voluntary donation.
"""
import argparse
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

def parse_address_summary(payload):
    """Validate Esplora public address statistics; never interpret malformed as zero."""
    if not isinstance(payload,dict):raise ValueError("Invalid address JSON")
    def stats(section):
        obj=payload.get(section)
        if not isinstance(obj,dict):raise ValueError("Missing "+section)
        out={}
        for key in ("funded_txo_sum","spent_txo_sum","tx_count"):
            val=obj.get(key)
            if isinstance(val,bool) or not isinstance(val,int) or val<0:
                raise ValueError("Invalid address "+section+"."+key)
            out[key]=val
        return out
    chain=stats("chain_stats")
    pending=stats("mempool_stats")
    if chain["spent_txo_sum"]>chain["funded_txo_sum"]:
        raise ValueError("Impossible negative confirmed address balance")
    confirmed=chain["funded_txo_sum"]-chain["spent_txo_sum"]
    adjustment=pending["funded_txo_sum"]-pending["spent_txo_sum"]
    return {
        "confirmed_sats":confirmed,
        "confirmed_btc":f"{confirmed//100_000_000}.{confirmed%100_000_000:08d}",
        "unconfirmed_net_change_sats":adjustment,
        "combined_sats_including_mempool":confirmed+adjustment,
        "confirmed_tx_count":chain["tx_count"],
        "mempool_tx_count":pending["tx_count"],
        "is_not_recent_earnings_or_revenue":True,
    }


def check_balance(address,source):
    """Public address balance stats, separate from newest-page transaction samples."""
    url=SOURCES[source].format(address=address).removesuffix("/txs")
    try:
        req=urllib.request.Request(url,headers={
            "Accept":"application/json","User-Agent":"NoncustodialReadOnlyBTCProof/1.1"})
        with urllib.request.urlopen(req,timeout=14) as response:
            data=json.loads(response.read(200000))
        return {"source":source,"url":url,"status":"AVAILABLE",
                "statistics":parse_address_summary(data)}
    except (urllib.error.URLError,TimeoutError,ValueError,OSError) as exc:
        return {"source":source,"url":url,"status":"UNAVAILABLE",
                "error":type(exc).__name__+":"+str(exc)[:180]}


def evaluate_balances(entries):
    valid=[item for item in entries if item["status"]=="AVAILABLE"]
    if not valid:
        return {"status":"NO_EXPLORER_BALANCE_EVIDENCE",
                "confirmed_sats":None,"confirmed_btc":None,
                "unconfirmed_net_change_sats":None,"explorers_agree":None,
                "sources_successful":0,"verified_new_earned_sats":None}
    fields=("confirmed_sats","unconfirmed_net_change_sats",
            "combined_sats_including_mempool","confirmed_tx_count","mempool_tx_count")
    agrees=(len(valid)==len(entries) and all(
        all(item["statistics"][field]==valid[0]["statistics"][field] for field in fields)
        for item in valid[1:]))
    consensus="TWO_EXPLORER_CONSENSUS" if agrees else (
        "SINGLE_SOURCE_NOT_CROSSCHECKED" if len(valid)==1 else
        "EXPLORER_DISAGREEMENT")
    stats=valid[0]["statistics"]
    return {"status":consensus,
            "confirmed_sats":stats["confirmed_sats"] if agrees else None,
            "confirmed_btc":stats["confirmed_btc"] if agrees else None,
            "unconfirmed_net_change_sats":stats["unconfirmed_net_change_sats"] if agrees else None,
            "explorers_agree":agrees,
            "sources_successful":len(valid),
            "individual_source_balances":[{"source":x["source"],
                "confirmed_sats":x["statistics"]["confirmed_sats"],
                "unconfirmed_net_change_sats":x["statistics"]["unconfirmed_net_change_sats"]}
                for x in valid],
            "verified_new_earned_sats":None,
            "note":"A balance snapshot can include deposits, spending, old balances and change; it cannot prove new income or payer origin."}


def self_test():
    valid={"chain_stats":{"funded_txo_sum":42_000,"spent_txo_sum":2_000,"tx_count":3},
           "mempool_stats":{"funded_txo_sum":1_000,"spent_txo_sum":0,"tx_count":1}}
    parsed=parse_address_summary(valid)
    assert parsed["confirmed_sats"]==40_000
    assert parsed["unconfirmed_net_change_sats"]==1_000
    assert parsed["confirmed_btc"]=="0.00040000"
    assert parsed["is_not_recent_earnings_or_revenue"]
    for invalid in (
        {},{"chain_stats":{},"mempool_stats":{}},
        {**valid,"chain_stats":{**valid["chain_stats"],"spent_txo_sum":50_000}},
        {**valid,"mempool_stats":{**valid["mempool_stats"],"tx_count":False}},
    ):
        try:parse_address_summary(invalid)
        except ValueError:pass
        else:raise AssertionError("Malformed evidence incorrectly accepted")
    both=[{"source":name,"status":"AVAILABLE","statistics":parsed}
          for name in ("mempool.space","blockstream.info")]
    ok=evaluate_balances(both)
    assert ok["status"]=="TWO_EXPLORER_CONSENSUS"
    assert ok["confirmed_sats"]==40_000 and ok["verified_new_earned_sats"] is None
    conflict=evaluate_balances([both[0],{**both[1],"statistics":{**parsed,"confirmed_sats":9999}}])
    assert conflict["status"]=="EXPLORER_DISAGREEMENT" and conflict["confirmed_sats"] is None
    partial=evaluate_balances([both[0],{"source":"blockstream.info","status":"UNAVAILABLE"}])
    assert partial["status"]=="SINGLE_SOURCE_NOT_CROSSCHECKED" and partial["confirmed_sats"] is None
    missing=evaluate_balances([{"source":"mempool.space","status":"UNAVAILABLE"}])
    assert missing["confirmed_sats"] is None
    print("BTC_INDEPENDENT_BALANCE_PROBE_SELF_TEST_PASS")


def run():
    outcome={"as_of_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
             "since_utc":CUTOFF.isoformat(),
             "receipts_are_not_automatically_income":True,"accounts":{}}
    for fleet,address in ACCOUNTS.items():
        per=[check(address,src) for src in SOURCES]
        balance_sources=[check_balance(address,src) for src in SOURCES]
        balance=evaluate_balances(balance_sources)
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
            "public_balance_consensus":balance,
            "public_balance_sources":balance_sources,
            "external_payment_or_donation_proven":False,
            "full_transaction_history_checked":False,
        }
    (OUT/"BTC_PUBLIC_RECEIPTS.json").write_text(json.dumps(outcome,indent=2)+"\n")
    lines=["# Read-only Bitcoin mainnet receipt probe","",
           "Time: "+outcome["as_of_utc"],""]
    for fleet,d in outcome["accounts"].items():
        lines+=["## "+fleet,d["address"],"Explorer responses: "+str(d["explorers_available"])+"/2",
                "Status: "+d["status"],""]
        bal=d["public_balance_consensus"]
        lines.append("Public balance check: "+bal["status"]+" (not new earned funds)")
        if bal["confirmed_sats"] is not None:
            lines.append("Cross-checked confirmed balance: "+str(bal["confirmed_btc"])+" BTC")
        else:
            lines.append("Confirmed balance: UNKNOWN — source missing or conflicting")
        for t in d["recent_outputs"]:
            lines.append("BTC "+str(t["btc"])+" | txid "+t["txid"]+" | vout "+str(t["vout"])+
                         " | independent sources "+", ".join(t["sources"])+" | payer unknown")
    lines+=["","Any confirmed on-chain transfer requires an independent payer or work-acceptance check before classifying as earnings.",
            "If explorers are unreachable, NO BALANCE CONCLUSION IS POSSIBLE."]
    (OUT/"BTC_PUBLIC_RECEIPTS.md").write_text("\n".join(lines)+"\n")
    print("MAINNET_RECEIPT_CHECK",json.dumps({
      fleet:{"status":d["status"],"explorers_available":d["explorers_available"],
             "recent_outputs":len(d["recent_outputs"]),
             "balance_status":d["public_balance_consensus"]["status"],
             "confirmed_balance_sats_or_unknown":d["public_balance_consensus"]["confirmed_sats"]}
      for fleet,d in outcome["accounts"].items()}))
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    assert len(ACCOUNTS)==2 and len(set(ACCOUNTS.values()))==2
    assert all(len(x)==42 and x.startswith("bc1q") for x in ACCOUNTS.values())
    if args.self_test:self_test()
    else:run()
