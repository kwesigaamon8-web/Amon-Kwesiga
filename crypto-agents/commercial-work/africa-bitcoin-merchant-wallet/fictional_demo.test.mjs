import test from 'node:test';
import assert from 'node:assert/strict';
import {fictionalPaymentScenario} from './fictional_demo.mjs';
import {RECEIVERS} from './wallet_core.mjs';
test('offline fictional demonstration has matching amount but explicitly no real Bitcoin received',()=>{
  const got=fictionalPaymentScenario({address:RECEIVERS.B1,amountSats:12000,label:'Fictional'});
  assert.equal(got.inspection.status,'CONFIRMED_OUTPUT_AMOUNT_MATCH');
  assert.equal(got.inspection.matched_sats,12000);
  assert.equal(got.inspection.confirmations,3);
  assert.equal(got.actual_transaction_id,null);
  assert.equal(got.public_blockchain_checked,false);
  assert.equal(got.bitcoin_received_verified,false);
  assert.equal(got.merchant_sale_verified,false);
});
test('fictional demo never skips address or amount validation',()=>{
  assert.throws(()=>fictionalPaymentScenario({address:'bc1_invalid',amountSats:12000}));
  assert.throws(()=>fictionalPaymentScenario({address:RECEIVERS.B2,amountSats:-1}));
  assert.throws(()=>fictionalPaymentScenario({address:RECEIVERS.B2,amountSats:'3.14'}));
});
