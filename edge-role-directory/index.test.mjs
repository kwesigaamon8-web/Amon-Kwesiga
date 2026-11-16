import test from "node:test";
import assert from "node:assert/strict";
import worker,{route,CONFIGURED_B_ROLE_POSITIONS,TOTAL_CONFIGURED_POSITIONS} from "./index.mjs";
test("role count honest",()=>{assert.equal(CONFIGURED_B_ROLE_POSITIONS,"750377265360");assert.equal(TOTAL_CONFIGURED_POSITIONS,"750377265361")});
test("valid deepest roles both fleets and preserved parent",()=>{
 for(const fleet of ["B1","B2"]){
  const x=route(fleet,"D10-M15-W50-S150-G500-H666");
  assert.equal(x.role_level,"H");
  assert.equal(x.physical_miner_allocated,false);
  assert.ok(x.parent.includes("S150-G500"));
 }
});
test("invalid components rejected",()=>{
 for(const r of ["D00-M01-W01","D11-M01-W01","D01-M16-W01","D01-M01-W51","D01-M01-W01-S151","D01-M01-W01-S001-G501","D01-M01-W01-S001-G001-H667","../x"]){
 assert.equal(route("B1",r),null,r);
 }
});
test("task lanes differ across real role IDs without granting external access",()=>{
 const s=new Set();
 for(let n=1;n<=50;n++){
 const p=route("B1","D01-M01-W"+String(n).padStart(2,"0"));
 s.add(p.task_lane);assert.equal(p.external_tools_granted,false);
 }
 assert.ok(s.size>=7);
});
test("public endpoints are truthful and read only",async()=>{
 const get=async p=>worker.fetch(new Request("https://example.com"+p));
 const cap=await (await get("/api/capacity")).json();
 assert.equal(cap.configured_total,"750377265361");
 assert.equal(cap.individual_hosted_servers_created,0);
 assert.equal(cap.actual_sha256_miners_created,0);
 assert.equal((await get("/")).status,200);
 assert.equal((await get("/api/role?company=B1&role=D01-M01-W01")).status,200);
 assert.equal((await get("/api/role?company=B1&role=D00-M01-W01")).status,404);
 assert.equal((await worker.fetch(new Request("https://example.com/api/capacity",{method:"POST"}))).status,405);
});
