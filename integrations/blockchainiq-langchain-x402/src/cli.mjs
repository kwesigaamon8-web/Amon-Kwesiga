import 'dotenv/config';
import { makeBlockchainIQBriefTool } from './tool.mjs';
const key = process.env.EVM_SPENDING_PRIVATE_KEY;
if (!key) {
  console.error('EVM_SPENDING_PRIVATE_KEY not set; no request or payment made.');
  process.exitCode = 2;
} else {
  const t = makeBlockchainIQBriefTool({ spendingPrivateKey: key });
  // A real payment of at most 0.01 USDC may occur on invocation.
  console.log(await t.invoke({}));
}
