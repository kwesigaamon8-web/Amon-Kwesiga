import test from "node:test";
import assert from "node:assert/strict";
import {RECEIVERS,validateMainnetAddress,makeInvoice,validateTxid,inspectTx,normalizeSats} from "./wallet_core.mjs";
const B1=RECEIVERS.B1, B2=RECEIVERS.B2;
function tx(outputs,status={confirmed:true,block_height:980000}){
  return {status,vout:outputs.map(([a,n])=>({scriptpubkey_address:a,value:n}))};
}
test("Owner-supplied BTC mainnet destinations pass Bech32 checksum",()=>{
  assert.equal(validateMainnetAddress(B1),true);
  assert.equal(validateMainnetAddress(B2),true);
  assert.notEqual(B1,B2);
});
test("Reject changed checksum, wrong network, mixed case",()=>{
  assert.equal(validateMainnetAddress(B1.slice(0,-1)+"q"),false);
  assert.equal(validateMainnetAddress("tb"+B1.slice(2)),false);
  assert.equal(validateMainnetAddress("BC"+B1.slice(2)),false);
  assert.equal(validateMainnetAddress(B1.slice(0,5).toUpperCase()+B1.slice(5)),false);
});
test("BIP21 invoice includes satoshi-accurate amount and encoded label",()=>{
  const inv=makeInvoice({address:B1,amountSats:"55000",label:"Food stall #7"});
  assert.equal(inv.btc,"0.00055000");
  assert.match(inv.bitcoin_uri,/^bitcoin:bc1/);
  assert.match(inv.bitcoin_uri,/amount=0.00055000/);
  assert.match(inv.bitcoin_uri,/label=Food%20stall%20%237/);
  assert.equal(inv.status,"PAYMENT_REQUEST_CREATED_NOT_PAID");
});
test("Reject invalid price and invalid addresses",()=>{
  for(const s of ["0","-1","1.5","1e3","  ","999999999999999999999"])assert.throws(()=>normalizeSats(s));
  assert.throws(()=>makeInvoice({address:"bc1fake",amountSats:"1"}));
});
test("Transaction ID must be 64 hexadecimal characters",()=>{
  assert.equal(validateTxid("a".repeat(64)),true);
  assert.equal(validateTxid("z".repeat(64)),false);
  assert.equal(validateTxid("a".repeat(63)),false);
});
test("Confirmed exact output is recognized but payer and ownership remain unknown",()=>{
  const inv=makeInvoice({address:B1,amountSats:1500});
  const x=inspectTx(tx([[B2,220],[B1,1500]]),inv,980002);
  assert.equal(x.status,"CONFIRMED_OUTPUT_AMOUNT_MATCH");
  assert.equal(x.confirmations,3);
  assert.equal(x.matched_sats,1500);
  assert.equal(x.invoice_paid_by_named_buyer_proven,false);
  assert.equal(x.owner_wallet_control_proven,false);
});
test("Multiple matching outputs in SAME transaction add up",()=>{
  const inv=makeInvoice({address:B1,amountSats:"3000"});
  const x=inspectTx(tx([[B1,1000],[B2,500],[B1,2000]]),inv,980000);
  assert.equal(x.matching_outputs.length,2);
  assert.deepEqual(x.matching_outputs.map(o=>o.vout),[0,2]);
  assert.equal(x.matched_sats,3000);
  assert.equal(x.status,"CONFIRMED_OUTPUT_AMOUNT_MATCH");
});
test("Reject unrelated transaction and underpayment",()=>{
  const inv=makeInvoice({address:B1,amountSats:2000});
  assert.equal(inspectTx(tx([[B2,2000]]),inv).status,"NO_OUTPUT_TO_INVOICE_ADDRESS");
  assert.equal(inspectTx(tx([[B1,1999]]),inv).status,"INSUFFICIENT_OUTPUTS");
});
test("Unconfirmed output is not confirmed money",()=>{
  const inv=makeInvoice({address:B2,amountSats:2000});
  const x=inspectTx(tx([[B2,2000]],{confirmed:false}),inv);
  assert.equal(x.status,"UNCONFIRMED_OUTPUT_MATCH");
  assert.equal(x.confirmations,null);
});
test("Malformed output and response fail closed",()=>{
  const inv=makeInvoice({address:B1,amountSats:2000});
  assert.throws(()=>inspectTx({},inv));
  assert.throws(()=>inspectTx(tx([[B1,"2000"]]),inv));
});
