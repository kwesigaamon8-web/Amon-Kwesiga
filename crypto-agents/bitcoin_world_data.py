"""B1/B2 worldwide Bitcoin public-data collector and reproducible source audit.

Global BTC metrics are one worldwide chain; country rows are public context,
NOT country-level Bitcoin mining/adoption measures. Sources are hard-allowlisted;
unknown/unavailable is never zero. Does not crawl persons, run miners, access
emails, submit bounties, use secrets or move funds.
"""
from __future__ import annotations
import argparse, csv, datetime as dt, hashlib, io, json, math, os
from pathlib import Path
import sys, urllib.error, urllib.parse, urllib.request

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
DEST=HERE/"bitcoin-world-data"
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(HERE/"marketing"))
from country_market_research import COUNTRY_CODES
from btc_receiver_safety import require_all_owner_receivers
import btc_public_address_snapshot as wallets

ALLOWED={"mempool.space","blockstream.info","api.worldbank.org"}
URLS={
    "mempool_tip":"https://mempool.space/api/blocks/tip/height",
    "blockstream_tip":"https://blockstream.info/api/blocks/tip/height",
    "fees":"https://mempool.space/api/v1/fees/recommended",
    "mempool":"https://mempool.space/api/mempool",
    "bitcoin_prices":"https://mempool.space/api/v1/prices",
    "difficulty":"https://mempool.space/api/v1/difficulty-adjustment",
    "hashrate_1m":"https://mempool.space/api/v1/mining/hashrate/1m",
    "pools_1w":"https://mempool.space/api/v1/mining/pools/1w",
    "reward_stats_144":"https://mempool.space/api/v1/mining/reward-stats/144",
    "worldbank_countries":"https://api.worldbank.org/v2/country?format=json&per_page=400",
}
CATEGORIES={
    "mempool_tip":"consensus","blockstream_tip":"consensus",
    "fees":"transaction_fees","mempool":"unconfirmed_transactions",
    "bitcoin_prices":"market_reference_quotes","difficulty":"mining_difficulty",
    "hashrate_1m":"global_network_hashrate_estimate",
    "pools_1w":"mining_pool_block_share_not_country_share",
    "reward_stats_144":"recent_mining_reward_stats",
    "worldbank_countries":"country_context_not_bitcoin_adoption",
}
SOURCE_GUIDE={
    "bitcoin_protocol":"https://bitcoin.org/en/halving",
    "public_explorer_api":"https://mempool.space/docs/api/rest",
    "independent_explorer":"https://blockstream.info/",
    "mining_geography_methodology":"https://ccaf.io/cbnsi/cbeci/mining_map/methodology",
    "country_adoption_crypto_not_btc_only":"https://www.chainalysis.com/reports/the-2026-geography-of-cryptocurrency-report/",
    "worldbank_api":"https://datahelpdesk.worldbank.org/knowledgebase/articles/889392",
}
SCHEMA="B1B2_BITCOIN_WORLD_DATA_SOURCE_VERIFIED_V1"
MAX_SOURCE=4_500_000

class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if not is_allowed(newurl):raise ValueError("REDIRECT_TO_UNAPPROVED_HOST")
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def is_allowed(url):
    p=urllib.parse.urlsplit(url)
    return p.scheme=="https" and p.hostname in ALLOWED and not p.username and not p.password and p.port in (None,443)

def real_fetch(url):
    if not is_allowed(url):raise ValueError("SOURCE_NOT_ALLOWLISTED")
    req=urllib.request.Request(url,headers={"User-Agent":"B1B2-GlobalBitcoin-PublicOSINT/1.0",
                                            "Accept":"application/json,text/plain"})
    with urllib.request.build_opener(SafeRedirect()).open(req,timeout=18) as r:
        if not is_allowed(r.geturl()):raise ValueError("SOURCE_REDIRECTED")
        if r.status!=200:raise ValueError("HTTP_NOT_200")
        body=r.read(MAX_SOURCE+1)
        if len(body)>MAX_SOURCE:raise ValueError("SOURCE_TOO_LARGE")
        return body.decode("utf-8")

