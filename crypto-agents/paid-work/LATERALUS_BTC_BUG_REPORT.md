# Lateralus high-signal bug report — quoted boolean words in LQL
**Status: prepared for maintainer submission, not submitted or accepted.**

## Bounty
- Upstream policy: https://github.com/bad-antics/lateralus-lang/blob/main/BOUNTIES.md
- Published recurring amount: $10 for an accepted high-signal bug report, subject to maintainer review and one-per-person-per-quarter rule
- Policy permits BTC/LN; do not assume a payment or acceptance
- Submission obstacle: current owner's connected GitHub app was denied issue-creation rights for the upstream repository (HTTP 403)

## Pinned evidence
- Upstream commit: `d078809df3f5db544b7efa7b0979c7a43ebb25e6`
- Upstream module: https://github.com/bad-antics/lateralus-lang/blob/d078809df3f5db544b7efa7b0979c7a43ebb25e6/lateralus_lang/query_engine.py
- Self-contained read-only reproduction script: [reproduce_lateralus_quoted_boolean.py](reproduce_lateralus_quoted_boolean.py)
- Runner: https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/b-paid-bug-evidence.yml
- Note: Run completion has not yet been independently inspected. The source itself proves a likely defect but unexecuted tests must not be called passing.

## Issue title
`[bounty] bug-report: LQL WHERE splits AND inside a quoted string literal`

## Reproduction
From an upstream checkout at the pinned commit:

```python
from lateralus_lang.query_engine import Query, lql

users = [
    {"status": "Research AND Development", "id": 1},
    {"status": "Operations", "id": 2},
]
print(Query().from_(users).where(
    lambda row: row["status"] == "Research AND Development"
).select("status").execute())
print(lql(
    "SELECT status FROM users WHERE status == 'Research AND Development'",
    {"users": users},
))
```

Both interfaces should return `[{'status': 'Research AND Development'}]`.

The current `_parse_condition()` checks whether `" AND "` appears anywhere in the expression, then uses `re.split(r'\bAND\b', expr, flags=re.IGNORECASE)`. It does this before recognizing quoted values, so `'Research AND Development'` is wrongly treated as two boolean clauses. The same risk exists for `'A OR B'`.

## Consequences
A user of the string-based LQL interface can silently receive wrong results for normal records containing words such as `AND` or `OR` in quoted field values, which can matter for filtering accounting or operational records.

## Suggested acceptance checks
1. Equality for a quoted `AND` value returns the matching row.
2. Equality for a quoted `OR` value returns the matching row.
3. Actual unquoted `AND` and `OR` clauses still work.
4. Escaped quotes and parentheses do not break parsing.

A fix should split boolean operators only outside quoted string values, with correct precedence. This report does not claim an upstream patch or maintainer acceptance.

## Payment request after acceptance
Please confirm whether this new report meets the micro-bounty requirements and whether BTC mainnet is an accepted payout route. The owner's published **receive-only B1 BTC mainnet** address is `bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z`. No upfront fees, wallet signing, or outbound transfers are authorized.

**Financial state: payout unconfirmed; on-chain incoming amount not established.**
