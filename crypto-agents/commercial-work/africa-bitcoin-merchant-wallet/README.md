# Bitcoin Merchant Watch Wallet (Africa)

An **actually runnable** static, receiving-only Bitcoin mainnet merchant wallet proof of concept. It creates standards-format BIP21 payment requests from a valid native SegWit address, then matches outputs in a public blockchain transaction by address and satoshi amount. It has no server-side keys, no wallet signatures, no custody and no outgoing transactions.

## Try the MVP

From the repository root:

```bash
python3 -m http.server 8000 --directory crypto-agents/commercial-work/africa-bitcoin-merchant-wallet
```

Then open **http://localhost:8000**. On a basic smartphone or low-bandwidth connection, the page itself loads without external scripts or CSS. Public blockchain verification needs network access to mempool.space.

1. Select **B1**, **B2** or **My own Bitcoin address**.
2. Enter a price in whole **satoshis** and an optional non-private reference.
3. Generate a `bitcoin:bc1...?amount=...` payment URI; it is a request **only**, not an actual deposit.
4. With a real, publicly available Bitcoin **transaction ID**, click **Look up transaction outputs**.
5. The result differentiates no address match, underpayment, unconfirmed matching output and confirmed matching output. If the explorer reports a tip height, confirmation count is included.

No seed phrase, private key, credentials, email or wallet spending is requested. There is no persistence.

## Tests

```bash
node --test crypto-agents/commercial-work/africa-bitcoin-merchant-wallet/wallet_core.test.mjs
```

No external npm dependencies. Unit tests cover real B1/B2 Bech32 mainnet checksum verification, wrong-network rejection, safe BIP21 URI generation, exact satoshi accounting, output matching, underpayment, unconfirmed funds and malformed explorer responses. End-to-end mempool.space browser access is **not** covered by offline tests. CI evidence is published by the repository's "Bitcoin Watch Wallet — Core Tests" workflow.

## Why African merchants could use this

A small retailer or freelancer can accept Bitcoin without giving a cloud checkout vendor possession of keys. A customer with a wallet can tap a standards-format payment URI, and a merchant can examine a TXID on public mainnet using a low-data interface. The tool provides evidence checks instead of a green "paid" badge inferred from a screenshot. It does not convert UGX to BTC, process mobile money, discover all wallet transactions, or prove the sender's identity.

## Limitations and security decisions

- **Watch-only**. This is an intentionally restricted payment-request wallet, not a spending/signing Bitcoin wallet. A user must use their existing secure wallet to control the destination address.
- **Only native Bitcoin mainnet SegWit** addresses beginning `bc1` are supported; no Lightning, Liquid, BCH, sBTC, Solana or USDC. Never send another network's assets to these addresses.
- A *confirmed matching output* is historical onchain evidence, **not** a confirmation that a specific buyer paid a particular invoice, that the recipient controls the address, or that the output is unspent.
- No merchant order ID is embedded in the chain payment. Reusing one address for several invoices can create ambiguous attribution; ideally issue a unique address using a proper external wallet.
- mempool.space is an **external public explorer**: it can see the public TXID queried, may be unavailable, and may have cross-origin/network restrictions. The app distinguishes unknown connectivity from an observed no-match.
- Confirmation count may be unknown if the tip-height endpoint fails. For irreversible deliveries, merchants should independently determine adequate confirmations and customer acceptance.
- No key generation, seed storage, key derivation, signatures, browser wallet connecting, fees, onchain broadcasting or spending are offered or authorized.
- The two B1/B2 default addresses are publicly owner-provided; this software **does not prove the owner's control of those addresses**. For a personal merchant demo choose your own verified address.

## Hackathon research (not an entry)

This original prototype may inform an entry to the [Dakar Bitcoin Hack by BTrust 2026](https://dakar-bitcoin-hack-2026.devpost.com/), which lists Bitcoin/Lightning-oriented African-impact projects, a 20 November 2026 deadline and prizes. Platform eligibility lists **students only**, and Devpost submission requires authentication. The user has **not been verified eligible, registered or submitted**, and a pure watch-only receiver **may not satisfy** the hackathon's wallet-implementation requirement. Prize amounts are **not earned money**. No email inquiries will be made.

## Commercial uses

The code can serve as a reproducible sample for a legitimately contracted merchant checkout integration, customized reporting or safe BTC-payment reconciliation. A willing, real buyer must first agree scope, tests, price and a compatible incoming crypto payment route. Publication does not create a customer, debt or commission. Public [opt-in client intake](https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/18).

## QA evidence

Unit tests are designed to fail if any owner B1/B2 address is not a checksum-valid Bitcoin mainnet address. This is important because a plausible-looking `bc1` string alone can still be invalid.
