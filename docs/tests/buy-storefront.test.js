const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const root = path.resolve(__dirname, "../..");
const read = x => fs.readFileSync(path.join(root,x),"utf8");
const page = read("docs/buy.html");
const workflow = read(".github/workflows/b1-b2-free-studio-renewal.yml");
test("no-subscription storefront is source-backed and has 18 selectable services",()=>{
  assert.match(page,/No subscription/);
  assert.match(page,/No account or payment needed to browse/);
  assert.match(page,/data-index="17"/);
  assert.match(page,/data-index="0"/);
  assert.equal((page.match(/<article class="offer"/g)||[]).length,18);
  assert.match(page,/<a class="btn" href="#offers">See services/);
  assert.match(page,/ENIGMA B1\/B2/);
});
test("buyer data never sent or stored by the static order preparer",()=>{
  assert.match(page,/navigator\.clipboard\.writeText\(order\)/);
  assert.match(page,/document\.getElementById\("generated"\)\.textContent=order/);
  assert.doesNotMatch(page,/fetch\s*\(|XMLHttpRequest|localStorage|sessionStorage|new WebSocket/);
  assert.match(page,/No automatic contract or invoice/);
  assert.match(page,/\[hidden\]\{display:none!important\}/);
});
test("correct approved receive-only address network statements and no unauthorised wallet functions",()=>{
  assert.match(page,/bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z/);
  assert.match(page,/bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9/);
  assert.match(page,/0x734989a439F146885C12907cd9Dd191b03d5B07e/);
  assert.match(page,/Conditional B1 native Circle USDC on Base mainnet/);
  assert.match(page,/only after agreement/);
  assert.doesNotMatch(page,/ethereum\.request|sendTransaction|privateKey/);
});
test("static site deploy includes page and its principal linked assets",()=>{
  const assets=[
    "buy.html","enigma-1000-individual-offers.html",
    "ENIGMA_1000_Original_Codes.zip","ENIGMA_1000_INDIVIDUAL_SKUS.csv",
    "miner-bonus.html","global-1000.html","global-1000-manifest.json",
    "assets/global-500-engine.mjs","world-open-data-reports.html",
    "reports/2026-11-22_EAST_AFRICA_DIGITAL_READINESS.md",
    "reports/2026-11-22_EAST_AFRICA_MACRO_SIGNALS.md"
  ];
  const line=workflow.match(/zip -q \.\.\/studio-preview\.zip[^\n]+/);
  assert.ok(line,"zip list exists");
  for(const a of assets){
    assert.ok(line[0].split(" ").includes(a),"zip missing "+a);
    assert.ok(fs.existsSync(path.join(root,"docs",a)),"source missing "+a);
  }
});
