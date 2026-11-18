import test from 'node:test';
import assert from 'node:assert/strict';
import { atomicFromDecimal, formatAtomic, parseCsv, reconcile, toCsv } from './core.mjs';

const txA = 'a'.repeat(64);
const txB = 'b'.repeat(64);

const row = (txid, output_index, asset, network, direction, amount) => ({ txid, output_index, asset, network, direction, amount });

test('converts BTC satoshis and Base USDC micro-units exactly without floating point', () => {
  assert.equal(atomicFromDecimal('0.00123456', 'BTC', 'bitcoin-mainnet'), '123456');
  assert.equal(atomicFromDecimal('123.456789', 'USDC', 'base-mainnet'), '123456789');
  assert.equal(formatAtomic('123456', 'BTC', 'bitcoin-mainnet'), '0.00123456');
  assert.equal(formatAtomic('123456789', 'USDC', 'base-mainnet'), '123.456789');
});

test('rejects excess precision, negative amounts and unsupported asset/network pairs', () => {
  assert.throws(() => atomicFromDecimal('0.000000001', 'BTC', 'bitcoin-mainnet'), /at most 8 decimal places/);
  assert.throws(() => atomicFromDecimal('-1', 'BTC', 'bitcoin-mainnet'), /Invalid non-negative decimal amount/);
  assert.throws(() => atomicFromDecimal('1', 'USDC', 'bitcoin-mainnet'), /Unsupported asset\/network pair/);
});

test('parses quoted CSV fields, escaped quotes and CRLF', () => {
  const rows = parseCsv('txid,reference,amount\r\n"' + txA + '","invoice, \"\"north\"\"",1.25\r\n');
  assert.equal(rows.length, 1);
  assert.equal(rows[0].reference, 'invoice, "north"');
  assert.equal(rows[0].amount, '1.25');
});

test('matches exact BTC and Base USDC outputs', () => {
  const chain = [
    row(txA, '0', 'BTC', 'bitcoin-mainnet', 'in', '0.0012'),
    row(txB, '3', 'USDC', 'base-mainnet', 'in', '250.00'),
  ];
  const ledger = [
    row(txA, '0', 'BTC', 'bitcoin-mainnet', 'in', '0.0012'),
    row(txB, '3', 'USDC', 'base-mainnet', 'in', '250.00'),
  ];
  const result = reconcile(chain, ledger);
  assert.deepEqual(result.rows.map((item) => item.status), ['MATCHED', 'MATCHED']);
  assert.equal(result.counts.MATCHED, 2);
  assert.equal(result.totals.invalid_rows, 0);
});

test('flags amount and output-index mismatches', () => {
  const result = reconcile(
    [row(txA, '0', 'BTC', 'bitcoin-mainnet', 'out', '0.0005'), row(txB, '2', 'USDC', 'base-mainnet', 'in', '10')],
    [row(txA, '0', 'BTC', 'bitcoin-mainnet', 'out', '0.0004'), row(txB, '3', 'USDC', 'base-mainnet', 'in', '10')],
  );
  assert.deepEqual(result.rows.map((item) => item.status), ['AMOUNT_MISMATCH', 'OUTPUT_INDEX_MISMATCH']);
  assert.equal(result.rows[0].difference, '0.0001');
});


test('normalizes output indexes with leading zeroes', () => {
  const result = reconcile(
    [row(txA, '00', 'BTC', 'bitcoin-mainnet', 'in', '0.001')],
    [row(txA, '0', 'BTC', 'bitcoin-mainnet', 'in', '0.001')],
  );
  assert.equal(result.rows[0].status, 'MATCHED');
});

test('preserves the sign of chain amount minus ledger amount', () => {
  const result = reconcile(
    [row(txA, '0', 'BTC', 'bitcoin-mainnet', 'in', '0.0004')],
    [row(txA, '0', 'BTC', 'bitcoin-mainnet', 'in', '0.0005')],
  );
  assert.equal(result.rows[0].difference, '-0.0001');
});

test('flags chain-only and ledger-only records separately', () => {
  const result = reconcile(
    [row(txA, '0', 'BTC', 'bitcoin-mainnet', 'in', '0.1')],
    [row(txB, '0', 'BTC', 'bitcoin-mainnet', 'out', '0.2')],
  );
  assert.deepEqual(result.rows.map((item) => item.status).sort(), ['MISSING_IN_LEDGER', 'MISSING_ON_CHAIN']);
});

test('flags duplicate output keys rather than silently double-counting', () => {
  const result = reconcile(
    [row(txA, '0', 'BTC', 'bitcoin-mainnet', 'in', '0.1'), row(txA, '0', 'BTC', 'bitcoin-mainnet', 'in', '0.1')],
    [row(txA, '0', 'BTC', 'bitcoin-mainnet', 'in', '0.1')],
  );
  assert.equal(result.rows.length, 1);
  assert.equal(result.rows[0].status, 'DUPLICATE_KEY');
});

test('marks multiple rows without output indexes ambiguous', () => {
  const result = reconcile(
    [row(txA, '', 'BTC', 'bitcoin-mainnet', 'in', '0.1'), row(txA, '', 'BTC', 'bitcoin-mainnet', 'in', '0.2')],
    [row(txA, '', 'BTC', 'bitcoin-mainnet', 'in', '0.1')],
  );
  assert.equal(result.rows.filter((item) => item.status === 'AMBIGUOUS').length, 3);
});

test('invalid rows are reported and excluded from automatic matching', () => {
  const result = reconcile(
    [{ txid: 'not-a-txid', asset: 'BTC', network: 'bitcoin-mainnet', direction: 'in', amount: '0.1', _row: 7 }],
    [],
  );
  assert.equal(result.errors.length, 1);
  assert.equal(result.errors[0].row, 7);
  assert.equal(result.totals.chain_valid_rows, 0);
});

test('exports a safely quoted CSV report', () => {
  const csv = toCsv([{ status: 'MATCHED', txid: txA, note: 'exact, safe "match"' }]);
  assert.match(csv, /"exact, safe ""match"""/);
  assert.match(csv, /status,txid,output_index/);
});
