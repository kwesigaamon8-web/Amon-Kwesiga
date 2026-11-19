import assert from 'node:assert/strict';
import { createHmac } from 'node:crypto';
import { test } from 'node:test';
import { createIntent, createLedger, processSignedWebhook, NATIVE_USDC } from './checkout.mjs';

const receiver = '0x1111111111111111111111111111111111111111';
const hash = ch => '0x' + ch.repeat(64);
const secret = 'unit-test-only-secret-has-at-least-32-characters';
const intent = createIntent({ orderId: 'INV_2026_01', chainId: 8453, receiver,
  usdc: '10.000001', createdAt: 1795000000 });
const event = (i = intent, overrides = {}) => ({
  orderId: i.orderId, chainId: i.chainId, receiver: i.receiver, token: i.token,
  amountMicro: i.amountMicro, txHash: hash('a'), logIndex: 0, removed: false, ...overrides
});
const sign = e => {
  const rawBody = JSON.stringify(e);
  return { rawBody, signature: 'sha256=' + createHmac('sha256', secret).update(rawBody).digest('hex') };
};
const proof = (e, overrides = {}) => ({
  ok: true, removed: false, chainId: e.chainId, token: e.token, receiver: e.receiver,
  amountMicro: e.amountMicro, txHash: e.txHash, logIndex: e.logIndex, confirmations: 20,
  ...overrides
});
const execute = (i, e, ledger, overrides = {}, cb = undefined) => processSignedWebhook({
  ...sign(e), secret, intent: i, ledger, verifyOnChain: cb || (async () => proof(e, overrides))
});
test('uses only Circle native USDC with six exact decimals', () => {
  assert.equal(intent.amountMicro, '10000001');
  assert.equal(intent.token, NATIVE_USDC[8453]);
  assert.equal(createIntent({ orderId: 'P', chainId: 137, receiver, usdc: '0.000001',
    createdAt: 1795000000 }).token, NATIVE_USDC[137]);
  assert.throws(() => createIntent({ orderId: 'a', chainId: 1, receiver, usdc: '1', createdAt: 1 }), /UNSUPPORTED_CHAIN/);
  for (const usdc of ['1.0000001', '1e5', '-2', '0', '0.000000', '2,000', '01', '1.']) {
    assert.throws(() => createIntent({ orderId: 'a', chainId: 8453, receiver, usdc, createdAt: 1 }));
  }
});
test('accepts signed, chain-verified payment once; replay is idempotent', async () => {
  const ledger = createLedger(), e = event();
  assert.equal((await execute(intent, e, ledger)).status, 'CONFIRMED_BY_RPC_ADAPTER');
  assert.equal((await execute(intent, e, ledger)).status, 'ALREADY_ACCEPTED');
  assert.equal(ledger.paidOrders.size, 1);
});
test('rejects forged HMAC without even querying a chain adapter', async () => {
  let calls = 0;
  await assert.rejects(processSignedWebhook({
    ...sign(event()), signature: 'sha256=' + 'f'.repeat(64), secret, intent,
    ledger: createLedger(), verifyOnChain: async () => { calls++; return proof(event()); }
  }), /SIGNATURE_MISMATCH/);
  assert.equal(calls, 0);
});
test('rejects wrong order, network, token, payee, quantity, replay marker', async () => {
  for (const o of [
    {orderId:'other'}, {chainId:137}, {token:NATIVE_USDC[137]},
    {receiver:'0x2222222222222222222222222222222222222222'},
    {amountMicro:'9999999'}, {removed:true}
  ]) {
    const e = event(intent,o), ledger=createLedger();
    await assert.rejects(execute(intent,e,ledger));
    assert.equal(ledger.paidOrders.size,0);
  }
});
test('rejects confirmations, reorg and untrusted/wrong receipt', async () => {
  const e=event();
  for (const o of [
    {confirmations:0}, {confirmations:11}, {ok:false}, {removed:true},
    {chainId:137}, {token:NATIVE_USDC[137]},
    {receiver:'0x2222222222222222222222222222222222222222'},
    {amountMicro:'10000000'}, {txHash:hash('b')}, {logIndex:2}
  ]) {
    const ledger=createLedger();
    await assert.rejects(execute(intent,e,ledger,o), /CHAIN_PROOF/);
    assert.equal(ledger.seenTxLogs.size,0);
  }
});
test('prevents same transfer log paying two different invoices',async()=>{
  const ledger=createLedger(), e=event();
  await execute(intent,e,ledger);
  const second=createIntent({orderId:'OTHER',chainId:8453,receiver,usdc:'10.000001',createdAt:1795000000});
  await assert.rejects(execute(second,event(second),ledger),/TX_LOG_ALREADY_USED_FOR_OTHER_ORDER/);
});
test('prevents different transfer logs paying one invoice twice',async()=>{
  const ledger=createLedger();
  await execute(intent,event(),ledger);
  await assert.rejects(execute(intent,event(intent,{txHash:hash('b')}),ledger),/ORDER_ALREADY_PAID_BY_DIFFERENT_TX/);
});
test('on replay, chain verification is repeated to detect reorgs', async () => {
  const ledger=createLedger(), e=event();
  await execute(intent,e,ledger);
  await assert.rejects(execute(intent,e,ledger,{removed:true}),/CHAIN_PROOF/);
});
test('refuses to settle without independent proof adapter', async () => {
  const e=event();
  await assert.rejects(processSignedWebhook({ ...sign(e), secret, intent, ledger:createLedger() }),
    /DURABLE_LEDGER_AND_RPC_ADAPTER_REQUIRED/);
});
