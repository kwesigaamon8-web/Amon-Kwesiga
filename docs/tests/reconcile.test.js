const t=require('node:test'), assert=require('node:assert/strict'), R=require('../assets/reconcile.js');
t('matches exact cents once and isolates extra records',()=>{
 const x=R.reconcile('reference,amount\nA,10.25\nB,5.00\nC,7.00\n','reference,amount\nA,10.25\nB,6.00\nD,1.00\n');
 assert.deepEqual(x.summary,{firstRows:3,secondRows:3,matched:1,mismatches:1,ambiguous:0,firstOnly:1,secondOnly:1,invalid:0});
 assert.equal(x.rows.find(r=>r.result==='AMOUNT_MISMATCH').difference,'-1.00');
});
t('duplicate references are consumed one-to-one',()=>{
 const x=R.reconcile('ref,amount\nA,5.00\nA,5.00\n','ref,amount\nA,5.00\n');
 assert.equal(x.summary.matched,1); assert.equal(x.summary.firstOnly,1);
});
t('multiple possible unequal references remain ambiguous',()=>{
 const x=R.reconcile('ref,amount\nA,7.00\n','ref,amount\nA,1.00\nA,2.00\n');
 assert.equal(x.summary.ambiguous,1);assert.equal(x.summary.secondOnly,2);
});
t('malformed and thousands-separated amounts are flagged',()=>{
 const x=R.reconcile('reference,amount\nA,1.234\nB,"1,200"\nC,10\n','reference,amount\nA,1.23\nB,1200\nC,10.00\n');
 assert.equal(x.summary.invalid,2); assert.equal(x.summary.matched,1);
});
t('leading-zero reference IDs remain distinct',()=>{
 const x=R.reconcile('reference,amount\n001,10\n1,10\n','reference,amount\n1,10\n001,12\n');
 assert.equal(x.summary.matched,1); assert.equal(x.summary.mismatches,1);
});
t('BigInt exact cents avoids float rounding',()=>{
 assert.equal(R.fmt(R.cents('123456789012345678.90')),'123456789012345678.90');
 assert.equal(R.fmt(R.cents('-0.05')),'-0.05');
 assert.equal(R.cents('1.234'),null);
});
t('CSV export protects formula-like references',()=>{
 const x=R.reconcile('reference,amount\n=1+1,2\n','reference,amount\n=1+1,2\n');
 assert.equal(x.summary.matched,1); assert.ok(x.csv.includes("'=1+1"));
});
t('column schema errors are visible',()=>{
 assert.throws(()=>R.reconcile('id,value\nA,1\n','ref,cost\nA,1\n'),/Second CSV/);
});
