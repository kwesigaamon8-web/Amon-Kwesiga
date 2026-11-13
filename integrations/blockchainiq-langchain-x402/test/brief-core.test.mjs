import assert from 'node:assert/strict';
import test from 'node:test';
import { ENDPOINT, BASE_MAINNET, BASE_USDC, readBlockchainIQBrief, selectAllowedPayment } from '../src/brief-core.mjs';
const good = (amount = '10000') => ({ network: BASE_MAINNET, asset: BASE_USDC, scheme: 'exact', amount });
test('selects an affordable Base USDC quote', () => {
  assert.deepEqual(selectAllowedPayment(2, [good('10000')]), good('10000'));
});
test('chooses least expensive eligible quote', () => {
  assert.equal(selectAllowedPayment(2, [good('10000'), good('3000')]).amount, '3000');
});
test('rejects expensive, unsupported chain, and unsupported token', () => {
  for (const opt of [good('10001'), good('0'), {...good(), network:'eip155:1'}, {...good(), asset:'0xwrong'}, {...good(), scheme:'upto'}, {...good(), amount:'not a number'}]) {
    assert.throws(() => selectAllowedPayment(2,[opt]), /No allowed/);
  }
});
test('requests only fixed GET resource; captures settlement header', async () => {
  let count=0;
  const fetchMock=async (url,opts) => {
    count++;
    assert.equal(url,ENDPOINT);
    assert.deepEqual(opts,{ method:'GET',redirect:'error' });
    return new Response(JSON.stringify({prices:{BTC:80000}}),{status:200,headers:{'PAYMENT-RESPONSE':'fixture-header','Content-Type':'application/json'}});
  };
  const result=await readBlockchainIQBrief(fetchMock);
  assert.equal(count,1);
  assert.equal(result.data.prices.BTC,80000);
  assert.equal(result.settlementHeader,'fixture-header');
});
test('refuses unsuccessful requests', async () => {
  await assert.rejects(readBlockchainIQBrief(async()=>new Response('',{status:402})),/HTTP 402/);
});
