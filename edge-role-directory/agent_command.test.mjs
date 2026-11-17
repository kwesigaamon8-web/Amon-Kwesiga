import test from "node:test";
import assert from "node:assert/strict";
import worker,{route} from "./index.mjs";
import {commandFor,rootCommandInfo,PUBLIC_COMMAND_URL} from "./agent_command.mjs";

test("one public owner command, not a claim that workers are online",()=>{
 const root=rootCommandInfo();
 assert.match(PUBLIC_COMMAND_URL,/^https:\/\/raw\.githubusercontent\.com\/kwesigaamon8-web\/Amon-Kwesiga\/main\/crypto-agents\/PUBLIC_AGENT_COMMAND\.json$/);
 assert.equal(root.command_url,PUBLIC_COMMAND_URL);
 assert.equal(root.actually_running_agent_instances_verified_by_this_directory,0);
 assert.equal(root.no_automatic_remote_dispatch_or_cryptocurrency_receipt_claim,true);
});
test("both fleets use the same source and their correct independent BTC routes",()=>{
 for(const [fleet,handle,address] of [
  ["B1","transferexperiment","bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z"],
  ["B2","BountyScoutAI","bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9"]]){
  for(const role of ["D01","D01-A","D01-B","D01-M01-W01","D10-M15-W50-S150-G500-H666"]){
   const x=commandFor(fleet,role,route);
   assert.ok(x,role);
   assert.equal(x.registered_company_agent,handle);
   assert.equal(x.receiving_only_bitcoin_mainnet_address,address);
   assert.equal(x.instruction_source,PUBLIC_COMMAND_URL);
   assert.equal(x.agent_instance_verified,false);
   assert.equal(x.individual_acknowledgment_received,false);
   assert.ok(x.communication_rules.includes("NO_EMAILS"));
  }
 }
});
test("hierarchy preserves one parent and actual full ancestry",()=>{
 const d=commandFor("B2","D04",route);
 assert.deepEqual(d.reporting_path,["HUMAN_OWNER","CHIEF_D","BountyScoutAI/D04"]);
 assert.equal(d.original_direct_parent,"CHIEF_D");
 const a=commandFor("B2","D04-B",route);
 assert.equal(a.original_direct_parent,"BountyScoutAI/D04");
 const x=commandFor("B2","D04-M02-W10-S001-G001-H666",route);
 assert.equal(x.original_direct_parent,"BountyScoutAI/D04-M02-W10-S001-G001");
 assert.deepEqual(x.reporting_path.slice(0,4),[
  "HUMAN_OWNER","CHIEF_D","BountyScoutAI/D04","BountyScoutAI/D04-M02"]);
 const chief=commandFor("CHIEF","D",route);
 assert.equal(chief.role_id,"CHIEF/D");
});
test("rejects invalid companies and IDs",()=>{
 for(const [c,r] of [["B3","D01"],["B1","D00"],["B1","D11"],["B1","D01-C"],
 ["B1","D01-M16-W01"],["B2","D01-M01-W51"],["B2","D01-M01-W01-S151"],
 ["B1","D01-M01-W01-S001-G501"],["B1","D01-M01-W01-S001-G001-H667"],
 ["B2","../x"],["CHIEF","D01"]]){
   assert.equal(commandFor(c,r,route),null,c+"/"+r);
 }
});
test("command endpoint is read only and does not claim earnings",async()=>{
 const base="https://example.test";
 const get=async (u)=>worker.fetch(new Request(base+u));
 const general=await (await get("/api/command")).json();
 assert.equal(general.command_url,PUBLIC_COMMAND_URL);
 const x=await (await get("/api/command?company=B1&role=D01-A")).json();
 assert.equal(x.original_direct_parent,"transferexperiment/D01");
 const deepest=await (await get("/api/command?company=B2&role=D10-M15-W50-S150-G500-H666")).json();
 assert.equal(deepest.level,"H");
 assert.equal(deepest.actual_external_platform_contact_verified,false);
 assert.equal((await get("/api/command?company=B2")).status,422);
 assert.equal((await get("/api/command?company=B2&role=D11")).status,404);
 assert.equal((await worker.fetch(new Request(base+"/api/command",{method:"POST"}))).status,405);
});
