export const SUPPORTED_RAILS = Object.freeze({
  'BTC|BITCOIN-MAINNET': 8,
  'USDC|BASE-MAINNET': 6,
});

const TXID_RE = /^(?:0x)?[0-9a-f]{64}$/i;
const INTEGER_RE = /^\d+$/;

export function parseCsv(input) {
  const text = String(input ?? '').replace(/^\uFEFF/, '');
  const rows = [];
  let row = [];
  let cell = '';
  let quoted = false;

  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') {
        cell += '"';
        i += 1;
      } else if (ch === '"') {
        quoted = false;
      } else {
        cell += ch;
      }
    } else if (ch === '"' && cell.length === 0) {
      quoted = true;
    } else if (ch === ',') {
      row.push(cell);
      cell = '';
    } else if (ch === '\n') {
      row.push(cell.replace(/\r$/, ''));
      if (row.some((value) => value.trim() !== '')) rows.push(row);
      row = [];
      cell = '';
    } else {
      cell += ch;
    }
  }

  if (quoted) throw new Error('CSV contains an unclosed quoted field.');
  if (cell.length > 0 || row.length > 0) {
    row.push(cell.replace(/\r$/, ''));
    if (row.some((value) => value.trim() !== '')) rows.push(row);
  }
  if (rows.length === 0) return [];

  const headers = rows.shift().map((value) => value.trim().toLowerCase());
  if (headers.some((header) => !header)) throw new Error('CSV has an empty column heading.');
  if (new Set(headers).size !== headers.length) throw new Error('CSV has duplicate column headings.');

  return rows.map((values, index) => {
    const record = { _row: index + 2 };
    headers.forEach((header, column) => {
      record[header] = String(values[column] ?? '').trim();
    });
    return record;
  });
}

export function atomicFromDecimal(value, asset, network) {
  const decimals = SUPPORTED_RAILS[`${String(asset).trim().toUpperCase()}|${String(network).trim().toUpperCase()}`];
  if (decimals === undefined) throw new Error(`Unsupported asset/network pair: ${asset} on ${network}.`);
  const raw = String(value ?? '').trim();
  if (!/^(?:\d+)(?:\.\d+)?$/.test(raw)) throw new Error(`Invalid non-negative decimal amount: ${raw || '(blank)'}.`);
  const [whole, fraction = ''] = raw.split('.');
  if (fraction.length > decimals) throw new Error(`${asset} supports at most ${decimals} decimal places on ${network}.`);
  const scale = 10n ** BigInt(decimals);
  return (BigInt(whole) * scale + BigInt((fraction + '0'.repeat(decimals)).slice(0, decimals) || '0')).toString();
}

export function formatAtomic(value, asset, network) {
  const decimals = SUPPORTED_RAILS[`${String(asset).trim().toUpperCase()}|${String(network).trim().toUpperCase()}`];
  if (decimals === undefined) return String(value ?? '');
  if (!INTEGER_RE.test(String(value))) return '';
  const amount = BigInt(value);
  const scale = 10n ** BigInt(decimals);
  const whole = amount / scale;
  const fraction = (amount % scale).toString().padStart(decimals, '0').replace(/0+$/, '');
  return fraction ? `${whole}.${fraction}` : whole.toString();
}

function normalizeDirection(value) {
  const direction = String(value ?? '').trim().toLowerCase();
  const aliases = { incoming: 'in', inbound: 'in', received: 'in', outgoing: 'out', outbound: 'out', sent: 'out' };
  return aliases[direction] ?? direction;
}

function normalizeRows(rows, source) {
  const normalized = [];
  const errors = [];

  rows.forEach((raw, index) => {
    const rowNumber = Number(raw._row) || index + 2;
    const txidInput = String(raw.txid ?? '').trim();
    const txid = txidInput.replace(/^0x/i, '').toLowerCase();
    const asset = String(raw.asset ?? '').trim().toUpperCase();
    const network = String(raw.network ?? '').trim().toUpperCase();
    const direction = normalizeDirection(raw.direction);
    const outputIndexInput = raw.output_index ?? raw.vout ?? raw.log_index ?? '';
    const outputIndex = String(outputIndexInput).trim();
    const amountInput = String(raw.amount_atomic ?? raw.amount ?? '').trim();
    let amountAtomic = '';

    const rowErrors = [];
    if (!TXID_RE.test(txidInput)) rowErrors.push('txid must be a 64-character hexadecimal transaction ID (optional 0x prefix).');
    if (!asset) rowErrors.push('asset is required.');
    if (!network) rowErrors.push('network is required.');
    if (!['in', 'out'].includes(direction)) rowErrors.push('direction must be in/incoming or out/outgoing.');
    if (outputIndex && !INTEGER_RE.test(outputIndex)) rowErrors.push('output_index/vout/log_index must be a non-negative integer.');

    try {
      if (raw.amount_atomic !== undefined && String(raw.amount_atomic).trim() !== '') {
        if (!INTEGER_RE.test(amountInput)) throw new Error('amount_atomic must be a non-negative integer string.');
        amountAtomic = BigInt(amountInput).toString();
        const decimals = SUPPORTED_RAILS[`${asset}|${network}`];
        if (decimals === undefined) throw new Error(`Unsupported asset/network pair: ${asset} on ${network}.`);
      } else {
        amountAtomic = atomicFromDecimal(amountInput, asset, network);
      }
    } catch (error) {
      rowErrors.push(error.message);
    }

    if (rowErrors.length) {
      errors.push({ source, row: rowNumber, errors: rowErrors });
      return;
    }

    normalized.push({
      source,
      row: rowNumber,
      txid,
      outputIndex: outputIndex || null,
      asset,
      network,
      direction,
      amountAtomic,
      amount: formatAtomic(amountAtomic, asset, network),
      date: String(raw.date ?? '').trim(),
      reference: String(raw.reference ?? raw.memo ?? '').trim(),
      account: String(raw.account ?? '').trim(),
    });
  });

  return { rows: normalized, errors };
}

