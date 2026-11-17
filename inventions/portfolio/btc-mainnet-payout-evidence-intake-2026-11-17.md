# BTC mainnet payment evidence intake — original no-spend microservice prototype (2026-11-17)

**Status:** Uncommissioned public demonstration. Not a contract, buyer acceptance, settlement, or proof that any wallet received funds.

## Buyer problem and differentiation
Freelance marketplaces, small agencies and bounty sponsors need a repeatable way to distinguish a blockchain transfer from a payment *owed for accepted work*. Generic block explorers prove chain outputs but not the contractual entitlement. This microservice combines a read-only UTXO observation with separate buyer acceptance and invoice evidence; it never signs or moves funds.

## Proposed fixed-scope service
For an explicitly consenting BTC-mainnet payer, produce one signed-off evidence memo covering up to five payer-supplied TXIDs and one agreed invoice, for a **negotiable BTC-mainnet fee agreed before work**. No fee or buyer is currently agreed. Existing competitors: mempool.space and Blockstream Explorer (transaction observation), invoice software (invoice state). Distinction: manual payer-to-invoice linkage and honest UNKNOWN outcomes.

## Input schema (public non-sensitive data only)
```json
{
 "invoice_id":"DEMO-001",
 "agreed_btc_sats":120000,
 "payer_reference":"DEMO-PAYER",
 "acceptance_url":null,
 "btc_mainnet_address":"bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z",
 "observations":[{"txid":"64 lowercase hex characters","vout":0,"value_sats":120000,"recipient_matches":true,"confirmations":null}]
}
```

## Deterministic validation rules
1. Reject negative values, non-integer sats/vout, malformed TXID, and non-mainnet receiving address.
2. An observed transaction is never automatically classified as income; require documented acceptance, payer attribution, and confirmed on-chain output.
3. Mark settlement **UNKNOWN** when confirmations cannot be independently read; do not assume zero.
4. A matching recipient and amount alone are **INSUFFICIENT** to classify a transaction as customer revenue; self-transfers and unrelated deposits are excluded.
5. A valid BTC mainnet destination is not a Lightning invoice. Do not use exchange or other-chain candidates.

## QA vectors (synthetic; no actual funds)
| Case | Output match | Confirmations | Buyer acceptance | Expected |
|---|---|---|---|---|
| A | yes | 3 | yes | Eligible for manual payer-link review, not automatically paid |
| B | yes | unknown | yes | UNKNOWN chain settlement |
| C | no | 6 | yes | WRONG_RECIPIENT |
| D | yes | 6 | no | UNACCEPTED_WORK |
| E | yes | 6 | yes, payer unlinked | UNATTRIBUTED_TRANSFER |

## Delivery and evidence gate
A real report must cite a public explorer TXID/output, exact amount, confirmations, recipient, date, invoice terms, buyer acceptance, and explicit payer relation. Never request a private key, signature, payment or gas for verification. Do not publish customer-private invoices without consent.

## Commercial gate
Market: Bitcoin-paid freelance writers, bounty maintainers, and small agencies. Before doing commissioned work, identify one actual willing payer, exact scope, BTC-mainnet settlement consent, and a permitted authenticated contact channel. Current stage: **PROTOTYPE ONLY**. No verified client, accepted order, submission or receipt.