def parse_payload(raw):
    if isinstance(raw,(dict,list,int,float)):return raw
    if isinstance(raw,bytes):raw=raw.decode("utf-8")
    if not isinstance(raw,str):raise ValueError("WRONG_RESPONSE_TYPE")
    raw=raw.strip()
    if raw.isdecimal():return int(raw)
    return json.loads(raw)

def valid_natural(v):
    return type(v) is int and 0<=v<10_000_000_000_000

def numeric(v,minval=0,maxval=1e40):
    return isinstance(v,(float,int)) and not isinstance(v,bool) and math.isfinite(v) and minval<=v<=maxval

def limited_str(v,cap=120):
    return " ".join(str(v or "").split())[:cap]

def source_obs(name,raw):
    """Allowlist extraction, never execute remote code or infer missing fields."""
    obj=parse_payload(raw)
    if name in ("mempool_tip","blockstream_tip"):
        if not valid_natural(obj) or obj<800_000:
            raise ValueError("INVALID_BITCOIN_HEIGHT")
        return {"height":obj}
    if name=="fees":
        if not isinstance(obj,dict):raise ValueError("INVALID_FEES_SHAPE")
        out={}
        for k in ("fastestFee","halfHourFee","hourFee","economyFee","minimumFee"):
            if numeric(obj.get(k),0,100000):
                out[k]=obj[k]
        if not out:raise ValueError("FEES_WITHOUT_RECOMMENDATIONS")
        return {"sat_per_vbyte":out,"not_a_guaranteed_confirmation_time":True}
    if name=="mempool":
        if not isinstance(obj,dict):raise ValueError("INVALID_MEMPOOL_SHAPE")
        out={}
        for k in ("count","vsize","total_fee"):
            if numeric(obj.get(k),0,1e19):out[k]=obj[k]
        if not out:raise ValueError("EMPTY_MEMPOOL_DATA")
        return out
    if name=="bitcoin_prices":
        if not isinstance(obj,dict):raise ValueError("INVALID_PRICE_SHAPE")
        out={}
        for k in ("USD","EUR","GBP","CAD","AUD","CHF","JPY"):
            if numeric(obj.get(k),0.01,1e12):out[k]=obj[k]
        if not out:raise ValueError("EMPTY_PRICE_QUOTES")
        if valid_natural(obj.get("time")):out["provider_time_unix"]=obj["time"]
        out["price_not_executable_trade_quote"]=True
        return out
    if name=="difficulty":
        if not isinstance(obj,dict):raise ValueError("INVALID_DIFFICULTY_SHAPE")
        out={}
        for k in ("progressPercent","difficultyChange","remainingBlocks","remainingTime",
                  "previousRetarget","nextRetargetHeight","timeAvg"):
            if numeric(obj.get(k),-1e20,1e20):out[k]=obj[k]
        if not out:raise ValueError("NO_DIFFICULTY_FIELDS")
        return out
    if name=="hashrate_1m":
        if not isinstance(obj,dict):raise ValueError("INVALID_HASHRATE_SHAPE")
        observations=obj.get("hashrates")
        if not isinstance(observations,list) or not observations:raise ValueError("NO_HASHRATE_DATA")
        recent=[]
        for point in observations[-12:]:
            if not isinstance(point,dict):continue
            rate=point.get("avgHashrate")
            if not numeric(rate,1,1e30):continue
            recent.append({"timestamp":point.get("timestamp") if valid_natural(point.get("timestamp")) else None,
                           "avg_hashrate_hash_per_s":rate})
        if not recent:raise ValueError("NO_VALID_HASHRATE")
        return {"last_12_observations":recent,
                "latest_rate_exahash_per_s":round(recent[-1]["avg_hashrate_hash_per_s"]/1e18,2),
                "estimate_not_measured_individual_machines":True}
    if name=="pools_1w":
        if not isinstance(obj,dict) or not isinstance(obj.get("pools"),list):
            raise ValueError("INVALID_POOLS_SHAPE")
        pools=[]
        for pool in obj["pools"][:40]:
            if not isinstance(pool,dict):continue
            row={"name":limited_str(pool.get("name")),"slug":limited_str(pool.get("slug"),75)}
            if valid_natural(pool.get("blockCount")):row["blocks_found_in_provider_window"]=pool["blockCount"]
            if row["name"]:pools.append(row)
        if not pools:raise ValueError("NO_POOL_IDENTIFIERS")
        return {"trailing_window":"1w","pools":pools,
                "is_pool_not_country_distribution":True,
                "real_mining_facility_locations_unobserved":True}
    if name=="reward_stats_144":
        if not isinstance(obj,dict):raise ValueError("INVALID_REWARD_SHAPE")
        out={}
        for k,v in obj.items():
            if k in ("startBlock","endBlock","totalReward","totalFee","totalTx","totalTransactions","totalRewardBTC","totalFeeBTC") and numeric(v,0,1e25):
                out[k]=v
        if not out:raise ValueError("NO_REWARD_STATS_FIELDS")
        out["window"]="144 blocks";return out
    if name=="worldbank_countries":
        if not isinstance(obj,list) or len(obj)!=2 or not isinstance(obj[0],dict) or not isinstance(obj[1],list):
            raise ValueError("WORLD_BANK_BAD_SCHEMA")
        if obj[0].get("pages")!=1 or obj[0].get("total")!=len(obj[1]):
            raise ValueError("WORLD_BANK_PAGE_INCOMPLETE")
        mapped={}
        for d in obj[1]:
            if not isinstance(d,dict):continue
            code=d.get("iso2Code")
            region=d.get("region") or {}
            if code not in COUNTRY_CODES or not isinstance(region,dict) or region.get("value")=="Aggregates":continue
            mapped[code]={"display_name":limited_str(d.get("name")),
                          "worldbank_region":limited_str(region.get("value")),
                          "income_group":limited_str((d.get("incomeLevel") or {}).get("value"))}
        if not mapped:raise ValueError("WORLD_BANK_NO_VALID_COUNTRIES")
        return {"country_context":mapped,
                "bitcoin_mining_locations_inferred":False,
                "bitcoin_ownership_adoption_inferred":False}
    raise ValueError("UNRECOGNIZED_SOURCE")

