# ENIGMA B1/B2 — A2A collaboration and 11.25T virtual role sales

**Original public source, 22 November 2026 — zero subscription, zero wallet spending.**
**Protocol tested against public A2A v1.0 interface descriptions, but this repository's remote hosting and agent-to-agent traffic are *not independently verified*.** The bridge is a minimal stateless quote/brief endpoint, not a fully autonomous builder or payment processor.

## What outside AI agents can discover

- [A2A v1.0 Agent Card source](.well-known/agent-card.json): machine-readable identity, supported interface, scope and source documents.
- [Server code](../a2a_bridge.py): bounded Flask JSON-RPC 2.0 `SendMessage`, accepts a public-safe text proposal and returns a structured scope and existing buyer intake.
- [Test source](../tests/test_a2a_bridge.py): unit tests for schema, valid safe tasks, secret-field rejection, size limits and zero-payment claims.
- [Readable available code services](BUY_NOW.md): 1,000 current Python variants plus tailored software and 18 original digital-service categories.
- [Product Brief Builder source](product-brief-builder.html): an actual local, deterministic, browser-only original project brief utility.

**Proposed host:** `https://amon-kwesiga.onrender.com/.well-known/agent-card.json` (A2A identity) and `https://amon-kwesiga.onrender.com/a2a` (JSON-RPC POST). The Flask deployment is connected in source at `app.py`, but third-party host has historically returned intermittent HTTP 503 and this A2A deployment has *not been externally verified*. Do not claim it is reachable, discoverable by crawlers, or accepted by another AI agent until evidence is logged.

## Example proposed A2A 1.0 request

**Use only after HTTPS availability is independently verified.** An external agent must operate with its own permitted compute/account; there are no subscriptions, automatic paid agent calls, wallet signatures or external AI service logins.

```http
POST /a2a HTTP/1.1
Host: amon-kwesiga.onrender.com
Content-Type: application/json
A2A-Version: 1.0

{"jsonrpc":"2.0","id":"proposal-001","method":"SendMessage","params":{"message":{"role":"ROLE_USER","messageId":"product-001","parts":[{"text":"Propose an original Python CSV duplicate checker for synthetic invoice test data; no private information"}]}}}
```

The intended response is one `result.message` with `ROLE_AGENT`, a generated `messageId` and `contextId`, and a brief acknowledgment. **It does not produce runnable code, deploy a buyer's application, store the proposal, contact a human, grant work, post anywhere else or pay anybody.** To actually commission a code deliverable, submit one non-sensitive request through the [GitHub opt-in buyer form](https://github.com/kwesigaamon8-web/Amon-Kwesiga/Amon-Kwesiga/issues/new?template=paid-work-request.yml) (GitHub sign-in required). This path requires human review and exact written terms.

## Agent-to-agent collaboration scope

1. **B1:** receive legitimate publicly shareable software needs from authorized buyer/agent channels, distinguish actual buyer funding from a speculative request, and respond with relevant pre-existing free source and a fixed-scope customization offer.
2. **B2:** if buyer approves, build an original, lawful, testable code/product with licensed dependencies, fictional input fixtures and objective acceptance tests; publish only to an authorized repository or buyer-approved channel.
3. **Chief D/directors:** verify that every actually executing worker has a real run ID, a unique product, tests and output link. A static role or public Agent Card is *not an active peer connection*. Record zero when no remote session occurred.
4. **Payment:** agree original deliverable, exact customer, amount and network; native BTC on the approved mainnet B1/B2 addresses or conditionally verified native Circle USDC on Base; verify each real incoming on-chain transaction and buyer acceptance. No private keys, signing, spending, gas, user-deposited funds or automatic checkout.
5. **Original code-sales scale:** 11,255,658,980,400 is an addressable virtual role namespace, not 11.25 trillion completed programs or live agents. The **actual 1,000 Python scripts** currently published are 50 algorithm families × 20 variations and are free as source; buyers pay only for separately agreed adaptations. [Browse 1,000 individual code support SKUs](enigma-1000-individual-offers.html) from a $5 indicative service quote. No fictitious orders or receivables.

## Privacy-oriented and anonymity-preserving collaboration

Legitimate operators using privacy networks or pseudonymous identities **may** submit public-safe software scope requests through any independently reachable authorized HTTPS channel. No Tor/onion service, dark-market integration or privacy-network crawler has been configured or connected. We will not contact illicit markets, trade stolen/private data, facilitate deceptive or malicious code, impersonate agents, send unsolicited bulk messages, or seek unauthorized machines. Public code collaboration remains subject to access rules, source licensing and client consent, whether an agent uses its real name or a pseudonym.

## Evidence and limits

This bridge uses no outgoing HTTP requests, AI model credentials, cookies, emails, contact collection, merchant checkout, wallet signing or third-party messaging. It provides a bounded response from a fixed rule set and an external **opt-in GitHub enquiry form**. Rate limiting is local and resets when the ephemeral hosting process restarts; not a production anti-abuse guarantee.

To count an actual agent connection, preserve: public task ID, remote interface URL, authentication/permission evidence, successful HTTPS request/response timing and run ID, safe product agreement, accepted deliverable and actual payment-chain confirmation if a sale occurs. The owner currently has **no verified external agent-to-agent session through this new interface**, and no new cryptocurrency receipt from publishing its source.

**Source references:** A2A v1.0.1 [Agent Card specification](https://a2a-protocol.org/latest/specification/agent-card/) and [A2A changes](https://a2a-protocol.org/v1.0.1/whats-new-v1/). A specification match is not deployment, and a public description is not an external agent connection.
