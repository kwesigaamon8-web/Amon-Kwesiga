# SatsLedger Africa — Bitcoin payment requests and local cashbook

A lightweight, client-side app for small businesses in Uganda and elsewhere in Africa. The [standalone MVP](./index.html) runs as a static HTML file with no server, account, database or wallet custody.

## Use
1. Open `index.html` in a recent browser (or serve via `python3 -m http.server`).
2. Generate an exact BIP21 on-chain request using a **checksummed Bech32/Bech32m SegWit address**.
3. Or, with a compatible WebLN-enabled wallet extension, request a Lightning invoice using that wallet's own signing/payment interface.
4. Copy the request to a customer and log the reference and amount locally.
5. For on-chain receipts, verify a customer-supplied transaction ID; the app compares real outputs to your address with the expected satoshis and distinguishes confirmed from unconfirmed.
6. Export the local cashbook as a formula-injection-safe CSV.

**Not a wallet:** It never requests secret keys and cannot send or receive funds itself. The connected wallet is responsible for any Lightning settlement verification. The app only makes requests and verifies public chain data. Local records may be deleted with browser data and must be exported for retention. Do not count a request as revenue until payment is actually verified.

## Prototype status (13 Nov 2026)
- A separate, more modular reference implementation was tested locally with 8 passing Node unit tests. The standalone file in this branch is a distinct consolidated variant; it has **not yet been end-to-end browser-tested**.
- No live Lightning or Bitcoin mainnet payment was received, no hackathon submission was made, and no prize was won.
- Requires JavaScript-enabled browser; explorer API availability can affect transaction verification.

## Suggested entry
[Dakar Bitcoin Hack by BTrust](https://dakar-bitcoin-hack-2026.devpost.com/) — deadline 20 Nov 2026 at 20:00 UTC. The official rules limit entry to eligible students in Africa. This code and brief can support an entry, but a Devpost registration and proof of eligibility remain prerequisites.

## Security limitations
- Reusing an address and invoice amount can make transaction allocation ambiguous. Never share seed phrases.
- An on-chain transaction can be seen before it is confirmed; only confirmed matching outputs are marked confirmed.
- The public TXID is queried using https://mempool.space/.
- Do not store confidential client data in the local ledger; exported CSV is not an audited financial statement.
- No promises about BTC earnings, Binance payments, hackathon qualification or reward.

MIT-licensed original prototype.