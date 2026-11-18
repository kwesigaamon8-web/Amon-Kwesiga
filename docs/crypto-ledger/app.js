import { parseCsv, reconcile, toCsv } from './core.mjs';

const byId = (id) => document.getElementById(id);
const chainCsv = byId('chainCsv');
const ledgerCsv = byId('ledgerCsv');
const runMessage = byId('runMessage');
const resultsSection = byId('resultsSection');
const resultsBody = byId('resultsBody');
const summary = byId('summary');
const errorsBox = byId('errors');
let lastReport = null;

const demoChain = `txid,output_index,asset,network,direction,amount,fee,date,reference
${'a'.repeat(64)},0,BTC,bitcoin-mainnet,in,0.00120000,0.00001000,2026-11-18,invoice-001
${'b'.repeat(64)},3,USDC,base-mainnet,in,250.000000,0.150000,2026-11-18,invoice-002
${'c'.repeat(64)},1,BTC,bitcoin-mainnet,out,0.00050000,0.00001000,2026-11-18,expense-003
${'d'.repeat(64)},0,BTC,bitcoin-mainnet,in,0.00070000,0.00001000,2026-11-18,unbooked-004
${'e'.repeat(64)},0,USDC,base-mainnet,in,100.000000,0.100000,2026-11-18,unbooked-005`;

const demoLedger = `txid,output_index,asset,network,direction,amount,date,account,reference
${'a'.repeat(64)},0,BTC,bitcoin-mainnet,in,0.00120000,2026-11-18,Crypto asset,invoice-001
${'b'.repeat(64)},3,USDC,base-mainnet,in,250.000000,2026-11-18,Stablecoin asset,invoice-002
${'c'.repeat(64)},1,BTC,bitcoin-mainnet,out,0.00040000,2026-11-18,Operating expense,expense-003
${'f'.repeat(64)},0,BTC,bitcoin-mainnet,in,0.00200000,2026-11-18,Crypto asset,ledger-only-006`;

function addTextCell(row, value, className = '') {
  const cell = document.createElement('td');
  cell.textContent = String(value ?? '');
  if (className) cell.className = className;
  row.append(cell);
}

function renderReport(report) {
  const cards = [
    ['Matched', report.counts.MATCHED ?? 0],
    ['Missing in ledger', report.counts.MISSING_IN_LEDGER ?? 0],
    ['Missing on chain', report.counts.MISSING_ON_CHAIN ?? 0],
    ['Exceptions', (report.counts.AMOUNT_MISMATCH ?? 0) + (report.counts.DIMENSION_MISMATCH ?? 0) + (report.counts.OUTPUT_INDEX_MISMATCH ?? 0) + (report.counts.DUPLICATE_KEY ?? 0) + (report.counts.AMBIGUOUS ?? 0)],
    ['Invalid rows', report.totals.invalid_rows],
  ];
  summary.replaceChildren();
  cards.forEach(([label, value]) => {
    const item = document.createElement('div');
    item.className = 'summary-item';
    const number = document.createElement('strong');
    number.textContent = String(value);
    const caption = document.createElement('span');
    caption.textContent = label;
    item.append(number, caption);
    summary.append(item);
  });

  resultsBody.replaceChildren();
  report.rows.forEach((item) => {
    const row = document.createElement('tr');
    addTextCell(row, item.status, `status ${item.status}`);
    addTextCell(row, item.txid);
    addTextCell(row, item.output_index);
    addTextCell(row, `${item.asset} · ${item.network}`);
    addTextCell(row, item.chain_amount);
    addTextCell(row, item.ledger_amount);
    addTextCell(row, item.difference);
    addTextCell(row, item.note);
    resultsBody.append(row);
  });

  if (report.errors.length) {
    errorsBox.hidden = false;
    errorsBox.replaceChildren();
    const heading = document.createElement('strong');
    heading.textContent = 'Rows excluded because their source data is invalid';
    const list = document.createElement('ul');
    report.errors.forEach((error) => {
      const item = document.createElement('li');
      item.textContent = `${error.source} row ${error.row}: ${error.errors.join(' ')}`;
      list.append(item);
    });
    errorsBox.append(heading, list);
  } else {
    errorsBox.hidden = true;
    errorsBox.replaceChildren();
  }

  resultsSection.hidden = false;
  byId('exportButton').disabled = report.rows.length === 0;
  runMessage.textContent = `Run complete: ${report.totals.chain_valid_rows} valid chain rows, ${report.totals.ledger_valid_rows} valid ledger rows, ${report.totals.result_rows} comparison rows.`;
}

function runReconciliation() {
  try {
    const chainRows = parseCsv(chainCsv.value);
    const ledgerRows = parseCsv(ledgerCsv.value);
    if (!chainRows.length && !ledgerRows.length) throw new Error('Load or paste at least one CSV export first.');
    lastReport = reconcile(chainRows, ledgerRows);
    renderReport(lastReport);
  } catch (error) {
    lastReport = null;
    byId('exportButton').disabled = true;
    runMessage.textContent = `Could not run reconciliation: ${error.message}`;
  }
}

function bindFile(inputId, textarea) {
  byId(inputId).addEventListener('change', async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    if (file.size > 5_000_000) {
      runMessage.textContent = 'File is larger than 5 MB. Split it into smaller CSV files before loading.';
      event.target.value = '';
      return;
    }
    try {
      textarea.value = await file.text();
      runMessage.textContent = `Loaded ${file.name} locally. Nothing has been uploaded.`;
    } catch {
      runMessage.textContent = 'Could not read the selected file in this browser.';
    }
  });
}

bindFile('chainFile', chainCsv);
bindFile('ledgerFile', ledgerCsv);
byId('runButton').addEventListener('click', runReconciliation);
byId('demoButton').addEventListener('click', () => {
  chainCsv.value = demoChain;
  ledgerCsv.value = demoLedger;
  runMessage.textContent = 'Fictional sample rows loaded locally. No real transaction or wallet is queried.';
  runReconciliation();
});
byId('clearButton').addEventListener('click', () => {
  chainCsv.value = '';
  ledgerCsv.value = '';
  byId('chainFile').value = '';
  byId('ledgerFile').value = '';
  resultsSection.hidden = true;
  resultsBody.replaceChildren();
  summary.replaceChildren();
  errorsBox.hidden = true;
  errorsBox.replaceChildren();
  lastReport = null;
  byId('exportButton').disabled = true;
  runMessage.textContent = 'Inputs cleared. No data is retained by this page.';
});
byId('exportButton').addEventListener('click', () => {
  if (!lastReport) return;
  const blob = new Blob([toCsv(lastReport.rows)], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'crypto-ledger-reconciliation.csv';
  document.body.append(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
});