def halving(height):
    if not valid_natural(height):return None
    epoch=height//210000
    reward=0 if epoch>=33 else 5_000_000_000 >> epoch
    nxt=(epoch+1)*210000
    return {"current_height":height,"halving_epoch":epoch,
            "block_subsidy_satoshis":reward,"block_subsidy_btc":reward/1e8,
            "next_halving_height":nxt,"blocks_until_next_halving":max(0,nxt-height),
            "consensus_subsidy_excludes_transaction_fees":True}

def fetch_all(fetch=real_fetch,include_wallets=True):
    now=dt.datetime.now(dt.timezone.utc).isoformat()
    result={"schema":SCHEMA,"collected_utc":now,
            "scope":"global BTC protocol and public network; country-level data separately sourced",
            "api_fetches":{},"global":{},"countries":[],
            "source_catalogue":SOURCE_GUIDE,
            "btc_specific_adoption_rankings_verified":0,
            "worldwide_all_mining_locations_verified":False,
            "private_individual_information_collected":False,
            "btc_receipts_newly_earned_verified":False}
    observations={}
    for name,url in URLS.items():
        detail={"url":url,"category":CATEGORIES[name],"checked_at_utc":dt.datetime.now(dt.timezone.utc).isoformat()}
        try:
            data=source_obs(name,fetch(url))
            detail["status"]="OK"
            observations[name]=data
        except (ValueError,KeyError,TypeError,UnicodeError,urllib.error.URLError,TimeoutError,OSError) as e:
            detail["status"]="UNAVAILABLE_OR_SCHEMA_FAILED"
            detail["error_type"]=type(e).__name__
        result["api_fetches"][name]=detail
    a=observations.get("mempool_tip",{}).get("height")
    b=observations.get("blockstream_tip",{}).get("height")
    if a is not None and b is not None and abs(a-b)<=3:
        result["global"]["chain_tip"]={"height":max(a,b),"status":"TWO_EXPLORERS_WITHIN_THREE_BLOCKS",
                                      "sampled_tips":{"mempool_space":a,"blockstream_info":b}}
        result["global"]["issuance_schedule"]=halving(max(a,b))
    else:
        result["global"]["chain_tip"]={"height":None,"status":"NO_TWO_SOURCE_NEAR_CONSENSUS",
                                      "sampled_tips":{"mempool_space":a,"blockstream_info":b}}
        result["global"]["issuance_schedule"]=None
    for name in ("fees","mempool","bitcoin_prices","difficulty","hashrate_1m","pools_1w","reward_stats_144"):
        result["global"][name]=observations.get(name)
    official=observations.get("worldbank_countries",{}).get("country_context",{})
    for code in COUNTRY_CODES:
        ctx=official.get(code)
        result["countries"].append({
            "iso3166_alpha2":code,"worldbank_public_country_context":ctx,
            "bitcoin_mining_share_pct":None,"bitcoin_mining_equipment_count":None,
            "bitcoin_nodes_in_country":None,"bitcoin_holders_count":None,
            "bitcoin_ownership_rate_pct":None,"bitcoin_regulation_current":None,
            "bitcoin_legal_tender_status":None,
            "bitcoin_country_specific_status":"UNVERIFIED_NOT_ZERO",
            "country_mining_share_cannot_be_inferred_from_pool_blocks":True})
    result["country_rows_with_official_context"]=sum(x["worldbank_public_country_context"] is not None for x in result["countries"])
    if include_wallets:
        require_all_owner_receivers()
        receipts={}
        for fleet,addr in wallets.ADDRESSES.items():
            try:
                check=wallets.inspect(addr)
                receipts[fleet]={"address":addr,"read_only":True,
                    "chain_result":check,"is_new_earned_payment_verified":False}
            except (ValueError,TypeError,OSError) as e:
                receipts[fleet]={"address":addr,"status":"UNAVAILABLE",
                                 "error_type":type(e).__name__,
                                 "is_new_earned_payment_verified":False}
        result["owner_receiving_observation"]=receipts
    else:
        result["owner_receiving_observation"]={"status":"NOT_CHECKED_IN_OFFLINE_TEST"}
    return result