function comparePair(chain, ledger, matchMethod) {
  const common = {
    txid: chain.txid,
    output_index: chain.outputIndex ?? ledger.outputIndex ?? '',
    asset: chain.asset,
    network: chain.network,
    direction: chain.direction,
    chain_amount: chain.amount,
    ledger_amount: ledger.amount,
    chain_row: chain.row,
    ledger_row: ledger.row,
    match_method: matchMethod,
  };

  if (chain.asset !== ledger.asset || chain.network !== ledger.network || chain.direction !== ledger.direction) {
    return { ...common, status: 'DIMENSION_MISMATCH', difference: '', note: 'Asset, network or direction differs. Review the source records.' };
  }
  if (chain.amountAtomic !== ledger.amountAtomic) {
    const difference = BigInt(chain.amountAtomic) - BigInt(ledger.amountAtomic);
    const formattedDifference = difference < 0n
      ? `-${formatAtomic((-difference).toString(), chain.asset, chain.network)}`
      : formatAtomic(difference.toString(), chain.asset, chain.network);
    return { ...common, status: 'AMOUNT_MISMATCH', difference: formattedDifference, note: 'Difference is chain amount minus ledger amount. Fees and exchange-rate valuation are not netted here.' };
  }
  return { ...common, status: 'MATCHED', difference: '0', note: matchMethod === 'txid-only' ? 'Matched by transaction ID only; add an output index for stronger matching.' : 'Exact transaction/output, asset, network, direction and amount match.' };
}

