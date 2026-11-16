# B Agent Network — billions of virtual role addresses; practical permitted hosting

**Source built 16 November 2026. NOT DEPLOYED.** No connected Cloudflare Workers deployment credential, custom domain or authenticated DNS write access was available to this task. No account was created, no hosting bill paid, no model or mining hardware started, and no external clients or receipts were generated.

## What can be hosted now once a legal host account is connected

One web endpoint *resolves all 750,377,265,360 configured B1/B2 worker role identifiers plus one Chief D* on demand: \`GET /api/role?company=B1&role=D01-M01-W01\` etc. The service does not pre-create hundreds of billions of individual server instances, wallet accounts, jobs or AI inference processes. Routing requires O(1) memory per request and no role database. The \`/api/opportunities\` URL offers 12 plausible **categories**, not fictitious real paying offers. It provides \`/health\`, \`/api/capacity\` and \`/api/mining\` with clear limits and a simple browser UI at \`/\`. This is a directory and earning-work router, not actual AI inference or a Bitcoin SHA-256 miner.

**Source files:** \`edge-role-directory/index.mjs\`, \`index.test.mjs\`, \`wrangler.toml\`. The index is standard Worker module syntax and uses only Web standard Request/Response and URL. Run offline \`node --test edge-role-directory/index.test.mjs\`. Cloudflare deployment through real owner-authorized Workers dashboard/wrangler is required; source commit alone cannot publish a URL. The existing Flask bot service in \`virtual_bot_service.py\` provides real model API calls ONLY once owner-approved model credentials, customer authorization, actual billing budget and reliable commercial hosting are connected.

## Current free/low-cost hosts: use the correct tier, not account farming

| Host official policy | Recommended legal use | Hard limit / blocker |
|---|---|---|
| Cloudflare Workers Free: https://developers.cloudflare.com/workers/platform/limits/ | First choice for THIS lightweight edge role directory | 100,000 requests/day, 10 ms CPU/request, 128 MB; free does NOT grant billions of distinct machines or long-running LLM inference |
| Netlify Free: https://www.netlify.com/pricing/ | Public website, bounded functions/storage | 300 credits per month; usage beyond free allocation cannot be assumed free |
| Render Free: https://render.com/docs/free | Test Flask \`/bots\` and an accessible public page | Prior actual Render deployment FAILED; free plans sleep and have limitations; no live site confirmed |
| Koyeb Free: https://www.koyeb.com/docs/reference/instances | Alternative Flask demo only | One Free web instance per organization, 0.1 vCPU, 512 MB, zero after 1 hour idle; not background worker service |
| Oracle Always Free: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm | Potential limited actual Linux VM and authorized backend | Capacity/region/account/verification, abuse rules, idle reclaim; no real account connected |
| Hugging Face Static Spaces: https://huggingface.co/docs/hub/spaces-overview | Public static website/demo | Free static but new compute Gradio/Docker creation requires paid plan, no permission to create with current read-only connected account |
| Google Cloud Run: https://cloud.google.com/run/pricing | Event-driven bounded backend after approval | Requires connected billing account; free-tier quota not unlimited; unauthorized spend prohibited |
| Deno Deploy: https://docs.deno.com/deploy/pricing_and_limits/ | Small experimental router; not primary | Existing service sunsets April 2027; avoid critical long-term dependency |
| Vercel Hobby: https://vercel.com/legal/terms | Noncommercial demo only | Terms prohibit commercial uses on Hobby; do not deploy paid bot business on it |
| GitHub Pages: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits | Public noncommercial technical documentation | Static only; explicitly not for an online business or commercial SaaS |
| GitHub Actions: https://docs.github.com/en/actions | Test code and report source evidence | Not a free 24/7 commercial bot farm or third-party mining host |

**Multi-hosting policy:** use distinct providers only for genuinely needed functions and with their explicit permission. Do not create bulk free accounts, spoof devices or identities, bypass quotas or convert shared hosted web resources into free cryptocurrency miners. Account connection still requires a real account owner to approve it.

## Genuine money routes
1. Get an actual buyer/accepted task: safe coding, documentation, software QA, data processing, customer support chatbot pilot, or a legitimate funded bounty.
2. Deliver original useful work through an actually permitted external account and get genuine acceptance.
3. Invoice, identify exact BTC/USDC compatible chain/token, account and memo if needed, and verify real paid transaction or authenticated custodian credit. Never count unconfirmed mining shares as money.
4. In parallel identify **real consenting SHA-256 ASIC operators** willing to discuss pool collaboration. Real hashrate, consent, electricity costs and actual paid pool receipts are essential. These virtual role records do not mine.
5. Start only owner-approved hosting model usage and subscriptions with cost and authentication gates. Payment and externally accepted work are unverified as of this code change.

## Deployment choice and reality
**Highest expected zero-charge value:** ONE Cloudflare Workers Free role directory + separate owner-authorized model/chat backend. This resolves arbitrary identities cheaply, not active model instances. Render connected-app deployment can be configured after the user connects it and its prior failed app is repaired. Other free websites are backups, not thousands of free independent compute servers. Only use actual physical ASIC rigs (with operator consent) to generate meaningful Bitcoin SHA-256 work.

## Consent-first pooled SHA-256 operator setup template
The latest user instruction emphasizes real shared mining into existing B1/B2 receiving addresses. The read-only public `GET /api/mining/setup?company=B1&worker=rig01` generates a **non-executing** Public Pool PPLNS setup example using exactly that company's existing native BTC mainnet address and public TLS 14333 port. It does not invent a new wallet, connect hardware, change any device, recruit a miner or earn BTC. Only an operator who owns or expressly controls a real physical ASIC device may choose to configure it and must knowingly agree to use the named owner receiving address, including any voluntary donation/profit-sharing conditions. A pool-side share is NOT an onchain BTC payment, and no operator is claimed until actual dashboard proof. Each operator can retain its own separate rightful rewards rather than participate; no unilateral reward diversion.

## Working chatbot integration (2026-11-16)

The new \`/chat\` page and \`POST /api/chat\` handler connect the edge identity directory to the previously implemented Flask \`POST /api/bots/chat\` specialist model backend, **but only after real backend deployment and authorization**. The new modules are \`edge-role-directory/chat_proxy.mjs\` and \`chat_page.mjs\`. The router checks role, fleet, customer bearer token syntax, strict message/size limits and forwards only to an operator-configured, HTTPS-only \`BOT_BACKEND_ORIGIN\`, never a caller-supplied address. The Flask backend still independently verifies per-customer secret digest, confirmed paid invoice/explicit authorization, allowed exact role and per-process quota and uses only the budgeted owner-selected model. No fake reply or external action fallback.

\`\`\`bash
# This is a suggested command for a REAL owner-authorized Cloudflare deployment.
# Requires login, correct domain and a hosted Flask app; never paste API keys in git.
npx wrangler login
cd edge-role-directory
npx wrangler deploy
# In Workers Settings > Variables configure
# BOT_BACKEND_ORIGIN = https://YOUR-AUTHORIZED-BOT-BACKEND.EXAMPLE
# Flask separately requires BOT_SERVICE_ENABLED=1, BOT_OPENAI_API_KEY, BOT_MODEL, BOT_CLIENTS_JSON.
\`\`\`

**Caution:** Backend may still be unavailable due to the prior Render deployment failure and absent API account access. No public Cloudflare deployment or real customer chat has been verified. The in-memory customer quota in Flask does NOT survive restarts or scale across multiple hosts, so a durable database-backed counter and real invoice ledger are required before marketing production subscriptions. No bulk trial/anonymous access and no free infrastructure mining.
