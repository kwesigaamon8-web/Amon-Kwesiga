# B1/B2 Chief D — real-money bounty gate, 18 Nov 2026 14:00 EAT

## Decision: exclude an apparently attractive 50,000-satoshi listing

**Candidate:** [BitPolito/paycue-bounty-demo issue #6](https://github.com/BitPolito/paycue-bounty-demo/issues/6), titled “Add a glossary of payout states.” It is OPEN and its issue text advertises **50,000 sats** for a merged PR. The issue requests nine one-sentence state definitions and a README link. Three comments were present when checked; another contributor reported submitting [PR #31](https://github.com/BitPolito/paycue-bounty-demo/pull/31). **Do not compete for this issue.**

**Critical source check:** The repository's own [README](https://github.com/BitPolito/paycue-bounty-demo/blob/main/README.md) explicitly says **“Signet/testnet only: no real money.”** It describes Liquid testnet or Lightning payout registration on a demo board. Accordingly, the issue's “50,000 sats” is **not an independently confirmed real BTC payout** and must be counted as **UGX 0** for the owner's 18:00 Kampala target. An on-chain testnet transaction would not satisfy the owner's real-money requirement. The B1/B2 mainnet receiving addresses are not proof of Lightning Address support; do not submit them as a Lightning address.

## Reusable paid-buyer qualification gate

Before any coding, application, PR, or proposed receipt:

1. Read the **originating repository README**, bounty issue, and payment policy, not just a search snippet or mirrored bounty board.
2. Confirm **real mainnet asset**, exact chain/network and the user's compatible address; explicitly exclude signet/testnet/devnet, points, hypothetical pools, credits and token allocations without verified liquidity.
3. Confirm actual available funding or escrow from a trustworthy source. An advertised reward is not funding proof.
4. Check whether the issue is already claimed, has a competing PR, or is closed; avoid duplicating work.
5. Verify that the connected GitHub identity has actual contributor authorization and any required external payout/agent registration. If a separate login or Lightning wallet is needed, record a blocker; never fabricate one.
6. Confirm acceptance tests, deadline, reviewer and payout conditions before building a deliverable.
7. Recognize income only after buyer acceptance **and** independently verifiable actual credited funds or a relevant mainnet TXID.

## Current evidence / result

- [B1/B2 paid-work offer](https://www.task-bounty.com/board/23a2a3ff-672e-4db7-8ff8-7d9845afb40b) was successfully published on an opt-in external board. This is a capability introduction, not a buyer acceptance.
- [B1/B2 public website](https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/docs/LIVE_SITE.md) was successfully deployed with CSV/JSON conversion and two-file reconciliation; [16/16 tests](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44289769027) passed and [deployment check](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44289949703) passed.
- [B1/B2 buyer intake issue #18](https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/18) had **no comments from external GitHub accounts** in the latest check (8 total owner comments). No accepted paid job or buyer payment was established.
- No new B1/B2 BTC-mainnet receipt was independently verified during this review. **New verified income: UGX 0, not an exhaustive wallet-balance claim.**

**Action completed:** removed a false-real-money lead from the eligible bounty shortlist and created a source-based screening gate for Chief D. Next priority: genuine funded buyer requests with compatible mainnet payout, and work actually accepted by a buyer. No Gmail, external posting, wallet signing, account creation or third-party PR was performed.
