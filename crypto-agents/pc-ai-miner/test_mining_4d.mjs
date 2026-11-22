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

test("Solo pool variance is not daily payout and declines for small miners",()=>{
  const cpu=estimate4D({hashrate:10,unit:"MH",hardwareOwnerConsent:true,payoutPermission:true});
  const asic=estimate4D({hashrate:200,unit:"TH",watts:3500,usdPerKwh:0.05,hardwareOwnerConsent:true,payoutPermission:true});
  assert.ok(cpu.annualSoloBlockProbability>0);
  assert.ok(cpu.annualSoloBlockProbability<asic.annualSoloBlockProbability);
  assert.ok(asic.annualSoloBlockProbability>0.0108&&asic.annualSoloBlockProbability<0.0109);
  assert.equal(asic.receivedBtcVerified,false);
});
test("Realistic capex payback is much longer than daily positive margin suggests",()=>{
  const x=estimate4D({hashrate:200,unit:"TH",watts:3500,usdPerKwh:0.05,
    hardwareCostUsd:3500,maintenanceUsdPerDay:0,hardwareOwnerConsent:true,payoutPermission:true});
  assert.ok(x.simpleEquipmentPaybackDays>2500);
  assert.ok(x.simpleEquipmentPaybackDays<2520);
  assert.ok(x.netAfterOperatingCostsUsdPerDay>0);
  assert.ok(x.simpleEquipmentPaybackDays/365>6.8);
  const maintenance=estimate4D({hashrate:200,unit:"TH",watts:3500,usdPerKwh:0.05,
    hardwareCostUsd:3500,maintenanceUsdPerDay:2,hardwareOwnerConsent:true,payoutPermission:true});
  assert.equal(maintenance.decision,"UNECONOMIC_AT_INPUTS");
  assert.equal(maintenance.simpleEquipmentPaybackDays,null);
});
test("Additional cost inputs must be finite and nonnegative",()=>{
  for(const options of [{hardwareCostUsd:-1},{maintenanceUsdPerDay:-1},{hardwareCostUsd:Infinity},{maintenanceUsdPerDay:NaN}]){
    assert.throws(()=>estimate4D(options),RangeError);
  }
});
