// Clearly synthetic, OFFLINE demo. Never use as proof of received Bitcoin.
// For a wallet configured by the visitor; creates no blockchain transaction.
import {makeInvoice,inspectTx,validateMainnetAddress} from './wallet_core.mjs';

export function fictionalPaymentScenario({address, amountSats, label='Fictional merchant test'}){
  if(!validateMainnetAddress(address))throw new Error('Use a valid Bitcoin mainnet address');
  const invoice=makeInvoice({address,amountSats,label});
  const syntheticTransaction={
    status:{confirmed:true,block_height:100},
    vout:[{scriptpubkey_address:invoice.address,value:invoice.sats}]
  };
  const observed=inspectTx(syntheticTransaction,invoice,102);
  return {
    demo_type:'FICTIONAL_OFFLINE_TRANSACTION',
    actual_transaction_id:null,
    public_blockchain_checked:false,
    bitcoin_received_verified:false,
    merchant_sale_verified:false,
    notes:'Synthetic test object used solely to demonstrate how evidence matching works. Nothing was broadcast, paid or confirmed on the real Bitcoin network.',
    invoice,
    inspection:observed
  };
}
