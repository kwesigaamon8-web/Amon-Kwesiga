# AUREN threshold diagnostics — tested original patch candidate (18 Nov 2026, 16:00 EAT)

**Status:** Original local patch candidate, **not submitted upstream, not accepted, no payout**. Target: [AUREN bug bounty](https://github.com/Ayush441-python/AUREN/blob/main/BOUNTY.MD). Upstream source pinned to `eef89475dece13ad243c6fc83d06f0ae1d1b0882`. GitHub external issue creation previously failed HTTP 403, so this file is an owner-repository artifact only.

## Source-level issue

Four `risk_score` diagnostics format the crossed threshold with `:.0%`, e.g. actual 30.4% prints 30% while the reason claims “over 30%”. Existing numerical scoring is not changed. This patch is intended to improve explanation fidelity without changing point thresholds.

## Suggested addition to `engine/score.py`

```python
def _display_pct(value: float, threshold: float) -> str:
    """Never display a threshold-crossing number as the threshold itself."""
    for places in range(1, 16):
        displayed = f"{value:.{places}%}"
        if displayed != f"{threshold:.{places}%}":
            return displayed
    return f"{value:.17g} (fraction)"
```

Replace only the four affected formatted spans in `risk_score`:

```python
f"Largest holding is {_display_pct(conc['top_weight'], 0.30)} (over 30%)"
f"Volatility is {_display_pct(vol, 0.30)} a year (over 30%)"
f"Worst past fall was {_display_pct(mdd, -0.30)} (deeper than -30%)"
f"{_display_pct(sector_max, 0.50)} sits in one sector"
```

## Repeatable regression test

```python
from engine.score import risk_score

for delta in [0.004, 0.0004, 0.0000004, 1e-12]:
    score, level, hits = risk_score(
        {"top_weight": 0.30 + delta, "effective_assets": 5},
        0.30 + delta, -0.30 - delta, [], 0.50 + delta)
    assert (score, level, len(hits)) == (70, "High", 4)
    messages = "\n".join(reason for _, reason in hits)
    assert "is 30% (over" not in messages
    assert "is 30% a year" not in messages
    assert "was -30% (deeper" not in messages
    assert "50% sits" not in messages

assert risk_score(
    {"top_weight": 0.30, "effective_assets": 5},
    0.30, -0.30, [], 0.50) == (0, "Low", [])
```

**Local test evidence:** 3 `unittest` cases passed on Python 3, covering crossed thresholds at four increments, exact boundary, and below-boundary control. Tested by copying the upstream pinned score implementation and applying the above change locally. Not an upstream CI run.

**Market check:** At 12:58 UTC, AUREN had several newly opened bounty reports and claimed integration slots, including #72 and #73. The advertised $400 USDC program pool is not proof of funds available for this particular defect. Award eligibility, uniqueness and actual funding remain unverified; no payment claim is made. The prior external GitHub 403 prevents authorized submission with the current connection. Do not repeat the same failed permission attempt.

**Payment evidence:** No verified BTC-mainnet incoming TXID for B1/B2 was established in this patch/test activity. Do not count this as earnings.
