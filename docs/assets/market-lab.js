"use strict";
/* B1/B2 AI Studio original Free Business & Marketing Lab.
 * Pure local-only functions. No network requests, account access, or automatic posts.
 * Source licensed under docs/FREE_SOFTWARE_LICENSE.md. */
(function(root,factory){
 const api=factory();
 if(typeof module==="object"&&module.exports)module.exports=api;
 root.B1B2MarketLab=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
 const LIMIT=100000;
 function input(v){const s=String(v==null?"":v);if(s.length>LIMIT)throw Error("Input exceeds 100 KB");return s;}
 function trimmed(v,n=250){return input(v).trim().slice(0,n);}
 function money(v,label="Amount"){const s=String(v).trim();if(!/^\d{1,12}(?:\.\d{1,2})?$/.test(s))throw Error(label+" must be nonnegative money with at most two decimals");const [whole,part=""]=s.split(".");return BigInt(whole)*100n+BigInt((part+"00").slice(0,2));}
 function format(c){return (c<0n?"-":"")+((c<0n?-c:c)/100n).toString()+"."+((c<0n?-c:c)%100n).toString().padStart(2,"0");}
 function integer(v,name){const s=String(v).trim();if(!/^\d{1,9}$/.test(s))throw Error(name+" must be a nonnegative whole number");return Number(s);}
 function json(s){let o;try{o=JSON.parse(input(s));}catch{throw Error("Provide valid JSON");}if(!o||typeof o!=="object"||Array.isArray(o))throw Error("Provide a JSON object");return o;}
 function csv(s){const text=input(s).replace(/\r\n?/g,"\n").trim();if(!text)throw Error("CSV is empty");const lines=text.split("\n");if(lines.length>5001)throw Error("Maximum 5000 data rows");const rows=lines.map((l,i)=>{const cells=l.split(",").map(x=>x.trim());if(cells.some(x=>x.includes('"')))throw Error("For this simple planner, CSV quoted fields are not supported. Remove commas inside fields.");return cells;});const width=rows[0].length;if(rows.some(r=>r.length!==width))throw Error("CSV row width mismatch");return rows;}
 function httpUrl(x){
  const s=trimmed(x,2000);let u;try{u=new URL(s);}catch{throw Error("Use a complete HTTPS website URL");}
  if(u.protocol!=="https:")throw Error("Only HTTPS URLs accepted");
  if(u.username||u.password)throw Error("URLs with passwords or usernames not supported");
  return u;
 }
 function utm(raw){
  const x=json(raw),u=httpUrl(x.url);
  const labels=["source","medium","campaign","content","term"];
  for(const label of labels){
   const v=trimmed(x[label],120);
   if(label!=="content"&&label!=="term"&&!v)throw Error(label+" is required");
   if(v)u.searchParams.set("utm_"+label,v);
  }
  return {url:u.toString(),campaign:trimmed(x.campaign),note:"Generates tagged links only; does not publish or track any user."};
 }
 function inventory(raw){
  const rows=csv(raw),head=rows.shift().map(x=>x.toLowerCase()),expected=["sku","on_hand","weekly_demand","lead_weeks","safety_stock"];
  if(head.join("|")!==expected.join("|"))throw Error("Use headers: "+expected.join(","));
  const seen=new Set();const results=rows.map((r,i)=>{
   const sku=trimmed(r[0],100);if(!sku||seen.has(sku))throw Error("Blank or duplicate SKU at row "+(i+2));seen.add(sku);
   const [hand,demand,lead,safety]=r.slice(1).map((v,j)=>integer(v,expected[j+1]));
   const target=lead*demand+safety;
   if(!Number.isSafeInteger(target))throw Error("Quantity calculation too large");
   return {sku,on_hand:hand,weekly_demand:demand,lead_weeks:lead,safety_stock:safety,reorder_point:target,suggested_order:Math.max(0,target-hand),status:hand<target?"REORDER":"SUFFICIENT"};
  });
  return {rows:results.length,to_reorder:results.filter(x=>x.status==="REORDER").length,items:results,note:"Indicative quantities; verify real demand, lead times and stock data."};
 }
 function quote(raw){
  const x=json(raw),currency=trimmed(x.currency||"USD",3).toUpperCase();
  if(!/^[A-Z]{3}$/.test(currency))throw Error("Currency must be three letters");
  if(!Array.isArray(x.items)||x.items.length<1||x.items.length>200)throw Error("Provide 1-200 items");
  let total=0n;const items=x.items.map((it,i)=>{
   const qty=integer(it.quantity,"Quantity");if(qty<1||qty>100000)throw Error("Quantity must be 1-100000");
   const unit=money(it.unit_price,"Unit price"),line=BigInt(qty)*unit;total+=line;
   return {description:trimmed(it.description),quantity:qty,unit_price:format(unit),line_total:format(line)};
  });
  const pct=integer(x.deposit_percent||0,"Deposit percentage");if(pct>100)throw Error("Deposit cannot exceed 100%");
  const deposit=(total*BigInt(pct)+50n)/100n;
  return {currency,items,subtotal:format(total),deposit_percent:pct,deposit_required:format(deposit),balance_after_deposit:format(total-deposit),note:"Draft only. Not an accepted offer, invoice or contract."};
 }
 function schedule(raw){
  const rows=csv(raw),head=rows.shift().map(x=>x.toLowerCase());
  if(head.join(",")!=="name,platform,day,owner,status")throw Error("Headers: name,platform,day,owner,status");
  const statuses=["idea","draft","approved","published"];const data=rows.map((r,i)=>{
   const [name,platform,day,owner,status]=r;
   if(!name||!platform||!owner)throw Error("Missing entry at row "+(i+2));
   if(!/^\d{4}-\d\d-\d\d$/.test(day)||new Date(day+"T00:00:00Z").toISOString().slice(0,10)!==day)throw Error("Invalid date at row "+(i+2));
   if(!statuses.includes(status.toLowerCase()))throw Error("Status must be idea, draft, approved or published");
   return {name:trimmed(name),platform:trimmed(platform),day,owner:trimmed(owner),status:status.toLowerCase(),
           verified_public_url:null};
  });
  return {planned_rows:data.length,published_claims_unverified:data.filter(x=>x.status==="published").length,
   calendar:data.sort((a,b)=>a.day.localeCompare(b.day)),
   note:"This is a manual plan; a 'published' field is NOT proof that a post exists. Record a verified URL separately."};
 }
 function feedback(raw){
  const rows=csv(raw),head=rows.shift().map(x=>x.toLowerCase());
  if(head.join(",")!=="product,rating,comment")throw Error("Headers: product,rating,comment");
  let count=0,sum=0;const byProduct=Object.create(null);
  for(const [product,value,comment] of rows){
   const rating=integer(value,"Rating");if(rating<1||rating>5)throw Error("Ratings must be 1-5");
   const p=trimmed(product,100);if(!p)throw Error("Product name required");
   if(!Object.prototype.hasOwnProperty.call(byProduct,p))Object.defineProperty(byProduct,p,{value:{count:0,total:0,comments:[]},enumerable:true,writable:true,configurable:true});
   const slot=byProduct[p];slot.count++;slot.total+=rating;if(slot.comments.length<5)slot.comments.push(trimmed(comment,120));count++;sum+=rating;
  }
  const groups=Object.entries(byProduct).map(([product,v])=>({product,review_count:v.count,average_rating:Number((v.total/v.count).toFixed(2)),sample_comments:v.comments}));
  return {records:count,average_rating:count?Number((sum/count).toFixed(2)):null,by_product:groups,
   note:"Summarizes supplied feedback; does not verify authenticity or represent real customers."};
 }
 function release(raw){
  const x=json(raw),name=trimmed(x.name,80),version=trimmed(x.version,32),summary=trimmed(x.summary,300),url=trimmed(x.source_url,1500);
  if(!name||!version||!summary)throw Error("name, version and summary are required");
  if(!/^[\w.-]+$/.test(version))throw Error("Version characters invalid");
  if(url)httpUrl(url);
  const changes=(Array.isArray(x.changes)?x.changes:[]).slice(0,20).map(y=>trimmed(y,180)).filter(Boolean);
  const tests=(Array.isArray(x.tests)?x.tests:[]).slice(0,20).map(y=>trimmed(y,180)).filter(Boolean);
  return {markdown:"# "+name+" v"+version+"\n\n"+summary+"\n\n## Changes\n"+(changes.map(z=>"- "+z).join("\n")||"- No changes supplied")+
   "\n\n## Test evidence\n"+(tests.map(z=>"- "+z).join("\n")||"- Testing not supplied")+
   "\n\n## Source\n"+(url||"Source not provided")+
   "\n\nDo not claim customer deployments, payments, or releases without independent verification.",
   note:"Generated text is a draft, not evidence of a completed release."};
 }
 const tools=[
 {id:"utm-links",name:"UTM Campaign Link Builder",category:"Marketing",type:"JSON",sample:JSON.stringify({url:"https://example.org/tools",source:"community",medium:"social",campaign:"free-software-launch",content:"toolbox"},null,2),run:utm},
 {id:"inventory",name:"Stock Reorder Planner",category:"Business",type:"CSV",sample:"sku,on_hand,weekly_demand,lead_weeks,safety_stock\nSAMPLE-101,6,5,2,3\nSAMPLE-102,40,5,2,5",run:inventory},
 {id:"quote",name:"Freelance Quote & Deposit Calculator",category:"Business",type:"JSON",sample:JSON.stringify({currency:"USD",deposit_percent:40,items:[{description:"Technical document",quantity:2,unit_price:"25.00"}]},null,2),run:quote},
 {id:"post-calendar",name:"Permissioned Social Campaign Planner",category:"Marketing",type:"CSV",sample:"name,platform,day,owner,status\nToolbox demo,GitHub,2026-11-21,B1,draft\nBug fix release,Dev forum,2026-11-23,B2,idea",run:schedule},
 {id:"feedback",name:"Customer Feedback Summary",category:"Research",type:"CSV",sample:"product,rating,comment\nToolbox,5,Simple to use\nToolbox,4,Add examples\nMini Apps,4,Useful demos",run:feedback},
 {id:"release",name:"Software Release Notes Generator",category:"Developer",type:"JSON",sample:JSON.stringify({name:"Example App",version:"1.1.0",summary:"Improves local file handling",changes:["Adds more examples","Fixes line parsing"],tests:["Local unit tests passed"],source_url:"https://example.org/source"},null,2),run:release}
 ];
 return {tools,run(id,data){const x=tools.find(t=>t.id===id);if(!x)throw Error("Unknown application");return x.run(data);},utm,inventory,quote,schedule,feedback,release};
});
