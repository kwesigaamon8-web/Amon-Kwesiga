// On-demand B1/B2 role directory for one edge worker.
// Does not run LLMs, create Bitcoin hashrate, send payments or provision servers.
import {relayChat} from "./chat_proxy.mjs";
import {CHAT_HTML} from "./chat_page.mjs";
export const CONFIGURED_B_ROLE_POSITIONS="750377265360";
export const TOTAL_CONFIGURED_POSITIONS="750377265361"; // plus one Chief D
const fleets={B1:"transferexperiment",B2:"BountyScoutAI"};
const lanes=[
  ["Original coding","Build original tested fixes for a real funded buyer"],
  ["QA and testing","Verify a buyer's real program and provide reproducible tests"],
  ["Data transformation","Create original CSV/JSON conversions for an accepted client"],
  ["Technical writing","Draft useful original documentation for genuine buyers"],
  ["Customer-support assistant","Offer bounded text-response service to an actual customer"],
  ["Buyer scouting","Source one legitimate paid client and qualify the true payer"],
  ["Eligibility verification","Check funded bounty, deadline and duplicate claims"],
  ["Hosting researcher","Compare real available serverless and VM service limits"],
  ["Mining partnership researcher","Find a consenting real ASIC owner and test economics, never remotely mine"],
  ["Payment reconciliation","Check verified correct-chain TXID and customer's accepted invoice"],
  ["Code repair","Create one reproducible fix in a permitted codebase"],
  ["Source quality audit","Distinguish real clients and payers from claims and spam"]
];
const valid=[/^D(?:0[1-9]|10)$/, /^M(?:0[1-9]|1[0-5])$/, /^W(?:0[1-9]|[1-4][0-9]|50)$/,
 /^S(?:00[1-9]|0[1-9][0-9]|1[0-4][0-9]|150)$/,
 /^G(?:00[1-9]|0[1-9][0-9]|[1-4][0-9][0-9]|500)$/,
 /^H(?:00[1-9]|0[1-9][0-9]|[1-5][0-9][0-9]|6(?:[0-5][0-9]|6[0-6]))$/];
