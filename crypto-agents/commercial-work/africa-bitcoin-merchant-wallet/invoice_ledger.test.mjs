import test from "node:test";
import assert from "node:assert/strict";
import {RECEIVERS} from "./wallet_core.mjs";
import {newLedger,addInvoice,recordTxEvidence,invoiceEvidenceSummary,exportLedgerJSON} from "./invoice_ledger.mjs";
const b1=RECEIVERS.B1,b2=RECEIVERS.B2;
const TX1="1".repeat(64),TX2="2".repeat(64),TX3="3".repeat(64);
function tx(rows,confirmed=true){
  return {status:{confirmed,...(confirmed?{block_height:100}: {})},
    vout:rows.map(([a,s])=>({scriptpubkey_address:a,value:s}))};
}
const setup=()=>addInvoice(newLedger(),{id:"INV1",address:b1,amountSats:3000,label:"Merchant example"});
test("A real invoice is created but not marked paid",()=>{
  const ledger=setup();
  assert.equal(ledger.invoices[0].status,"PAYMENT_REQUEST_CREATED_NOT_PAID");
  assert.equal(invoiceEvidenceSummary(ledger,"INV1").status,"NO_SUFFICIENT_ONCHAIN_EVIDENCE");
  assert.equal(ledger.evidence.length,0);
});
test("Reject invalid IDs, invalid invoice amounts and duplicate IDs",()=>{
  assert.throws(()=>addInvoice(newLedger(),{id:"",address:b1,amountSats:3000}));
  assert.throws(()=>addInvoice(newLedger(),{id:"bad space",address:b1,amountSats:3000}));
  assert.throws(()=>addInvoice(newLedger(),{id:"INV1",address:b1,amountSats:0}));
  assert.throws(()=>addInvoice(setup(),{id:"INV1",address:b2,amountSats:2000}));
});
test("Partial confirmed outputs combine across independent transactions",()=>{
  let l=setup();
  l=recordTxEvidence(l,{invoiceId:"INV1",txid:TX1,transaction:tx([[b1,1000]])});
  assert.equal(invoiceEvidenceSummary(l,"INV1").status,"PARTIAL_CONFIRMED_OUTPUTS");
  l=recordTxEvidence(l,{invoiceId:"INV1",txid:TX2,transaction:tx([[b2,1],[b1,2000]])});
  const summary=invoiceEvidenceSummary(l,"INV1");
  assert.equal(summary.confirmed_sats,3000);
  assert.equal(summary.status,"CONFIRMED_ONCHAIN_OUTPUTS_MATCH_OR_EXCEED_AMOUNT");
  assert.equal(summary.buyer_payment_or_invoice_settlement_proven,false);
});
test("Repeat checking the same TXID cannot double-count payment",()=>{
  let l=setup();
  const t=tx([[b1,1500]]);
  l=recordTxEvidence(l,{invoiceId:"INV1",txid:TX1,transaction:t});
  l=recordTxEvidence(l,{invoiceId:"INV1",txid:TX1,transaction:t,tipHeight:102});
  assert.equal(l.evidence.length,1);
  assert.equal(invoiceEvidenceSummary(l,"INV1").confirmed_sats,1500);
  assert.equal(l.evidence[0].confirmations,3);
});
test("One output cannot be sold as proof for two invoices",()=>{
  let l=setup();
  l=addInvoice(l,{id:"INV2",address:b1,amountSats:1000});
  l=recordTxEvidence(l,{invoiceId:"INV1",txid:TX1,transaction:tx([[b1,3000]])});
  assert.throws(()=>recordTxEvidence(l,{invoiceId:"INV2",txid:TX1,transaction:tx([[b1,3000]])}),
    /already allocated/);
});
test("A shared receiving address signals customer attribution uncertainty",()=>{
  let l=setup();
  l=addInvoice(l,{id:"INV2",address:b1,amountSats:5000});
  assert.equal(invoiceEvidenceSummary(l,"INV1").shared_address_other_invoice_count,1);
  assert.equal(invoiceEvidenceSummary(l,"INV1").exact_customer_attribution_automatic,false);
});
test("Unconfirmed and confirmed outputs are accounted for separately",()=>{
  let l=setup();
  l=recordTxEvidence(l,{invoiceId:"INV1",txid:TX1,transaction:tx([[b1,1000]],true)});
  l=recordTxEvidence(l,{invoiceId:"INV1",txid:TX2,transaction:tx([[b1,2000]],false)});
  const p=invoiceEvidenceSummary(l,"INV1");
  assert.equal(p.confirmed_sats,1000);
  assert.equal(p.unconfirmed_sats,2000);
  assert.equal(p.status,"UNCONFIRMED_OR_PARTLY_CONFIRMED_OUTPUTS");
});
test("Explorer replay can downgrade evidence if transaction is reorged",()=>{
  let l=setup();
  l=recordTxEvidence(l,{invoiceId:"INV1",txid:TX1,transaction:tx([[b1,3000]],true)});
  assert.equal(invoiceEvidenceSummary(l,"INV1").confirmed_sats,3000);
  l=recordTxEvidence(l,{invoiceId:"INV1",txid:TX1,transaction:tx([[b1,3000]],false)});
  assert.equal(invoiceEvidenceSummary(l,"INV1").confirmed_sats,0);
  assert.equal(invoiceEvidenceSummary(l,"INV1").unconfirmed_sats,3000);
});
test("Reject unrelated transaction outputs and malformed hashes",()=>{
  const l=setup();
  assert.throws(()=>recordTxEvidence(l,{invoiceId:"INV1",txid:TX3,transaction:tx([[b2,3000]])}),/No output/);
  assert.throws(()=>recordTxEvidence(l,{invoiceId:"INV1",txid:"nope",transaction:tx([[b1,3000]])}),/Invalid Bitcoin/);
});
test("Ledger is JSON-exportable, inputs are not mutated",()=>{
  let l=setup();
  const prev=JSON.stringify(l);
  const next=recordTxEvidence(l,{invoiceId:"INV1",txid:TX1,transaction:tx([[b1,3000]])});
  assert.equal(JSON.stringify(l),prev);
  assert.equal(JSON.parse(exportLedgerJSON(next)).evidence.length,1);
  assert.equal(JSON.parse(exportLedgerJSON(next)).evidence[0].linked_sale_verified,false);
});
