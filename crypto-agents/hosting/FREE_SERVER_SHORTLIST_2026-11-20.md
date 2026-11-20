# B1/B2 — Free Server Shortlist and Zero-Cost Deployment Priorities

**Research date:** 20 November 2026. **Owner purpose:** Support real, lawful B1/B2 Bitcoin research, eligible paid work, original deliverables, and read-only payment verification without up-front infrastructure spending. This is a research report and readiness plan, **not** evidence that an external hosting account was opened or a server was deployed.

## Decision in one paragraph

Use existing connected **GitHub Actions** only for finite source-backed jobs and tests; propose **Cloudflare Workers Free** for a tiny persistent-access command/status endpoint with cron and public-source polling if an authorized Cloudflare account is connected; keep **Hugging Face Static Spaces** for the existing public presentation layer; only consider **Oracle Cloud Always Free** as an actual small Linux VM if the owner has a valid single account, home-region free capacity and accepts its card/identity requirements. Render Free, Koyeb Free and HelioHost are fallbacks for a small web status/API service, **not** unlimited independently running AI workers or miners.

## Official-source comparison — capacity, fit and blockers

| Priority | Host | Official reference | Current free allowance or hardware | Good B1/B2 job | Main blocker / current connection | Deploy proven? |
|---|---|---|---|---|---|---|
| 1 | GitHub Actions public standard runners | https://docs.github.com/en/actions/reference/runners/github-hosted-runners | Public standard jobs no per-minute charge; Linux `ubuntu-latest` 4 CPU, 16 GB RAM; plan-level concurrency and policy limits | Finite repo software checks, time-limited primary-source research, isolated role tests and evidence artifacts | **Already connected**; source runs documented, but workflows must obey platform use policies, finite runtime and concurrency; not a continuous VPS/miner | YES for existing GitHub Actions, **NOT a new server** |
| 2 | Cloudflare Workers Free | https://developers.cloudflare.com/workers/platform/limits/ | 100,000 req/day, 10 ms CPU/request, 128 MB RAM; 5 cron triggers/account as observed Nov 2026 | Tiny HTTP status/queue interface, signed or owner-controlled command metadata checks, periodic public API queries within rate limits | **No connected Cloudflare deployment account**; per-request CPU budget cannot run Python ML inference | NO |
| 3 | Oracle Cloud Always Free | https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm | Up to 2 AMD micro VMs; A1 Arm 1,500 OCPU-hours and 9,000 GB-hours monthly (equivalent to 2 OCPUs and 12GB RAM for a month) | A modest owner-operated Python queue/worker and reporting service | Most accounts need valid phone/card; one account per person; free shapes limited by home-region capacity, inactive instance reclamation; can charge above free limits on paid-account services | NO |
| 4 | Render Free web service | https://render.com/docs/free | 750 free instance hours per workspace/month; sleeps after 15 minutes idle; ephemeral storage | Existing Flask or equivalent API status page; wake-on-request | Existing owner Render service previously reported failed deployment; free background workers/cron/persistent disks not included; excess bandwidth may be charged | NO healthy status independently verified |
| 5 | Koyeb Free Web Instance | https://www.koyeb.com/docs/reference/instances | One free HTTP instance per organization, 0.1 vCPU, 512MB RAM, 2GB SSD; sleeps after 1h idle | Lightweight web health/status and preview | No free dedicated Worker Service, no persistent volume, no connected account; verification/card requirements depend on signup | NO |
| 6 | HelioHost | https://heliohost.org/ | Community free web hosting including Python/Node.js, scripts and limited cron, subject to access/quotas | Lightweight Python/Node web page or status/periodic script with written permission | Not a full VPS; actual sign-up and free allocation not verified; do not create duplicate registrations | NO |
| 7 | Hugging Face Static Spaces | https://huggingface.co/docs/hub/spaces-overview | Static Spaces free; new compute-backed Gradio/Docker Space requires paid plan under Nov 2026 policy | Public B1/B2 proof portal and original software demos that run client-side | Existing owner space `Amonkkkk/b1b2-superworker-assembly`; write/deploy permissions not independently confirmed here; no free always-on Python inference from a static Space | Static Space exists; no new deployment |
| 8 | PythonAnywhere Beginner | https://help.pythonanywhere.com/pages/FreeAccountsFeatures/ | 100 CPU seconds/day; 512 MiB storage; one web app that needs renewal; new free accounts do not get scheduled tasks | Tiny prototype only | Strict outbound allowlist and low compute allowance, no new-account cron or always-on worker | NO |
| Conditional | Google Cloud Run | https://cloud.google.com/run/pricing | Request-based free allowance, e.g. 2M requests/month plus specified CPU/RAM quotas | Isolated event-driven container jobs if owner has authorized billing account | Billing required and overages possible; cannot guarantee $0 without controls | NO |

