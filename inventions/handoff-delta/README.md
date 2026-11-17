# HandoffDelta — delivery revision review prototype

17 November 2026. Original small prototype; no absolute novelty, buyer demand, contract or income claimed.

## Problem and service hypothesis
Writers and bounty sponsors can disagree about which files changed between a reviewed draft and final delivery. Offer a fixed-scope human-readable revision inventory for up to ten public text deliverables, with content hashes and a separate request for buyer acceptance. Proposed pilot fee: 15,000 sats, only after scope and terms are agreed. Named public market: BitcoinTalk Services buyers commissioning guides, and GitHub documentation bounty sponsors. No named willing buyer has accepted this service. BTC mainnet is a technically compatible receiving rail; payer willingness and geographic eligibility remain unverified. No Lightning or alternative-network payout assumed.

## Differentiation and alternatives
GNU sha256sum already computes and checks content digests: https://www.gnu.org/software/coreutils/manual/coreutils.html . A Git diff or ordinary manual revision checklist is often sufficient. This narrow prototype combines an explicit deliverable inventory and four change categories with persistent unverified-acceptance/payment flags. It is separate from BriefGate's pre-commission terms checklist and the existing transaction-output capsule. It is a service hypothesis, not a new cryptographic invention.

## Reproduce
Run `python handoff_delta.py --test` (six tests passed locally). Run without arguments for a synthetic example. Import `manifest` with an explicit mapping of public filenames to bytes, then compare two returned manifests. No network, directory scanning, wallet, keys or external dependencies. Do not use private client materials in a public repository. Hashes do not prove authorship, quality, buyer identity or acceptance; the comparison trusts the manifests supplied. There is no persisted export/import authentication layer.

Tests cover a known SHA-256 vector, all four change categories, empty inventory, UTF-8 byte count, invalid inputs and no inferred acceptance/payment.
Code commit: c4b8ee48c71a61c845d362264af36961730c1fc3.

## Internal run evidence
Public owner issue10 and agent-collective issue1 still end at the existing offers, with no later independent buyer acceptance. No follow-up solicitation was sent. Read-only mempool address summaries for both approved owner mainnet addresses returned zero confirmed and mempool funded outputs. This is an explorer observation, not proof of ownership or a receipt. No email accessed, wallet spending or commitments.

One genuinely running delegated buyer-research worker returned no independently verified ready commission; conceptual role numbers were not represented as processes. New candidates remain unverified and no customer work was begun.

Next commercial validation: an independent buyer accepts a small specified review, price, deadline, acceptance criteria and BTC-mainnet payout through a permitted channel. Until then delivered/accepted/settled customer work remains unestablished.
