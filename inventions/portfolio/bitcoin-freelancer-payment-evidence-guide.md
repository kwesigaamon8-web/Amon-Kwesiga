# How to Verify a Bitcoin Freelancer Payment Without Confusing a Transaction with Income

*Original educational writing sample · 17 November 2026 · Bitcoin mainnet · Approximately 850 words*

**Meta description:** Learn how to verify a Bitcoin payment to a freelance worker using a transaction ID, matching output, satoshis and confirmations—and what a blockchain cannot prove.

A buyer says, “I've paid you in Bitcoin.” The freelancer sees a transaction ID, opens a block explorer and spots a green confirmation badge. It feels as though the job is settled. But three different questions are being collapsed into one: did a transaction happen, did Bitcoin reach the address the worker supplied, and did a particular customer pay for a particular deliverable?

Only the second question can be answered from a matching blockchain output. The third needs business evidence outside the chain.

## 1. Ask for the exact rail before sending work

A Bitcoin mainnet address is not a Lightning invoice. Mainnet payments appear as transactions with outputs; Lightning payments are routed through payment channels and use separate invoices, receipts or wallet records. A payer who offers “Bitcoin” should state which rail they intend to use and whether they can pay the worker's approved receiving address. Do not paste a wallet seed, private key or backup phrase into a freelance marketplace.

Before the job begins, agree on the scope, price in BTC or satoshis, payment deadline, and how acceptance will be demonstrated. A public issue, signed order or authenticated message can establish those terms.

## 2. Start with a transaction ID, not a screenshot

A transaction identifier (TXID) is usually a 64-character hexadecimal value that can be looked up through an independent Bitcoin mainnet explorer. Screenshots of wallets are easy to misunderstand: a wallet can show a pending payment, a test transaction, someone else's receiving address or an amount before fees.

The public mempool.space API offers a read-only transaction endpoint:

`GET https://mempool.space/api/tx/{txid}`

The response has `vin` inputs, `vout` outputs and a `status` object. In a Bitcoin transfer, the receiver is identified by a specific output, not merely by the TXID as a whole. One transaction may pay several different addresses. Source: [mempool.space REST API](https://mempool.space/docs/api/rest).

## 3. Match the address and output index

For each `vout`, check whether `scriptpubkey_address` equals the receiving address agreed with the buyer. Record that output's zero-based position (`vout` index) and `value` in satoshis. If two separate outputs in the same transaction pay the same address, record both, but never count the whole transaction value as the payment.

**Illustrative example, not a real transfer:**

- Work price: 120,000 satoshis.
- Transaction outputs: 120,000 sats to the worker, 410,000 sats to an unrelated change address.
- Verified candidate receipt: **120,000 sats = 0.00120000 BTC**.
- Evidence key: `TXID:vout_index`, plus the exact receiving address and chain.

The payment's presence in a transaction is also not proof that it belongs to the job. The sender could be the worker moving their own coins, a supporter making a gift or a completely unrelated payer.

## 4. Record confirmation status accurately

An explorer may show a valid transaction still sitting in the mempool, without a confirming block. In that case report **unconfirmed incoming output**, not “fully settled.” Once the transaction is in a block, the confirmation count increases as more blocks build on the chain. The mempool.space `status` object states whether the transaction is confirmed and, if so, its block height. A current tip height can be used to estimate confirmations:

`confirmations = chain_tip_height - transaction_block_height + 1`

This number changes over time and depends on the explorer's current view. Different employers can set different acceptance policies: a small transaction may have a different threshold from a large one. Do not invent a universal “safe” number.

If an explorer times out, is rate-limited or returns an unexpected response, the status is **UNKNOWN**, not zero received. Use another independent explorer or try later; do not reclassify a service failure as payment failure.

## 5. Keep acceptance separate from receipt

A useful evidence capsule should have four individually supported stages:

| Stage | Evidence |
|---|---|
| Offered | Buyer, exact scope, proposed price and agreed payout rail |
| Delivered | URL or hash of the completed original work |
| Accepted | Written confirmation from the authorized buyer, against agreed criteria |
| Received | Bitcoin mainnet TXID, matching output index, actual sats and current confirmation status |

Only the last stage is directly visible on a Bitcoin explorer. Even a properly matching, confirmed output does not establish the payer's identity or explain why the transfer happened. Keep the signed or authenticated acceptance alongside the transaction proof.

For a refund, reversal request, fee dispute or allegation of non-delivery, this separation is much more useful than a screenshot of a wallet balance.

## 6. Beware the work-before-payment trap

A genuine buyer should be able to explain who reviews the work, how completion is judged and what happens if the deliverable is accepted. A marketplace claiming that its jobs are “escrow protected” ought to identify the escrow provider and verifiable funding or payout terms. Never pay a registration deposit, transfer Bitcoin to unlock earnings, or sign a transaction to release a supposed prize.

When a platform advertises only a price and an application button, it is a **lead**, not a funded job. Verify the buyer before producing hours of unpaid work.

## A practical no-custody workflow

1. Get a written fixed-scope job with BTC-mainnet payout terms.
2. Deliver original work using an agreed verifiable location.
3. Obtain an authorized acceptance message.
4. Independently inspect the TXID and every output matching the worker's address.
5. Record the amount, output index, confirmation state, time checked and explorer source.
6. Maintain separate totals for offered, accepted, unpaid and received.

A small, free static demo of this workflow is available as the [Proof-to-Payout Capsule](https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/inventions/proof-to-payout-capsule.html). It checks public BTC transaction-output matches but does not prove that an employer commissioned the work. That distinction is the whole point.

---

**Primary sources:** [mempool.space REST API documentation](https://mempool.space/docs/api/rest), particularly its transaction, address-transaction and confirmation-status endpoints. Source-linked technical assertions should be rechecked on the date a publication goes live.

*Editorial note:* No buyer, transaction or settlement in this article is presented as a real payment. No payment credential or wallet key is needed for public transaction verification.
