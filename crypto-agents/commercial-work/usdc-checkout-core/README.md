# Native-USDC checkout verification: portfolio demo

Original Node 22, standard-library-only component for merchants accepting Circle-native USDC on **Base (8453)** or **Polygon PoS (137)**. It is a **partial software demonstration**, NOT a live checkout, gateway, wallet, paid contract, or independently verified chain payment.

## Demonstrated functions

- Invoice creation with exact micro-USDC integer amounts; reject unsupported chains or fractional digits beyond six.
- Strict matching of order ID, exact chain, native token contract, recipient and amount.
- Timing-safe HMAC verification of trusted-provider webhook signatures before processing events.
- Independent on-chain proof callback required: a signed payload alone does NOT establish a real payment.
- Twelve-confirmation default, chain evidence consistency, transaction-log idempotency, collision/reuse rejection and replay revalidation.

## Test

Use Node 22:

```bash
node --test crypto-agents/commercial-work/usdc-checkout-core/checkout.test.mjs
```

Tests use fabricated receipts with an explicitly injected fake proof callback. **Passing tests cannot establish on-chain settlement.** No chain access, signing, gas, deposits or API charges occur.

## Work still required for production

1. Implement a separate hardened RPC/indexer adapter that verifies the real ERC-20 Transfer event and network, contract, destination, amount, tx hash, log index, block, finality and reorganization history; caller must not trust webhook fields as chain proof.
2. Replace this module's in-memory Maps with durable atomic SQL transactions and unique constraints to prevent double payment during concurrent requests and after process restarts. The example is unsafe for real order fulfillment.
3. Add HTTP/TLS endpoint, webhook timestamp/nonce policies, durable replay protection, per-provider secret rotation, order authentication, rate limiting, audit trail and encrypted secrets outside GitHub.
4. Add merchant wallet-connect UI and the business's approved receiving addresses. Implement compliance controls and manually approved refund workflow; do not transfer coins automatically.
5. Run independent production-like integration tests and obtain a genuine buyer's funded escrow and written acceptance before work on customer data.

Issuer source: [Circle's native USDC Base contract](https://www.circle.com/blog/usdc-now-available-natively-on-base) and [native Polygon USDC](https://www.circle.com/blog/native-usdc-now-available-on-polygon-pos). Bridged USDbC or USDC.e is deliberately excluded.

External prospect: [Worldwide USDC checkout integration brief](https://work001.com/jobs/usdc-checkout-integration/) advertises $1,800–3,000, but its client, escrow, payment history and opportunity have **not** been independently verified. No account application or commission has been submitted. Market claims must not be treated as receipts.

**Financial result:** no approved paid work, invoice or confirmed BTC/USDC payment.
