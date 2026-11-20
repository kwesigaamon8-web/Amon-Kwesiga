(function () {
  'use strict';
  const $ = s => document.querySelector(s);
  const tools = window.StudioTools;
  const example = 'invoice_id,customer,amount,status\nINV-101,Acme Co,120.50,paid\nINV-102,Blue Ltd,75.00,pending\nINV-102,Blue Ltd,75.00,pending\nINV-103,"Fresh, Inc",180.25,paid\nINV-104,Zen Co,,pending\n';
  let dataset = null, outputContent = null, outputName = null;
  function alert(msg, good) { const el = $('#tool-status'); el.textContent = msg; el.className = 'notice ' + (good ? 'notice-good' : 'notice-error'); el.hidden = false; }
  function resetOutput() { outputContent = null; $('#download').disabled = true; $('#result').textContent = 'Select a tool, load sample data or upload a non-sensitive file, and click Run check.'; }
  function prepare() {
    const text = $('#data-input').value;
    const type = $('#source-format').value;
    const d = type === 'json' ? tools.parseJSON(text) : tools.parseCSV(text);
    dataset = d;
    const key = $('#key-field'); const amount = $('#amount-field');
    for (const select of [key, amount]) {
      const prior = select.value;
      select.replaceChildren(new Option('None', ''));
      for (const field of d.fields) select.add(new Option(field,field));
      if (d.fields.includes(prior)) select.value = prior;
    }
    if (!key.value) key.value = d.fields.find(x => /^(invoice_?id|id|reference|sku)$/i.test(x)) || '';
    if (!amount.value) amount.value = d.fields.find(x => /^(amount|total|price|value)$/i.test(x)) || '';
    return d;
  }
  function run() {
    try {
      const d = prepare();
      const mode = $('#tool-mode').value;
      let summary;
      if (mode === 'audit') {
        const report = tools.analyze(d, $('#key-field').value, $('#amount-field').value);
        summary = ['DATA QUALITY CHECK (LOCAL ONLY)', '',
          'Records: ' + report.rowCount, 'Columns: ' + report.columns,
          'Duplicate keys: ' + report.duplicateCount,
          'Rows with non-numeric amounts: ' + report.invalidAmountRows.length,
          report.amountField ? 'Sum of recognized ' + report.amountField + ': ' + report.amountTotal : 'No numeric total requested.',
          '', 'Empty cells by column:', ...Object.entries(report.missing).map(([k,v]) => '  ' + k + ': ' + v),
          '', 'Duplicate details: ', ...report.duplicates.slice(0,100).map(x=> '  Row ' + x.row + ' = ' + x.value + ' (first row ' + x.firstRow + ')'),
          '', 'This is descriptive data QA, not an audit opinion.'].join('\n');
        outputContent = JSON.stringify(report,null,2); outputName = 'b1b2-quality-report.json';
      } else if (mode === 'json') {
        outputContent = JSON.stringify(d.items, null, 2); outputName = 'b1b2-converted.json';
        summary = 'CONVERTED JSON (preview)\n\n' + outputContent.slice(0,4500);
      } else {
        outputContent = tools.toCSV(d); outputName = 'b1b2-converted.csv';
        summary = 'CONVERTED CSV (preview)\n\n' + outputContent.slice(0,4500);
      }
      $('#result').textContent = summary;
      $('#download').disabled = false;
      alert('Processed ' + d.items.length.toLocaleString() + ' records in your browser; no file uploaded to a server.',true);
    } catch (e) { resetOutput(); alert(e.message || 'The input could not be processed.',false); }
  }
  $('#run-check').addEventListener('click',run);
  $('#load-sample').addEventListener('click', () => { $('#source-format').value = 'csv'; $('#data-input').value = example; $('#tool-mode').value='audit'; $('#key-field').replaceChildren(new Option('Auto-detect on run', '')); $('#amount-field').replaceChildren(new Option('Auto-detect on run', '')); $('#tool-status').hidden=true; resetOutput(); run(); });
  $('#clear-data').addEventListener('click', () => { $('#data-input').value=''; $('#tool-status').hidden=true; resetOutput(); });
  $('#file-input').addEventListener('change', async (e) => {
    const file = e.target.files[0]; if (!file) return;
    if (file.size > tools.MAX_BYTES) { alert('Maximum file size is 5 MB.',false); return; }
    $('#source-format').value = file.name.toLowerCase().endsWith('.json') ? 'json' : 'csv';
    $('#data-input').value = await file.text(); $('#tool-status').hidden=true; resetOutput();
  });
  $('#download').addEventListener('click', () => {
    if (outputContent === null) return;
    const blob = new Blob([outputContent],{type:outputName.endsWith('json')?'application/json':'text/csv'});
    const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download=outputName; document.body.append(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(url),3000);
  });
  $('#tool-mode').addEventListener('change', resetOutput);
  $('#data-input').addEventListener('input', resetOutput);
  $('#year').textContent = new Date().getFullYear();
})();
