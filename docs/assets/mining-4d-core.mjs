// ENIGMA 4D mining decision model. READ-ONLY: never connects to pools or wallets.
// Arithmetic uses expected-value network difficulty. Actual payouts can be zero.
export const DIFFICULTY_REFERENCE = Object.freeze({date:"2026-11-21", difficulty:134820000000000, source:"https://www.coinwarz.com/bitcoin-difficulty"});
const MULTIPLIERS = Object.freeze({MH:1e6,GH:1e9,TH:1e12,PH:1e15});
export const HOST_POLICY = Object.freeze({
 "owner-hardware":{status:"POSSIBLE_WITH_CONSENT",purpose:"mining on owned hardware only"},
 "partner-hardware":{status:"POSSIBLE_WITH_CONSENT",purpose:"only with explicit operator and payout agreement"},
 "github-actions":{status:"BLOCKED",purpose:"GitHub Actions disallows cryptomining"},
 "render":{status:"BLOCKED",purpose:"Render Acceptable Use Policy disallows cryptomining"},
 "google-free-trial":{status:"BLOCKED",purpose:"Google Cloud free-trial terms disallow cryptomining"},
 "hf-static":{status:"COORDINATION_ONLY",purpose:"Static sites are not mining hardware"},
 "other-cloud":{status:"NOT_VERIFIED",purpose:"Requires the provider's explicit applicable permission"}
});
const sane=(x,label,allowZero=true)=>{if(typeof x!=="number"||!Number.isFinite(x)||x<0||(!allowZero&&x===0))throw new RangeError(label+" must be a finite positive number");return x;};
export function estimate4D({hashrate=10,unit="MH",difficulty=DIFFICULTY_REFERENCE.difficulty,blockRewardBtc=3.125,btcUsd=60000,watts=25,usdPerKwh=0.12,poolFeePct=0,payoutThresholdBtc=0,hardwareCostUsd=0,maintenanceUsdPerDay=0,host="owner-hardware",hardwareOwnerConsent=false,payoutPermission=false}={}){
  if(!(unit in MULTIPLIERS))throw new RangeError("invalid hash-rate unit");
  if(!(host in HOST_POLICY))throw new RangeError("unknown host policy");
  sane(hashrate,"hashrate",false);sane(difficulty,"difficulty",false);
  sane(blockRewardBtc,"block reward",false);sane(btcUsd,"BTC price",false);
  sane(watts,"power");sane(usdPerKwh,"electricity");
  sane(poolFeePct,"pool fee");sane(payoutThresholdBtc,"payout threshold");
  sane(hardwareCostUsd,"hardware cost");sane(maintenanceUsdPerDay,"maintenance");
  if(poolFeePct>100)throw new RangeError("pool fee exceeds 100%");
  const hashesPerSecond=hashrate*MULTIPLIERS[unit];
  if(!Number.isFinite(hashesPerSecond))throw new RangeError("hashrate overflows calculation");
  const expectedBlocksPerDay=hashesPerSecond*86400/(difficulty*4294967296);
  const expectedBtcPerDay=expectedBlocksPerDay*blockRewardBtc*(1-poolFeePct/100);
  const expectedUsdPerDay=expectedBtcPerDay*btcUsd;
  const powerCostUsdPerDay=watts/1000*24*usdPerKwh;
  const netBeforeEquipmentUsdPerDay=expectedUsdPerDay-powerCostUsdPerDay;
  const netAfterOperatingCostsUsdPerDay=netBeforeEquipmentUsdPerDay-maintenanceUsdPerDay;
  const annualSoloBlockProbability=-Math.expm1(-expectedBlocksPerDay*365);
  const simpleEquipmentPaybackDays=hardwareCostUsd>0&&netAfterOperatingCostsUsdPerDay>0?hardwareCostUsd/netAfterOperatingCostsUsdPerDay:null;
  if(![expectedBlocksPerDay,expectedBtcPerDay,expectedUsdPerDay,powerCostUsdPerDay,netBeforeEquipmentUsdPerDay,netAfterOperatingCostsUsdPerDay,annualSoloBlockProbability].every(Number.isFinite))throw new RangeError("inputs overflow safe calculation");
  const breakEvenElectricityUsdPerKwh=watts===0?null:expectedUsdPerDay/(watts/1000*24);
  const theoreticalThresholdDays=payoutThresholdBtc===0?null:expectedBtcPerDay>0?payoutThresholdBtc/expectedBtcPerDay:null;
  const p=HOST_POLICY[host];
  const permissionGate=(p.status==="POSSIBLE_WITH_CONSENT" && hardwareOwnerConsent===true && payoutPermission===true);
  const approval="BLOCKED"===p.status?"BLOCKED_PROVIDER_TERMS":p.status!=="POSSIBLE_WITH_CONSENT"?"NO_MINING_COMPUTE_APPROVAL":!permissionGate?"BLOCKED_MISSING_CONSENT":netAfterOperatingCostsUsdPerDay<=0?"UNECONOMIC_AT_INPUTS":"ECONOMICS_POSITIVE_NOT_A_PAYOUT";
  return {hashesPerSecond,expectedBlocksPerDay,expectedBtcPerDay,expectedSatsPerDay:expectedBtcPerDay*1e8,expectedUsdPerDay,powerCostUsdPerDay,netBeforeEquipmentUsdPerDay,netAfterOperatingCostsUsdPerDay,annualSoloBlockProbability,simpleEquipmentPaybackDays,hardwareCostUsd,maintenanceUsdPerDay,breakEvenElectricityUsdPerKwh,theoreticalThresholdDays,hostPolicy:p.status,decision:approval,estimatedNotReceived:true,liveMinerConnected:false,receivedBtcVerified:false,assumptions:"Expected BTC is statistical, not regular earnings; solo miners may go years without a block. This excludes transaction fees, equipment depreciation, downtime and taxes. Simple payback is not a discounted cashflow valuation. No mining starts."};
}
