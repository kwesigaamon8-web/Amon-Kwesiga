const assert=require('node:assert/strict');
const t=require('node:test');
const P=require('./payment-proof-core.js');
const HASH='a'.repeat(64);
t('Owner receive-only addresses exact',()=>{
 assert.equal(P.BTC.B1,'bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z');
 assert.equal(P.BTC.B2,'bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9');
});
t('BTC decimal arithmetic is integer satoshis, not floats',()=>{
 assert.equal(P.amountToSats('0.00000001'),1n);
 assert.equal(P.amountToSats('0.10000009'),10000009n);
 assert.equal(P.amountToSats('1'),100000000n);
 assert.equal(P.satsToBTC(10000009n),'0.10000009');
 for(const invalid of ['-1','1.000000001','1e-2','0.000000000','1,234','NaN',''])assert.throws(()=>P.amountToSats(invalid));
});
t('BIP21 address amount and service label safe',()=>{
 assert.equal(P.makeUri('B1','0.0001','software delivered'),'bitcoin:'+P.BTC.B1+'?amount=0.0001&label=software%20delivered');
 assert.throws(()=>P.makeUri('B1','0','free'));
 assert.throws(()=>P.makeUri('B3','1','bad'));
});
t('Confirmed matching outputs use EXACT address and sum only matching outputs',()=>{
 const tx={txid:HASH,status:{confirmed:true,block_height:100},vout:[
  {scriptpubkey_address:P.BTC.B1,value:9000},
  {scriptpubkey_address:P.BTC.B2,value:500},
  {scriptpubkey_address:P.BTC.B1,value:1001},
 ]};
 const d=P.assessTransaction(tx,'B1',102,10000n);
 assert.equal(d.matching_outputs,2);
 assert.equal(d.amount_to_receiver_sats,'10001');
 assert.equal(d.confirmations,3);
 assert.equal(d.on_chain_receiver_and_minimum_matched,true);
 assert.equal(d.status,'ON_CHAIN_MATCH_CONFIRMED');
 const b=P.assessTransaction(tx,'B2',102,1000n);
 assert.equal(b.status,'CONFIRMED_BELOW_REQUESTED_AMOUNT');
 assert.equal(b.on_chain_receiver_and_minimum_matched,false);
});
t('Unconfirmed, no matching output or invalid value never counts',()=>{
 const base={txid:HASH,status:{confirmed:false},vout:[{scriptpubkey_address:P.BTC.B1,value:10000}]};
 const d=P.assessTransaction(base,'B1',200,10000n);
 assert.equal(d.confirmations,0);
 assert.equal(d.status,'UNCONFIRMED_DO_NOT_TREAT_AS_SETTLED');
 assert.equal(d.on_chain_receiver_and_minimum_matched,false);
 const miss=P.assessTransaction({...base,status:{confirmed:true,block_height:190}},'B2',200,0n);
 assert.equal(miss.status,'NO_PAYMENT_TO_SELECTED_ADDRESS');
 assert.equal(miss.on_chain_receiver_and_minimum_matched,false);
 assert.throws(()=>P.assessTransaction({txid:HASH,vout:[{scriptpubkey_address:P.BTC.B1,value:'10000'}]},'B1',190,0n));
});
t('Read-only lookups only send a public txid',async()=>{
 const requested=[];
 const mock=async(url)=>{requested.push(url);return {ok:true,json:async()=>url.endsWith('/height')?302:{txid:HASH,vout:[{scriptpubkey_address:P.BTC.B1,value:10000}],status:{confirmed:true,block_height:300}}}};
 const got=await P.fetchAndAssess(HASH,'B1',10000n,mock);
 assert.deepEqual(requested,['https://mempool.space/api/tx/'+HASH,'https://mempool.space/api/blocks/tip/height']);
 assert.equal(got.confirmations,3);
 assert.equal(got.on_chain_receiver_and_minimum_matched,true);
});
t('API errors and mismatched hash fail closed',async()=>{
 const notfound=async()=>({ok:false,status:404});
 await assert.rejects(()=>P.fetchAndAssess(HASH,'B1',1n,notfound),/HTTP 404/);
 const mismatch=async()=>({ok:true,json:async()=>({txid:'b'.repeat(64)})});
 await assert.rejects(()=>P.fetchAndAssess(HASH,'B1',1n,mismatch),/different transaction ID/);
 await assert.rejects(()=>P.fetchAndAssess('x','B1',1n,()=>{}),/64 hexadecimal/);
});