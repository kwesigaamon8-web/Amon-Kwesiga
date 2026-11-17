# BriefGate — pre-work terms checklist

Prototype tested 17 November 2026. Run `python brief_gate.py --test`: eight tests passed (complete-but-unverified, Lightning mismatch, missing agreement, wrong recipient, expired deadline, boolean fee, worker spending, empty brief). Source commit: 9fe1d27add8b318c14e5699093d9c056f412e3e3.

Problem: a headline fee and a wallet address do not establish an actionable commission. This offline checker lists missing scope/acceptance/funding/eligibility evidence and only permits the two owner-approved BTC-mainnet receiving routes. It never verifies URL contents, claims buyer identity, accepts contracts or sends funds. Even a complete synthetic fixture stays unverified. No absolute novelty claimed.

Buyer hypothesis: BitcoinTalk Services writers and small GitHub bounty sponsors who need a pre-work terms review. Spend trigger: commissioning an unfamiliar counterparty. Proposed one-brief review fee: 20,000 sats, subject to a buyer agreeing; no sale or demand validated. Mainnet is technically compatible with approved receiving routes, but individual buyer willingness remains unknown. Use existing opt-in offer threads; do not spam new solicitations.

Alternatives: GitHub issue forms already collect structured validated inputs (https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms). Bitcoin payment URIs already encode payment information (https://github.com/bitcoin/bips/blob/master/bip-0021.mediawiki, now superseded by BIP321). This prototype adds a narrow offline commissioning checklist; it does not replace either or the existing post-delivery Proof-to-Payout Capsule.

Buyer checks this run: owner issue #10 and Circadian-agent/agent-collective #1 had no later genuine buyer acceptance after the published offers. AntiSwap's original forum request requires assigned wallet tests and exchanges; no authenticated commissioning or approved spending was established. BTCTasks' ten-article page still lacks named buyer and independent escrow evidence, so no private information submitted. No email accessed; no wallet actions.

Next validation gate: a named independent buyer explicitly agrees a brief, fee, acceptance criteria and BTC-mainnet settlement through a permitted public channel. Until then this is an internal product hypothesis, not commissioned customer work.
