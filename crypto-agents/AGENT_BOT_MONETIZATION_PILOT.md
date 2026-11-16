# B Agent Assistants — on-demand bot monetization pilot

**Owner instruction:** 16 November 2026, "monetize that reconfigure each to be like chatgpt bot."
**Status:** working, testable source implementation; NOT a live billable company, registered ChatGPT plugin, OpenAI endorsement, API-funded model, paid customer or verified payment. No customer funds have been collected here.

## What is genuinely different now
A single multitenant Flask app serves **role-specific conversational assistants** at \`/bots\`, catalog at \`/api/bots/catalog\`, read-only role inspection at \`/api/bots/role/<fleet>/<role>\`, and protected \`POST /api/bots/chat\`. Each valid B1 or B2 role ID maps **on demand** to an independent role specialty and capability-first persona by the existing two-company/one-parent dispatcher. This covers the mathematical **750,377,265,360 configured B roles plus ONE Chief D role**, but DOES NOT precreate 750B model instances. The single Chief D is a supervisor, not a publicly sold human customer chatbot.

The app uses OpenAI's official Responses API only **if the owner actually configures an approved API project and budget**. OpenAI API billing is separate from ChatGPT subscriptions and can incur charges. [Official Responses API](https://developers.openai.com/api/reference/resources/responses/methods/create) and [API pricing](https://developers.openai.com/api/docs/pricing).

**Naming:** Product identity is "B Agent Assistants", NOT "ChatGPT", "GPT-6 Bot", or any representation that OpenAI endorses this service. Never put an OpenAI product/model brand in the product name. [Official OpenAI brand guidance](https://openai.com/brand/).

The API cannot autonomously do web search, mine BTC, deploy hosting, contact a customer, sign a wallet, or verify payments. It only generates textual customer assistance and says so. Every customer has a separate access key and must explicitly be provisioned with a verified paid invoice (or otherwise genuinely authorized zero-revenue pilot), allowed exact roles and hard quota.

## Saleable specialist categories — proposed, not actual paid products
- Buyer Research — scope and research proposals.
- Opportunity Verification — payer/award, eligibility and duplicate-claim reviews.
- Original Work Assistant — original first-draft technical/data work.
- Quality Reviewer — QA, test guidance and checklists.
- Sales Writing Assistant — short contextual non-spam messages.
- Payment Evidence Assistant — reconciliation guidance **not wallet custody or actual payment verification**.
- Mining Research Assistant — real ASIC/pool economic reasoning, **not remote mining**.
- Hosting Research Assistant — official terms comparisons, **not cloud deployment**.
- Evidence Reviewer — evidence-based summaries and original-source evaluation.
- Software Repair Assistant — debugging guidance and test reasoning.

**Suggested paid pilot prices (EXAMPLES ONLY, not published quotes, receipts, prices guaranteed profitable):** single specialist $15/month for 30 successful or attempted requests (cap 300 output tokens per answer); team $45/month for 120 requests across assigned specialist roles. Actual costs/pricing must be checked against current API model pricing, hosting billing, taxes, demand and buyer acceptance BEFORE quoting. No automatic crypto checkout or billing is implemented; accept payment only by a separately authorized manual invoice and reconcile the correct asset/network or legitimate fiat payment before marking \`invoice_verified\`.

## Owner setup / hard blockers
1. Fix original Render service's failed deployment settings or use another approved legal service; **GitHub CI passing does not imply Render is running**. Render Free is a prototype host that spins down on idle and loses ephemeral local state. [Render free limits](https://render.com/docs/free).
2. Obtain owner-authorized, budget-limited API key and an exact supported text model; store as **private host environment variables**. **Never paste credentials into GitHub or this file.** The service refuses chat if any required field is absent.
3. Set \`BOT_SERVICE_ENABLED=1\`, \`BOT_OPENAI_API_KEY=<private key>\`, \`BOT_MODEL=<approved supported model>\`. No key, no model, or disabled flag => 503 and **no provider call or charge**.
4. Prepare a customer-only secret (at least 24 characters) and its SHA-256 digest offline. Set a **secret** environment variable \`BOT_CLIENTS_JSON\` with a record matching the example below, only **after actual approved customer onboarding and verified payment**. Do not put raw key or real personal customer data in source or chat logs.
5. Provide the exact provisioned role and secret to the customer via a private permitted channel. Customer browser form keeps key in memory, never browser storage. Requests hit \`POST /api/bots/chat\` only via HTTPS.
6. Verify health, authentic model response and real per-customer meter before taking money. For a true commercial launch, add a durable shared database (not ephemeral free Render memory) to meter quotas, authenticated customer lifecycle, separate reliable paid invoice ledger, proper audit/backup/rate controls, data deletion/retention policy, usage-cost reconciliations and abuse monitoring. As implemented, counters are **only per running process** and reset on restart, so the prototype **must not be advertised as production-grade metered billing**.

### Provisioning schema (fake demonstration key, not an activated customer)
\`\`\`json
{
  "example-client": {
    "token_sha256": "<SHA-256 of separately issued long secret>",
    "enabled": true,
    "invoice_verified": true,
    "valid_until": "2026-12-31",
    "allowed_roles": ["transferexperiment/D01-M01-W01"],
    "monthly_limit": 30,
    "minute_limit": 2
  }
}
\`\`\`
This lives ONLY in private \`BOT_CLIENTS_JSON\`, not a repository file. \`invoice_verified\` is a manual owner-approved business record, **not a secure payment-gateway callback**.

### Model and cost controls
Responses API \`POST /v1/responses\` uses fixed provider domain, owner-selected model, role-specific instructions, max 8 conversation items, 1400 characters each, max 300 output tokens per call, and \`store:false\`. No provider keys are sent to customers. Server requires bearer customer token with SHA-256 comparison, date validity, invoice verification and exact allowed role; rejects unauthorized calls. Token quotas are max 6/minute and 400/month per customer, plus 500 total per month per server process as an emergency default. Counters record attempted calls; actual fees must be checked at the provider account.

## What can be claimed now
- Code is implemented for a **single real on-demand conversational model backend across billions of lazy role IDs**, subject to provider and customer access.
- The role catalog is publicly inspectable, and a protected assistant chat endpoint has a testable real Responses API integration with no fake model fallback.
- Static index and original dashboard remain intact. No BTC mining, autonomous third-party outreach or blockchain signing is part of the customer chat endpoint.
- **NOT VERIFIED:** actual public Render deployment, API credentials, actual live customer model exchange, client acceptance/receipt, sale, earned BTC/USDC or 750B concurrent AI processes.

## Live QA
[Repo test workflow](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions) runs offline mocked-service contract tests and existing dashboard tests. Passing mocks verifies wiring, auth and limits, **not** real model inference, service uptime, or customers.
