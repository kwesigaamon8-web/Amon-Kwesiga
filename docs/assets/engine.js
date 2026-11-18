/* B1/B2 Studio browser-side data tools. MIT-style permission: original code, 2026. */
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.StudioTools = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const MAX_BYTES = 5 * 1024 * 1024;
  const MAX_ROWS = 30000;
  function cleanHeader(name) { return String(name).replace(/^\uFEFF/, '').trim(); }
  function parseCSV(input) {
    if (typeof input !== 'string') throw new Error('CSV must be text.');
    if (new TextEncoder().encode(input).length > MAX_BYTES) throw new Error('File exceeds the 5 MB browser limit.');
    let rows = [], row = [], part = '', quoted = false, fieldStart = true, closedQuote = false;
    for (let i = 0; i < input.length; i++) {
      const c = input[i];
      if (quoted) {
        if (c === '"') {
          if (input[i + 1] === '"') { part += '"'; i++; }
          else { quoted = false; closedQuote = true; }
        } else part += c;
      } else if (c === '"') {
        if (!fieldStart) throw new Error('Unexpected quote at character ' + (i + 1) + '.');
        quoted = true;
      } else if (c === ',') {
        row.push(part); part = ''; fieldStart = true; closedQuote = false;
      } else if (c === '\r' || c === '\n') {
        if (c === '\r' && input[i + 1] === '\n') i++;
        row.push(part); part = ''; fieldStart = true; closedQuote = false;
        if (row.some(x => x !== '') || row.length > 1) rows.push(row);
        row = [];
        if (rows.length > MAX_ROWS + 1) throw new Error('CSV exceeds the 30,000-row limit.');
      } else { if (closedQuote) throw new Error('Unexpected text after quoted field at character ' + (i + 1) + '.'); part += c; fieldStart = false; }
    }
    if (quoted) throw new Error('Unclosed quoted field.');
    if (part.length || row.length) { row.push(part); if (row.some(x => x !== '') || row.length > 1) rows.push(row); }
    if (!rows.length) throw new Error('No CSV rows found.');
    const fields = rows.shift().map(cleanHeader);
    if (fields.some(x => !x)) throw new Error('Column headers must not be empty.');
    if (new Set(fields.map(x => x.toLowerCase())).size !== fields.length) throw new Error('Duplicate column headers detected.');
    if (fields.length > 100) throw new Error('Too many columns (maximum 100).');
    const items = rows.map((cells, i) => {
      if (cells.length !== fields.length) throw new Error('Row ' + (i + 2) + ' has ' + cells.length + ' columns; expected ' + fields.length + '.');
      return Object.fromEntries(fields.map((field, n) => [field, cells[n]]));
    });
    return { fields, items };
  }
  function parseJSON(input) {
    if (new TextEncoder().encode(input).length > MAX_BYTES) throw new Error('File exceeds the 5 MB browser limit.');
    let items;
    try { items = JSON.parse(input); } catch (_) { throw new Error('Invalid JSON. Supply an array of flat objects.'); }
    if (!Array.isArray(items)) throw new Error('JSON root must be an array.');
    if (items.length > MAX_ROWS) throw new Error('Too many JSON records (maximum 30,000).');
    if (items.some(x => !x || typeof x !== 'object' || Array.isArray(x))) throw new Error('Every JSON array entry must be an object.');
    const fields = [];
    for (const record of items) {
      for (const k of Object.keys(record)) {
        if (!fields.includes(k)) fields.push(k);
        const v = record[k];
        if (v && typeof v === 'object') throw new Error('Nested JSON values are not supported.');
      }
    }
    if (fields.length > 100) throw new Error('Too many columns (maximum 100).');
    return { fields, items: items.map(x => Object.fromEntries(fields.map(k => [k, x[k] == null ? '' : String(x[k])])))};
  }
  function csvEscape(v, excelSafe) {
    let s = String(v == null ? '' : v);
    // Formula injection prevention for CSV files opened in spreadsheet software.
    // Exact raw string preservation is available by passing excelSafe:false.
    if (excelSafe && /^[\s]*[=+@-]/.test(s) && !/^[+-]?(?:\d+\.?\d*|\.\d+)$/.test(s.trim())) s = "'" + s;
    return /[",\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  function toCSV(dataset, options = {}) {
    const fields = dataset.fields, safe = options.excelSafe !== false;
    return [fields.map(f => csvEscape(f, safe)).join(','), ...dataset.items.map(row => fields.map(f => csvEscape(row[f], safe)).join(','))].join('\r\n') + '\r\n';
  }
  function analyze(dataset, keyField, amountField) {
    const { fields, items } = dataset;
    if (keyField && !fields.includes(keyField)) throw new Error('Key field not found.');
    if (amountField && !fields.includes(amountField)) throw new Error('Amount field not found.');
    const duplicates = [], missing = {}, invalidAmounts = [];
    const seen = new Map(); let total = 0, amountCount = 0;
    for (const f of fields) missing[f] = 0;
    items.forEach((item, idx) => {
      for (const f of fields) if (String(item[f] == null ? '' : item[f]).trim() === '') missing[f]++;
      if (keyField) {
        const key = String(item[keyField] == null ? '' : item[keyField]).trim();
        if (key !== '') {
          if (seen.has(key)) duplicates.push({ row: idx + 2, firstRow: seen.get(key), value: key });
          else seen.set(key, idx + 2);
        }
      }
      if (amountField) {
        const value = String(item[amountField] == null ? '' : item[amountField]).trim();
        if (value !== '') {
          // Reject thousands separators/currency characters rather than silently miscalculating.
          const clean = value;
          if (!/^[+-]?(?:\d+\.?\d*|\.\d+)$/.test(clean) || !Number.isFinite(Number(clean))) invalidAmounts.push(idx + 2);
          else { total += Number(clean); amountCount++; }
        }
      }
    });
    return { rowCount: items.length, columns: fields.length, fields, missing, duplicates,
      duplicateCount: duplicates.length, keyField: keyField || null, amountField: amountField || null,
      amountTotal: amountField ? Number(total.toFixed(6)) : null, amountRows: amountCount,
      invalidAmountRows: invalidAmounts, checkedLocally: true,
      note: 'Browser-only descriptive checks. Not an audit opinion, financial assurance, or payment verification.'};
  }
  return {parseCSV, parseJSON, toCSV, analyze, MAX_BYTES};
});