export function reconcile(chainInput, ledgerInput) {
  const chain = normalizeRows(chainInput, 'chain');
  const ledger = normalizeRows(ledgerInput, 'ledger');
  const byTx = (rows) => {
    const map = new Map();
    rows.forEach((row) => {
      if (!map.has(row.txid)) map.set(row.txid, []);
      map.get(row.txid).push(row);
    });
    return map;
  };
  const chainByTx = byTx(chain.rows);
  const ledgerByTx = byTx(ledger.rows);
  const txids = [...new Set([...chainByTx.keys(), ...ledgerByTx.keys()])].sort();
  const results = [];

  for (const txid of txids) {
    const cRows = chainByTx.get(txid) ?? [];
    const lRows = ledgerByTx.get(txid) ?? [];

    if (cRows.length === 0) {
      lRows.forEach((row) => results.push({ txid, output_index: row.outputIndex ?? '', asset: row.asset, network: row.network, direction: row.direction, chain_amount: '', ledger_amount: row.amount, difference: '', chain_row: '', ledger_row: row.row, match_method: '', status: 'MISSING_ON_CHAIN', note: 'Ledger row has no matching transaction in the chain export.' }));
      continue;
    }
    if (lRows.length === 0) {
      cRows.forEach((row) => results.push({ txid, output_index: row.outputIndex ?? '', asset: row.asset, network: row.network, direction: row.direction, chain_amount: row.amount, ledger_amount: '', difference: '', chain_row: row.row, ledger_row: '', match_method: '', status: 'MISSING_IN_LEDGER', note: 'Chain output has no matching ledger row.' }));
      continue;
    }

    if (cRows.length === 1 && lRows.length === 1) {
      const c = cRows[0];
      const l = lRows[0];
      if (c.outputIndex && l.outputIndex && c.outputIndex !== l.outputIndex) {
        results.push({ txid, output_index: `${c.outputIndex} ≠ ${l.outputIndex}`, asset: c.asset, network: c.network, direction: c.direction, chain_amount: c.amount, ledger_amount: l.amount, difference: '', chain_row: c.row, ledger_row: l.row, match_method: 'txid-only', status: 'OUTPUT_INDEX_MISMATCH', note: 'Transaction IDs match but output indexes differ.' });
      } else {
        results.push(comparePair(c, l, c.outputIndex && l.outputIndex ? 'txid+output_index' : 'txid-only'));
      }
      continue;
    }

    const chainIndexed = cRows.filter((row) => row.outputIndex !== null);
    const ledgerIndexed = lRows.filter((row) => row.outputIndex !== null);
    const chainUnindexed = cRows.filter((row) => row.outputIndex === null);
    const ledgerUnindexed = lRows.filter((row) => row.outputIndex === null);

    if (chainUnindexed.length || ledgerUnindexed.length) {
      chainUnindexed.forEach((row) => results.push({ txid, output_index: '', asset: row.asset, network: row.network, direction: row.direction, chain_amount: row.amount, ledger_amount: '', difference: '', chain_row: row.row, ledger_row: '', match_method: '', status: 'AMBIGUOUS', note: 'Multiple rows share this transaction ID and this row has no output index; automatic matching is unsafe.' }));
      ledgerUnindexed.forEach((row) => results.push({ txid, output_index: '', asset: row.asset, network: row.network, direction: row.direction, chain_amount: '', ledger_amount: row.amount, difference: '', chain_row: '', ledger_row: row.row, match_method: '', status: 'AMBIGUOUS', note: 'Multiple rows share this transaction ID and this row has no output index; automatic matching is unsafe.' }));
    }

    const cMap = new Map();
    const lMap = new Map();
    chainIndexed.forEach((row) => { if (!cMap.has(row.outputIndex)) cMap.set(row.outputIndex, []); cMap.get(row.outputIndex).push(row); });
    ledgerIndexed.forEach((row) => { if (!lMap.has(row.outputIndex)) lMap.set(row.outputIndex, []); lMap.get(row.outputIndex).push(row); });
    const indexes = [...new Set([...cMap.keys(), ...lMap.keys()])].sort((a, b) => Number(a) - Number(b));

    for (const outputIndex of indexes) {
      const cs = cMap.get(outputIndex) ?? [];
      const ls = lMap.get(outputIndex) ?? [];
      if (cs.length > 1 || ls.length > 1) {
        results.push({ txid, output_index: outputIndex, asset: cs[0]?.asset ?? ls[0]?.asset ?? '', network: cs[0]?.network ?? ls[0]?.network ?? '', direction: cs[0]?.direction ?? ls[0]?.direction ?? '', chain_amount: cs.map((x) => x.amount).join(' | '), ledger_amount: ls.map((x) => x.amount).join(' | '), difference: '', chain_row: cs.map((x) => x.row).join('|'), ledger_row: ls.map((x) => x.row).join('|'), match_method: 'txid+output_index', status: 'DUPLICATE_KEY', note: 'Duplicate output index on one or both sides; resolve manually.' });
      } else if (cs.length === 0) {
        const row = ls[0];
        results.push({ txid, output_index: outputIndex, asset: row.asset, network: row.network, direction: row.direction, chain_amount: '', ledger_amount: row.amount, difference: '', chain_row: '', ledger_row: row.row, match_method: 'txid+output_index', status: 'MISSING_ON_CHAIN', note: 'Ledger output index has no matching chain row.' });
      } else if (ls.length === 0) {
        const row = cs[0];
        results.push({ txid, output_index: outputIndex, asset: row.asset, network: row.network, direction: row.direction, chain_amount: row.amount, ledger_amount: '', difference: '', chain_row: row.row, ledger_row: '', match_method: 'txid+output_index', status: 'MISSING_IN_LEDGER', note: 'Chain output index has no matching ledger row.' });
      } else {
        results.push(comparePair(cs[0], ls[0], 'txid+output_index'));
      }
    }
  }

  const allErrors = [...chain.errors, ...ledger.errors];
  const counts = results.reduce((acc, row) => { acc[row.status] = (acc[row.status] ?? 0) + 1; return acc; }, {});
  return {
    rows: results,
    errors: allErrors,
    counts,
    totals: { chain_valid_rows: chain.rows.length, ledger_valid_rows: ledger.rows.length, result_rows: results.length, invalid_rows: allErrors.length },
  };
}

export function toCsv(rows) {
  const columns = ['status', 'txid', 'output_index', 'asset', 'network', 'direction', 'chain_amount', 'ledger_amount', 'difference', 'chain_row', 'ledger_row', 'match_method', 'note'];
  const quote = (value) => {
    const text = String(value ?? '');
    return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
  };
  return [columns.join(','), ...rows.map((row) => columns.map((column) => quote(row[column])).join(','))].join('\r\n');
}