def write_outputs(d):
    DEST.mkdir(parents=True,exist_ok=True)
    full=DEST/"latest_snapshot.json"
    full.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    with (DEST/"countries.csv").open("w",encoding="utf-8",newline="") as f:
        fields=["iso3166_alpha2","country_display_name","worldbank_region",
                "bitcoin_mining_share_pct","bitcoin_ownership_rate_pct",
                "bitcoin_nodes_in_country","bitcoin_regulation_current",
                "bitcoin_country_specific_status"]
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for item in d["countries"]:
            info=item["worldbank_public_country_context"] or {}
            w.writerow({"iso3166_alpha2":item["iso3166_alpha2"],
                        "country_display_name":info.get("display_name") or "",
                        "worldbank_region":info.get("worldbank_region") or "",
                        "bitcoin_country_specific_status":item["bitcoin_country_specific_status"]})
    g=d["global"];tip=g["chain_tip"]
    lines=["# Worldwide Bitcoin intelligence — verified public-source snapshot","",
           "Collected: "+d["collected_utc"],"",
           "## Network","",
           "- Block tip: "+(str(tip["height"]) if tip["height"] is not None else "UNKNOWN")+" ("+tip["status"]+")",
           "- Bitcoin block subsidy: "+(str(g["issuance_schedule"]["block_subsidy_btc"])+" BTC" if g["issuance_schedule"] else "UNKNOWN"),
           "- Global estimated hashrate: "+(str(g["hashrate_1m"]["latest_rate_exahash_per_s"])+" EH/s" if g["hashrate_1m"] else "UNKNOWN"),
           "- Reference BTC/USD: "+(str(g["bitcoin_prices"].get("USD")) if g["bitcoin_prices"] else "UNKNOWN"),
           "- Pending transactions: "+(str(g["mempool"].get("count")) if g["mempool"] else "UNKNOWN"),
           "- Fee recommendations: "+(json.dumps(g["fees"]["sat_per_vbyte"]) if g["fees"] else "UNKNOWN"),"",
           "## Mining and worldwide country coverage","",
           "- Pool list: "+(str(len(g["pools_1w"]["pools"]))+" pool entries (trailing week, not countries)" if g["pools_1w"] else "UNAVAILABLE"),
           "- ISO 3166-1 country/territory codes: "+str(len(d["countries"])),
           "- Country codes with separate World Bank context: "+str(d["country_rows_with_official_context"]),
           "- Bitcoin miners, holders, national legal status or mining share are NOT derived from population, internet adoption or pool identity.",
           "- Missing source data means UNKNOWN, not 0.",
           "", "## Source health",""]
    for name,info in d["api_fetches"].items():
        lines.append("- "+name+": "+info["status"]+" — "+info["url"])
    lines+=["","## Independent research catalog",""]
    lines +=["- "+k+": "+url for k,url in SOURCE_GUIDE.items()]
    lines+=["","## Owner payment verification",""]
    for fleet,o in d["owner_receiving_observation"].items():
        status=o.get("chain_result",{}).get("status") or o.get("status","UNKNOWN")
        val=o.get("chain_result",{}).get("observed_confirmed_unspent_sats")
        lines.append("- "+fleet+": "+status+"; confirmed unspent sats "+str(val if val is not None else "UNKNOWN")+"; earned payer origin not proven")
    lines+=["","**No emails, wallet signing, BTC transfers, mining, paid customer claims, private-node scans or unauthorized network access.**",
            "**This is a live-source partial global dataset, NOT literally all blockchain transactions or all private mining machines.**",""]
    (DEST/"WORLD_REPORT.md").write_text("\n".join(lines),encoding="utf-8")
    print("BTC_WORLD_DATA_SUMMARY "+json.dumps({
        "collected_utc":d["collected_utc"],
        "source_ok":sum(v["status"]=="OK" for v in d["api_fetches"].values()),
        "source_failed":sum(v["status"]!="OK" for v in d["api_fetches"].values()),
        "country_codes":len(d["countries"]),
        "official_context":d["country_rows_with_official_context"],
        "chain_tip":tip["height"],
        "btc_usd":(g["bitcoin_prices"] or {}).get("USD"),
        "hashrate_EHs":(g["hashrate_1m"] or {}).get("latest_rate_exahash_per_s"),
        "btc_earned_confirmed":False,
        "wallets":{k:{"status":v.get("chain_result",{}).get("status"),
                       "confirmed_sats":v.get("chain_result",{}).get("observed_confirmed_unspent_sats")}
                   for k,v in d["owner_receiving_observation"].items()}
    },sort_keys=True))

