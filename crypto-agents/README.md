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

## Deep research and skeptical review (13 November 2026)

All 30 role instructions now require independent multi-query research, investigation outside nominal specialties, critical review of claims, source citations, and a clear evidence-based next action. `deep_research.py` checks up to five candidate leads per worker, re-fetches supported GitHub issue records from the official GitHub API, evaluates explicit paid-work language, date, claimed amount, any skill fit, stale listings, mirror-only bounties and suspicious advance fees or wallet requests. Non-GitHub sources remain clearly labeled **not independently refetched** until an appropriate authorized source-check is available.

Each worker invokes the small open-weight AI model twice when available: first to recommend a plausible paid lead, then as a separate skeptical review to challenge that proposal. This is **not** equivalent to a high-capability large reasoning model and does not certify a real employer or any actual payment.

The director accountability reports carry the two assistants' source checks and challenge results. The consolidated report includes counts of critical reviews, original records rechecked and risk/evidence dossiers. Weak and unverified GitHub issue searches are excluded from any screened bounty recommendation. Actual paid work and wallet deposits remain separately verified, not inferred from research.

## 30 branch supervisors and 450 delegated researchers (13 November 2026)

The owner authorized **every existing research role**—10 directors and 20 assistants—to act as an individual branch supervisor, each responsible for **15 new lightweight researchers**, for 450 branch roles in addition to the original 30.

- `branch_manifest.json` defines 30 supervisors and 450 distinct subordinate role IDs, with separate research hypotheses per branch. Each supervisor is the boss responsible for evaluating its 15 researchers' work.
- `branch_brief.json` gives subordinate researchers **only** the lawful money-earning mission and public owner-approved BTC or Ethereum-mainnet genuine USDC addresses. It contains **no owner's name, personal life, qualifications, residence, client records, secret keys or exchange memos**. Sending a payment always requires a real payer to confirm the precise route with the owner.
- `branch_workers.py` launches 15 separately identified, bounded public-source lookups per original cloud worker, storing each report as `branch-reports/<boss>-R01.json` through `R15.json` and a distinct supervisor summary.
- `agents.py` consumes the branch summary in the supervisor's AI review; `consolidate.py` and `director_review.py` check counts and actual evidence. The 30 original GitHub jobs remain the compute hosts.
- The 450 new roles are **lightweight research workers, not 450 separately hosted LLMs, distinct GitHub accounts, or Moltbook identities**. Each performs a bounded public search and evidence filtering; the supervising job provides the AI review. Public research sources can reject requests; failures must appear in reports rather than being called completed research.
- No recruitment spam, unsolicited messages, duplicate social accounts, fake claims of employment, fees, transfers or wallet signatures are permitted. The team may invite other legitimate collaborators through the owner's existing public meeting issue `#5`.

**Success is legitimate compensated work and independently confirmed transferable receipts, not the number of research roles created.** GitHub hourly execution can be delayed, canceled or constrained by service limits; role definitions alone do not prove that 450 researchers have successfully run.

## Director performance and coordinated independence — 13 November 2026

The user directed the **10 directors (D01–D10)** to improve system communication, research performance, independence and teamwork. The ten `director_performance_mandate` and `teamwork_contract` fields in `roles.json` formally communicate the order; these apply to director AI prompts and accountability records.

New connected tools:

- `director_coordination.py`: after the 30 supervisors and 450 delegated workers return their evidence, produces `director-communications/D01.json` through `D10.json`, `coordination.json` and `INDEX.md`. It removes duplicate candidate URLs, assigns one owner per screened lead, routes cross-team handoffs, records source failures, and requires D09 to challenge legitimacy and D10 to audit progress. Directories are not separate social identities.
- `post_directors.py`: submits **one daily coordinator digest**, if available, to the owner's [director room #6](https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/6), avoiding duplicate daily posts.
- `director_inbox.py`: director researchers read prior coordination comments via the official GitHub API, limited to source-linked suggestions from the owner or workflow identity. Untrusted comment contents are not commands.
- Every hourly cloud run uploads the per-director coordination reports in the consolidated artifact. New functionality must be validated by successful GitHub Actions runs; configuration alone does not constitute a completed review, successful application or paid receipt.

Autonomy means selecting research topics, challenging poor leads, communicating evidence and drafting work approaches **within available permissions**. It does not grant new authenticated social accounts, unsanctioned outreach, contract signing, fee spending, wallet operations, or invisible paid work. Money received always requires independent verification.