function reply(obj,status=200){return new Response(JSON.stringify(obj),{status,headers:{"content-type":"application/json; charset=utf-8","cache-control":"public,max-age=20","x-content-type-options":"nosniff"}});}
export function route(company,role) {
 if(company==="CHIEF"&&role==="D") return {id:"CHIEF/D",parent:"HUMAN_OWNER",role_status:"configured_single_supervisor",actual_model_connected:false};
 const fleet=fleets[company];
 if(!fleet||typeof role!=="string"||role.length>95)return null;
 const p=role.split("-");
 if(p.length<3||p.length>6||p.some((piece,i)=>!valid[i].test(piece)))return null;
 let v=company==="B1"?2166136261:7090102;
 for(const c of role) v=(Math.imul(v,33)^c.charCodeAt(0))>>>0;
 const chosen=lanes[v%lanes.length];
 return {id:fleet+"/"+role,parent:fleet+"/"+p.slice(0,-1).join("-"),director:fleet+"/"+p[0],
  role_level:["W","S","G","H"][p.length-3],task_lane:chosen[0],feasible_task:chosen[1],
  role_status:"CONFIGURED_VIRTUAL_ID_NOT_RUNNING",
  verified_model_instance:false,physical_miner_allocated:false,external_tools_granted:false,
  money_earned_from_this_role:"NOT_VERIFIED",account_authentication_available:false,
  evidence_required:"real source, authenticated buyer/owner permission, delivered work, acceptance, confirmed correct-chain payment"};
}
export function voluntaryPoolTemplate(company,workerName){
 const addresses={
  B1:"bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z",
  B2:"bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9"
 };
 if(!addresses[company]||typeof workerName!=="string"||!/^[a-zA-Z0-9_-]{1,32}$/.test(workerName))return null;
 return {
  company,owner_receiving_address:addresses[company],
  pool:"Public Pool PPLNS (NOT SOLO)",
  source:"https://web.public-pool.io/",
  stratum_tls:"stratum+tls://public-pool.io:14333",
  stratum_tcp:"stratum+tcp://public-pool.io:13333",
  miner_username:addresses[company]+"."+workerName,
  miner_password:"consult_miner_manufacturer_pool_setup",
  hardware_requirement:"ACTUAL operator-owned SHA-256 ASIC with explicit operator consent",
  approval_required:"Physical rig operator must independently authorize payout to the named Bitcoin address and agree any compensation/allocation",
  payouts:"PPLNS rewards are only distributed after actual pool block rewards and eligible recorded work; never guarantee income",
  participating_ASICs_verified_by_endpoint:0,
  new_BTC_payouts_verified_by_endpoint:0,
  mining_activated_by_template:false,
  no_transfer_or_hardware_configuration_performed:true
 };
}
const page=[
 '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
 '<title>B Agent Network — On-demand Role Directory</title><style>',
 'body{font:16px system-ui,sans-serif;background:#f3f7fa;color:#182737;max-width:790px;margin:34px auto;padding:0 16px}',
 'main{background:white;padding:24px;border:1px solid #dce5ee;border-radius:14px}',
 'input,select,button{font:inherit;padding:11px;margin:6px;border-radius:8px;border:1px solid #b4c3d4}',
 'button{color:white;background:#1c579a;border:0;font-weight:600;cursor:pointer}',
 'pre{padding:15px;white-space:pre-wrap;overflow-wrap:anywhere;background:#edf3fa;border-radius:8px}',
 '.note{color:#536378;line-height:1.6}a{color:#1c579a}</style></head><body><main>',
 '<h1>B Agent Network</h1><p class="note">All configured identities can be looked up on demand once deployed. An ID is not an independent server, an executing AI model or a Bitcoin miner.</p>',
 '<label>Company <select id="c"><option>B1</option><option>B2</option></select></label>',
 '<label>Role ID <input id="r" value="D01-M01-W01" maxlength="95" autocomplete="off"></label>',
 '<button id="find">Find earning assignment</button><pre id="o">Choose a role to look up.</pre>',
 '<p class="note">Possible legal earning work: coding, QA, data services, customer-support assistants, writing, funded bounties, payment verification, and voluntary ASIC-mining partnerships.</p>',
 '<p><a href="/chat">Chat with a provisioned specialist</a> · <a href="/api/capacity">Capacity disclosure</a> · <a href="/api/opportunities">Opportunity categories</a> · <a href="/api/mining">Mining requirements</a></p>',
 '<p class="note">This web directory is not a cryptocurrency miner, a payment processor, or a live LLM hosting backend. The existing /bots private pilot is a separate Flask app.</p>',
 '</main><script>',
 'document.getElementById("find").addEventListener("click",async()=>{',
 'const u="/api/role?company="+encodeURIComponent(document.getElementById("c").value)+"&role="+encodeURIComponent(document.getElementById("r").value.trim());',
 'const out=document.getElementById("o");out.textContent="Looking up role...";',
 'try{const r=await fetch(u);out.textContent=JSON.stringify(await r.json(),null,2)}catch(e){out.textContent="Service unavailable"}});',
 '</script></body></html>'
].join("");
export default {
 async fetch(req,env={}) {
  const requestedPath=new URL(req.url).pathname;
  if(requestedPath==="/api/chat")return relayChat(req,env,route);
  if(req.method!=="GET"&&req.method!=="HEAD")return reply({error:"Read-only except customer-provisioned chat"},405);
  const url=new URL(req.url);
  if(url.pathname==="/"||url.pathname==="/directory")
   return new Response(req.method==="HEAD"?null:page,{headers:{"content-type":"text/html; charset=utf-8","cache-control":"public,max-age=120","x-content-type-options":"nosniff"}});
  if(url.pathname==="/chat")return new Response(req.method==="HEAD"?null:CHAT_HTML,
    {headers:{"content-type":"text/html; charset=utf-8","cache-control":"public,max-age=120","x-content-type-options":"nosniff"}});
  if(url.pathname==="/health")return reply({status:"identity_directory_responding",llm_model_running:false,mining_hardware_running:false});
  if(url.pathname==="/api/role"){
   const data=route(url.searchParams.get("company"),url.searchParams.get("role"));
   return data?reply(data):reply({error:"No such role ID/company"},404);
  }
  if(url.pathname==="/api/capacity")return reply({
   configured_B_role_positions:CONFIGURED_B_ROLE_POSITIONS,
   chief_D_configured:"1",configured_total:TOTAL_CONFIGURED_POSITIONS,
   virtual_role_resolver:"addressable_on_demand_only_if_deployed",
   individual_hosted_servers_created:0,actual_chat_models_started:0,
   actual_sha256_miners_created:0,verified_owner_crypto_receipts:0,
   paid_customer_count_verified_by_directory:0,
   sustainable_execution_requires:"actual authorized hosted backend, user demand, separate real model capacity, usage fees and actual willing mining hardware operators"
  });
  if(url.pathname==="/api/opportunities")return reply({lanes:lanes.map(x=>({name:x[0],possible_work:x[1]})),
   live_funded_jobs_verified:false,customer_acceptance_or_income_verified:false});
  if(url.pathname==="/api/mining/setup"){
    const data=voluntaryPoolTemplate(url.searchParams.get("company"),url.searchParams.get("worker"));
    return data?reply(data):reply({error:"Only B1/B2 and a short alphanumeric real miner name allowed"},422);
  }
  if(url.pathname==="/api/mining")return reply({
   source:"https://web.public-pool.io/",
   pool_pplns:"stratum+tls://public-pool.io:14333",
   pool_solo:"stratum+tls://public-pool.io:4333",
   hardware_required:"consenting operator-controlled physical SHA-256 ASIC for competitive Bitcoin mining",
   actual_hashrate_created:0,verified_new_pool_rewards:0,
   prohibited:"unconsented machines, free web hosting/trial platforms, GitHub Actions mining",
   financial_proof:"operator opt-in, rig identity/hashrate, pool terms, accepted shares and actual payout TXID"
  });
  return reply({error:"Route not found"},404);
 }
};
