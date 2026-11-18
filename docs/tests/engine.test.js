const test=require('node:test');
const assert=require('node:assert/strict');
const {parseCSV,parseJSON,toCSV,analyze}=require('../assets/engine.js');
test('quoted CSV with escaped quote and multiline cell',()=>{
 const d=parseCSV('id,description,amount\r\nA,"Hello, world",12\r\nB,"He said ""Yes""\nand left",15\r\n');
 assert.equal(d.items.length,2);assert.equal(d.items[0].description,'Hello, world');assert.equal(d.items[1].description,'He said "Yes"\nand left');
});
test('malformed CSV rejected',()=>{assert.throws(()=>parseCSV('a,b\n1,"bad'),/Unclosed/);assert.throws(()=>parseCSV('a,a\n1,2'),/Duplicate/);assert.throws(()=>parseCSV('a,b\n1'),/Row 2/);});
test('conversion round trip',()=>{const d=parseJSON('[{"id":"A","amount":3},{"id":"B","amount":7}]');assert.deepEqual(parseCSV(toCSV(d)).items,d.items);});
test('flat JSON only',()=>{assert.throws(()=>parseJSON('{"id":1}'),/array/);assert.throws(()=>parseJSON('[{"x":{"nested":1}}]'),/Nested/);});
test('missing values, duplicate IDs, valid numeric amounts',()=>{const d=parseCSV('id,amount\nA,10.25\nA,5\nB,\nC,garbage\n');const x=analyze(d,'id','amount');assert.equal(x.duplicateCount,1);assert.deepEqual(x.duplicates[0],{row:3,firstRow:2,value:'A'});assert.equal(x.missing.amount,1);assert.equal(x.amountTotal,15.25);assert.deepEqual(x.invalidAmountRows,[5]);});
test('CSV formula-like text is escaped for Excel unless opted out',()=>{const x=parseCSV('name,amount\n=1+1,5\n');assert.equal(parseCSV(toCSV(x)).items[0].name,"'=1+1");assert.equal(parseCSV(toCSV(x,{excelSafe:false})).items[0].name,'=1+1');});
test('unexpected trailing text after CSV quoted field rejected',()=>{assert.throws(()=>parseCSV('a,b\n"hello"oops,2'),/Unexpected text/);});
