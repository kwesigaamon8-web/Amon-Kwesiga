# SatsLedger — Bitcoin Payment Request & Reconciliation Demo

**Independent prototype** built to show how a small business can prepare a native Bitcoin payment request and reconcile BTC receipts to invoices. It is a **portfolio demonstration**, not a custody service, payment processor, or production accounting system.

## Demo

Open [index.html](./index.html) in a modern browser. The application runs as a standalone HTML file with no server, account or wallet connection.

- **Payment requests:** Enter a customer, reference and BTC amount, then generate a BIP21 `bitcoin:` payment URI and printable request. An address-only QR is included for the prefilled address; it does not encode an amount.
- **Receipt reconciliation:** Load separate invoice and receipt CSVs, or the included fictional sample. Match by invoice reference and show paid, unpaid, underpaid, overpaid and unassigned receipts. Export a CSV report. Calculations use integer satoshis.
- **Watch-only address check:** Optionally query `mempool.space` for publicly reported address activity. This requires network access and sends the *public address* to that provider.

**Receipt CSV headers:** `invoice_id,txid,amount_sats,confirmations`  
**Invoice CSV headers:** `invoice_id,customer,amount_sats`

## Important limitations

- All sample transactions and invoices are **fictional**, not evidence of earnings.
- No private keys, seeds, passwords, account access or signing are required. The tool cannot hold, spend or send BTC.
- Confirmations in uploaded CSVs are **unverified user-supplied numbers**. Verify settlement and exact transaction amounts with your node or a trusted blockchain explorer.
- The watch-only lookup is best-effort. An unavailable lookup does **not** mean the balance is zero.
- The address shown is a **public Bitcoin mainnet address**. Do not use this program for Lightning invoices, Stacks sBTC or other assets.
- Before deploying for clients, add robust address checksum validation, trusted transaction matching, receipt deduplication, persistent accounting records, privacy controls, independent security review and production tests.

## What this demonstrates

Accounting-led product thinking: linking an invoice to transaction evidence, classifying exceptions and documenting settlement assumptions in a way managers and auditors can follow.

**Availability:** Open to scoped, paid projects involving Bitcoin transaction reconciliation, financial control reviews, CSV/ledger cleaning, spreadsheet reports and documentation. Contact the repository owner for project discussion.