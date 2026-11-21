# ENIGMA sponsored bug candidate — AUREN ticker normalization collision
**Date:** 2026-11-21 · **Sponsor:** [AUREN](https://github.com/Ayush441-python/AUREN) · **Source checked:** [api.py](https://github.com/Ayush441-python/AUREN/blob/1ec8dba56cb82981fe334da8ed4311c7c4b3632d/api.py) at commit `1ec8dba56cb82981fe334da8ed4311c7c4b3632d`.

## Status
**Original reproducible issue prepared — NOT SUBMITTED to AUREN, NOT ACCEPTED, NOT FUNDED, NOT PAID.** The connected GitHub app returned **403 Resource not accessible by integration** when attempting to create the upstream bug issue. This is an integration permission failure; do not misrepresent GitHub-owner repository publication as a sponsor submission.

Sponsor's [BOUNTY.md](https://github.com/Ayush441-python/AUREN/blob/main/BOUNTY.md) publicly advertises **$10–$50 USDC** for accepted reproducible bug/logic reports, with Base or Ethereum USDC as possible payout. This is an *advertisement only*; no escrow, available allocation, acceptance or historical payout was independently verified. Its guidelines say to open a GitHub issue tagged `bug`, include reproduction and expected versus actual behavior.

## Proposed upstream issue title
`[Bug Bounty] /risk silently discards colliding ticker keys: input ordering changes portfolio exposure`

## Findings
The API's `_normalize_and_validate_weights(weights)` contains:

```python
clean_weights = {k.strip().upper(): v for k, v in weights.items()}
w = pd.Series(clean_weights, dtype=float)
return w / w.sum()
```

Two distinct JSON keys can collide after trimming and case-folding. The later key silently overwrites the earlier one; merely reordering the same key/value entries alters canonical weights.

**Payload A:**
```json
{"weights":{"NVDA":99," nvda ":1,"MSFT":100}}
```

**Payload B (same key/value pairs, different order):**
```json
{"weights":{" nvda ":1,"NVDA":99,"MSFT":100}}
```

Both raw weights total **200**. The current helper silently drops one of the `NVDA` entries:

| Result | A | B |
|---|---:|---:|
| Canonical key/value total before normalization | 101 | 199 |
| Normalized NVDA | 0.009900990099009901 | 0.49748743718592964 |
| Normalized MSFT | 0.9900990099009901 | 0.5025125628140703 |
| Largest holding | ~99.01% | ~50.25% |

This directly corrupts reported `normalized_weights` and resulting concentration/stress values. It is not a duplicated *raw* JSON key—the names differ before normalization.

## Reproduction and regression
[Download/test the standalone reproduction source](./reproduce.py) with `python -m pytest -q reproduce.py` (requires `pandas`). It mirrors the exact normalization statements from the inspected sponsor source; it **does not invoke** the sponsor's hosted API. Local independent test: **3 passed** with pandas 2.2.3. Tests cover order-dependent data loss, rejecting both collision orders, and normal non-colliding tickers.

## Proposed minimum correction
Build the canonical dictionary one entry at a time, **raising HTTP 400 on a collision** before data loss:

```python
clean_weights = {}
for raw_ticker, value in weights.items():
    ticker = raw_ticker.strip().upper()
    if ticker in clean_weights:
        raise HTTPException(
            status_code=400,
            detail=f"Duplicate ticker after normalization: {ticker}",
        )
    clean_weights[ticker] = value
```

Alternatively aggregate aliases only if documented and deliberately supported by the sponsor. In either policy, input order must not change exposure. Regression tests should cover mixed case, whitespace, reversing key order, and ordinary unique portfolios.

## Duplication and authorization checks
GitHub issue searches for the AUREN repository found **no matching existing issue** for `mixed-case ticker`, `canonical ticker collision`, `whitespace collision`, or `normalized weights overwrite`; this is not an exhaustive guarantee of novelty.

No owner's accounting/tax/audit clients, private records, Gmail/emails, wallet keys, signing or paid infrastructure were accessed. No unauthorized third-party repository write was performed; the attempted issue creation failed and did not publish. Under the owner's ENIGMA receiving policy, payment is a separate matter that can only follow sponsor confirmation and an accepted job, with a correctly verified Base-USDC receiving route.

## Upstream submission route (requires authorized GitHub user access)
[Open AUREN's GitHub issues](https://github.com/Ayush441-python/AUREN/issues) and submit this original report as a `bug` if the sponsor continues accepting bounties. The issue form and GitHub account authorization must be completed by a user/agent with appropriate external repository access. Do not claim a bounty until the maintainer explicitly accepts and a real on-chain payment is independently verified.
