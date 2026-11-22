import test from "node:test";
import assert from "node:assert/strict";
import {estimate4D,HOST_POLICY} from "../../docs/assets/mining-4d-core.mjs";

test("10MH/s CPU expected value remains tiny and unprofitable",()=>{
  const x=estimate4D({hashrate:10,unit:"MH",hardwareOwnerConsent:true,payoutPermission:true});
  assert.ok(x.expectedSatsPerDay>0.00045&&x.expectedSatsPerDay<0.0005);
  assert.ok(x.netBeforeEquipmentUsdPerDay<0);
  assert.equal(x.decision,"UNECONOMIC_AT_INPUTS");
  assert.equal(x.receivedBtcVerified,false);
});
test("An efficient, authorized ASIC can pass only theoretical economics",()=>{
  const x=estimate4D({hashrate:200,unit:"TH",watts:3500,usdPerKwh:0.05,hardwareOwnerConsent:true,payoutPermission:true});
  assert.ok(x.netBeforeEquipmentUsdPerDay>0);
  assert.equal(x.decision,"ECONOMICS_POSITIVE_NOT_A_PAYOUT");
  assert.equal(x.liveMinerConnected,false);
});
test("Known disallowed free compute is blocked even with consent",()=>{
  for(const host of ["github-actions","render","google-free-trial"]){
    assert.equal(HOST_POLICY[host].status,"BLOCKED");
    assert.equal(estimate4D({host,hardwareOwnerConsent:true,payoutPermission:true}).decision,"BLOCKED_PROVIDER_TERMS");
  }
});
test("Static hosting and unverified cloud never count as mining",()=>{
  for(const host of ["hf-static","other-cloud"]){
    assert.equal(estimate4D({host,hardwareOwnerConsent:true,payoutPermission:true}).decision,"NO_MINING_COMPUTE_APPROVAL");
  }
});
test("Equipment owner's consent AND agreed payout routing required",()=>{
  assert.equal(estimate4D({}).decision,"BLOCKED_MISSING_CONSENT");
  assert.equal(estimate4D({hardwareOwnerConsent:true}).decision,"BLOCKED_MISSING_CONSENT");
});
test("Bad or overflowing calculations rejected",()=>{
  for(const inputs of [{hashrate:1e308,unit:"PH"},{hashrate:0},{difficulty:0},{btcUsd:-1},{poolFeePct:101},{watts:Infinity}]){
    assert.throws(()=>estimate4D(inputs),RangeError);
  }
});
test("Theoretical threshold never becomes a receipt claim",()=>{
  const x=estimate4D({payoutThresholdBtc:0.0001});
  assert.ok(x.theoreticalThresholdDays>0);
  assert.equal(x.receivedBtcVerified,false);
  assert.equal(x.estimatedNotReceived,true);
});
