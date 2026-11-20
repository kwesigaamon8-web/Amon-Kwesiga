# B1/B2 Worldwide Task-to-Payment Factory

**Installed:** 20 November 2026.  
**Human objective:** find actual useful tasks worldwide, build original work, independently test, report to a real customer, submit only through an authorized route, request payment to approved B1/B2 receiving addresses, and verify the incoming transaction.

## Actual code, runs and work evidence

| Component | Actual implementation | Boundary |
| --- | --- | --- |
| Open-source task discovery | [world_work_factory.py](../world_work_factory.py) | Reads a bounded third-party index; verifies original GitHub issues and latest available comments; cannot verify a funded client by title alone |
| Current source queue | [discovery.json](./discovery.json) | **34 discovered / 34 original GitHub issue checks**, no source proved all payment eligibility gates |
| Qualification report | [REPORT.md](./REPORT.md) | Rejects non-submittable mirrors; holds old, crowded, unfunded, wrong-asset or sponsor-unconfirmed tasks |
| Original deliverable creation | [invoice-payment reconciliation](../commercial-work/invoice-payment-reconciliation/reconcile.py) | Generates a truthful demonstration on *fictional* invoice/payment records, not a claimed client order |
| Executed tests and report | [synthetic example](./deliverables/invoice-reconciliation-synthetic-example/) | Existing original reconciliation unit tests actually run, sample report and digest retained |
| Accepted job + payable BTC gate | [world_work_payer_gate.py](../world_work_payer_gate.py) | Fetches real original issuer's acceptance comment; composes *unsent* BTC-mainnet request; two independent explorer transactions and independently checked issuer payment statement required |
| Source and model workers | [shared hierarchy](../hierarchy_command_core.py) | Real invoked workers must verify original owner/parent; 11.25 trillion are only virtual address slots |
| Repeatable bounded shift | [GitHub Actions worldwide task factory](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/chief-d-world-task-factory.yml) | Every four hours; sources may become inaccessible or unrelated tasks may remain unverified |

**Independently executed passing run:** [#44800022602](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44800022602), 20 Nov 2026 19:13 UTC. It checked **34/34 original GitHub issues** from a public index, passed source checks and the original sample work tests, generated production-report evidence, and showed **zero verified eligible funded tasks** with compatible native BTC payment, **zero external submissions**, **zero sponsor acceptances** and **zero new earned BTC**. The discovery feed covers a finite snapshot; it cannot represent *all work needed on Earth*.

## Required audited work states

1. **DISCOVERED:** original task URL and issuer found; only a prospect, not yet accepted or funded.
2. **ORIGINAL_SOURCE_CHECKED:** issuer's source/terms verified, current comments screened and contribution restrictions checked. Still *no guarantee of funding*.
3. **FUNDED_ELIGIBLE:** verify issuer's available budget or escrow and Uganda eligibility; compatible payment rail and approved owner receiving address; no access/spending fee and no unsafe prompt/credential disclosure.
4. **SCOPE_ACCEPTED:** preserve original issuer's specific acceptance criteria, amount, delivery format, exact GitHub issue/claim and actual authorization to undertake the work.
5. **DELIVERABLE_TESTED:** create substantive original source/analysis/software, run reproducible tests, store immutable commit SHA/checksum and report with honest limitations.
6. **SUBMITTED_VERIFIED:** use only the actual permitted authenticated platform; retain platform-provided PR/issue/submission URL. **Do not count local draft reports or one's own marketing issues as customer submissions.**
7. **SPONSOR_ACCEPTED:** source-check the buyer/maintainer's documented acceptance or merge. No fee is earned just because code or a report exists.
8. **PAYMENT_REQUEST_CONFIRMED:** after sponsor accepts, use [world_work_payer_gate.py](../world_work_payer_gate.py) to verify the original issuer and *exact agreed satoshis* and create a request. Post it only once through a legitimate, authorized platform and record the real comment URL, **not email**.
9. **ONCHAIN_PAYMENT_VERIFIED:** two independent BTC explorers confirm the identical mainnet TXID paid to the correct B1/B2 address, with the issuer's authentic matching payment statement and accepted deliverable. Do not infer who sent BTC from a wallet balance alone.

## Available BTC mainnet payment destinations

**B1 / transferexperiment:** `bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z`  
**B2 / BountyScoutAI:** `bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9`

Both pass the official Bitcoin Bech32 checksum code in this repo. Payer must use **native Bitcoin mainnet**, not Lightning, testnet, Stacks/sBTC or Base/EVM USDC for those destinations. Payment amount must be agreed *before* the payment request. Other network addresses remain on hold until exact chain, asset and owner receipt capability are reverified.

## Actual source examples — investigate, not automatically submit

- [IES-BoilerRoom HTTP/2 bounty](https://github.com/IES-BoilerRoom/grpc-http2-hpack-framing/issues/2) advertises USDC but **explicitly refuses unsolicited human/manual PRs**: REJECT.
- [Fractal-Neurons 3-year protocol forensic task](https://github.com/Fractal-Neurons/pacta/issues/118) advertises two $20 Base-USDC human-researcher slots, requires demanding original dated on-chain evidence and successful maintainer replay. **Not a BTC mainnet payment; not an accepted task for these workers**.
- [Claude Builders change-log bounty #1](https://github.com/claude-builders-bounty/claude-builders-bounty/issues/1) has thousands of comments and competing solutions. Issuer's automated payout language conflicts with [Opire's official payments rules](https://docs.opire.dev/rewards/pricing), which state that bounty creators arrange payment directly after review. **HOLD** until payer/claim/payout are independently confirmed.
- [Bounty Radar public original-source index](https://muhib-karim.github.io/bounty-radar/bounties.json): useful *discovery*, not confirmation of available money.
- [AIBTC active bounty board](https://aibtc.com/bounties): often pays **sBTC on Stacks**, which is not the native Bitcoin mainnet receiving format for B1/B2; hold until any separately authorized compatible settlement path is proven.

## Responsibility and reporting

**Chief D:** decide genuine buyer-facing task priority; reject unfunded work; review signed acceptance and receipt evidence.  
**B1/B2 directors:** independently inspect country/sector source and sponsor eligibility; avoid duplicate claims.  
**Assistants/managers:** assign *actual bounded live processes* only where funded, eligible scope is confirmed.  
**Worker tiers:** write original work and reproducible test; archive source links and result hashes; stop on authentication or funding blockers.  
**Payment verification:** separate local build success from actual buyer contract, submission, acceptance, and on-chain BTC receipt.

Each shift report must say: **source checked → real deliverable completed → authenticated submission → sponsor accepted → payment requested → on-chain amount verified**, with numbers and URLs. Missing evidence = **NOT VERIFIED**, never an invented zero-fee contract or fake payment.

No unauthorized account creation, unsolicited mass outreach, email read/search/draft/send, private keys, outgoing wallet transfers, paid cloud services, hidden-network exploitation or use of strangers' compute. Public research and original test work only. A genuine customer can decline work or payment; no algorithm can force a buyer to pay.
