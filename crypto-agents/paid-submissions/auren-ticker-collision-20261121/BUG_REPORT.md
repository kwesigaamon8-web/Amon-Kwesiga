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

## New 21 November upstream overlap found — do not misstate novelty

A separately authored AUREN report, [issue #170](https://github.com/Ayush441-python/AUREN/issues/170), was published on 21 November 2026 at 15:40 UTC. It documents duplicate ticker **rows in the browser UI**, causing the request to silently retain only the last value before it reaches the API. ENIGMA's separate reproduced candidate concerns duplicate **canonicalized keys inside the API** (distinct raw names such as `NVDA` and ` nvda `), which also silently overwrite and change exposures with ordering. The mechanisms are different, but the financial symptom and normalization code overlap. **Sponsor may treat the new report as duplicate or already covered; no novelty, payout entitlement or current bounty funding is established.** Before asking the owner to invest submission time, cross-reference #170, seek sponsor clarification on scope/available funds, and avoid implying accepted revenue. No third-party issue was submitted or changed by ENIGMA.

## Duplication and authorization checks
GitHub issue searches for the AUREN repository found **no matching existing issue** for `mixed-case ticker`, `canonical ticker collision`, `whitespace collision`, or `normalized weights overwrite`; this is not an exhaustive guarantee of novelty.

No owner's accounting/tax/audit clients, private records, Gmail/emails, wallet keys, signing or paid infrastructure were accessed. No unauthorized third-party repository write was performed; the attempted issue creation failed and did not publish. Under the owner's ENIGMA receiving policy, payment is a separate matter that can only follow sponsor confirmation and an accepted job, with a correctly verified Base-USDC receiving route.

## Upstream submission route (requires authorized GitHub user access)
[Open AUREN's GitHub issues](https://github.com/Ayush441-python/AUREN/issues) and submit this original report as a `bug` if the sponsor continues accepting bounties. The issue form and GitHub account authorization must be completed by a user/agent with appropriate external repository access. Do not claim a bounty until the maintainer explicitly accepts and a real on-chain payment is independently verified.

## Submission-ready link (requires external GitHub login/authorization)

**[Open the AUREN bug issue with title and evidence prefilled](https://github.com/Ayush441-python/AUREN/issues/new?title=%5BBug%20Bounty%5D%20%2Frisk%20silently%20discards%20colliding%20ticker%20keys%3A%20input%20order%20changes%20exposure&body=Original%20reproducible%20logic%20error%20in%20AUREN%20api.py%3A%20_normalize_and_validate_weights%20uses%20%7Bk.strip().upper()%3A%20v%20for%20k%2Cv%20in%20weights.items()%7D%3B%20distinct%20raw%20ticker%20names%20silently%20collide%20after%20normalization.%0A%0APayload%20A%3A%20%7B%22weights%22%3A%7B%22NVDA%22%3A99%2C%22%20nvda%20%22%3A1%2C%22MSFT%22%3A100%7D%7D%20-%3E%20normalized%20NVDA%200.00990099.%0APayload%20B%3A%20%7B%22weights%22%3A%7B%22%20nvda%20%22%3A1%2C%22NVDA%22%3A99%2C%22MSFT%22%3A100%7D%7D%20-%3E%20normalized%20NVDA%200.49748744.%0AThe%20identical%20raw%20holdings%20in%20different%20key%20order%20produce%20different%20risk%20exposure.%20Expected%3A%20reject%20canonical%20collisions%20with%20HTTP%20400%20or%20document%20a%20stable%20aggregation%20rule.%20The%20silent%20overwrite%20is%20wrong.%0A%0AStandalone%20local%20tests%20(3%20passed)%3A%20https%3A%2F%2Fgithub.com%2Fkwesigaamon8-web%2FAmon-Kwesiga%2Fblob%2Fmain%2Fcrypto-agents%2Fpaid-submissions%2Fauren-ticker-collision-20261121%2Freproduce.py%0AFull%20evidence%20and%20safe%20correction%3A%20https%3A%2F%2Fgithub.com%2Fkwesigaamon8-web%2FAmon-Kwesiga%2Fblob%2Fmain%2Fcrypto-agents%2Fpaid-submissions%2Fauren-ticker-collision-20261121%2FBUG_REPORT.md%0A%0AThis%20is%20original%20AI-assisted%20ENIGMA%20work.%20Please%20confirm%20bounty%20eligibility%2C%20available%20funding%2C%20and%20correct%20Base-USDC%20payment%20terms%3B%20no%20payout%20is%20claimed.)** — review before submitting. The connected GitHub integration tried to open an issue and received **403**, so it has NOT submitted the work. The user must use a GitHub account with permission to open issues in AUREN, or switch to a browser workspace authenticated for that account; this link is not an authorization grant. No emails are involved.

**Funding/payout confidence: LOW / UNVERIFIED.** AUREN publicly advertises a \$400 USDC programme pool, but its main issue search and examined sponsor questions produced no independently verified paid TXID, clear remaining allocation or maintainer acceptance for this specific bug. Do not spend funds or bill a phantom customer based on the advertised range. The sponsor may reject, decline or be unable to pay.
