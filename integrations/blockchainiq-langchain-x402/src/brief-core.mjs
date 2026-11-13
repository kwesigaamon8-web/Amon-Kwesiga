/** Blockchain IQ brief URL and strict, zero-surprise payment policy. */
export const ENDPOINT = 'https://www.blockchainiq.co/api/x402/v1/brief';
export const BASE_MAINNET = 'eip155:8453';
export const BASE_USDC = '0x833589fCD6eDb6E08f4C7C32D4f71b54bdA02913';
export const MAX_USDC_MICRO = 10_000n; // 0.01 USDC

export function selectAllowedPayment(version, accepts) {
  if (!Array.isArray(accepts) || accepts.length === 0) {
    throw new Error('No x402 payment options quoted');
  }
  const permitted = accepts.filter((p) => {
    if (p.network !== BASE_MAINNET) return false;
    if ((p.asset ?? '').toLowerCase() !== BASE_USDC.toLowerCase()) return false;
    if ((p.scheme ?? '') !== 'exact') return false;
    const raw = p.amount ?? p.value;
    if (typeof raw !== 'string' && typeof raw !== 'number') return false;
    try { const n = BigInt(raw); return n > 0n && n <= MAX_USDC_MICRO; }
    catch { return false; }
  });
  if (permitted.length === 0) {
    throw new Error('No allowed Base USDC quote <= 0.01 USDC. Refusing payment.');
  }
  return permitted.sort((a, b) => {
    const av = BigInt(a.amount ?? a.value);
    const bv = BigInt(b.amount ?? b.value);
    return av < bv ? -1 : av > bv ? 1 : 0;
  })[0];
}

export async function readBlockchainIQBrief(paidFetch) {
  if (typeof paidFetch !== 'function') throw new TypeError('paidFetch must be a function');
  const response = await paidFetch(ENDPOINT, { method: 'GET', redirect: 'error' });
  if (!response || !response.ok) {
    throw new Error(`Blockchain IQ brief failed (HTTP ${response?.status ?? 'unknown'})`);
  }
  const data = await response.json();
  if (!data || typeof data !== 'object' || Array.isArray(data)) {
    throw new Error('Expected a JSON object from Blockchain IQ');
  }
  const settlementHeader = response.headers?.get?.('PAYMENT-RESPONSE') ?? null;
  return { data, settlementHeader };
}
