# Quote lock trace checker

Original offline prototype for reviewing supplied display-state snapshots. It does not visit a merchant, request a quote, operate a wallet, execute a payment or verify backend behavior.

## Problem and attribution

Another contributor's [public report](https://stacker.news/items/1616549), in the [Hats & Stuff feedback thread](https://stacker.news/items/1616276), describes a review page retaining a locked-price claim after a ten-minute quote expired. The coordinator retrieved that public thread on 18 November 2026. This is **not our finding**, and we have not independently reproduced it on the merchant. This implementation was written from generic trace-checking requirements, uses only synthetic fixtures, and is not a submission to that bounty.

## Buyer hypothesis and existing alternatives

Possible buyers are small Bitcoin merchants whose checkout uses expiring quotes. The spend trigger is a checkout release or a report that displayed price-lock status and quote lifetime disagree. The named market signal is Hats & Stuff's request for useful shop feedback; its competitive 57,000-sat prize is not an agreement with us, and other contributors have already reported the motivating issue. We will not submit a duplicate report.

An indicative future pilot would review one buyer-supplied, authorized trace for **10,000 sats**, with scope and acceptance agreed before work. This is a pricing hypothesis, not a sent or accepted quote. Bitcoin-mainnet payout willingness is unconfirmed; Lightning cannot pay the owner's approved mainnet addresses directly. No paid engagement is claimed.

Existing alternatives already do much of the work. [Playwright Clock](https://playwright.dev/docs/clock) simulates time and timers within browser tests. [Lighthouse](https://developer.chrome.com/docs/lighthouse/overview) runs broad web-quality audits. This small checker adds a portable, offline interpretation of explicitly supplied quote-state observations, including unknown expiry and missing post-expiry coverage. It is not a replacement for those tools or a claim of absolute novelty.

## Run

Python standard library only:

```sh
python quote_lock_trace.py example.json
python -m unittest -v test_quote_lock_trace.py
```

Validation on 18 November 2026: 17 unit tests passed. The synthetic example returned `REVIEW`, including its exact-expiry claim and unknown-expiry sample. Tests cover timezone equivalence, the expiry boundary, absent coverage, inconsistent expiry, malformed input, input limits and unchanged input data.

The CLI accepts one local UTF-8 JSON file, at most 1 MiB, containing only a `snapshots` array with at most 1,000 entries. Each entry requires:

- `quote_id`: same nonempty identifier throughout, at most 128 characters.
- `observed_at`: ISO timestamp with seconds and explicit `Z` or numeric timezone offset.
- `expires_at`: timestamp in the same format, or JSON `null` when unknown.
- `locked_claim_visible` and `pay_button_enabled`: JSON booleans. Null or missing display facts are rejected, not treated as false.

Observations must increase strictly in absolute time. Equivalent UTC instants count as duplicates. Known expiry instants must agree throughout the quote; a changed quote or changed known expiry requires a separate trace. Unknown expiry is not backfilled from another snapshot. Duplicate JSON keys, malformed timestamps, naive timestamps and unexpected fields are rejected. Invalid inputs exit with code 2; valid reports exit with code 0 regardless of report status.

## Meaning of reports

- `REVIEW`: a supplied snapshot at or after known expiry contains a visible locked claim or an enabled pay button. These are separate flags. An enabled button does **not** prove that a backend accepted payment.
- `UNKNOWN`: no review flag was observed, but expiry is unknown in at least one sample, the trace is empty, or no sample reaches known expiry.
- `PASS`: at least one sample reaches known expiry, all expiry facts are known, and neither selected flag is present in those samples. This is a limited trace result, **not** a security, payment, freshness or continuous-behavior assurance.

`has_unknown_expiry` retains missing-expiry information even when the overall result is `REVIEW`. `at_or_after_expiry_observed` separately records coverage. Output omits quote identifiers and raw page contents, but callers must still use only authorized data and review metadata before publication.

The included example returns `REVIEW`: its second snapshot hits the exact expiry boundary with a locked claim; its third snapshot has unknown expiry. Everything in that file is synthetic.

## Limits

The checker trusts the supplied clocks and observations. It cannot detect missed transitions between samples, clock skew, false observations, backend quote refresh, actual price changes, endpoint acceptance, purchase success or a vulnerability. It does not render HTML or inspect a live site. A genuine commercial review would require agreed scope, authorized observations and an independent buyer; this prototype is not commissioned or accepted work.
