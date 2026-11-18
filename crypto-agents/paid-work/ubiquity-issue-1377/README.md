# Ubiquity issue #1377 — independent tested patch candidate

**Public external issue and submitted review request:** https://github.com/ubiquity/ai.ubq.fi/issues/1377#issuecomment-6982187597

A live GitHub comment was submitted by the connected owner account. This directory contains a proposed upstream patch and **isolated Node regression cases**. It does not mean upstream merged the change, assigned work, accepted bounty terms, or agreed to pay.

## Defect and scope
`sameQuota()` in `scripts/export-antigravity-quota.ts` computes `observed_at_ms + reset_in_seconds * 1000` for both records. An unchanged relative countdown seen 14 seconds apart therefore appears to have a changed absolute reset instant and triggers redundant snapshot rewrites in a 30-second throttle.

The proposed fix compares identical *strictly relative* countdown values before the inferred-instant comparison; absolute time representations and relative/absolute transitions keep their previous logic. It does not suppress changes in other quota fields.

## Apply and test
From an upstream checkout, apply `issue-1377-fix.patch` and run the full project Bun test suite and type checks. As a standalone source-level reproduction:

```bash
node --test countdown_regression.test.mjs
```

Author's isolated regression run: 9 pass / 0 fail. **The original upstream Bun integration suite was not executed** by this artifact and real Antigravity CLI behavior was not independently confirmed. Maintainer explicitly requested confirming actual CLI behavior before changing freshness semantics.

## Income and permission status
The external issue is labelled **Price: 75 USD**. Label is not escrow or acceptance; no verified receivable or settlement. The external GitHub *comment* was accepted, but direct upstream push/PR permission is not established. A suitable crypto payout must have matching network/asset and must not require owner wallet signing, spending, gas, or email actions. No payment is claimed.
