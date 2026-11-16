"""Read-only cross-chain owner public wallet scan. Balances != new earnings."""
import json, urllib.request, urllib.error, datetime
from decimal import Decimal
from pathlib import Path

OUT=Path("multichain-payment-reports")
OUT.mkdir(exist_ok=True)
text=Path("crypto-agents/PUBLIC_RECEIVING_ADDRESSES.md").read_text()
part=text.split("## Self-custody addresses")[1].split("## Exchange deposit identifiers")[0]
routes={}
for line in part.splitlines():
    p=[v.strip().strip(chr(96)) for v in line.split("|")]
    if len(p)==5 and p[1] in ("BTC-01","BTC-02","SOL-01","SOL-02","EVM-01","EVM-02","TRX-01","TRX-02","XLM-01","XLM-02"):
        routes[p[1]]=p[3]
assert len(routes)==10, "Only 10 publicly approved self-custody candidates"
USDC_SOL="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDC_BASE="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
USDC_ETH="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"

def read(url,method=None,params=None):
    try:
        body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode() if method else None
        req=urllib.request.Request(url,data=body,headers={"Accept":"application/json","User-Agent":"OwnerMultichainReadOnlyAudit/1.0",**({"Content-Type":"application/json"} if body else {})})
        with urllib.request.urlopen(req,timeout=8) as r:return {"ok":True,"value":json.loads(r.read(750000)),"http":r.status}
    except urllib.error.HTTPError as exc:
        return {"ok":False,"http":exc.code,"error":"HTTPError:"+str(exc)[:100]}
    except Exception as exc:
        return {"ok":False,"error":type(exc).__name__+":"+str(exc)[:100]}

def check(ident,network,url,callback):
    row={"route":ident,"network":network,"address":routes[ident],"native_balance":None,"trusted_usdc":None,"other_tokens_unverified":None,"status":"UNKNOWN_API_NOT_VERIFIED","sources":[],"earned_payment_verified":False}
    def get(url,method=None,params=None):
        o=read(url,method,params)
        row["sources"].append({"url":url,"method":method,"http":o.get("http"),"status":"OK" if o["ok"] else "UNAVAILABLE","error":o.get("error")})
        return o["value"] if o["ok"] else None
    try:callback(row,get)
    except Exception as e:row["error"]=type(e).__name__+":"+str(e)[:100]
    return row

def btc(x,get):
    p=get("https://mempool.space/api/address/"+x["address"])
    if isinstance(p,dict) and isinstance(p.get("chain_stats"),dict):
        a=p["chain_stats"];f=a.get("funded_txo_sum");s=a.get("spent_txo_sum")
        if isinstance(f,int) and isinstance(s,int):
            x["native_balance"]=str((f-s)/100000000)
            x["status"]="CURRENT_BALANCE_OBSERVED_NOT_EARNINGS"
        x["reported_tx_count"]=a.get("tx_count")

def sol(x,get):
    ep="https://api.mainnet-beta.solana.com"
    p=get(ep,"getBalance",[x["address"],{"commitment":"confirmed"}])
    if isinstance(p,dict) and isinstance(p.get("result"),dict):
        x["native_balance"]=str(p["result"]["value"]/1000000000)
        x["status"]="CURRENT_BALANCE_OBSERVED_NOT_EARNINGS"
    p=get(ep,"getTokenAccountsByOwner",[x["address"],{"mint":USDC_SOL},{"encoding":"jsonParsed","commitment":"confirmed"}])
    if isinstance(p,dict) and isinstance(p.get("result"),dict):
        vals=p["result"].get("value",[])
        amounts=[]
        for v in vals:
            info=((v.get("account") or {}).get("data") or {}).get("parsed",{}).get("info",{})
            if info.get("mint")==USDC_SOL:
                amounts.append(info.get("tokenAmount",{}).get("uiAmountString","0"))
        x["trusted_usdc"]=amounts
        if x["status"].startswith("UNKNOWN"):x["status"]="USDC_TOKEN_READ_OK_NATIVE_UNKNOWN"
    p=get(ep,"getSignaturesForAddress",[x["address"],{"limit":2}])
    if isinstance(p,dict) and isinstance(p.get("result"),list) and p["result"]:
        x["latest_activity_signature"]=p["result"][0].get("signature")
        x["activity_is_not_income"]=True

