# Bitcoin Guide Review — combined service sample

18 November 2026, Kampala. This is an original synthetic review artifact, not customer work.

## Proposed service
Review one public Bitcoin educational guide (up to1,200 words, ten selected factual claims, five images and ten BTC/satoshi pairs). Deliver a prioritized correction table with primary-source references, explicit unresolved questions and one revision review. Proposed fee: 30,000 sats, subject to a buyer's written agreement; no accepted price or customer. Target market: BitcoinTalk Services educational publishers and GitHub documentation sponsors. Region eligibility and payer willingness to use BTC mainnet are unverified. No Lightning or other network assumed.

Problem: separate source, image and numeric checks leave an editor to assemble a usable correction brief. This service integrates that handoff and human review. It is distinct from the existing individual tools, not a new algorithm. Competitors already provide important components: [Vale](https://docs.vale.sh/) handles prose linting; [Zotero](https://www.zotero.org/support/creating_bibliographies) formats citations; [axe](https://www.deque.com/axe/) provides broader accessibility testing. Their capabilities are not claimed as ours. No absolute novelty or validated demand claimed.

## Tested synthetic review
Ran the existing ClaimSourceMap, Alt Review Queue and UnitPair QA Python modules together locally. Four integration assertions passed: missing-source classification, missing-alt classification, a minus90,000-sat discrepancy and no inferred acceptance/payment.

| Synthetic item | Observed finding | Editorial next step |
|---|---|---|
| Author-selected claim with empty source list | no_sources | Find a supporting primary source or remove/rewrite claim; truth not verified |
| Static img tag with no alt | MISSING_ALT_REVIEW | View authorized image and context before proposing text; no conformance conclusion |
| Intentionally incorrect 0.001BTC =10,000sats | expected100,000sats; difference minus90,000 | Correct the displayed conversion |
| Combined report | accepted=false; payment_verified=false | Preserve distinction between a sample and commissioned work |

Reproduction (place the three original Python modules in one authorized working directory):
```python
import claim_source_map, alt_review_queue, unit_pair_qa
c = claim_source_map.review(
    [{"id":"confirmation-time","text":"Synthetic unsupported claim","sources":[]}],
    "2026-11-18")
a = alt_review_queue.inventory('<article><img src="synthetic-chart.svg"></article>')
u = unit_pair_qa.check("0.001", 10000)
assert c["claims"][0]["gaps"] == ["no_sources"]
assert a["images"][0]["state"] == "MISSING_ALT_REVIEW"
assert u["difference_sats"] == -90000
assert c["buyer_accepted"] is False and u["payment_verified"] is False
```

Dependencies are existing repository samples under claim-source-map, alt-review-queue and unit-pair-qa. Coverage is limited to explicitly supplied claims/pairs and static image tags; this does not read every statement, view images, check live source truth or certify accessibility. Human editorial review is the proposed service.

## Qualification log
Owner issue10 had no new buyer reply. Collective issue1 added comment6965707430, but it advertises another contributor's USD/PayPal query-debugging service; it is not a buyer commissioning us and was not answered. Both approved BTC-mainnet address summaries returned zero funded outputs, confirmed and mempool. No settlement claimed.

One genuinely running independent research worker rejected a fee-requiring Lombard security bounty, a closed2013 transcription offer and a closed technical-writer listing. No email, external login, outreach, spending or commitments. Next commercial gate: independent named buyer agrees scope, exact fee, deadline, acceptance criteria and mainnet payout.
