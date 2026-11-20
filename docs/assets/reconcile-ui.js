(function () {
  'use strict';
  const e=id=>document.getElementById(id);
  let download=null;
  function sample() {
    e('recon-first').value='reference,amount\nPAY-001,145.50\nPAY-002,95.00\nPAY-003,42.75\nPAY-004,10.00\n';
    e('recon-second').value='reference,amount\nPAY-001,145.50\nPAY-002,90.00\nPAY-003,42.75\nPAY-005,18.00\n';
    e('recon-output').textContent='Click Compare files to inspect a fictional example.';
    e('recon-status').textContent='Fictional sample loaded. Nothing has been uploaded.';
    download=null;e('recon-download').disabled=true;
  }
  e('recon-sample').addEventListener('click',sample);
  e('recon-run').addEventListener('click',()=>{
    try {
      const data=window.StudioReconcile.reconcile(e('recon-first').value,e('recon-second').value);
      const s=data.summary;
      e('recon-output').textContent=[
        'TWO-FILE RECONCILIATION (LOCAL ONLY)',
        'First CSV rows: '+s.firstRows,'Second CSV rows: '+s.secondRows,
        'Exact matches: '+s.matched,'Amount mismatches: '+s.mismatches,
        'Ambiguous repeated references: '+s.ambiguous,
        'Only in first file: '+s.firstOnly,'Only in second file: '+s.secondOnly,
        'Invalid money amounts: '+s.invalid,'',
        'First 35 findings:',
        ...data.rows.slice(0,35).map(x=>x.result+' | '+x.reference+' | '+(x.first_amount||'-')+' | '+(x.second_amount||'-')+' | '+x.difference),
        '',data.caveat
      ].join('\n');
      download=data.csv;e('recon-download').disabled=false;
      e('recon-status').textContent='Reconciled locally in the browser. Download the testable CSV findings.';
    } catch(err) {
      download=null;e('recon-download').disabled=true;
      e('recon-status').textContent=err.message||'Invalid input';
      e('recon-output').textContent='No result. Check both CSV headers and rows.';
    }
  });
  e('recon-download').addEventListener('click',()=>{
    if(download===null)return;
    const blob=new Blob([download],{type:'text/csv'});
    const url=URL.createObjectURL(blob);
    const a=document.createElement('a');
    a.href=url;a.download='b1b2-two-file-reconciliation.csv';
    document.body.append(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),3000);
  });
  for(const id of ['recon-first','recon-second'])e(id).addEventListener('input',()=>{
    download=null;e('recon-download').disabled=true;
  });
  sample();
})();
