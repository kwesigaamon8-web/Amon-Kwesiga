# Draft technical proposal — open-source Bitcoin merchant invoice evidence for small businesses

**Status:** Research-backed proposal prepared, **NOT SUBMITTED** to Tether, no application accepted, and no money requested from any user wallet. Submission would bind the applicant to legal terms and requires the human owner to independently review and accept those terms. No Gmail, email reading, email drafting, email sending, external login, wallet signing, spending or KYC representation has occurred.

## Source and eligibility

- Tether officially announced on 11 May 2026 a developer grants programme for local-first AI, wallet infrastructure, e-commerce integrations, documentation and related tooling. Tether announced indicative individual payouts of about **US$1,500 to US$4,000 in USD₮ or Bitcoin**, tied to completed deliverables. Source: https://tether.io/news/tether-launches-developer-grants-program-to-fund-local-first-ai-and-payments-infrastructure/
- Official opportunity directory: https://tether.dev/grants/bounties/ . On 17 November 2026 the public listing showed **ANE Acceleration for llama.cpp — CoreML Backend + QVAC**, advertised at 5,000 USD₮; this is **NOT a Bitcoin merchant-wallet award**, and no equivalent merchant-wallet fixed bounty was verified.
- Official general application page: https://tether.dev/grants/apply-for-a-grant/ . The application is an embedded third-party web form. No form was submitted.
- Official terms: https://tether.dev/grants/terms/ ; may require KYC, age and jurisdiction eligibility checks, owner approval of a legally binding application and later contract. The terms grant Tether a non-exclusive, perpetual license to submitted application materials. Neither the owner nor these workers have accepted those terms through this repository.

## Proposed project

**Name:** Africa Merchant BTC Watch and Invoice Evidence Kit

**Problem:** Small businesses can generate a Bitcoin payment request, but a screenshot or a buyer-supplied TXID alone is insufficient proof that a payment reached the intended address and that the sale was legitimately settled. Reused receiving addresses create further ambiguity. SaaS checkout services may require custody, contracts or data exposure.

**Solution:** A free, auditable, noncustodial, low-dependency web tool that:
1. Validates native mainnet SegWit addresses using BIP173/BIP350 checksums;
2. Generates BIP21 invoice payment URIs with exact satoshi amounts and percent-encoded references;
3. Fetches public Bitcoin transaction outputs read-only with explicit network/error distinctions;
4. Aggregates partial confirmed/unconfirmed outputs and counts confirmations where available;
5. Maintains a local invoice evidence ledger that prevents the **same TXID:vout** from being counted against separate invoices and updates evidence when confirmation state changes;
6. Clearly separates **onchain output evidence** from customer acceptance, payer identity, address ownership and actual business income.

**Actual working public code:**
- https://github.com/kwesigaamon8-web/Amon-Kwesiga/tree/main/crypto-agents/commercial-work/africa-bitcoin-merchant-wallet
- Current project includes the standalone webpage, `wallet_core.mjs`, `invoice_ledger.mjs`, unit tests and an automated GitHub Actions test job.
- The initial wallet core had 10 independently executed tests passing on GitHub Actions: https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44120172101
- The new ledger tests are in CI; **do not mark them passed until the corresponding GitHub Actions run completes successfully**.
- Existing limitations: no automatic unique receive address derivation, no transaction history pagination, no key management, no integration with Tether WDK, no proof of merchant adoption or authenticated commercial buyer.

## Requested funding — proposal only

**Indicative funding request:** US$2,500 equivalent, *if Tether independently offers and approves a relevant grant*, with a **native Bitcoin mainnet BTC payout preference**. This is a proposed ask, not a verified offer, approved grant, earned debt or expected deposit. Confirm application rules and payment rails prior to any request; **Stacks sBTC and BTC Lightning cannot be sent directly to a native `bc1` address**.

The project may only expand to Tether WDK after reviewing its actual SDK capabilities and applicable licensing; present public code does not use it.

## Proposed milestone acceptance

| Milestone | Testable deliverable | Proposed amount | Payment status |
|---|---|---:|---|
| 1. Core evidence | Reproducible Bech32/BIP21/tx-output unit tests, documented limits | US$500 | Not contracted |
| 2. Ledger integrity | Partial payments, duplicate TXID:vout allocation rejection, confirmation changes, exported evidence tests | US$650 | Not contracted |
| 3. Merchant resilience | Two independent public-source fallbacks, paginated optional receipt history, error/caching behavior, 10 new tests | US$650 | Not contracted |
| 4. Local-first usability | Offline invoice creation; low-bandwidth mobile UX; accessibility; a permitted anonymized merchant walkthrough and open documentation | US$700 | Not contracted |
| **Total proposed** | | **US$2,500** | **No award / no payment** |

Amounts above are our **internal proposal**; they are not Tether's fixed bounty terms. Milestones 3 and 4 are not currently delivered. Merchant walkthroughs require each participant's consent; no contact is authorized by this document.

## Security and privacy

- No wallet key import, creation, signing, withdrawal, transfer or gas expenditure is supported by this prototype.
- Public TXIDs/receiving addresses may be disclosed to the chosen explorer on a user-initiated lookup; no private customer data is intentionally transmitted.
- Blockchain output matching alone is **not** customer payment attribution. Do not label a BTC invoice commercially paid merely because an address received coin.
- For a hosted deployment: require code review, privacy notice, CSP, integrity controls, accessibility review, secure dependency policy and abuse controls.
- Open-source licence selection must be reviewed by the actual rights holder before redistributing under a specific licence.

## Commercial and payment action gate

1. Obtain real sponsor acceptance of the technical scope and funding, not just a public website headline.
2. The human owner must review eligibility, potential KYC, binding terms and any intellectual-property licence.
3. Use only an actually approved authenticated form submission channel; **never Gmail/email** without separate explicit owner authorization.
4. Do not count the grant until the sponsor accepts the work and actual incoming cryptocurrency with correct blockchain/asset/address is independently evidenced.
5. B1/B2 configured 750B roles are not independent continuously running workers; measure the actual model/OS work and transactions.

**BTC receiving routes supplied by the owner for possible compatible native mainnet payments:**
- B1: `bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z`
- B2: `bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9`

Owner control of these addresses has not been cryptographically proven by this grant draft. No payment claim arises from listing them.