def evm(x,get):
    """Check actual native ETH and canonical USDC via chain-checked read-only RPC.

    Base Blockscout API blocked this specific GitHub runner (HTTP 403).
    JSON-RPC direct calls provide a separate path; source errors remain UNKNOWN.
    """
    base=x["network"]=="Base"
    mint=USDC_BASE if base else USDC_ETH
    expected=8453 if base else 1
    hosts=(("https://mainnet.base.org","https://base.publicnode.com")
           if base else ("https://ethereum-rpc.publicnode.com","https://ethereum.publicnode.com"))
    x["canonical_usdc_contract"]=mint
    x["canonical_usdc_decimals"]=6
    x["public_rpc_chain_expected"]=expected
    x["rpc_chain_verified"]=False
    selector="0x70a08231" # ERC20 balanceOf(address), READ ONLY, not a transaction.
    calldata=selector+x["address"][2:].lower().rjust(64,"0")
    for host in hosts:
        check_chain=get(host,"eth_chainId",[])
        if not isinstance(check_chain,dict) or check_chain.get("error") or not isinstance(check_chain.get("result"),str):
            continue
        try:got=int(check_chain["result"],16)
        except (TypeError,ValueError):continue
        if got!=expected:
            x.setdefault("wrong_chain_endpoint",[]).append({"url":host,"reported_chain":got})
            continue
        x["rpc_chain_verified"]=True
        if x["native_balance"] is None:
            raw=get(host,"eth_getBalance",[x["address"],"latest"])
            if isinstance(raw,dict) and not raw.get("error") and isinstance(raw.get("result"),str):
                try:x["native_balance"]=str(Decimal(int(raw["result"],16))/Decimal(10**18))
                except (TypeError,ValueError,ArithmeticError):pass
        if x["trusted_usdc"] is None:
            raw=get(host,"eth_call",[{"to":mint,"data":calldata},"latest"])
            if isinstance(raw,dict) and not raw.get("error") and isinstance(raw.get("result"),str):
                try:
                    units=int(raw["result"],16)
                    x["trusted_usdc"]=[str(Decimal(units)/Decimal(10**6))]
                except (TypeError,ValueError,ArithmeticError):pass
        if x["native_balance"] is not None and x["trusted_usdc"] is not None:
            x["status"]="NATIVE_AND_CANONICAL_USDC_BALANCES_OBSERVED_NOT_EARNINGS"
            break

    # Blockscout is a read-only fallback, not an official declaration of income.
    if x["native_balance"] is None or x["trusted_usdc"] is None:
        explorer="https://base.blockscout.com" if base else "https://eth.blockscout.com"
        if x["native_balance"] is None:
            p=get(explorer+"/api/v2/addresses/"+x["address"])
            if isinstance(p,dict) and p.get("coin_balance") is not None:
                try:
                    x["native_balance"]=str(Decimal(int(p["coin_balance"]))/Decimal(10**18))
                except (ValueError,TypeError,ArithmeticError):pass
        if x["trusted_usdc"] is None:
            p=get(explorer+"/api/v2/addresses/"+x["address"]+"/token-balances")
            if isinstance(p,list):
                amounts=[]
                x["other_tokens_unverified"]=0
                for item in p:
                    t=item.get("token") or {}
                    if str(t.get("address_hash","")).lower()==mint:
                        try:amounts.append(str(Decimal(int(item["value"]))/Decimal(10**6)))
                        except (ValueError,TypeError,ArithmeticError):pass
                    else:x["other_tokens_unverified"]+=1
                x["trusted_usdc"]=amounts

    if x["native_balance"] is not None and x["trusted_usdc"] is not None:
        x["status"]="NATIVE_AND_CANONICAL_USDC_BALANCES_OBSERVED_NOT_EARNINGS"
    elif x["native_balance"] is not None or x["trusted_usdc"] is not None:
        x["status"]="PARTIAL_BALANCE_OBSERVED_OTHER_ASSETS_UNKNOWN_NOT_EARNINGS"
    else:x["status"]="UNKNOWN_EVM_BALANCE_BOTH_SOURCES_FAILED"


def tron(x,get):
    p=get("https://api.trongrid.io/v1/accounts/"+x["address"])
    if isinstance(p,dict) and p.get("success") is True:
        arr=p.get("data") or []
        if arr:
            x["native_balance"]=str(arr[0].get("balance",0)/1000000)
            x["status"]="CURRENT_BALANCE_OBSERVED_NOT_EARNINGS"
            x["other_tokens_unverified"]=len(arr[0].get("trc20",[]) or [])
        else:x["status"]="ACCOUNT_ABSENT_IN_RESPONSE_NOT_HISTORICAL_ZERO"

def stellar(x,get):
    p=get("https://horizon.stellar.org/accounts/"+x["address"])
    if isinstance(p,dict) and isinstance(p.get("balances"),list):
        for z in p["balances"]:
            if z.get("asset_type")=="native":
                x["native_balance"]=z.get("balance")
                x["status"]="CURRENT_BALANCE_OBSERVED_NOT_EARNINGS"
            else:x["other_tokens_unverified"]=(x["other_tokens_unverified"] or 0)+1
    elif x["sources"][-1].get("http")==404:
        x["status"]="ACCOUNT_NOT_FOUND_AT_THIS_SNAPSHOT"

results=[]
for code in ("BTC-01","BTC-02"):results.append(check(code,"Bitcoin",None,btc))
for code in ("SOL-01","SOL-02"):results.append(check(code,"Solana",None,sol))
for code in ("EVM-01","EVM-02"):
    for chain in ("Base","Ethereum"):results.append(check(code,chain,None,evm))
for code in ("TRX-01","TRX-02"):results.append(check(code,"TRON",None,tron))
for code in ("XLM-01","XLM-02"):results.append(check(code,"Stellar",None,stellar))

report={"utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"only_public_self_custody":True,"exchange_accounts_needs_authenticated_balance":True,"payment_proven":False,"wallet_ownership_verified":False,"results":results}
(OUT/"balances.json").write_text(json.dumps(report,indent=2)+"\n")
lines=["# Read-only multichain wallet audit",report["utc"],"Balances and transactions do NOT establish new externally earned money.","","| Route | Chain | Native balance | Known genuine USDC | Status |","|---|---|---:|---|---|"]
for x in results:
    lines.append("| "+x["route"]+" | "+x["network"]+" | "+str(x["native_balance"] if x["native_balance"] is not None else "UNKNOWN")+" | "+str(x["trusted_usdc"] if x["trusted_usdc"] is not None else "UNKNOWN")+" | "+x["status"]+" |")
lines.extend(["","**Exchange deposit candidates are excluded:** their exchange account credits cannot be inferred from public address activity.","No public wallet key or transfer action is used. Unknown tokens are not counted as genuine USDC."])
(OUT/"balances.md").write_text("\n".join(lines)+"\n")
print("B_PUBLIC_MULTICHAIN_AUDIT",json.dumps({"utc":report["utc"],"results":[{"route":x["route"],"chain":x["network"],"native_balance":x["native_balance"],"genuine_USDC":x["trusted_usdc"],"status":x["status"]} for x in results],"proven_new_earnings":False}))
