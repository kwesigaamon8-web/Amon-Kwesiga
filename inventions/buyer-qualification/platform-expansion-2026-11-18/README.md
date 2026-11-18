# Paid-work channels beyond GitHub: payment and access evidence

Reviewed 18 November 2026. This public-source work sample checks whether a contractor restricted to native Bitcoin mainnet can actually pursue a listing. It does not endorse platforms, verify their solvency, or claim an awarded job. No applications, account registrations, messages, wallet operations or payments occurred in this review.

The useful distinction is between **a code host**, **a buyer's advertised job**, **a compatible payment method**, and **an accepted paid engagement**. None establishes the next by itself.

| Channel | Evidence found | Native BTC-mainnet fit | Current decision |
|---|---|---|---|
| GitLab | A public query for open `Bounty`-labelled issues in `gitlab-org/gitlab` returned no rows; a label lookup required authentication. | Sponsor-specific; not established. | Keep project-specific discovery available. One empty filtered query says nothing about all GitLab projects. |
| Codeberg | Official documentation offers free account use subject to its terms and free-software mission. | No funded sponsor identified. | Potential collaboration venue; not a paid-work award. Repository access was not available through the search tool. |
| chainjobs | Two writing listings were inspected. Its FAQ describes direct negotiated settlement, zero commission and free applications. | Possible only if a buyer explicitly agrees; reviewed listings advertise USDC or bank transfer. | Prospects only. Application is private and requires sign-in; authenticated access was not established. |
| Bitlance | Official work page specifies settlement to a Lightning wallet. The live job list reported a loading error. | Lightning is distinct from mainnet BTC. | Do not submit a mainnet address as a Lightning receiving route. |
| HackerOne | Official payment documentation supports direct BTC-wallet payouts, including Legacy and BECH32, with a US$15 crypto minimum. | Payment format is a plausible fit; no accepted award exists. | Account setup and the published claim flow involve email. Identity verification and an approved tax form are also required. No permitted claim route established in this review. |
| LaborX | Detailed FAQ lists WBTC on Ethereum and BTCB on BNB Chain; it states a 10% freelancer fee. | Wrapped tokens are not native BTC. | Hold. Premium marketing differs from the detailed fee wording, so do not assume fee-free use. |

## Two published job listings, neither yet qualified

| Buyer handle | Listing and advertised fee | Evidence still needed |
|---|---|---|
| `pushpendra12jxops` | [Crypto Education Hub writing listing](https://chainjobs.app/jobs/637c25f7-a9c1-49cb-841f-ef76b565ebec), 30–50 USDC/project; posted 12 November, visible until 12 December 2026. | Buyer authenticity and funding, an exact deliverable and deadline, acceptance criteria, native-mainnet payment agreement, and an authorized application route. |
| `maisha` | [Web3 Content Creator](https://chainjobs.app/jobs/daccde86-c787-4e29-b7be-d537c024820a), negotiable weekly budget with USDC or bank transfer; posted 11 November, visible until 11 December 2026. | Same gates, plus a materially more specific scope. |

The board says it does not handle or verify payments. Its reviews can reflect a chat without a completed job, so a review alone is not proof that a buyer paid someone. Neither listing has been contacted or commissioned here.

## Sources and reproducibility

- [GitLab filtered public issue query](https://gitlab.com/api/v4/projects/gitlab-org%2Fgitlab/issues?labels=Bounty&state=opened&per_page=10): a deliberately narrow snapshot, not a global search.
- [GitLab historical handbook proposal](https://gitlab.com/gitlab-com/content-sites/handbook/-/merge_requests/7174): background on sponsor-specific bounty arrangements, not current funding evidence.
- [Codeberg official FAQ](https://docs.codeberg.org/getting-started/faq/).
- [chainjobs official payment, applications and review FAQ](https://chainjobs.app/how-it-works).
- [Bitlance official work page](https://www.bitlance.work/findwork?category=admin).
- [HackerOne payment preferences](https://docs.hackerone.com/en/articles/8395720-payment-preferences), [account setup](https://docs.hackerone.com/en/articles/8365247-create-an-account), and [payment FAQ](https://docs.hackerone.com/en/articles/8399426-payment-faqs). Exact current net payout deductions remain unverified; do not infer them from an older FAQ.
- [LaborX official payment and fee FAQ](https://laborx.com/).

`platform-evidence.json` records the observations, URLs, unknowns and prospect status in machine-readable form. Reopen the sources before applying: listings and terms change. No region eligibility has been confirmed for a particular applicant.

## Service hypothesis and competing alternatives

Possible buyer: a small remote-work community or contractor who needs a short list compatible with a specific receiving network and application constraint. Spend trigger: otherwise spending hours applying to listings that cannot actually pay through the permitted route.

Proposed, unagreed pilot: **10,000 sats** for a source-cited review of three requested platforms and up to five live listings, with unknowns explicitly retained. This is a pricing hypothesis, not an accepted offer or invoice. A real buyer would first need to agree scope, deadline, acceptance criteria and BTC-mainnet payment terms. No outbound offer was sent for this sample.

General alternatives include marketplace search filters and platform comparison articles, such as [Spark's freelancer payment comparison](https://www.spark.money/tools/bitcoin-freelancer-payment-comparison). This sample's narrower value is checking the specific listing, actual payment network and permitted application path together. It does not claim a new category of product or absolute novelty. It also does not replace the repository's existing bounty acceptance gate: this is a researched dataset and report, not another gate implementation.

Validation: primary pages and two individual listings were inspected; a separate reviewer checked HackerOne and LaborX. The JSON is checked for unique platforms, required source URLs, explicit unknowns and consistency with the zero-action/zero-award record. This is evidence about the review process, not proof of platform safety, buyer acceptance or payment.
