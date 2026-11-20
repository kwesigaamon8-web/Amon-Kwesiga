"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const tools=require("../assets/free-toolbox.js");
const cases=[
 ["csv-to-json","name,value\nAlice,10\nBob,20","",[{"name":"Alice","value":"10"},{"name":"Bob","value":"20"}]],
 ["json-to-csv",'[{"name":"Ada","amount":10},{"name":"B","amount":20}]',"","name,amount\r\nAda,10\r\nB,20"],
 ["csv-profile","h1,h2\n1,2\n3,\n4,5","",{data_rows:3,columns:2,empty_data_cells:1}],
 ["json-format",'{"a":1,"b":true}',"",'{\n  "a": 1,\n  "b": true\n}'],
 ["json-minify",'{\n  "a": 1\n}',"",'{"a":1}'],
 ["json-keys",'{"a":{"b":1},"c":2}',"","a\na.b\nc"],
 ["base64-encode","Hello, 世界","","SGVsbG8sIOS4lueVjA=="],
 ["base64-decode","SGVsbG8sIOS4lueVjA==","","Hello, 世界"],
 ["url-encode","a b?","","a%20b%3F"],
 ["url-decode","a%20b%3F","","a b?"],
 ["html-escape",'<a title="ok">&',"","&lt;a title=&quot;ok&quot;&gt;&amp;"],
 ["decimal-to-hex","255","","0xff"],
 ["text-stats","One two\nTwo","",{words:3,lines:2,unique_words:2}],
 ["word-frequency","dog cat dog","","dog: 2\ncat: 1"],
 ["slug","Café & Friends!","","cafe-friends"],
 ["title-case","hello world","","Hello World"],
 ["unique-lines","A\nB\nA","","A\nB"],
 ["sort-lines","10\n2\n1","","1\n2\n10"],
 ["reverse-lines","A\nB\nC","","C\nB\nA"],
 ["number-lines","A\nB","","  1  A\n  2  B"],
 ["trim-lines"," A \n B ","","A\nB"],
 ["remove-blanks","A\n\nB","","A\nB"],
 ["checklist","A\nB","","- [ ] A\n- [ ] B"],
 ["compare-lines","A\nB","B\nC",{only_first:["A"],only_second:["C"],in_both:["B"]}],
 ["percentage","100","125","25.00%"],
 ["vat","1000","18",{net:1000,tax:180,gross:1180,rate_percent:18}],
 ["timestamp","2026-11-20T09:00:00+03:00","",{iso_utc:"2026-11-20T06:00:00.000Z",unix_seconds:1795154400}],
 ["contrast","#000000","#ffffff",{contrast_ratio:21,wcag_aa_normal:true,wcag_aa_large:true,wcag_aaa_normal:true}],
 ["hex-rgb","#0088ff","","0, 136, 255"]
];
test("Exactly 29 separately selectable working utilities",()=>assert.equal(tools.catalog.length,29));
for(const [id,a,b,expected] of cases) {
 test("utility: "+id,()=>{
  const result=tools.run(id,a,b);
  if(typeof expected==="string") assert.equal(result,expected);
  else if(id==="csv-to-json")assert.deepEqual(JSON.parse(result),expected);
  else for(const [key,value] of Object.entries(expected))assert.deepEqual(JSON.parse(result)[key],value);
 });
}
test("CSV handles quoted comma, quote and multiline",()=>{
 assert.deepEqual(tools.parseCSV('a,b\n"x,y","say ""yes"""\n"hello\nworld",ok'),[
  ["a","b"],["x,y",'say "yes"'],["hello\nworld","ok"]
 ]);
});
test("CSV unmatched quote refuses malformed content",()=>{
 assert.throws(()=>tools.csvToJSON('a,b\n"broken,1'),/Unclosed/);
});
test("Duplicate CSV column headings are rejected",()=>{
 assert.throws(()=>tools.csvToJSON("id,id\n1,2"),/Duplicate/);
});
test("Spreadsheet formula injection guarded on exports",()=>{
 const out=tools.jsonToCSV('[{"a":"=2+2","b":"@SUM(A1:A2)"}]');
 assert.match(out,/'=2\+2/);
 assert.match(out,/'@SUM/);
});
test("Prototype-sensitive JSON keys safely represented",()=>{
 const result=JSON.parse(tools.csvToJSON("__proto__,constructor\nx,y"));
 assert.equal(result[0].__proto__,"x");
 assert.equal(result[0].constructor,"y");
});
test("Unicode can round-trip through Base64",()=>{
 const text="🌍 Écriture 日本語";
 assert.equal(tools.base64Decode(tools.base64Encode(text)),text);
});
test("Bad Base64 and UTF-8 are rejected",()=>{
 assert.throws(()=>tools.base64Decode("%%%"),/Invalid/);
 assert.throws(()=>tools.base64Decode("//8="),/valid|UTF|encoded/i);
});
test("Dividing by zero is rejected",()=>assert.throws(()=>tools.percentageChange("0","2"),/zero/));
test("Unsafe VAT rate rejected",()=>assert.throws(()=>tools.vatCalculator("1","-2"),/nonnegative/));
test("No HTML execution: escape tags as text",()=>assert.equal(tools.run("html-escape","<script>",""),"&lt;script&gt;"));
test("Size guard for maliciously large inputs",()=>assert.throws(()=>tools.run("slug","a".repeat(1024*1024+1),""),/limit/));
