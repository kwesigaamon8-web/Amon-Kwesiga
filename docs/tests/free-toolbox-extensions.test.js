"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const api=require("../assets/free-toolbox.js");require("../assets/free-toolbox-extensions.js");
const r=(id,a="",b="")=>api.run(id,a,b),j=(id,a,b)=>JSON.parse(r(id,a,b));
test("All 55 tools are registered once",()=>{assert.equal(api.catalog.length,55);assert.equal(new Set(api.catalog.map(x=>x.id)).size,55);});
const examples=[
["url-parse","https://example.com/a?x=1","",v=>j("url-parse","https://example.com/a?x=1").host==="example.com"],
["query-to-json","?a=1&a=2","",v=>JSON.stringify(j("query-to-json","?a=1&a=2").a)==='["1","2"]'],
["json-to-query",'{"a":1,"b":2}',"",v=>v==="a=1&b=2"],
["rot13","Hello","",v=>v==="Uryyb"],
["hex-encode","Hi","",v=>v==="4869"],
["hex-decode","4869","",v=>v==="Hi"],
["binary-decimal","1010","",v=>v==="10"],
["decimal-binary","10","",v=>v==="1010"],
["utf8-byte-count","é","",v=>j("utf8-byte-count","é").utf8_bytes===2],
["jwt-inspect","eyJhbGciOiJub25lIn0.eyJzdWIiOiJ0ZXN0In0.","",v=>j("jwt-inspect","eyJhbGciOiJub25lIn0.eyJzdWIiOiJ0ZXN0In0.").payload.sub==="test"],
["regex-escape","a.b","",v=>v==="a\\.b"],
["json-sort",'{"b":1,"a":2}',"",v=>v.indexOf('"a"')<v.indexOf('"b"')],
["json-diff",'{"a":1}','{"a":2}',v=>j("json-diff",'{"a":1}','{"a":2}').differences.length===1],
["json-pointer",'{"a":2}',"/a",v=>v==="2"],
["json-to-typescript",'{"a":"hello"}',"",v=>v.includes('"a": string')],
["lines-to-json","a\nb","",v=>v==='[\n  "a",\n  "b"\n]'],
["json-to-lines",'["a","b"]',"",v=>v==="a\nb"],
["csv-unique","a,b\n1,2\n1,2","",v=>v==="a,b\r\n1,2"],
["csv-column","a,b\n1,2","b",v=>v==="b\r\n2"],
["csv-sort","a,b\n5,10\n2,2","a",v=>v==="a,b\r\n2,2\r\n5,10"],
["days-between","2026-11-20","2026-11-30",v=>v==="10 days"],
["discount","100","25",v=>j("discount","100","25").after_discount===75],
["vat-included","118","18",v=>j("vat-included","118","18").net===100],
["rgb-to-hex","0,136,255","",v=>v==="#0088ff"],
["uuid-v4","","",v=>/^[0-9a-f-]{36}$/.test(v)],
["password-gen","20","",v=>v.length===20]
];
for(const [id,a,b,check] of examples)test(id+" sample",()=>assert.equal(check(r(id,a,b)),true,id));
test("Bad URL protocol rejected",()=>assert.throws(()=>r("url-parse","javascript:alert(1)"),/HTTP/));
test("No JWT signature verification falsely claimed",()=>assert.match(r("jwt-inspect","eyJhbGciOiJub25lIn0.eyJzdWIiOiJ0ZXN0In0."),/UNVERIFIED/));
test("No prototype pollution in query",()=>{let x=j("query-to-json","__proto__=safe");assert.equal(x["__proto__"],"safe");assert.equal({}.polluted,undefined);});
test("Invalid hex rejected",()=>assert.throws(()=>r("hex-decode","broken"),/Invalid/));
test("Impossible date rejected",()=>assert.throws(()=>r("days-between","2026-02-30","2026-03-01"),/Invalid/));
test("Incorrect CSV header rejected",()=>assert.throws(()=>r("csv-column","a,b\n1,2","none"),/not found/));
test("High password length rejected",()=>assert.throws(()=>r("password-gen","9999"),/8-128/));
