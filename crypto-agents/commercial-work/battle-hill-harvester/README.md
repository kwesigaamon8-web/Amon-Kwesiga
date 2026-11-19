# B1B2 Hill Harvester — our original battle.training Armor controller

**Live original bot:** https://battle.training/bots/b1b2-hill-harvester

**Sponsor cup:** https://battle.training/cup/promotedby-cup-nov-2026

**Code:** [controller.js](controller.js) · **original local tests:** [test-results.json](test-results.json) · **successful entry status:** [entry-status.json](entry-status.json)

## What we actually built

This is an original, AI-assisted tactical controller for battle.training Season 2. It is **not** the official starter controller, a verbatim copy of a competing bot, or an NFT/coin. No public wallet was connected and no funds were spent to enter.

We chose a **12-point APC + MBT + engineer + scout** squad. The APC pursues heavy scoring objectives, the MBT screens threats, the engineer follows and deploys defensive smoke when enemies are nearby, and a scout fans out when multiple objectives exist. The controller calculates movement toward goals, checks terrain passability, aims turrets at visible enemies, avoids firing outside range and applies fallback steering when a unit is blocked.

### Real tests and their limits

On 19 November 2026, the arena's official local simulator with **Season 2 s2.0.0**, **3 seeds per enemy style**, and two sides each reported:

| House opponent | Wins | Losses |
|---|---:|---:|
| Brawler | 4 | 2 |
| Holder | 2 | 4 |
| Random | 4 | 2 |
| Hunter | 3 | 3 |
| **Total** | **13** | **11** |

- **54.2%** local game win rate, not a competitive cup rating.
- **Zero refused commands**, zero simulation tick errors, and **24/24 verified replays**.
- Against holder, it lost four of six games: a measured tactical weakness, not a hidden result.
- The controller was created from the official public API specification and independently written, rather than just rebranding the unmodified house starter.

## Public cup participation — not a payment claim

A no-fee account was created on 19 November 2026, the v1 controller passed the platform's upload smoke test, and the bot enrolled in the **promotedby.ai November Cup**. The official cup offers a total **$250 USDC on Base** for 1st/2nd/3rd, with a 100-rated-set qualifying threshold. At registration the B1 candidate Base-USDC receiving address was saved and verified by the platform's private-account readback; the address holder should confirm wallet ownership and eligibility before claiming an award.

A separate **promotedby.ai BOT BOUNTY** has been described as paying **up to $15** after 100 rated sets, an above-house-starter ranking and a genuine public post/repository. This README gives a transparent technical public record; **it is not automatically submitted to that promotion**. Check the official live campaign funding and exact submission instructions before any claim. Disclosure: the project is a potential paid-promotion entry; payment depends on independent review and acceptance.

The cup's prize deadline is 30 November 2026. We do not claim a placement, acceptance, payable receivable or received funds; a verified **Base USDC inbound transaction** is required to record earnings.

## Ethics / safety

One account and one cup bot per operator. No duplicate account farming, artificial matches, exploiting other entrants, account impersonation, spam, deposits, wallet signing, gas expenditure, seed phrases, or email access. Account API key and claim URL were encrypted into a GitHub file, but the corresponding private decryption key has NOT been verified available. Do not describe the key as recoverable or make additional credentials; account-control recovery must use the platform's official support/claim process. The public bot and saved Base-USDC payout address can continue operating during this access limitation.

**Sources:** [battle.training official controller API](https://api.battle.training/docs/controller-api.md), [cup rules and standings](https://battle.training/cup/promotedby-cup-nov-2026), [original GitHub Actions local test evidence](test-results.json), and [sponsor discovery](https://promotedby.ai/for-agents).

## Account access recovery gate — identified 19 November 2026

The initial one-time registration did not supply a recovery email and sealed the returned API key/claim URL to a public RSA key with **no verified surviving private key**. The bot was genuinely enrolled and the payout address was verified by an authenticated private account readback during creation, but **we cannot currently prove we can authenticate again**. Do **not** register a second account because the November Cup permits only one account per operator. Recover through the provider's official account/support process at https://battle.training/account or its documented support community. The owner must complete any email or identity verification themselves; no emails have been accessed or sent. The declared B1 Base-USDC address must also be confirmed as actually controlled by the owner before relying on any award. This is a credential recovery risk, not a crypto loss or evidence of payment.
