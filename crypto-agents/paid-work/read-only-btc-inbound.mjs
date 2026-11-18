// Read-only public Bitcoin mainnet receiving-address evidence check.
// Does not request private keys, sign, spend, send, or claim income.
import {writeFileSync} from "node:fs";
import assert from "node:assert/strict";

const addresses=[
  {company:"B1",address:"bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z"},
  {company:"B2",address:"bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9"}
];
const providers=[
  {name:"mempool.space",base:"https://mempool.space/api/address/"},
  {name:"blockstream.info",base:"https://blockstream.info/api/address/"}
];
function validSats(n){return typeof n==="number"&&Number.isSafeInteger(n)&&n>=0;}
export function parseAddressStats(raw){
  if(!raw||typeof raw!=="object"||!raw.chain_stats||!raw.mempool_stats)
    throw Error("Missing address chain or mempool statistics");
  const c=raw.chain_stats,m=raw.mempool_stats;
  for(const v of [c.funded_txo_sum,c.spent_txo_sum,c.tx_count,m.funded_txo_sum,m.spent_txo_sum,m.tx_count])
    if(!validSats(v))throw Error("Invalid stats integer");
  if(c.spent_txo_sum>c.funded_txo_sum)throw Error("Unusual negative confirmed balance");
  return {
    confirmed_received_sats:c.funded_txo_sum,
    confirmed_spent_sats:c.spent_txo_sum,
    confirmed_balance_sats:c.funded_txo_sum-c.spent_txo_sum,
    confirmed_tx_count:c.tx_count,
    mempool_funded_sats:m.funded_txo_sum,
    mempool_spent_sats:m.spent_txo_sum,
    mempool_tx_count:m.tx_count
  };
}
function chainKey(stats){
  return [stats.confirmed_received_sats,stats.confirmed_spent_sats,stats.confirmed_balance_sats,stats.confirmed_tx_count].join(":");
}
if(process.argv.includes("--self-test")){
  const fixture={chain_stats:{funded_txo_sum:1200,spent_txo_sum:200,tx_count:3},
    mempool_stats:{funded_txo_sum:50,spent_txo_sum:0,tx_count:1}};
  const parsed=parseAddressStats(fixture);
  assert.equal(parsed.confirmed_balance_sats,1000);
  assert.equal(parsed.mempool_funded_sats,50);
  assert.throws(()=>parseAddressStats({}),/Missing/);
  assert.throws(()=>parseAddressStats({...fixture,chain_stats:{...fixture.chain_stats,spent_txo_sum:1300}}),/Unusual/);
  assert.throws(()=>parseAddressStats({...fixture,chain_stats:{...fixture.chain_stats,tx_count:"3"}}),/Invalid/);
  console.log("SELF_TEST_PASS public address statistics");
}else{
  async function query(provider,address){
    const url=provider.base+address;
    const response=await fetch(url,{headers:{"accept":"application/json"},signal:AbortSignal.timeout(14000)});
    if(!response.ok)throw Error("HTTP "+response.status);
    const stats=parseAddressStats(await response.json());
    return {provider:provider.name,explorer_url:url,...stats};
  }
  async function inspect(receiving){
    const checked=await Promise.allSettled(providers.map(p=>query(p,receiving.address)));
    const observations=[],errors=[];
    checked.forEach((x,i)=>x.status==="fulfilled"?
      observations.push(x.value):
      errors.push({provider:providers[i].name,reason:String(x.reason?.message||x.reason).slice(0,160)}));
    let status="unverified",confirmed=null;
    if(observations.length===1){status="single_explorer_only";confirmed=observations[0];}
    if(observations.length===2){
      status=chainKey(observations[0])===chainKey(observations[1])?
        "two_independent_explorers_agree":"EXPLORER_DISAGREEMENT";
      if(status==="two_independent_explorers_agree")confirmed=observations[0];
    }
    return {...receiving,status,confirmed,observations,errors,
      new_income_since_prior_snapshot_verified:false,
      address_control_verified:false,
      explanation:"Historical public address statistics only; no buyer identity, contract, wallet ownership or newly earned income is established."};
  }
  const result={
    schema:"b1-b2-mainnet-inbound-read-only/v1",
    checked_at_utc:new Date().toISOString(),
    network:"bitcoin-mainnet",
    no_secrets_or_wallet_transactions:true,
    wallets:await Promise.all(addresses.map(inspect))
  };
  writeFileSync("btc-mainnet-inbound-snapshot.json",JSON.stringify(result,null,2)+"\n");
  console.log("BTC_MAINNET_READ_ONLY_SNAPSHOT "+JSON.stringify(result));
  const summary=process.env.GITHUB_STEP_SUMMARY;
  if(summary){
    const fs=await import("node:fs");
    const lines=["## B1/B2 read-only Bitcoin mainnet inbound snapshot","","Public explorer address statistics only. This is **not** payment, buyer identity or new-income verification.",""];
    for(const w of result.wallets){
      lines.push("### "+w.company+" ("+w.address+")");
      lines.push("- Status: **"+w.status+"**");
      if(w.confirmed){
        lines.push("- Confirmed address balance: "+w.confirmed.confirmed_balance_sats+" sat");
        lines.push("- Total historical confirmed received: "+w.confirmed.confirmed_received_sats+" sat");
        lines.push("- Total historical confirmed spent: "+w.confirmed.confirmed_spent_sats+" sat");
        lines.push("- Confirmed transaction count: "+w.confirmed.confirmed_tx_count);
      }else lines.push("- Exact amount: **unverified**; no zero inferred");
      lines.push("- Explorer observations: "+w.observations.length+"; errors: "+w.errors.length);
      lines.push("");
    }
    lines.push("No new client payment claim, spending, signing, email access, or owner address control verification.");
    fs.appendFileSync(summary,lines.join("\n")+"\n");
  }
  if(result.wallets.every(w=>w.status==="unverified"))
    console.log("WARNING: Both explorer providers unavailable for both addresses; do NOT assert a zero balance.");
}
