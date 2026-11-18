# Crypto Ledger Reconciliation Workbench

An offline-first, read-only CSV tool for comparing BTC and USDC transaction exports against general-ledger exports. It is designed for small Web3 finance teams, contractors and bookkeepers who need a reproducible exception list without connecting a wallet or sending transaction data to a service.

## Run locally

From this directory, start a local static server:

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000`. Select **Load fictional demo** to run the included synthetic example, or import/paste two CSV exports and choose **Run reconciliation**. Use **Export report CSV** to download the comparison.

## CSV fields

Required on both sides:

- `txid`: 64 hexadecimal characters; an optional `0x` prefix is accepted for EVM transaction hashes.
- `asset`: `BTC` or `USDC`.
- `network`: `bitcoin-mainnet` for BTC or `base-mainnet` for USDC.
- `direction`: `in`/`incoming` or `out`/`outgoing`.
- `amount`: exact decimal amount, or use `amount_atomic` as an integer string.

Recommended:

- `output_index`: Bitcoin `vout` index or EVM `log_index`.
- `date`, `reference`/`memo`, `account`.

The tool supports BTC at 8 decimal places (satoshis) and USDC on Base at 6 decimal places (micro-units). It rejects unsupported asset/network pairs, negative amounts and excess decimal precision. Amounts are converted with `BigInt`, not floating-point arithmetic.

## Matching and exception handling

- Preferred match key: transaction ID + output/log index.
- A single row on each side can match by transaction ID alone, but the report labels this weaker method.
- Duplicate keys, missing output indexes on multi-row transactions, output-index differences, amount mismatches, asset/network/direction mismatches, chain-only rows and ledger-only rows are kept visible for human review. The signed difference is chain amount minus ledger amount.
- Transaction-level fees are not allocated across outputs. Do not add a transaction fee to every output; reconcile fees separately.
- The CSV parser supports quoted commas, escaped quotes and CRLF line endings.

## Market position and limits

Established products already offer much broader integrations and automation. [Koinly](https://koinly.io/crypto-accounting-software/) advertises 900+ integrations, CSV/API imports and QuickBooks/Xero sync; [CoinLedger](https://coinledger.io/tools/best-crypto-accounting-software) offers an accountant suite and wallet/exchange connections. This workbench is **not** a replacement for those platforms, a crypto sub-ledger or a tax engine.

Its narrower proposition is an independent, local-only exception check for a buyer who already has two exports and wants a small, reviewable comparison without connecting wallets or uploading records to another SaaS provider. It does not calculate cost basis, fair value, FX rates, tax, journal entries or IFRS treatment. That privacy-first workflow is a hypothesis to validate with real buyers, not proof of market demand.

## Privacy and safety

- All processing runs locally in the browser tab. There are no external scripts, APIs, uploads, cookies, analytics, wallet connections, private keys, signatures, spending functions or persistent storage.
- The fictional demo uses fabricated transaction IDs and amounts. It does not represent real deposits or earned revenue.
- Do not import seed phrases, private keys, credentials or unnecessary personal/customer information.
- The report is a reconciliation aid, not an audit opinion, tax calculation, IFRS conclusion or proof of customer identity, address ownership, source of funds, transaction completeness or fair value.
- Do not post accounting entries without reviewing the original exports, transaction purpose, valuation date, fees and the entity's accounting policy.

## Tests

No npm dependencies are required:

```bash
node --test core.test.mjs
```

Tests cover exact BTC/USDC decimal conversion, unsupported rails, CSV quoting, exact matches, amount and output-index mismatches, missing records, duplicate keys, ambiguous rows, invalid data and safe CSV export.

## Commercial pilot

Indicative offer: reconcile up to 500 exported crypto transaction rows against a ledger export, produce an exception report and document unresolved items. Proposed fee: **US$50 equivalent in native BTC on Bitcoin mainnet**, subject to a written scope, exact satoshi quote and acceptance checks agreed with a real buyer before work begins. No advance payment, wallet access or private keys are required. A buyer can request a scoped pilot through the repository's existing [public intake](https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/new?template=paid-work-request.yml).

This is an original prototype and a commercial lead, not a booked engagement or a claim that anyone has paid.
