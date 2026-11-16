import test from "node:test";
import assert from "node:assert/strict";
import app,{route} from "./index.mjs";
import {profile} from "./superworker.mjs";
test("superworker ancestry and no phantom activity",()=>{
 const x=profile(route("B2","D04-M05-W10-S100-G300-H666"));
 assert.equal(x.original_parent,"BountyScoutAI/D04-M05-W10-S100-G300");
 assert.deepEqual(x.upward_reporting_chain.slice(-2),["CHIEF_D","HUMAN_OWNER"]);
 assert.equal(x.actual_models_started,0);
 assert.equal(x.actual_ASIC_miners_started,0);
 assert.equal(x.earned_BTC_verified,false);
});
test("public plan endpoint validates roles and doesn't activate miners",async()=>{
 const ok=await app.fetch(new Request("https://example.org/api/superworker?company=B1&role=D10-M15-W50"));
 assert.equal(ok.status,200);
 assert.equal((await ok.json()).status,"CONFIGURED_SUPERWORKER_NOT_EXECUTING");
 const bad=await app.fetch(new Request("https://example.org/api/superworker?company=B1&role=INVALID"));
 assert.equal(bad.status,404);
});