## B1/B2 deployment architecture (maximum real evidence, minimum vanity)

```
HUMAN OWNER -> Chief D canonical GitHub command files
                     |
              GitHub Actions
           finite public research and tested deliverables
                     |
          public source-backed result artifacts
             /                    \
 Cloudflare read-only         Static Hugging Face
 command/status API           dashboard and portfolio
  (not yet deployed)           (existing static site)
                     |
     optional consented Oracle VM for small actual
     Python supervisor/worker queue, only if verified
     free-eligible and explicitly approved
```

A real miner is a separately owned and authorized ASIC/rig, **not** any of these free platform jobs; payout direction requires the miner's explicit permission and the correct B1 vs B2 Bitcoin mainnet address. Never mine on GitHub Actions, free trials, strangers' equipment or these free hosting plans. No free host itself brings an eligible BTC-paying customer.

## Exactly what can happen now with authorized access

1. **Existing GitHub:** keep bounded QA, real research, software bug-fix evidence and customer source analysis; review the latest jobs and model-completion evidence before raising concurrency. Post concrete original deliverables only where permitted. Avoid continuous or abusive compute, and respect public-runner concurrency.
2. **Cloudflare candidate:** owner connects a legitimate Cloudflare account and explicitly approves a free Worker. Deploy only a minimal READ-ONLY `/health` and `/command-status` endpoint. Fetch the canonical public repo metadata, verify it against the mirror, return source commit/order ID and clearly separated actual runtime evidence. No executing arbitrary input, no wallet private keys, no customer messaging, no AI CPU inference, no automatic payouts.
3. **Oracle candidate:** provision at most the eligible genuine owner-controlled Always Free instance only after card/identity, capacity, home-region and $0 limit evaluation. Require CPU/memory/rate limits, real heartbeat/model receipts, and clear stop conditions. Do not assume 24/7 availability or provider acceptance before provisioning.
4. **Existing Render:** inspect deployment error and fix a lightweight web status app only if no spend and within workspace quota. Do not keep it awake with artificial request traffic.
5. **HelioHost/Koyeb:** optional alternatives for simple public site or tiny web service, with real account approval and provider terms first. Do not spawn fake multiple accounts or evade quotas.
6. **Monetization first:** prioritize one real qualified Bitcoin-paying buyer, one accepted deliverable and one independently verified BTC TXID per fleet; infrastructure success alone is NOT earnings.

## Evidence and account inventory as of this assessment

- `GitHub connected`: yes. Owner repo: https://github.com/kwesigaamon8-web/Amon-Kwesiga
- `Hugging Face existing static Space`: referenced at https://huggingface.co/spaces/Amonkkkk/b1b2-superworker-assembly; static hosting != running model.
- `Render existing service`: reported in prior owner notes but no healthy current deployment established.
- `Cloudflare/Oracle/Koyeb/HelioHost external accounts`: **NOT CONNECTED / NOT DEPLOYED** in this task.
- `New paid charges or accounts created`: **NONE**.
- `New ASIC miners authenticated / mining payouts attributable to this plan`: **NONE VERIFIED**.
- `Independent BTC income attributable to this research`: **NONE VERIFIED**.
- `Gmail/email access`: **NONE**. Standing no-email restriction respected.

*All pricing, availability, and quotas may change; check official provider account eligibility and plan page at deployment. This report uses provider documentation consulted on 20 November 2026 and does not imply user-specific signup approval.*