def self_test():
    assert len(COUNTRY_CODES)==249 and len(set(COUNTRY_CODES))==249
    assert not is_allowed("https://user:pass@mempool.space/api/")
    assert not is_allowed("http://mempool.space/api/")
    assert not is_allowed("https://example.com/api")
    for name in URLS:
        assert is_allowed(URLS[name])
    assert source_obs("mempool_tip","976999")["height"]==976999
    assert source_obs("fees",{"fastestFee":4,"hourFee":2,"economyFee":1})["sat_per_vbyte"]["hourFee"]==2
    assert source_obs("bitcoin_prices",{"USD":62000,"time":1780000000})["USD"]==62000
    assert source_obs("hashrate_1m",{"hashrates":[{"timestamp":100,"avgHashrate":1.1e21}]})["latest_rate_exahash_per_s"]==1100
    assert source_obs("pools_1w",{"pools":[{"name":"Independent Pool","slug":"independent","blockCount":4}]})["is_pool_not_country_distribution"]
    assert source_obs("worldbank_countries",[{"pages":1,"total":1},[{"iso2Code":"UG","name":"Uganda","region":{"value":"Sub-Saharan Africa"}}]])["country_context"]["UG"]["display_name"]=="Uganda"
    for obj in ({"pages":2,"total":1},):
        try:source_obs("worldbank_countries",[obj,[{"iso2Code":"UG"}]])
        except ValueError:pass
        else:raise AssertionError("World Bank incomplete page accepted")
    assert halving(840000)["block_subsidy_btc"]==3.125
    assert halving(1049999)["blocks_until_next_halving"]==1
    assert halving(1050000)["block_subsidy_btc"]==1.5625
    assert not fetch_all(lambda url: (_ for _ in ()).throw(OSError("offline")),False)["btc_receipts_newly_earned_verified"]
    print("B1B2_BITCOIN_WORLD_DATA_TESTS_PASS")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    self_test()
    if a.self_test:return
    d=fetch_all()
    write_outputs(d)

if __name__=="__main__":main()
