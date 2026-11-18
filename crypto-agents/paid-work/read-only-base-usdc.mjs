// B1 owner-supplied Base candidate address; READ ONLY native Circle USDC balanceOf.
// No seed, wallet connection, transaction, signing, email or spending.
import assert from "node:assert/strict";
import {writeFileSync,appendFileSync} from "node:fs";
const wallet="0x734989a439F146885C12907cd9Dd191b03d5B07e";
const usdc="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"; // Circle official Base native USDC
const endpoints=[
  {name:"Base official",url:"https://mainnet.base.org"},
  {name:"PublicNode",url:"https://base-rpc.publicnode.com"}
];
export function decodeBalanceOf(hex){
  if(typeof hex!=="string"||!/^0x[0-9a-fA-F]+$/.test(hex))throw Error("Invalid RPC result");
  return BigInt(hex);
}
export function fmtUnits(n,decimals){
  if(typeof n!=="bigint"||n<0n)throw Error("Invalid token units");
  const scale=10n**BigInt(decimals);
  return String(n/scale)+"."+String(n%scale).padStart(decimals,"0");
}
async function rpc(endpoint,method,params,seq){
  const res=await fetch(endpoint.url,{
    method:"POST",headers:{"content-type":"application/json"},
    body:JSON.stringify({jsonrpc:"2.0",id:seq,method,params}),
    signal:AbortSignal.timeout(17000)
  });
  if(!res.ok)throw Error(method+" HTTP "+res.status);
  const data=await res.json();
  if(data.error)throw Error(method+" RPC error "+String(data.error.code));
  if(data.id!==seq||typeof data.result!=="string")throw Error(method+" malformed reply");
  return data.result;
}
async function inspect(end){
  const chain=await rpc(end,"eth_chainId",[],1);
  if(BigInt(chain)!==8453n)throw Error("Wrong chain ID (expected 8453)");
  const call="0x70a08231"+wallet.slice(2).toLowerCase().padStart(64,"0");
  const [balance,eth,block]=await Promise.all([
    rpc(end,"eth_call",[{to:usdc,data:call},"latest"],2),
    rpc(end,"eth_getBalance",[wallet,"latest"],3),
    rpc(end,"eth_blockNumber",[],4)
  ]);
  const raw=decodeBalanceOf(balance),native=decodeBalanceOf(eth);
  return {provider:end.name,rpc:end.url,chain_id:8453,
    usdc_native_token_contract:usdc,usdc_raw_units:raw.toString(),
    usdc_balance:fmtUnits(raw,6),
    base_eth_wei:native.toString(),base_eth_balance:fmtUnits(native,18),
    provider_latest_block:parseInt(block,16)};
}
if(process.argv.includes("--self-test")){
  assert.equal(fmtUnits(1234567n,6),"1.234567");
  assert.equal(fmtUnits(0n,6),"0.000000");
  assert.equal(decodeBalanceOf("0x0"),0n);
  assert.throws(()=>decodeBalanceOf("error"));
  assert.throws(()=>fmtUnits(-1n,6));
  console.log("SELF_TEST_PASS Base USDC exact integer balance formatting");
}else{
  const results=await Promise.allSettled(endpoints.map(inspect));
  const observations=[],errors=[];
  results.forEach((x,i)=>x.status==="fulfilled"?observations.push(x.value):
    errors.push({provider:endpoints[i].name,reason:String(x.reason?.message||x.reason).slice(0,130)}));
  let status="unverified",balance=null;
  if(observations.length===1){status="single_rpc_observation";balance=observations[0];}
  if(observations.length===2){
    const agree=observations[0].usdc_raw_units===observations[1].usdc_raw_units;
    status=agree?"two_rpc_usdc_balances_agree":"RPC_USDC_BALANCE_DISAGREEMENT";
    if(agree)balance=observations[0];
  }
  const snapshot={
    schema:"b1-base-native-usdc-read-only/v1",checked_at_utc:new Date().toISOString(),
    candidate_receiving_address:wallet,network:"Base mainnet",chain_id:8453,
    token:"Circle native USDC",token_contract:usdc,
    contract_documentation:"https://developers.circle.com/stablecoins/usdc-contract-addresses",
    status,balance,observations,errors,
    newly_earned_or_received_since_previous_snapshot_verified:false,
    owner_wallet_control_verified:false,
    guidance:"Balance, if observed, is not proof of who owns the address, who paid, new revenue, or spending authorization."
  };
  writeFileSync("base-usdc-b1-public-snapshot.json",JSON.stringify(snapshot,null,2)+"\n");
  console.log("BASE_USDC_B1_READ_ONLY_SNAPSHOT "+JSON.stringify(snapshot));
  if(process.env.GITHUB_STEP_SUMMARY){
    const lines=["## B1 Base native Circle-USDC read-only balance","",
      "- Checked: "+snapshot.checked_at_utc,
      "- Address: "+wallet,
      "- Native Circle USDC contract: "+usdc,
      "- Status: **"+status+"**"];
    if(balance)lines.push("- USDC balance: **"+balance.usdc_balance+"**","- Base ETH balance (gas asset): "+balance.base_eth_balance);
    else lines.push("- Balance: **unverified**, not inferred as zero");
    lines.push("- Sources with successful result: "+observations.length,"- This does not prove new income, a paid customer, or address ownership.");
    appendFileSync(process.env.GITHUB_STEP_SUMMARY,lines.join("\n")+"\n");
  }
}
