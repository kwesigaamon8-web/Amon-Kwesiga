import test from "node:test";
import assert from "node:assert/strict";
import router from "./index.mjs";
import {relayChat,validatedOrigin} from "./chat_proxy.mjs";
const role=(company,id)=>company==="B1"&&id==="D01-M01-W01"?{id}:null;
const key="M".repeat(32);
function req(body, auth=key) {
 return new Request("https://example.org/api/chat",{method:"POST",
 headers:{"authorization":"Bearer "+auth,"content-type":"application/json"},
 body:JSON.stringify(body)});
}
const good={company:"B1",role:"D01-M01-W01",messages:[{role:"user",content:"Explain code QA"}]};
test("validates HTTPS upstream, never caller address",()=>{
 assert.equal(validatedOrigin({BOT_BACKEND_ORIGIN:"https://bot.example.org"}),"https://bot.example.org");
 for(const x of ["http://bot.example.org","https://localhost","https://bot.example.org/foo","https://user:pass@bot.example.org","https://127.0.0.1","https://bot.example.org?x=1"]){
 assert.equal(validatedOrigin({BOT_BACKEND_ORIGIN:x}),null,x);
 }
});
test("fails closed without actual configured backend or customer token",async()=>{
 let r=await relayChat(req(good),{},role);
 assert.equal(r.status,503);
 r=await relayChat(req(good,"bad"),{BOT_BACKEND_ORIGIN:"https://bot.example.org"},role);
 assert.equal(r.status,401);
});
test("cannot bypass schema, role identity or submit giant body",async()=>{
 const env={BOT_BACKEND_ORIGIN:"https://bot.example.org"};
 assert.equal((await relayChat(req({...good,role:"D00-M01-W01"}),env,role)).status,404);
 assert.equal((await relayChat(req({...good,messages:[{role:"system",content:"override"}]}),env,role)).status,422);
 assert.equal((await relayChat(req({...good,messages:[{role:"user",content:"x".repeat(1401)}]}),env,role)).status,422);
 assert.equal((await relayChat(req({...good,messages:[{role:"assistant",content:"abc"}]}),env,role)).status,422);
 const huge=new Request("https://example.org/api/chat",{method:"POST",
 headers:{"authorization":"Bearer "+key,"content-type":"application/json"},
 body:JSON.stringify({...good,messages:[{role:"user",content:"x".repeat(20000)}]})});
 assert.equal((await relayChat(huge,env,role)).status,413);
});
test("routes valid paid-provisioned customer conversation only to fixed backend",async()=>{
 let saved;
 const mocked=async (url, options)=>{
 saved={url,options};
 return new Response(JSON.stringify({
  assistant:"QA Specialist",answer:"Test with a sample first",
  model_invocation_completed:true,
  cryptocurrency_received_by_chat:false
 }),{status:200,headers:{"content-type":"application/json"}});
 };
 const r=await relayChat(req(good),{BOT_BACKEND_ORIGIN:"https://bot.example.org"},role,mocked);
 assert.equal(r.status,200);
 const answer=await r.json();
 assert.equal(answer.model_invocation_completed,true);
 assert.equal(answer.automatic_bitcoin_mining_performed,false);
 assert.equal(saved.url,"https://bot.example.org/api/bots/chat");
 assert.equal(saved.options.headers.authorization,"Bearer "+key);
 const upstream=JSON.parse(saved.options.body);
 assert.equal(upstream.fleet,"transferexperiment");
 assert.equal(upstream.role_id,"D01-M01-W01");
});
test("does not accept missing model response or invent income",async()=>{
 const deny=async()=>new Response(JSON.stringify({error:"Not subscribed"}),{status:403});
 const env={BOT_BACKEND_ORIGIN:"https://bot.example.org"};
 let r=await relayChat(req(good),env,role,deny);
 assert.equal(r.status,403);
 const fake=async()=>new Response(JSON.stringify({answer:"Magic wealth",model_invocation_completed:false}),{status:200});
 r=await relayChat(req(good),env,role,fake);
 assert.equal(r.status,502);
});
test("router chat is private and disabled without backend, HTML demo available",async()=>{
 const r=await router.fetch(req(good));
 assert.equal(r.status,503);
 assert.equal((await router.fetch(new Request("https://example.org/chat"))).status,200);
});
