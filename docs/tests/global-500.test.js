import test from "node:test";
import assert from "node:assert/strict";
import {DOMAINS,ALGORITHMS,TOTAL_TOOLS,toolAt,toolById,
        calculate,CODES,countryAssignment,BTC_ROUTES} from "../assets/global-500-engine.mjs";
import {EXTRA_METHODS,calculateExtra,defaultsExtra} from "../assets/global-1000-expansion.mjs";
test("exactly 1000 unique usable tools across 100 methods and ten domains",()=>{
 assert.equal(ALGORITHMS.length,50);assert.equal(EXTRA_METHODS.length,50);assert.equal(DOMAINS.length,10);assert.equal(TOTAL_TOOLS,1000);
 const ids=new Set(),titles=new Set();
 for(let i=0;i<TOTAL_TOOLS;i++){
   const t=toolAt(i);ids.add(t.id);titles.add(t.name);
   assert.equal(toolById(t.id).id,t.id);
   assert.equal(t.payment_required,false);assert.equal(t.offline,true);
   assert.equal(t.index,i);
   const result=calculate(t.algorithm,t.defaults);
   assert.ok(Number.isFinite(result.value),"Failure "+t.id+" "+t.name+": "+result.value);
 }
 assert.equal(ids.size,1000);assert.equal(titles.size,1000);
 assert.equal(toolAt(0).id,"SW-001");assert.equal(toolAt(499).id,"SW-500");
 assert.equal(toolAt(500).id,"SW-501");assert.equal(toolAt(999).id,"SW-1000");
});
test("real verified arithmetic examples",()=>{
 assert.equal(calculate(0,{series:"1,2,3"}).value,6);
 assert.equal(calculate(1,{series:"1,2,3"}).value,2);
 assert.equal(calculate(2,{series:"1,2,3"}).value,2);
 assert.equal(calculate(2,{series:"2,4,7,9"}).value,5.5);
 assert.equal(calculate(3,{series:"1,3,9"}).value,8);
 assert.equal(calculate(9,{a:100,b:110}).value,10);
 assert.equal(calculate(12,{a:1000,b:5,c:2}).value,100);
 assert.equal(calculate(15,{a:200,b:30,c:10}).value,10);
 assert.equal(calculate(18,{a:100,b:20}).value,80);
 assert.equal(calculate(23,{a:10,b:5,c:20}).value,70);
 assert.equal(calculate(31,{a:100,b:60}).value,40);
 assert.equal(calculate(40,{a:150,b:100}).value,50);
 assert.equal(calculate(46,{a:1000,b:24,c:.2}).value,4.8);
 assert.equal(calculate(47,{a:4294967296,b:1,c:1,d:0}).value,86400);
 assert.equal(calculate(48,{a:4294967296,b:1}).value,1/(86400*365.25));
 assert.equal(calculate(49,{a:100,b:30,c:20,d:10}).value,40);
});
test("reject invalid values, rate bounds and unknown tools",()=>{
 for(const bad of ["SW-000","SW-1001","SW-BAD","SW-0099"])assert.throws(()=>toolById(bad));
 for(const bad of [-1,1000,NaN,1.5])assert.throws(()=>toolAt(bad));
 assert.throws(()=>calculate(13,{a:1,b:-101,c:3}));
 assert.throws(()=>calculate(15,{a:100,b:20,c:20}));
 assert.throws(()=>calculate(47,{a:0,b:100,c:3.125,d:2}));
 assert.throws(()=>calculate(47,{a:12,b:100,c:3.125,d:101}));
 assert.throws(()=>calculate(44,{series:"1,6"}));
 assert.throws(()=>calculate(0,{series:"what"}));
 assert.throws(()=>calculate(0,{series:Array.from({length:401},()=>1)}));
 assert.throws(()=>calculate(25,{a:100,b:0}));
});
test("249 ISO-country/territory dispatch slots are unique and unverified",()=>{
 assert.equal(CODES.length,249);
 assert.equal(new Set(CODES).size,249);
 for(const c of CODES){
  const x=countryAssignment(c);
  assert.equal(x.code,c);
  assert.ok(x.tool.id.startsWith("SW-"));
  assert.equal(x.verified_local_market_problem,false);
  assert.equal(x.verified_local_demand,false);
  assert.equal(x.verified_buyer,false);
  assert.ok(x.required_sources.length>=2);
 }
 assert.throws(()=>countryAssignment("ZZ"));
});
test("Bitcoin routes are only owner-published native mainnet receivers",()=>{
 assert.equal(BTC_ROUTES.B1,"bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z");
 assert.equal(BTC_ROUTES.B2,"bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9");
 assert.match(calculate(47,{a:1e7,b:1.5e14,c:3.125,d:2.5}).warning,/No profit or BTC payment is guaranteed/);
});

test("new public-interest programs have correct reference calculations",()=>{
 assert.equal(calculate(50,{a:18,b:20}).value,90);
 assert.equal(calculate(51,{a:20,b:18}).value,2);
 assert.equal(calculate(54,{a:120,b:20}).value,6);
 assert.equal(calculate(58,{a:80,b:1100,c:75}).value,66000);
 assert.equal(calculate(62,{a:100,b:8,c:30}).value,24);
 assert.equal(calculate(63,{a:5,b:350,c:5,d:78}).value,6.825);
 assert.equal(calculate(67,{a:4,b:100}).value,4);
 assert.equal(calculate(74,{a:3200,b:1.5}).value,3200/1.5);
 assert.equal(calculate(79,{a:2,b:6,c:20}).value,36);
 assert.equal(calculate(80,{a:3,b:5}).value,30);
 assert.equal(calculate(84,{a:85000,b:12,c:10}).value,66300);
 assert.equal(calculate(90,{a:200000,b:50000}).value,4);
 assert.equal(calculate(93,{a:2000,b:12,c:3,d:150}).value,1605.03);
 assert.equal(calculate(97,{a:.12,b:.8}).value,17/75);
 assert.equal(calculate(98,{a:300,b:30,c:4}).value,36);
 assert.equal(calculate(99,{a:400,b:250}).value,150);
});
test("new public-interest programs fail safely on invalid and dangerous inputs",()=>{
 assert.throws(()=>calculate(50,{a:3,b:0}));
 assert.throws(()=>calculate(58,{a:10,b:10,c:101}));
 assert.throws(()=>calculate(64,{a:3,b:2,c:0}));
 assert.throws(()=>calculate(80,{a:5,b:5}),/unstable/);
 assert.throws(()=>calculate(84,{a:100,b:60,c:50}),/cannot exceed/);
 assert.throws(()=>calculate(95,{a:100,b:101,c:0}));
 assert.throws(()=>calculate(97,{a:1.2,b:.5}));
 assert.throws(()=>calculate(100,{a:1}));
});
test("original app IDs remain backward compatible and new apps are local only",()=>{
 const older=toolAt(47);
 assert.equal(older.id,"SW-048");
 assert.equal(older.algorithm,47);
 assert.match(calculate(47,{a:1e7,b:1.5e14,c:3.125,d:2.5}).warning,/No profit/);
 const newer=toolAt(997);
 assert.equal(newer.id,"SW-998");
 assert.equal(newer.algorithm,97);
 assert.equal(newer.payment_required,false);
 assert.equal(newer.offline,true);
});
