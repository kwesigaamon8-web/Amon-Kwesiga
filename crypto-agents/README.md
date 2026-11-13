# Free cloud research fleet — 10 directors and 20 assistants

Thirty independent role-based GitHub Actions research workers are scheduled daily on the connected public repository. Each of the ten directors has exactly two assistants (A and B), and all workers have separate missions and output JSON artifacts.

Workflow: `.github/workflows/crypto-directors.yml`
- `agents.py`: each independent worker searches public leads, saves a source-linked JSON report, and attempts a free open-weight small-model review.
- `consolidate.py`: combines 30 reports, excludes weak/old/unsubstantiated search hits, and preserves the distinction between leads and income.
- `director_review.py`: creates a separate director accountability report from each director's own report and the reports of its two assistants. Director D10 additionally reports fleet-wide mission compliance.
- `director-reports/INDEX.md`: downloadable in the consolidated artifact, summarises the 10 director teams.

Each run creates `crypto-research-ROLE` artifacts and one `consolidated-opportunity-report` artifact with `summary.json`, `summary.md` and ten per-director reports.

**Mission:** Find legitimate worldwide paid work potentially yielding transferable BTC, USDC or conventional payments. Prioritise accounting, bookkeeping, QuickBooks, tax, remote contracting, open-source bounties and agent opportunities. **Actual verified earnings, not searches, are the goal.**

**Limitations:** These are independent scheduled research jobs, not separate Moltbook accounts, and cannot apply, sign, negotiate, post or collect payments by themselves. Leads are unverified and require payer, scope, Uganda eligibility, payout method, and authenticity checks. This workflow never asks for seed phrases, signs transactions, handles private keys, makes payments, or claims that a wallet has received funds. No paid service is required by the code; cloud runtime remains subject to the hosting platform's free-tier and policy limits.
