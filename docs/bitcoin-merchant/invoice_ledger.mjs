// Read-only Bitcoin merchant invoice/transaction allocation ledger.
// Does not sign transactions, access wallets, identify customers, or prove income.
import {makeInvoice,inspectTx,validateTxid,validateMainnetAddress} from "./wallet_core.mjs";
function copy(data){return JSON.parse(JSON.stringify(data));}
export function newLedger(){
  return {schema:"btc-merchant-ledger/v1",invoices:[],evidence:[]};
}
export function addInvoice(ledger,{id,address,amountSats,label=""}){
  checkLedger(ledger);
  const clean=String(id||"").trim();
  if(!/^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/.test(clean))
    throw new Error("Invoice ID must be 1-64 letters, numbers, underscores or hyphens");
  if(ledger.invoices.some(x=>x.id===clean))throw new Error("Invoice ID already exists");
  const invoice=makeInvoice({address,amountSats,label});
  const next=copy(ledger);
  next.invoices.push({...invoice,id:clean});
  return next;
}
function checkLedger(ledger){
  if(!ledger||ledger.schema!=="btc-merchant-ledger/v1"||
      !Array.isArray(ledger.invoices)||!Array.isArray(ledger.evidence))
    throw new Error("Invalid ledger");
}
export function recordTxEvidence(ledger,{invoiceId,txid,transaction,tipHeight=null}){
  checkLedger(ledger);
  const id=String(invoiceId||"").trim();
  const invoice=ledger.invoices.find(x=>x.id===id);
  if(!invoice||!validateMainnetAddress(invoice.address))throw new Error("Unknown invoice or receiving address");
  if(!validateTxid(txid))throw new Error("Invalid Bitcoin transaction ID");
  const hash=txid.toLowerCase();
  const proof=inspectTx(transaction,invoice,tipHeight);
  if(proof.matching_outputs.length===0)throw new Error("No output matches this invoice's receiving address");
  const uniqueKeys=proof.matching_outputs.map(x=>hash+":"+x.vout);
  for(const existing of ledger.evidence){
    if(existing.invoice_id===id&&existing.txid===hash)continue; // recheck, not additional payment
    if(existing.output_keys.some(key=>uniqueKeys.includes(key)))
      throw new Error("The same blockchain output is already allocated to another invoice");
  }
  const next=copy(ledger);
  next.evidence=next.evidence.filter(x=>!(x.invoice_id===id&&x.txid===hash));
  next.evidence.push({
    invoice_id:id,txid:hash,output_keys:uniqueKeys,
    matched_sats:proof.matched_sats,
    outputs:proof.matching_outputs,
    confirmed:proof.confirmed,
    confirmations:proof.confirmations,
    explorer_check_status:proof.status,
    checked_utc:new Date().toISOString(),
    payer_identity_verified:false,
    linked_sale_verified:false
  });
  return next;
}
export function invoiceEvidenceSummary(ledger,invoiceId){
  checkLedger(ledger);
  const invoice=ledger.invoices.find(x=>x.id===invoiceId);
  if(!invoice)throw new Error("Unknown invoice");
  const evidence=ledger.evidence.filter(x=>x.invoice_id===invoiceId);
  const confirmed_sats=evidence.filter(x=>x.confirmed).reduce((s,x)=>s+x.matched_sats,0);
  const unconfirmed_sats=evidence.filter(x=>!x.confirmed).reduce((s,x)=>s+x.matched_sats,0);
  if(!Number.isSafeInteger(confirmed_sats)||!Number.isSafeInteger(unconfirmed_sats))
    throw new Error("Output total overflow");
  const otherInvoices=ledger.invoices.filter(x=>x.id!==invoiceId&&x.address===invoice.address);
  return {
    invoice_id:invoiceId,network:"bitcoin-mainnet",expected_sats:invoice.sats,
    confirmed_sats,unconfirmed_sats,
    status:confirmed_sats>=invoice.sats?"CONFIRMED_ONCHAIN_OUTPUTS_MATCH_OR_EXCEED_AMOUNT":
      confirmed_sats+unconfirmed_sats>=invoice.sats?"UNCONFIRMED_OR_PARTLY_CONFIRMED_OUTPUTS":
      confirmed_sats>0?"PARTIAL_CONFIRMED_OUTPUTS":"NO_SUFFICIENT_ONCHAIN_EVIDENCE",
    shared_address_other_invoice_count:otherInvoices.length,
    buyer_payment_or_invoice_settlement_proven:false,
    exact_customer_attribution_automatic:false,
    reason:"Read-only public outputs and manually selected invoice; no payer identity, ownership, or commercial acceptance verified"
  };
}
export function exportLedgerJSON(ledger){
  checkLedger(ledger);
  return JSON.stringify(ledger,null,2)+"\n";
}
