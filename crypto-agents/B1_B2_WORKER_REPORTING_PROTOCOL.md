# B1/B2 operational reporting protocol — 20 November 2026

## What is implemented
Two actual scheduled Python worker pipelines now call `b_worker_intelligence_router.py` **after** their per-company hierarchical worker evidence aggregation. The code is in `crypto-agents/b_worker_intelligence_router.py`; isolated unit tests are in `crypto-agents/test_b_worker_intelligence_router.py`.

A normal run creates under `b1b2-intelligence/<source-fleet>/`:
- `ALL_VALID_ATTEMPTS.json` — each validated attempt, source worker identity, actual checked output status, direct-parent chain, evidence URLs, defects and next actions.
- `B1_INBOX.json` and `B1_INBOX.md` — B1 market and sales-action priority queue.
- `B2_INBOX.json` and `B2_INBOX.md` — B2 technical defects and test-action priority queue.
- `CHIEF_D_STATUS.json` — fleet-specific summary of attempted reports, breakdown, rejected identities and truth flags.

Both inboxes are shared as GitHub Actions artifacts and Markdown job summaries. The two fleet workflows have separate schedules and must not add their workers together as a single instantaneous active population.

## Actual message path (software, not fictitious model acknowledgements)

`executed H/G/S/W → parent S/G/W/manager → director → local B1 or B2 → Chief D`.

A worker report that includes a validated public research source is actionable to B1 only after independent buyer/terms/eligibility checks. Execution failures or missing evidence are actionable to B2. Each B receives its own company's reports plus cross-specialty reports from the other company when the relevant pipeline runs.

**A GitHub file is an inbox delivery artifact, not proof of Moltbook API access, reading, a manager's model acknowledgment, a real external publication, a sale or a crypto deposit.** This new system does not yet automatically send a message to a Moltbook account or issue a follow-up command to every lower-tier role. Those require functioning connected API credentials and genuinely executed tasks.

## Minimum worker report fields
1. Unique fleet-prefixed role identity and direct parent.
2. Actual process/model completion status and strict quality grade.
3. Original public source URL (if any) with no payer-validation claims.
4. Clearly stated next action and blockers.
5. Software-validated escalation path.
6. Recorded run/artifact link where available.
7. Explicit NOT VERIFIED or NOT ASSESSED for customer acceptance and monetary settlement unless checked with independent evidence outside this router.

## B1 must decide
Is this a genuine prospective buyer, permitted distribution route, valuable localized product introduction, or a false lead? Assign a narrow next action with evidence and prevent duplicate outreach. No emails, cold DMs, spam or unauthenticated automated posts.

## B2 must decide
Which defect can be reproduced and tested, whether a promised feature is really implemented, whether the public demo passes checks, and what code change can produce a better paid deliverable? No claim of shipped work without evidence.

## Chief D must decide
How many real executions were attempted and completed, what items are blocked, what prospect is ready for an authorized offer, whether accepted work exists, and whether a real transaction or valid payment document proves revenue. Neither role IDs nor unverified candidate URLs are sales.

## How to find reports
- [B1 real worker actions](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/real-ai-workers.yml)
- [B2 real worker actions](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/bountyscoutai-real-ai-workers.yml)
- [Lightweight routing CI](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/b1b2-intelligence-reporting-tests.yml)
- [B1/B2 joint mission room](https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/9)

Open a completed real-worker run, view the Markdown job summary, then download the artifact `b1b2-intelligence-transferexperiment` or `b1b2-intelligence-BountyScoutAI`. If there are zero executed worker reports in that run, the inboxes correctly say zero.

## Performance and scaling
Each company defines **375,188,632,680** virtual roles, totaling **750,377,265,360**, plus the separate Chief D definition. These counts are an addressable organizational hierarchy, **not real simultaneously active agents**. A true live worker count must be supported by an actual execution window, inference receipt and work artifact.

This design scales by processing **only actual reports** each run; it does not create billions of empty JSON files, thousands of accounts, excessive paid inference calls, or external messages. Add persistent queue, actual model acknowledgements, controlled task leasing and intake signatures before claiming end-to-end autonomous agent work.

## Safety and authority
- No email account use or sending is authorized.
- No wallet signing, payment transfer or account-secret publishing.
- Do not create misleading social posts or pretend inactive roles are operational.
- All external publications require actual platform authorization and relevance.
- Never treat public-source URLs as paying customers.
