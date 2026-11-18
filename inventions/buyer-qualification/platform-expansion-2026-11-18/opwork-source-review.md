# Marketplace action trace: a public-source work sample

Observed 18 November 2026, 09:05 EAT (06:05 UTC); a second worker independently inspected the source at 09:14 EAT. This is an uncommissioned review sample. No application, account, wallet interaction or transaction was performed.

## What the source establishes

Source: [OPWork public homepage](https://opwork.vercel.app/). These findings apply to the captured version, not every possible deployment.

| Source location | Observation | Evidentiary limit |
|---|---|---|
| `JOBS`, line 994 onward | Six job records are literals, including the 0.12 BTC writing listing. | A displayed budget and verification flag do not establish a funded buyer. |
| `FEED_EVENTS` and `renderLiveFeed`, lines 1042 and 1104 onward | Five literal events are displayed and randomly recycled. | The animation is not independently observed payment activity. |
| `applyToJob`, lines 1448–1456 | Wallet-state checking leads to a success message; this handler contains no submission call. | This path does not demonstrate an accepted application. |
| `submitJob`, lines 1461–1471 | Wallet/title checking leads to a success message; this handler contains no escrow call. | This path does not establish locked funds. |

Other functions call injected wallet-provider APIs. This review therefore does **not** establish that the whole site has no networking. Static inspection cannot determine all backend behavior or intent; it does not justify an allegation of fraud.

## Reproduce the observation

The companion [observation record](opwork-observation.json) identifies the source URL, capture time, UTF-8 byte count, full SHA-256 and segment hashes. Segment hashes use the inclusive line interval, LF separators and no trailing newline. Inspect the named source functions directly; do not connect a wallet just to reproduce this review. A changed digest means a new observation is required, not that the current page is defective. The full third-party HTML is not republished.

The captured file's digest and all referenced sections were checked locally. A separately running reviewer reproduced the four source observations. This validates the limited static findings; no browser action, server request trace, blockchain escrow or actual buyer was tested.

## Proposed paid service, subject to a real commission

**Marketplace action trace review:** inspect two public frontend paths and give a maintainer an evidence table separating the displayed result, the visible action path and the missing acceptance proof. The practical problem is a team inadvertently describing a prototype UI as a completed submission or settlement.

Named public buyer market: OPWork and the Bitcoin marketplace-maintainer community. OPWork is an inspected product, **not a verified customer**. No demand or willingness to pay for this service has been demonstrated.

Proposed pilot: **15,000 sats in native BTC mainnet**, with a public report, exact source locations and acceptance-test recommendations. A buyer must agree scope, deadline, acceptance criteria and the direct mainnet payout before material commissioned work. There is no agreed fee, invoice or earnings entry. Lightning and wrapped BTC would require a separately approved compatible arrangement.

## Existing alternatives and useful distinction

[Chrome DevTools Network](https://developer.chrome.com/docs/devtools/network) can inspect actual uploads, downloads and request initiators during authorized browser testing. [Playwright network events](https://playwright.dev/docs/network) can observe requests and responses and assert a response after an action. Both are strong existing alternatives for teams able to exercise a permitted test environment.

This sample provides a small source-evidence review without running third-party page code or using a wallet. It is less complete than an authorized runtime test. Its value would be precise findings and a suitable next test, not a claim of technical novelty or guaranteed security.

Suggested buyer acceptance checks: require a durable application identifier after successful submission; link any escrow state to the correct network, contract and independently checked transaction; and label sample activity as sample data. These are proposed checks, not claims about fixes deployed or work accepted.
