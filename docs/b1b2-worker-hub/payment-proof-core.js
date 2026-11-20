/* B1/B2 Bitcoin payment proof core.
 * Public, read-only. No private keys, transaction broadcast, wallet spending or mining.
 * Uses integer satoshis. A txid alone does not prove payment; check exact outputs + chain status.
 * API: https://mempool.space/docs/api/rest
 */
(function(root,factory) {
  const api=factory();
  if(typeof module==='object' && module.exports)module.exports=api;
  else root.B1B2Proof=api;
})(typeof globalThis!=='undefined'?globalThis:this,function() {
'use strict';
const BTC={
  B1:'bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z',
  B2:'bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9'
};
const API_ROOT='https://mempool.space/api';
function txidValid(s) {return typeof s==='string' && /^[0-9a-fA-F]{64}$/.test(s.trim());}
function amountToSats(value) {
  const v=String(value||'').trim();
  if(!/^(?:0|[1-9][0-9]*)(?:\.[0-9]{1,8})?$/.test(v))throw Error('Enter a nonnegative BTC amount with up to 8 decimals.');
  const [a,b='']=v.split('.');
  const sats=BigInt(a)*100000000n+BigInt((b+'00000000').slice(0,8));
  if(sats>2100000000000000n)throw Error('BTC amount exceeds maximum possible supply.');
  return sats;
}
function satsToBTC(sats) {
  let n=typeof sats==='bigint'?sats:BigInt(sats);
  if(n<0n)throw Error('Satoshis cannot be negative.');
  const p=(n/100000000n).toString(),r=(n%100000000n).toString().padStart(8,'0');
  return p+'.'+r;
}
function makeUri(fleet,btcAmount,label) {
  if(!Object.hasOwn(BTC,fleet))throw Error('Unknown receiving fleet.');
  const amount=amountToSats(btcAmount);
  if(amount===0n)throw Error('Specify an amount greater than zero for the payment request.');
  let uri='bitcoin:'+BTC[fleet]+'?amount='+satsToBTC(amount).replace(/0+$/,'').replace(/\.$/,'');
  if(label)uri+='&label='+encodeURIComponent(String(label).slice(0,100));
  return uri;
}
function assessTransaction(transaction,fleet,tipHeight,expectedSats) {
  if(!Object.hasOwn(BTC,fleet))throw Error('Choose B1 or B2.');
  if(!transaction||!txidValid(transaction.txid)||!Array.isArray(transaction.vout))throw Error('Invalid transaction data.');
  const expected=typeof expectedSats==='bigint'?expectedSats:BigInt(expectedSats||0);
  if(expected<0n)throw Error('Expected satoshis cannot be negative.');
  let matched=0n,outputCount=0;
  for(const output of transaction.vout) {
    if(!output||output.scriptpubkey_address!==BTC[fleet])continue;
    const v=output.value;
    if(!Number.isSafeInteger(v)||v<0)throw Error('Invalid satoshi amount returned by provider.');
    matched+=BigInt(v);outputCount++;
  }
  const st=transaction.status||{};
  const chainConfirmed=st.confirmed===true && Number.isSafeInteger(st.block_height)
      && Number.isSafeInteger(tipHeight) && tipHeight>=st.block_height && st.block_height>0;
  const confirmations=chainConfirmed?tipHeight-st.block_height+1:0;
  let status='NO_PAYMENT_TO_SELECTED_ADDRESS';
  if(matched>0n){
    if(!chainConfirmed)status='UNCONFIRMED_DO_NOT_TREAT_AS_SETTLED';
    else if(matched<expected)status='CONFIRMED_BELOW_REQUESTED_AMOUNT';
    else status='ON_CHAIN_MATCH_CONFIRMED';
  }
  const verified=matched>0n && confirmations>=1 && matched>=expected;
  return {
    txid:transaction.txid,network:'bitcoin-mainnet',fleet,
    address:BTC[fleet],matching_outputs:outputCount,
    amount_to_receiver_sats:matched.toString(),
    amount_to_receiver_btc:satsToBTC(matched),
    expected_sats:expected.toString(),
    expected_btc:satsToBTC(expected),
    chain_height:chainConfirmed?tipHeight:null,
    confirmations,confirmed:chainConfirmed,
    on_chain_receiver_and_minimum_matched:verified,status,
    warning:'Independent block explorer data; verify chain and receiving-wallet ownership. A confirmed output does not prove a contract was fulfilled or funds are still unspent.'
  };
}
async function fetchAndAssess(txid,fleet,expectedSats,fetcher=fetch) {
  if(!txidValid(txid))throw Error('Transaction ID must be 64 hexadecimal characters.');
  if(!Object.hasOwn(BTC,fleet))throw Error('Invalid owner receiver.');
  const hash=txid.toLowerCase();
  const fetchJson=async url=>{
    const response=await fetcher(url,{headers:{Accept:'application/json'},cache:'no-store'});
    if(!response.ok)throw Error('Bitcoin explorer returned HTTP '+response.status+'; confirmation unavailable, do not claim payment.');
    return response.json();
  };
  // The API only receives a public transaction ID, never a wallet secret.
  const tx=await fetchJson(API_ROOT+'/tx/'+hash);
  if(tx.txid.toLowerCase()!==hash)throw Error('Explorer returned a different transaction ID.');
  const height=await fetchJson(API_ROOT+'/blocks/tip/height');
  if(!Number.isSafeInteger(height))throw Error('Invalid blockchain tip returned by explorer.');
  return assessTransaction(tx,fleet,height,expectedSats);
}
return {BTC,API_ROOT,txidValid,amountToSats,satsToBTC,makeUri,assessTransaction,fetchAndAssess};
});