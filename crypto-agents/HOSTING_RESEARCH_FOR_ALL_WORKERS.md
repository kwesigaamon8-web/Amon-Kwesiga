# ALL REAL B1/B2 WORKERS — RESEARCH WHERE WE CAN BE HOSTED ONLINE
**Issued:** 16 November 2026 · **Canonical owner order:** `OWNER-20261116-133042-HOSTING-SEARCH-EVERY-WORKER`
**Parallel task**: investigate genuine free/authorized Internet hosting **without stopping work on actually paid clients and legitimate crypto receipts**. All 750,377,265,361 role positions inherit instructions upon **actual invocation**, not simultaneous activation.

## What every actually active worker must deliver
For each assigned host and an alternative, fetch/read current **official** documentation when possible, report: exact product URL, region and availability, allowed commercial compute vs static page, free plan and hard caps, unexpected billing risk, uptime/cold start, CPU/memory/VM, network and job scheduling, secret management, existing owner account authorization, legal cryptocurrency policy, and actionable $0 next step. Distinguish official page fetched from account deployed; a paid worker is not a free platform. Only if owner-controlled credentials and explicit approval are present may a real deployment be attempted. Don't use others' machines or mine on trial/free hosting.

| Candidate | Official source | True fit | 2026 caveat | Known owner connection |
|---|---|---|---|---|
| Cloudflare Workers Free | https://developers.cloudflare.com/workers/platform/limits/ | Tiny event/router/queue and HTTP status | 100,000 req/day, 10 ms CPU/request, 5 cron triggers; **not a full AI inference server** | Not connected |
| Oracle Always Free Compute | https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm | Constrained Linux/CPU VM possible | Capacity/home region, idle reclamation, account eligibility and possible identity/card requirements; do not provision without permission | Not connected |
| Render Free | https://render.com/docs/free | Existing simple Flask status app | Sleeps after 15 min idle, 750 free instance hours/workspace/month; ephemeral disk; possible excess network charges; **user's current service failed deploying even after unit tests passed** | Existing service; NOT healthy |
| Koyeb Free | https://www.koyeb.com/docs/reference/instances | One tiny HTTP process/demo | 0.1 vCPU, 512MB, 2GB, scales to zero after 1h; free Web Service, **not background Worker Service**; account/card not verified | Not connected |
| Netlify Free | https://www.netlify.com/pricing/ | Web front end and bounded functions | 300 credits/month, specific credit/usage and billing rules must be checked | Not connected |
| Hugging Face Static Spaces | https://huggingface.co/docs/hub/spaces-overview | Static dashboard, public demo | Static free; newly created compute Gradio/Docker requires paid plan, no persistent heavy inference on free account | Read-only account connection; no authorized compute deployment |
| GitHub Pages | https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits | Static open-source project docs | Cannot operate online business/SaaS or run a model; GitHub repo Pages disabled | Repo connected; Pages off |
| Vercel Hobby | https://vercel.com/docs/plans/hobby | Personal noncommercial demos | **Hobby noncommercial only**; not suitable for for-profit B fleet | Not connected |
| Cloud Run | https://cloud.google.com/run/pricing | Event-driven serverless API with free allowance | Billing account required and potential usage charges | Not connected |
| Deno Deploy | https://docs.deno.com/deploy/pricing_and_limits/ | Small JS edge programs | Official docs state sunset April 2027; unsuitable for long term | Not connected |

**Important:** Hosting gives compute or public web presence, **not a source of Bitcoin by itself**. The important fit is: a modest, permitted always-available queue/coordination service, and—only where actually included—CPU for an actual LLM. Free static pages will not run agents. GitHub Actions is for repo CI and legitimate code testing, not mining or unrelated persistent commercial model farm. Do not create duplicate free accounts, evade caps, authorize charges, request private keys, or claim all indexed roles are running.

## Evidence ledger each worker must send to parent
`fleet | actual_worker_id | canonical_direct_parent | owner_order_id | assigned_platform | official_url | retrieved_at_utc | retrieval_HTTP_status_or_ERROR | free_plan | permitted_workload | useful_for_our_specific_task | CPU/sleep/quota | billing_risk | owner_account_connected? | deployed_and_health_checked? | competing_host | concrete_next_action | QA_or_blocker`.

Use `SOURCE_NOT_FETCHED`, `UNKNOWN`, `NOT_CONNECTED`, or `BLOCKED` when appropriate. An existing connection does not prove deployment. The [hosting_scout.py](https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/hosting_scout.py) assigns two distinct sources deterministically to each genuinely invoked worker; a read-only HTTP probe independently tests source reachability without generating credentials or deployment.

## Director instructions
D01/D02 source worldwide hosts and official limits; D03/D04 challenge billing/card/terms; D05/D06 prepare legal minimal deployments only with permitted existing accounts; D07/D08 independent sources, user opt-in and peer validation; D09 enforce no spending, secure secrets and no abusive cryptomining; D10 continues **customer receivables and chain-specific crypto receipt checks**—hosting research must not consume D10's main task. Chief D consolidate a ranked top-3, recommend one site for static dashboard and one legal source of actual model compute, and state exact access/permission blocker.

## Render-specific high-priority action
Existing source [app.py/Flask dashboard CI](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/43874167727) passed 3/3 tests, but the existing Render service `srv-dbrkj73rjlhs73fk21qg` [still failed deployment](https://dashboard.render.com/web/srv-dbrkj73rjlhs73fk21qg/deploys/dep-dbtg47vf3r2c73fgcspg). Do **not** blindly retry or create more services. An authenticated account admin should inspect exact build/start/runtime/root configuration and deploy logs; a GitHub commit does not automatically sync Render dashboard service settings. Host scouting cannot fix missing account access.
