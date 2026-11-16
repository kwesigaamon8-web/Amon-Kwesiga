# B1/B2 free-resource independent assistant deployment plan

Status: research and design only. No worker activation is implied.

## Director responsibilities
D1 runtime inventory and real invocation evidence; D2 model-provider eligibility and limits; D3 task queue and deduplication; D4 public paid-opportunity discovery; D5 original deliverable preparation; D6 peer review; D7 authorized outreach preparation (no unsolicited automated messaging); D8 chain-specific payment verification; D9 infrastructure and cost/rate compliance; D10 financial audit and Chief D reporting.

## Free/open resources to evaluate
- GitHub Actions: https://docs.github.com/en/actions (respect account-specific free-minute, concurrency and acceptable-use limits; no cryptocurrency mining)
- LangGraph: https://github.com/langchain-ai/langgraph (agent orchestration; inference separate)
- CrewAI: https://github.com/crewAIInc/crewAI (multiagent role coordination; inference separate)
- Hugging Face Inference Providers: https://huggingface.co/docs/inference-providers (requires account/token and may charge or have limited credits; never assume unlimited free)
- Ollama: https://ollama.com (local model inference if compatible owner-controlled hardware exists; power and hardware not free)
- SQLite + Python standard library for durable task state, retries and audit logs.

## Implementation sequence
1. D1 inventories actual running GitHub workflows, connected model endpoints, quota and allowed hardware. No invented workers.
2. D2 verifies a permitted model API or local inference backend with explicit authentication and zero-spend guardrail. Stop if none exists.
3. D3 provisions durable task queue with worker IDs, lease, retry cap, budget, provider request cap and idempotency.
4. Pilot B1 research agent and B2 research agent as distinct real model invocations; D6 reviews outputs. Store timestamps and provider response identifiers.
5. Directors divide work by opportunities and tasks, exchange evidence through the queue, and stop duplicate tasks.
6. D10 reports verified ACTIVE and concurrent counts based on execution records, and separately accepted work, invoiced, unpaid and verified paid assets.
7. Scale in batches of 2, 5, 10, 20 only if capacity, terms, rate limits and owner approvals permit. 750,377,265,361 is a role namespace, not evidence of live agents.

## Initial paid-work focus
Find genuine public offers for accounting, bookkeeping, coding, translation, data cleanup and software testing that permit AI assistance and have documented payment terms. Produce original useful proposals or samples, not spam. Do not claim earnings before external acceptance or verified credit.

## Controls
Never use free tiers to evade limits via mass account creation. No unauthorized cloud hosting, cryptocurrency mining, wallet signing, credential handling, transfers, scraping contrary to terms or mass unsolicited outreach. Owner approval required for spend, new auth, sensitive disclosure and contracts.

## Evidence standard
Each worker: unique ID, task, model endpoint, start/end UTC, invocation receipt or run URL, output hash, reviewer outcome. Count active only from actual invocation evidence; count simultaneous only from overlapping execution windows. Status UNKNOWN when unverified.
