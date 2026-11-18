# Dakar Bitcoin Hack 2026 — original project submission package

**Project:** Bitcoin Merchant Watch Wallet — Africa  
**One-line pitch:** A privacy-first, receive-only Bitcoin wallet interface helping small African traders request native-BTC payments and verify actual blockchain outputs without exposing a seed phrase.

**Source and interactive code:** [Public project folder](https://github.com/kwesigaamon8-web/Amon-Kwesiga/tree/main/crypto-agents/commercial-work/africa-bitcoin-merchant-wallet)  
**Live MVP deployment evidence:** [Bitcoin Merchant Watch Wallet — Live Public MVP workflow](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/bitcoin-merchant-hackathon-demo.yml). Open its latest successful run for the temporary HTTPS address and expiry. Do not reuse an expired anonymous-host URL.  
**Automated test evidence:** [Wallet test workflow](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/btc-watch-wallet-test.yml).

## Suggested Devpost project description (ready to adapt, not submitted)

### Inspiration — local problem

Small merchants, market vendors and independent freelancers across Africa can receive Bitcoin from willing customers, but often lack a simple way to issue a standards-compatible payment request and independently see whether a claimed payment actually sent satoshis to the intended address. Screenshots and copied payment messages are not blockchain evidence; complex custody tools can also encourage unsafe handling of seed phrases.

### What we built

Bitcoin Merchant Watch Wallet is a tiny open-source, browser-run receive-only wallet tool. A merchant chooses a verified Bitcoin mainnet address (or enters their own), chooses an integer price in satoshis and an invoice reference, and creates a BIP21 payment URI usable by a compatible Bitcoin wallet. After the buyer sends a transaction ID, the app reads a public Bitcoin explorer and compares every output against the intended address and satoshi amount. It distinguishes unconfirmed, insufficient, missing, and confirmed output matches. A separate original invoice ledger module supports multiple invoices and rejects assigning one TXID/output to different invoices.

The project deliberately does **not** claim to be a full private-key wallet, exchange, mobile-money interface or proof that a specific buyer paid. The merchant retains control of their existing Bitcoin wallet. No key, signature, funds, custody or outgoing transaction ever enters the app.

### How it was built

- Standard HTML, CSS and JavaScript modules without framework or npm-runtime dependencies; responsive/mobile-first, limited network requests
- Native Bitcoin SegWit mainnet address validation, including BIP173/BIP350 checksum and witness-program checks
- Safe BIP21 URI composition with exact integer-satoshi inputs
- Public mempool.space transaction and tip-height lookups with graceful timeout/error handling
- Separate invoice/output evidence module with duplicate TXID:vout allocation checks and confirmation/reorg handling
- Automated Node built-in unit tests for correctness, malformed inputs, duplicate counting and dishonest paid-status claims

### What makes it useful

One merchant can run this on an inexpensive Android browser, supply only an **existing public receiving address** and ask buyers to open their own Bitcoin wallet. The interface does not ask a merchant to hand over custody, private keys, email credentials or signing permission. A receipt is not treated as settled simply because a buyer pasted a TXID; evidence must match the correct address and value and carry on-chain confirmation status.

**Honest impact hypothesis, not measured adoption:** A vendor receiving 2–10 legitimate BTC orders weekly could avoid a manual explorer walk-through for each one. No real merchant deployment, order count, conversion rate or earned fee has been demonstrated; these are potential outcomes to test.

### What's next

- Import a **public-only** descriptor or address list from a separate wallet, without custody or key derivation in the website
- Better local invoice history with encrypted or explicitly user-controlled export; avoid accidental sensitive cloud storage
- A lower-bandwidth explorer fallback, offline demo fixtures and accessible translations
- Pilot with consenting merchants who use their own wallets; separately measure errors caught and ease of use

## Three-minute demo script

**00:00–00:25 — Problem.** Many small merchants can share a BTC address but struggle to create a proper invoice or independently inspect the right output after receiving a TXID. A screenshot is not a receipt.

**00:25–00:55 — Wallet safety.** Open the hosted static page. Explain that it is a receive-only *wallet interface*; it never generates or requests a private key. Select a sample owner-approved B1/B2 address or a viewer's own verified mainnet address.

**00:55–01:25 — Create the BTC request.** Enter a fictional amount such as 10,000 satoshis and an innocuous reference. Generate the BIP21 link; show that this is labelled **not yet paid**.

**01:25–02:10 — Transaction evidence.** Paste a real publicly available Bitcoin TXID provided independently by the viewer, with no private transaction or buyer details. Verify whether that transaction actually sends sats to the chosen address; show unconfirmed/partial/no-match and confirmation count as available. Never claim a synthetic example is a real payment.

**02:10–02:35 — Correctness.** Run `node --test crypto-agents/commercial-work/africa-bitcoin-merchant-wallet/*.test.mjs` from the repository root. Explain how the ledger rejects a transaction output reused for multiple invoices.

**02:35–03:00 — African impact and scope.** Emphasize smartphone-friendly front end, no server-side merchant data, no credentials, and the limits: not a signing wallet, not Lightning, no conversion of UGX to BTC, no sender identity verification, not proof the output remains unspent.

## How to reproduce

```bash
git clone https://github.com/kwesigaamon8-web/Amon-Kwesiga.git
cd Amon-Kwesiga
node --test crypto-agents/commercial-work/africa-bitcoin-merchant-wallet/*.test.mjs
python3 -m http.server 8000 --directory crypto-agents/commercial-work/africa-bitcoin-merchant-wallet
```

Open `http://localhost:8000`. Static interface requires no secrets, private RPC provider or paid API. Actual public TXID checking does require internet access to the external explorer.

## Threat model, limitations and security review

| Risk | Current control / limit |
| --- | --- |
| Unsafe key custody | No seed, private key, signatures, wallet connection, spending or broadcasting |
| Sending money to the wrong chain | Only checksum-valid `bc1` Bitcoin mainnet SegWit address accepted |
| Decimal/invoice mismatch | Positive whole satoshis; fixed eight-place BIP21 BTC representation |
| Fake screenshot or mismatched TXID | Require actual explorer data and check every output's exact address and value |
| Reused transaction output across invoices | Separate ledger rejects identical TXID:vout reallocation |
| Blockchain reorganizations | Recheck can reduce confirmation status; never automatically infer final sale |
| Payer identity | Explicitly **not** verified; merchant must match their separate order evidence |
| Output unspent status | Explicitly **not** proved by a historical matching output |
| Privacy | No keys or customer data collected; explorer can observe queried public TXID |
| External provider outage | Error/unknown state, not a fabricated "not paid" result |
| Payment/address control | Recipient ownership of example B1/B2 addresses not independently demonstrated |

## Contest entry and financial status — important

- **Official rules:** https://dakar-bitcoin-hack-2026.devpost.com/rules
- **Official event:** https://dakar-bitcoin-hack-2026.devpost.com/
- **Deadline:** 20 November 2026, 20:00 UTC.
- **Conflicting official prize descriptions (not a guaranteed claim):** the main Devpost event page advertises first **$500 of BTC**, second **$250 of BTC**, third **$150 of BTC**, while its separate official **rules** state first **500,000 sats**, second **250,000 sats**, third **100,000 sats**. These figures are not equivalent. Treat the prize value and unit as **UNCONFIRMED** until organizers resolve the contradiction through an authorized contact channel. Do not convert either set into an expected receivable.
- **Eligibility:** the public event page says **students only**, legal adults, and excludes companies/professional organizations. The separate rules require a participant to **reside in Africa**. The individual owner's qualifying student status **must be personally confirmed** before submitting; residence alone does not establish it.
- **Submission:** must be made by an authenticated and eligible participant through Devpost. This package and deployment are **not a Devpost entry**, assignment, acceptance, winning outcome, payable invoice or receipt.
- The organizer's minimum wording says a Bitcoin/Lightning wallet implementation is required. This project contains a real **watch-only receiving interface**, but no spending wallet. Whether that satisfies the judges' wallet-implementation definition **is not confirmed**.
- Prizes are competitive. A reward is not income until the entrant actually wins, claims through the required platform, and receives a verified compatible transaction. No emails, credentials, wallet signing or outgoing transfers are authorized by this package.

## Technical and ownership statement

Original code and tests reside in the linked owner GitHub repository. Public BTC receive-only addresses shown in the demonstration were owner-provided, but ownership has not been proven on-chain. No fabricated user testimonials, live customer payments, partner logos, project acceptance, demo videos or hackathon submission are asserted.
