const test = require("node:test");const assert=require("node:assert/strict");const fs=require("node:fs");const path=require("node:path");
const root=path.resolve(__dirname,"../..");
const page=fs.readFileSync(path.join(root,"docs/product-brief-builder.html"),"utf8");
async function core(){return import("../assets/product-brief-core.mjs")}
test("deterministic useful brief from prompt",async()=>{
 const {createBrief}=await core();const input={prompt:"Build a reproducible CSV checker that finds all duplicate order IDs in safe fictional data.",name:"Duplicate Order Checker",kind:"data",acceptance:"Every duplicate is logged and the exception CSV is readable"};
 const a=createBrief(input),b=createBrief(input);
 assert.equal(a.id,b.id);assert.equal(a.tests.length,4);assert.match(a.markdown,/## Acceptance and QA tests/);
 assert.match(a.markdown,/NOT_VERIFIED/);assert.match(a.markdown,/Buyer-defined acceptance/);
 assert.equal(a.publication_status,"DRAFT_NOT_POSTED");
});
test("all five legitimate product types create defined tests",async()=>{
 const {createBrief}=await core();for(const kind of ["software","data","research","design","documentation"]){const v=createBrief({kind,prompt:"Create an original helpful digital product for a specific local buyer"});assert.equal(v.tests.length,3);assert.match(v.markdown,/No Gmail, subscriptions/);}
});
test("invalid prompt and unsupported categories reject",async()=>{
 const {createBrief}=await core();
 for(const data of [null,{prompt:"tiny"},{prompt:"Make something meaningful",kind:"illegal"}])assert.throws(()=>createBrief(data));
});
test("static browser doesn't claim to run AI or publish or pay",()=>{
 assert.match(page,/rules-based brief builder/);assert.match(page,/It does not build or publish/);assert.match(page,/It has not been submitted, posted, built or sold/);
 assert.match(page,/navigator.clipboard.writeText/);assert.match(page,/URL.createObjectURL/);
 assert.doesNotMatch(page,/fetch\s*\(|XMLHttpRequest|localStorage|sendTransaction|ethereum.request/);
});
