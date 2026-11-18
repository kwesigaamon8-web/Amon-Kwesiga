# AUREN bug-bounty submission — four contradictory threshold explanations

**Submission status:** NOT SUBMITTED to upstream. Authenticated external write attempt on 18 November 2026 failed with HTTP 403 `Resource not accessible by integration`. This is a ready-to-submit original bug report, not a paid contract.

**Proposed upstream destination:** https://github.com/Ayush441-python/AUREN/issues/new

**Title:** `[Bug Bounty] Four risk-score warnings contradict their own percentage thresholds after rounding`

## Summary

In `engine/score.py::risk_score`, comparisons use unrounded floating-point values but four displayed explanations use Python's `:.0%` formatter. A value just across a strict threshold is shown *as if it equals the threshold*, while the explanatory sentence says the limit was exceeded. The numerical score itself is computed as designed; this is a diagnostic fidelity bug, not an erroneous scoring claim.

**Upstream revision:** `eef89475dece13ad243c6fc83d06f0ae1d1b0882`.

## Exact reproduction

```python
from engine.score import risk_score

conc = {"top_weight": 0.304, "effective_assets": 5.0}
score, level, hits = risk_score(conc, vol=0.304, mdd=-0.304,
                                pairs=[], sector_max=0.504)
print(score, level)
for _, reason in hits:
    print(reason)

# Negative controls: exact thresholds do not trigger these rules.
print(risk_score({"top_weight": 0.30, "effective_assets": 5.0},
                 vol=0.30, mdd=-0.30, pairs=[], sector_max=0.50))
```

Actual output:

```text
70 High
Largest holding is 30% (over 30%)
Volatility is 30% a year (over 30%)
Worst past fall was -30% (deeper than -30%)
50% sits in one sector
(0, 'Low', [])
```

The actual values are **30.4%**, **30.4%**, **-30.4%** and **50.4%**. The emitted messages visually erase the amount by which four independent thresholds were crossed.

## Expected

Preserve the existing true/false thresholds and points, but include enough decimal precision to make a crossed threshold visibly distinct; for values extremely close to a limit, show more precision, or explicitly label it rounded. Regression tests should include 0.4 and 0.04 percentage point over-boundary cases, plus equal-threshold negative controls.

## Actual, independently tested evidence

- Reproducer: https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/paid-work/auren-risk-threshold-repro.py
- GitHub Actions upstream-pinned source execution: https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44300605113 — **success**
- Existing upstream reference: https://github.com/Ayush441-python/AUREN/blob/eef89475dece13ad243c6fc83d06f0ae1d1b0882/engine/score.py
- Relevant prior issue #39 is about rounded correlation values, not these four `risk_score` reasons.

This report is AI-assisted under the upstream `BOUNTY.MD` Bug Bounty category. It makes no claim of priority, approval, award, reward amount or payment. No wallet signing, spending, credentials or emails used.

## Submission blocker and recovery

The connected GitHub app is allowed to write to the owner's repository, but the attempt to create a public issue in `Ayush441-python/AUREN` returned HTTP 403. Do not reattempt unchanged credentials. An authenticated GitHub session with issue-creation permission on the upstream repository would be required to publish this report there; until then the report is fully prepared but not received by the sponsor.
