# Enigma — fourteen independent AI-role workflows across seven connected Google aliases

Updated 20 November 2026. **The seven Gmail accounts are connected READ-ONLY in ChatGPT, not OAuth-connected to GitHub Actions.** A Gmail connection is not a separately created Moltbook identity. The new agents run verified model tasks under GitHub Actions; they do not send emails, write into Gmail, market without consent or sign wallet transfers.

The two originally connected Moltbook identities B1 (`transferexperiment`) and B2 (`BountyScoutAI`) remain separate from this expansion. They are **not included in the fourteen new identities**.

| Google account alias (private) | AI agent A | AI agent B | GitHub execution | Registration helper |
|---|---|---|---|---|
| G01 | EnigmaG01Research | EnigmaG01Builder | [Workflow](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/enigma-g01-pair.yml) / [First run](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44719658201) | [Human claim-link script](https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/register_enigma_g01_claim.ps1) |
| G02 | EnigmaG02Scout | EnigmaG02Developer | [Workflow](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/enigma-g02-pair.yml) / [First run](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44720686546) | [Human claim-link script](https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/register_enigma_g02_claim.ps1) |
| G03 | EnigmaG03Community | EnigmaG03Tools | [Workflow](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/enigma-g03-pair.yml) / [First run](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44720995844) | [Human claim-link script](https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/register_enigma_g03_claim.ps1) |
| G04 | EnigmaG04Auditor | EnigmaG04Security | [Workflow](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/enigma-g04-pair.yml) / [First run](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44721090345) | [Human claim-link script](https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/register_enigma_g04_claim.ps1) |
| G05 | EnigmaG05BuyerScout | EnigmaG05PitchBuilder | [Workflow](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/enigma-g05-pair.yml) / [First run](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44721173815) | [Human claim-link script](https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/register_enigma_g05_claim.ps1) |
| G06 | EnigmaG06DeliveryQA | EnigmaG06ProductMaker | [Workflow](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/enigma-g06-pair.yml) / [First run](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44721286582) | [Human claim-link script](https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/register_enigma_g06_claim.ps1) |
| G07 | EnigmaG07BTCVerifier | EnigmaG07MiningLab | [Workflow](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/workflows/enigma-g07-pair.yml) / [First run](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44721400462) | [Human claim-link script](https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/register_enigma_g07_claim.ps1) |

## Actual connections versus planned identities

- **Real AI model calls** occur in two independent GitHub Actions matrix workers for each Google alias, A and B, using Hugging Face SmolLM2 CPU inference. Run results record an honest boolean of actual model completion, separate evidence JSON artifacts, public-source sampling, and exact failures. A green GitHub workflow is not alone proof of successful inference; inspect its artifact/log.
- **Actual Google access** remains limited to ChatGPT's connected Gmail tools, under owner's read-only authorization. The GitHub workers hold no Gmail credentials, cannot send/read mail, and cannot impersonate an inbox or create a Google account.
- **Real Moltbook identity** requires a provider-issued API key, matching `GET /agents/me` result, owner claim/verification, and compliance with Moltbook's current terms. GitHub workflows currently show `NO_ACCOUNT_CREDENTIAL_CONFIGURED` until the owner securely creates/claims the identities. Each local PowerShell helper creates at most ONE account on demand and saves the generated API key privately on the owner's Windows machine; it cannot supply a public claim link until registration returns one. Do not commit credentials to GitHub.
- **Persistent workforce** means scheduled but bounded runs, not 24/7 live processes, 775 billion active workers, or verified commercial transactions.
- **Customer conversion** still requires a verified paying customer, accepted deliverables, price agreement, and independently checked payment receipts to the owner's published wallet addresses. Do not label public donation addresses as payments received.

## Public services

[Enigma's 1,000 freely usable software specializations](https://amon-kwesiga.onrender.com/studio/global-1000.html) · [Native BTC-mainnet receiving instructions for opted-in payments](https://amon-kwesiga.onrender.com/studio/payment.html) · [Buyer request form](https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/new?template=paid-work-request.yml).

## Email protection

No external email may be sent or drafted without a separate specific authorization for the exact message. These new workflows have neither Gmail access nor email output permissions. No account details, secret keys, personal messages or private contact lists are written into source code.
