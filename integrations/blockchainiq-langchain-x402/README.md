# Blockchain IQ LangChain x402 market-brief tool

Unofficial LangChain JavaScript integration for the [Blockchain IQ x402 API](https://www.blockchainiq.co/agents), prepared against the [October 23, 2026 USDC integration bounty](https://www.blockchainiq.co/blog/x402-build-bounties).

## Features

- Defines an actual LangChain structured tool with `@langchain/core/tools`.
- Uses `@x402/fetch` and `@x402/evm` to handle an HTTP 402 payment request.
- Restricts payment to Base `eip155:8453`, Circle USDC (`0x833589fCD6eDb6E08f4C7C32D4f71b54bdA02913`), `exact` scheme and at most 10,000 microUSDC (0.01 USDC).
- Calls only `https://www.blockchainiq.co/api/x402/v1/brief` by GET.
- Parses JSON and decodes the PAYMENT-RESPONSE header when provided.
- Tests the payment allowlist and response parser with mocked requests.

## Run

Requires Node.js 20+, network access and a **disposable test wallet**, provisioned for the 0.01 USDC test purchase and relevant Base fees. Do NOT use a primary wallet's key or recovery phrase.

```bash
npm install
cp .env.example .env
# Set EVM_SPENDING_PRIVATE_KEY in .env for a disposable wallet
npm test
npm run brief
```

Or use in a LangChain application:

```js
import { makeBlockchainIQBriefTool } from './src/tool.mjs';
const marketBrief = makeBlockchainIQBriefTool({
  spendingPrivateKey: process.env.EVM_SPENDING_PRIVATE_KEY,
});
const result = await marketBrief.invoke({});
console.log(result);
```

**Security:** Never commit real keys, and do not invoke unattended without a budget and rate limits. The source quote is checked for chain, asset, scheme and maximum unit price. Each successful invocation may incur a real payment.

**Verification status (2026-11-13):** Five unit tests passed locally, and JavaScript modules passed syntax checks. Dependency installation, live paid call, on-chain settlement and transaction-hash capture **have not** been performed in this environment. This repository is not yet a qualifying payout claim. The sponsor requires a transaction hash for a real paid call. Do not represent this code as tested end-to-end.

**Licence:** MIT, original integration source.
