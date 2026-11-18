// Africa Bitcoin Merchant Watch Wallet — public mainnet receiving only.
// No key generation, signatures, custody, outgoing transactions or emails.
// BIP173/BIP350 checksum validation for native SegWit mainnet addresses.
export const RECEIVERS = Object.freeze({
  B1: "bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z",
  B2: "bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9",
});
const ALPHABET="qpzry9x8gf2tvdw0s3jn54khce6mua7l";
const GENERATOR=[0x3b6a57b2,0x26508e6d,0x1ea119fa,0x3d4233dd,0x2a1462b3];
function polymod(values){
  let chk=1;
  for(const v of values){
    const top=chk>>>25;
    chk=((chk&0x1ffffff)<<5)^v;
    for(let i=0;i<5;i++)if((top>>>i)&1)chk^=GENERATOR[i];
  }
  return chk;
}
function hrpExpand(hrp){
  const codes=[...hrp].map(c=>c.charCodeAt(0));
  return codes.map(c=>c>>>5).concat([0],codes.map(c=>c&31));
}
function convertBits(data,from,to,pad){
  let acc=0,bits=0;
  const out=[],max=(1<<to)-1;
  for(const value of data){
    if(value<0 || value>>from!==0)throw new Error("Invalid witness data");
    acc=(acc<<from)|value;
    bits+=from;
    while(bits>=to){
      bits-=to;
      out.push((acc>>>bits)&max);
    }
  }
  if(pad){if(bits)out.push((acc<<(to-bits))&max);}
  else if(bits>=from||((acc<<(to-bits))&max)!==0)throw new Error("Invalid witness padding");
  return out;
}
export function validateMainnetAddress(value){
  if(typeof value!=="string")return false;
  const a=value.trim();
  if(a.length<14||a.length>90||a.toLowerCase()!==a&&a.toUpperCase()!==a)return false;
  const lower=a.toLowerCase(),sep=lower.lastIndexOf("1");
  if(sep!==2||lower.slice(0,sep)!=="bc"||lower.length-sep-1<7)return false;
  const encoded=lower.slice(sep+1);
  if(![...encoded].every(c=>ALPHABET.includes(c)))return false;
  const data=[...encoded].map(c=>ALPHABET.indexOf(c));
  const version=data[0];
  if(version>16)return false;
  const constant=polymod(hrpExpand("bc").concat(data));
  if(version===0?constant!==1:constant!==0x2bc830a3)return false;
  let witness;
  try{witness=convertBits(data.slice(1,-6),5,8,false);}
  catch{return false;}
  if(witness.length<2||witness.length>40)return false;
  if(version===0&&witness.length!==20&&witness.length!==32)return false;
  return true;
}
export function normalizeSats(value){
  const s=String(value).trim();
  if(!/^[1-9][0-9]*$/.test(s))throw new Error("Enter a whole-number positive satoshi amount");
  const n=Number(s);
  if(!Number.isSafeInteger(n)||n>21_000_000*100_000_000)throw new Error("Amount exceeds Bitcoin supply limit");
  return n;
}
export function makeInvoice({address,amountSats,label=""}){
  if(!validateMainnetAddress(address))throw new Error("Enter a valid Bitcoin MAINNET SegWit address (bc1)");
  const sats=normalizeSats(amountSats);
  const btc=(sats/100_000_000).toFixed(8);
  const cleanLabel=String(label).trim().slice(0,100);
  const uri="bitcoin:"+address.trim().toLowerCase()+"?amount="+btc+
    (cleanLabel?"&label="+encodeURIComponent(cleanLabel):"");
  return {schema:"btc-watch-invoice/v1",network:"bitcoin-mainnet",
    address:address.trim().toLowerCase(),sats,btc,bitcoin_uri:uri,
    reference:cleanLabel,created_utc:new Date().toISOString(),
    status:"PAYMENT_REQUEST_CREATED_NOT_PAID",read_only:true};
}
export function validateTxid(txid){
  return typeof txid==="string"&&/^[0-9a-fA-F]{64}$/.test(txid.trim());
}
export function inspectTx(tx,invoice,tipHeight=null){
  if(!invoice||!validateMainnetAddress(invoice.address)||!Number.isSafeInteger(invoice.sats)||invoice.sats<=0)
    throw new Error("Invalid original invoice");
  if(!tx||!Array.isArray(tx.vout)||!tx.status||typeof tx.status.confirmed!=="boolean")
    throw new Error("Invalid blockchain explorer response");
  const matching=[];
  for(let i=0;i<tx.vout.length;i++){
    const item=tx.vout[i];
    if(item&&item.scriptpubkey_address===invoice.address){
      if(!Number.isSafeInteger(item.value)||item.value<0)throw new Error("Malformed output value");
      matching.push({vout:i,sats:item.value});
    }
  }
  const sats=matching.reduce((n,v)=>n+v.sats,0);
  if(!Number.isSafeInteger(sats))throw new Error("Output total too large");
  const confirmed=tx.status.confirmed===true;
  let confirmations=null;
  if(confirmed&&Number.isSafeInteger(tx.status.block_height)&&Number.isSafeInteger(tipHeight)&&
     tipHeight>=tx.status.block_height){
    confirmations=tipHeight-tx.status.block_height+1;
  }
  const amountMatched=sats>=invoice.sats&&matching.length>0;
  const status=!matching.length?"NO_OUTPUT_TO_INVOICE_ADDRESS":
    sats<invoice.sats?"INSUFFICIENT_OUTPUTS":
    !confirmed?"UNCONFIRMED_OUTPUT_MATCH":
    "CONFIRMED_OUTPUT_AMOUNT_MATCH";
  return {status,network:"bitcoin-mainnet",matching_outputs:matching,
    matched_sats:sats,expected_sats:invoice.sats,
    amount_match:amountMatched,confirmed,confirmations,
    invoice_paid_by_named_buyer_proven:false,customer_contract_proven:false,
    owner_wallet_control_proven:false,
    warning:"A transaction output is NOT proof of who paid or why, or that the owner still holds the coins."};
}
