import { tool } from '@langchain/core/tools';
import { z } from 'zod';
import { wrapFetchWithPaymentFromConfig, decodePaymentResponseHeader } from '@x402/fetch';
import { ExactEvmScheme } from '@x402/evm';
import { privateKeyToAccount } from 'viem/accounts';
import { BASE_MAINNET, readBlockchainIQBrief, selectAllowedPayment } from './brief-core.mjs';

/** Optional LangChain tool. Uses a disposable spending key; never log secrets. */
export function makeBlockchainIQBriefTool({ spendingPrivateKey, fetchImpl = fetch } = {}) {
  if (typeof spendingPrivateKey !== 'string' || !/^0x[0-9a-fA-F]{64}$/.test(spendingPrivateKey)) {
    throw new Error('Set a 0x-prefixed 32-byte EVM spending key via environment variable');
  }
  const account = privateKeyToAccount(spendingPrivateKey);
  const paidFetch = wrapFetchWithPaymentFromConfig(fetchImpl, {
    schemes: [{ network: BASE_MAINNET, client: new ExactEvmScheme(account) }],
    paymentRequirementsSelector: selectAllowedPayment,
  });

  return tool(async () => {
    const { data, settlementHeader } = await readBlockchainIQBrief(paidFetch);
    const settlement = settlementHeader ? decodePaymentResponseHeader(settlementHeader) : null;
    return JSON.stringify({ resource: 'brief', data, settlement });
  }, {
    name: 'blockchain_iq_market_brief_paid',
    description: 'Purchase Blockchain IQ crypto brief using x402 USDC on Base (maximum 0.01 USDC); return JSON and any settlement proof.',
    schema: z.object({}),
  });
}
