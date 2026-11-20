/* B1/B2: original no-upload, exact-cents two-file matching */
(function (root, factory) {
  const engine = typeof module === 'object' && module.exports ? require('./engine.js') : root.StudioTools;
  const api = factory(engine);
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.StudioReconcile = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (tools) {
  'use strict';
  function field(fields, names, which) {
    const found = names.map(n => fields.find(f => f.toLowerCase() === n)).find(Boolean);
    if (!found) throw new Error(which + ' requires reference and amount columns.');
    return found;
  }
  function cents(raw) {
    const s = String(raw == null ? '' : raw).trim();
    if (!/^[+-]?\d+(?:\.\d{1,2})?$/.test(s)) return null;
    const negative = s.startsWith('-');
    const pair = s.replace(/^[+-]/,'').split('.');
    const n = BigInt(pair[0]) * 100n + BigInt(((pair[1] || '') + '00').slice(0,2));
    return negative ? -n : n;
  }
  function fmt(c) {
    const neg = c < 0n, n = neg ? -c : c;
    return (neg ? '-' : '') + (n / 100n) + '.' + String(n % 100n).padStart(2,'0');
  }
  function reconcile(firstCsv, secondCsv) {
    const a = tools.parseCSV(firstCsv), b = tools.parseCSV(secondCsv);
    const refs=['reference','ref','invoice_id','transaction_id','id'], amts=['amount','total','value'];
    const aRef=field(a.fields,refs,'First CSV'), aAmt=field(a.fields,amts,'First CSV');
    const bRef=field(b.fields,refs,'Second CSV'), bAmt=field(b.fields,amts,'Second CSV');
    const ledger=b.items.map((r,i)=>({
      row:i+2, ref:String(r[bRef]).trim(), amount:String(r[bAmt]).trim(),
      parsed:cents(r[bAmt]), used:false
    }));
    const lookup=new Map();
    for (const entry of ledger) {
      if (!lookup.has(entry.ref)) lookup.set(entry.ref,[]);
      lookup.get(entry.ref).push(entry);
    }
    const rows=[], totals={};
    function add(status,x,y,diff) {
      totals[status]=(totals[status]||0)+1;
      rows.push({
        result:status, first_csv_row:x?String(x.row):'',
        reference:x?x.ref:y.ref, first_amount:x?x.amount:'',
        second_csv_row:y?String(y.row):'',
        second_amount:y?y.amount:'',
        difference:diff===null?'':fmt(diff)
      });
    }
    for(let i=0;i<a.items.length;i++) {
      const r=a.items[i];
      const x={row:i+2,ref:String(r[aRef]).trim(),amount:String(r[aAmt]).trim(),parsed:cents(r[aAmt])};
      if(x.parsed===null){add('INVALID_FIRST_AMOUNT',x,null,null);continue;}
      const candidates=(lookup.get(x.ref)||[]).filter(y=>!y.used&&y.parsed!==null);
      const exact=candidates.find(y=>y.parsed===x.parsed);
      if(exact){exact.used=true;add('MATCHED',x,exact,0n);}
      else if(candidates.length===1){
        const y=candidates[0];y.used=true;
        add('AMOUNT_MISMATCH',x,y,x.parsed-y.parsed);
      }
      else if(candidates.length>1)add('AMBIGUOUS_REFERENCE',x,null,null);
      else add('FIRST_ONLY',x,null,null);
    }
    for(const y of ledger)if(!y.used)add(y.parsed===null?'INVALID_SECOND_AMOUNT':'SECOND_ONLY',null,y,null);
    const fields=['result','first_csv_row','reference','first_amount','second_csv_row','second_amount','difference'];
    return {
      summary:{firstRows:a.items.length,secondRows:b.items.length,
        matched:totals.MATCHED||0,mismatches:totals.AMOUNT_MISMATCH||0,
        ambiguous:totals.AMBIGUOUS_REFERENCE||0,firstOnly:totals.FIRST_ONLY||0,
        secondOnly:totals.SECOND_ONLY||0,
        invalid:(totals.INVALID_FIRST_AMOUNT||0)+(totals.INVALID_SECOND_AMOUNT||0)},
      rows,csv:tools.toCSV({fields,items:rows}),
      caveat:'Exact case-sensitive one-to-one references and same-sign two-decimal amounts; no bank integration, fuzzy matching or audit opinion.'
    };
  }
  return {reconcile,cents,fmt};
});
