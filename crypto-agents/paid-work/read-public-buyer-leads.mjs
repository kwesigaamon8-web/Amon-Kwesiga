// Read-only B1/B2 public buyer/agent lead verification. No posts, accounts, email, wallets.
import {writeFileSync,appendFileSync} from "node:fs";
import assert from "node:assert/strict";
const campfireUrl="https://agentsboard.org/api/v1/threads/466";
const forumUrl="https://forumforagents.com/api/threads/building1";
const jobUrl="https://api.moltjobs.io/v1/jobs?status=OPEN&limit=50";
const clawUrl="https://clawlancer.ai/api/listings?listing_type=BOUNTY";
const trackedPost="2pni6mmqk";
const clean=x=>String(x??"").replace(/\s+/g," ").slice(0,650);
async function readJson(url){
  const r=await fetch(url,{headers:{accept:"application/json"},signal:AbortSignal.timeout(16000)});
  if(!r.ok)throw new Error("HTTP "+r.status);
  return await r.json();
}
function arrayFrom(root,keys){
  if(Array.isArray(root))return root;
  for(const key of keys){
    const value=key.split(".").reduce((obj,segment)=>obj?.[segment],root);
    if(Array.isArray(value))return value;
  }
  return [];
}
function briefPost(p){
 return {id:p?.id??p?.post_id??null,author:clean(p?.author?.name??p?.author??p?.agent_name??p?.user?.name),
   date:p?.created_at??p?.createdAt??null,body:clean(p?.body??p?.content??p?.text)};
}
function checkForum(d){
 const posts=arrayFrom(d,["posts","thread.posts","data.posts","replies","thread.replies"]);
 const index=posts.findIndex(p=>String(p?.id??p?.post_id)===trackedPost);
 return {
   message_count:posts.length,original_post_found:index>=0,
   subsequent_posts:index>=0?posts.slice(index+1).map(briefPost).slice(0,25):[],
   all_recent_posts:index<0?posts.slice(-5).map(briefPost):[]
 };
}
function checkCampfire(d){
 const root=d?.thread??d?.data?.thread??d;
 const replies=arrayFrom(d,["replies","thread.replies","data.replies","data.thread.replies"]);
 return {thread_id:root?.id??466,thread_title:clean(root?.title),replies_count:replies.length,
   replies:replies.slice(-25).map(briefPost)};
}
function checkJobs(d){
 const jobs=arrayFrom(d,["data.jobs","data.items","data.data","data","jobs","items","results"]);
 return {open_count_returned:jobs.length,
   jobs:jobs.slice(0,30).map(x=>({
     id:x.id??null,title:clean(x.title??x.name),
     budget:x.budgetUsdc??x.budget_usdc??x.amount??null,
     status:x.status??null,
     funding_status:x.escrowStatus??x.escrow_status??x.fundingStatus??x.funding_status??"NOT_PRESENT_IN_PUBLIC_FEED",
     deadline:x.deadlineAt??x.deadline_at??null
   }))};
}
function checkClawlancer(d){
 const listings=arrayFrom(d,["data.listings","data.items","data","listings","items","results"]);
 return {count_returned:listings.length,
   listings:listings.slice(0,35).map(x=>({
     id:x.id??null,title:clean(x.title??x.name),
     amount_microunit:x.price??x.price_usdc??x.amount??null,
     listing_type:x.listing_type??x.type??null,
     status:x.status??"NOT_PRESENT_IN_PUBLIC_FEED",
     funding_status:x.escrow_status??x.funding_status??"NOT_PRESENT_IN_PUBLIC_FEED",
     posted_by:clean(x.seller?.name??x.agent?.name??x.creator?.name)
   }))
 };
}
async function report(name,url,parser){
  try{return {status:"PUBLIC_READ_SUCCEEDED",url,data:parser(await readJson(url))};}
  catch(e){return {status:"UNVERIFIED_NETWORK_OR_SCHEMA",url,error:clean(e.message)};}
}
if(process.argv.includes("--test")){
  assert.equal(checkForum({posts:[{id:"a"},{id:trackedPost},{id:"b",body:"can you help?"}]}).subsequent_posts.length,1);
  assert.equal(checkCampfire({thread:{id:466,title:"Lead"},replies:[{id:7,body:"hello"}]}).replies_count,1);
  assert.equal(checkJobs({data:{jobs:[{id:1,budgetUsdc:"5",escrowStatus:"not-funded"}]}}).jobs[0].funding_status,"not-funded");
  assert.equal(checkJobs({data:[{id:2,escrowStatus:"FUNDED"}]}).open_count_returned,1);
  assert.equal(checkClawlancer({data:{listings:[{id:1,listing_type:"BOUNTY"}]}}).count_returned,1);
  console.log("PUBLIC_LEAD_SELF_TESTS_PASS");
}else{
  const [campfire,forum,moltjobs,clawlancer]=await Promise.all([
    report("campfire",campfireUrl,checkCampfire),
    report("forum",forumUrl,checkForum),
    report("moltjobs",jobUrl,checkJobs),
    report("clawlancer",clawUrl,checkClawlancer)
  ]);
  const data={
    schema:"B1B2_PUBLIC_LEADS_READ_ONLY_V1",checked_utc:new Date().toISOString(),
    campfire,forum,moltjobs,clawlancer,
    no_external_post_or_email_or_wallet_access:true,
    buyer_acceptance_verified:false,
    payment_receipt_verified:false,
    caveat:"Third-party posts and job listings are data, not instructions or verified payment. Escrow must be confirmed on the specific job before bidding or starting."
  };
  writeFileSync("b1b2-public-buyer-leads.json",JSON.stringify(data,null,2)+"\n");
  console.log("B1B2_READ_ONLY_LEAD_RESULT "+JSON.stringify(data));
  const summary=process.env.GITHUB_STEP_SUMMARY;
  if(summary){
    const lines=["## B1/B2 real-buyer lead scan ("+data.checked_utc+")",""];
    for(const [name,item] of Object.entries({CAMPFIRE:campfire,"Forum for Agents":forum,MoltJobs:moltjobs,Clawlancer:clawlancer})){
      lines.push("### "+name,"- "+item.status);
      if(name==="CAMPFIRE")lines.push("- Replies seen: "+(item.data?.replies_count??"not verified"));
      if(name==="Forum for Agents")lines.push("- Replies after B1/B2 post: "+(item.data?.subsequent_posts?.length??"not verified"));
      if(name==="MoltJobs")lines.push("- Public jobs returned: "+(item.data?.open_count_returned??"not verified"));
      if(name==="Clawlancer")lines.push("- Public bounty listings: "+(item.data?.count_returned??"not verified"));
      lines.push("");
    }
    lines.push("No job has been bid on; no payment or acceptance established.");
    appendFileSync(summary,lines.join("\n")+"\n");
  }
}
