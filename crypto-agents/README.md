# Free cloud research fleet — 10 directors and 20 assistants

Thirty independent role-based GitHub Actions research workers are scheduled hourly on the connected public repository (cron at minute 31, subject to GitHub scheduling availability and concurrency control). Each of the ten directors has exactly two assistants (A and B), and all workers have separate missions and output JSON artifacts.

Workflow: `.github/workflows/crypto-directors.yml`
- `social_scan.py`: publicly searchable Bluesky posts and Reddit discussions for paid job requests, bounties and client leads; unauthenticated, read-only and subject to provider availability.
- Social requests never post, message, follow users, or advertise wallet addresses. Social results are unverified leads requiring direct-source confirmation.
- Scheduling is periodic, not true nonstop execution; if a previous run remains active, concurrency cancels stale overlapping checks.
- `agents.py`: each independent worker searches public leads, saves a source-linked JSON report, and attempts a free open-weight small-model review.
- `consolidate.py`: combines 30 reports, excludes weak/old/unsubstantiated search hits, and preserves the distinction between leads and income.
- `director_review.py`: creates a separate director accountability report from each director's own report and the reports of its two assistants. Director D10 additionally reports fleet-wide mission compliance.
- `director-reports/INDEX.md`: downloadable in the consolidated artifact, summarises the 10 director teams.

Each run creates `crypto-research-ROLE` artifacts and one `consolidated-opportunity-report` artifact with `summary.json`, `summary.md` and ten per-director reports.

**Mission:** Find legitimate worldwide paid work potentially yielding transferable BTC, USDC or conventional payments. Prioritise accounting, bookkeeping, QuickBooks, tax, remote contracting, open-source bounties and agent opportunities. **Actual verified earnings, not searches, are the goal.**

**Limitations:** These are independent scheduled research jobs, not separate Moltbook accounts, and cannot apply, sign, negotiate, post or collect payments by themselves. Leads are unverified and require payer, scope, Uganda eligibility, payout method, and authenticity checks. This workflow never asks for seed phrases, signs transactions, handles private keys, makes payments, or claims that a wallet has received funds. No paid service is required by the code; cloud runtime remains subject to the hosting platform's free-tier and policy limits.

## Standing owner authorization — 13 November 2026

The owner has authorized all 10 directors and 20 assistants to **operate independently** within legally permissible, free, connected-tool capabilities. They may choose research directions, evaluate opportunities, compare payment terms, prepare truthful pitches, and surface or pursue legitimate paid work where authenticated integrations and site rules permit. They must prioritize payment into owner-approved addresses on their correct networks, especially real BTC and genuine USDC, and remain open to other transferable currencies.

The exact personal wallet address map is deliberately **not copied to this public repository**, which would unnecessarily publish the connection between the owner and every wallet. An agent may only supply an exact address to an actual verified payer through an appropriate approved channel when its network and asset have been confirmed. Binance deposit accounts require the exact exchange-supported USDC route and any memo; public chain history never proves a Binance balance credit. Never guess any unknown network, memo or issuer.

**Independence is not a claim of extra tools:** Today's GitHub workflow can autonomously research, review, prioritize and draft proposals, but cannot itself message payers, create Moltbook identities, submit applications, receive money or initiate any on-chain activity. Any lack of a required connection should be recorded as a specific blocker, not misrepresented as deployed outreach. No account fees, gas payments, contracts, private keys, wallet signing, or transfers are authorized.

## Open team meeting and cross-domain authority (13 November 2026)

[Join the public meeting in this repository](https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/5). The owner invited other researchers, AI agents and legitimate payers to contribute genuine job leads, verified bounties and client work. The meeting post shows the owner's approved BTC mainnet and Ethereum-mainnet USDC payment routes with safety restrictions; do not copy exchange custodial memos or the complete wallet mapping into public reports.

**No work silos:** All 30 roles now have explicit cross-domain research authority. Their original specialties remain useful for organization, not limits. Each role saves an independent report and each director evaluates the two assistant reports. The consolidated cloud job is configured to place **one daily public comment** containing 30 individually labeled report summaries on issue #5, but only if enough role reports exist. This automated comment is made by the GitHub workflow, not by 30 separate social-network accounts. Public meeting comments are for collaboration, not guaranteed earnings or spam.

The meeting publication step uses only repository issue permissions and reports whether the platform accepts its post. No public job applications, Moltbook posts, unsolicited messages, or financial transactions are enabled by this configuration.
