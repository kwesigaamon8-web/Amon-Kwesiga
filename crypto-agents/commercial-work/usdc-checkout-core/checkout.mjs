import { createHmac, timingSafeEqual } from 'node:crypto';

// Circle native USDC mainnet contracts; reject bridged tokens by default.
export const NATIVE_USDC = Object.freeze({
  8453: '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913',
  137: '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359',
});
const addr = /^0x[0-9a-fA-F]{40}$/;
const txid = /^0x[0-9a-fA-F]{64}$/;
const exact = x => typeof x === 'string' && /^\d+$/.test(x) && BigInt(x) > 0n;
const same = (a, b) => String(a).toLowerCase() === String(b).toLowerCase();

export function createIntent({ orderId, chainId, receiver, usdc, createdAt }) {
  if (!/^[A-Za-z0-9_-]{1,80}$/.test(orderId || '')) throw Error('BAD_ORDER_ID');
  if (!Object.hasOwn(NATIVE_USDC, chainId)) throw Error('UNSUPPORTED_CHAIN');
  if (!addr.test(receiver || '')) throw Error('BAD_RECEIVER');
  if (typeof usdc !== 'string' || !/^(0|[1-9]\d*)(\.\d{1,6})?$/.test(usdc)) throw Error('BAD_USDC_DECIMAL');
  const [whole, dec = ''] = usdc.split('.');
  const micro = BigInt(whole) * 1000000n + BigInt((dec + '000000').slice(0, 6));
  if (micro <= 0n || micro > 1000000000000000000n) throw Error('AMOUNT_OUT_OF_RANGE');
  if (!Number.isSafeInteger(createdAt) || createdAt <= 0) throw Error('BAD_CREATED_AT');
  return Object.freeze({ orderId, chainId: Number(chainId), receiver: receiver.toLowerCase(),
    token: NATIVE_USDC[chainId], amountMicro: String(micro), createdAt });
}

export function createLedger() {
  // Educational in-memory adapter ONLY. Replace with a durable ACID DB before accepting payment.
  return { seenTxLogs: new Map(), paidOrders: new Map() };
}

function verifiedSignature(raw, signature, secret) {
  if (typeof raw !== 'string' || raw.length > 16384) throw Error('BAD_RAW_BODY');
  if (typeof secret !== 'string' || secret.length < 32) throw Error('BAD_SIGNING_SECRET');
  if (typeof signature !== 'string' || !/^sha256=[0-9a-f]{64}$/i.test(signature)) throw Error('BAD_SIGNATURE');
  const received = Buffer.from(signature.slice(7), 'hex');
  const expected = createHmac('sha256', secret).update(raw).digest();
  if (!timingSafeEqual(received, expected)) throw Error('SIGNATURE_MISMATCH');
}

function expectEvent(e, intent) {
  if (!e || typeof e !== 'object' || Array.isArray(e)) throw Error('BAD_EVENT');
  if (e.orderId !== intent.orderId || e.chainId !== intent.chainId) throw Error('WRONG_ORDER_OR_CHAIN');
  if (!same(e.token, intent.token) || !same(e.receiver, intent.receiver)) throw Error('WRONG_TOKEN_OR_RECEIVER');
  if (!exact(e.amountMicro) || e.amountMicro !== intent.amountMicro) throw Error('WRONG_AMOUNT');
  if (!txid.test(e.txHash || '') || !Number.isSafeInteger(e.logIndex) || e.logIndex < 0) throw Error('BAD_TX_LOG');
  if (e.removed !== false) throw Error('REMOVED_OR_UNKNOWN_LOG');
}

// Webhook HMAC protects message authenticity, NOT chain truth.
// verifyOnChain must independently query an allowlisted RPC/receipt indexer.
export async function processSignedWebhook({ rawBody, signature, secret, intent, ledger, verifyOnChain,
  minConfirmations = 12 }) {
  verifiedSignature(rawBody, signature, secret);
  if (!ledger?.seenTxLogs || !ledger?.paidOrders || typeof verifyOnChain !== 'function') {
    throw Error('DURABLE_LEDGER_AND_RPC_ADAPTER_REQUIRED');
  }
  if (!Number.isSafeInteger(minConfirmations) || minConfirmations < 1) throw Error('BAD_FINALITY_POLICY');
  const event = JSON.parse(rawBody);
  expectEvent(event, intent);
  const key = intent.chainId + ':' + event.txHash.toLowerCase() + ':' + event.logIndex;
  const previous = ledger.seenTxLogs.get(key);
  if (previous && previous !== intent.orderId) throw Error('TX_LOG_ALREADY_USED_FOR_OTHER_ORDER');
  const paid = ledger.paidOrders.get(intent.orderId);
  if (paid && paid !== key) throw Error('ORDER_ALREADY_PAID_BY_DIFFERENT_TX');
  // Always reverify even on replay: a reorg can invalidate earlier confirmations.
  const chain = await verifyOnChain({ chainId: intent.chainId, txHash: event.txHash, logIndex: event.logIndex });
  if (!chain || chain.ok !== true || chain.removed !== false ||
    chain.chainId !== intent.chainId || !same(chain.token, intent.token) ||
    !same(chain.receiver, intent.receiver) || chain.amountMicro !== intent.amountMicro ||
    !Number.isSafeInteger(chain.confirmations) || chain.confirmations < minConfirmations ||
    !same(chain.txHash, event.txHash) || chain.logIndex !== event.logIndex) {
    throw Error('CHAIN_PROOF_MISSING_MISMATCH_OR_UNFINAL');
  }
  if (paid === key) return { status: 'ALREADY_ACCEPTED', orderId: intent.orderId, key };
  // Demo only: these two writes must be ONE atomic DB transaction in production.
  ledger.seenTxLogs.set(key, intent.orderId);
  ledger.paidOrders.set(intent.orderId, key);
  return { status: 'CONFIRMED_BY_RPC_ADAPTER', orderId: intent.orderId, key };
}
