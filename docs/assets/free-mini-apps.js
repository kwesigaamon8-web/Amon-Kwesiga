"use strict";
/* Six original, pure, in-browser B1/B2 mini-application engines. No network access. */
(function(root,factory){
 const api=factory();
 if(typeof module==="object"&&module.exports)module.exports=api;
 root.B1B2MiniApps=api;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
const limit=s=>{s=String(s==null?"":s);if(s.length>200000)throw Error("Maximum input 200KB.");return s;};
const clean=s=>limit(s).trim().slice(0,160);
function cents(value){
 const text=String(value).trim();
 if(!/^\d{1,10}(?:\.\d{1,2})?$/.test(text))throw Error("Enter positive decimal money with at most 2 decimals.");
 const [int,fraction=""]=text.split(".");
 return BigInt(int)*100n+BigInt((fraction+"00").slice(0,2));
}
function decimal(v){return (v/100n).toString()+"."+(v%100n).toString().padStart(2,"0");}
function pcRate(value){
 const rate=String(value==null?"0":value).trim();
 if(!/^\d{1,3}(?:\.\d{1,2})?$/.test(rate))throw Error("Tax must be a percent 0-100 with at most 2 decimals.");
 let r=cents(rate);if(r>10000n)throw Error("Tax rate cannot exceed 100%");
 return r;
}
function invoice(raw){
 const x=JSON.parse(limit(raw));
 if(!x || typeof x!=="object"||Array.isArray(x))throw Error("Invoice needs a JSON object");
 if(!Array.isArray(x.items)||x.items.length<1||x.items.length>100)throw Error("Invoice needs 1-100 line items.");
 const currency=String(x.currency||"USD").toUpperCase();
 if(!/^[A-Z]{3}$/.test(currency))throw Error("Currency must be ISO-like three letters.");
 let subtotal=0n;
 const items=x.items.map((item,index)=>{
  const qty=Number(item.quantity);
  if(!Number.isInteger(qty)||qty<1||qty>100000)throw Error("Quantity must be integer 1-100000.");
  const p=cents(item.unit_price);
  const total=p*BigInt(qty);subtotal+=total;
  return {line:index+1,description:clean(item.description),quantity:qty,unit_price:decimal(p),line_total:decimal(total)};
 });
 const taxPercent=pcRate(x.tax_percent||0);
 const tax=(subtotal*taxPercent+5000n)/10000n;
 return {issuer:clean(x.issuer),customer:clean(x.customer),invoice_number:clean(x.invoice_number),currency,items,
  subtotal:decimal(subtotal),tax_percent:decimal(taxPercent),tax:decimal(tax),total:decimal(subtotal+tax),
  note:"Draft only. Verify identity, rates, tax rules and contract terms independently before issuing."};
}
function ledger(raw){
 const rows=limit(raw).replace(/\r/g,"").trim().split("\n").filter(Boolean);
 if(rows.length<2)throw Error("Enter header then at least one row: type,category,amount.");
 const headers=rows[0].toLowerCase().split(",").map(x=>x.trim());
 if(headers.join(",")!=="type,category,amount")throw Error("Header must be type,category,amount.");
 const data=rows.slice(1);
 if(data.length>5000)throw Error("Maximum 5000 transactions.");
 let income=0n,expense=0n;const category=new Map();
 for(const [i,line] of data.entries()){
  const cells=line.split(",").map(x=>x.trim());if(cells.length!==3)throw Error("Line "+(i+2)+" must have 3 fields; use simple CSV without commas within values.");
  const [type,cat,amt]=cells;
  if(!["income","expense"].includes(type.toLowerCase()))throw Error("Type must be income or expense.");
  if(!cat)throw Error("Category cannot be blank");
  const value=cents(amt);
  if(type.toLowerCase()==="income")income+=value;else expense+=value;
  const key=type.toLowerCase()+" — "+clean(cat);
  category.set(key,(category.get(key)||0n)+value);
 }
 return {transaction_count:data.length,income:decimal(income),expense:decimal(expense),
   net:((income-expense)<0n?"-":"")+decimal((income-expense)<0n?expense-income:income-expense),
   categories:Object.fromEntries([...category].map(([k,v])=>[k,decimal(v)])),
   note:"Local descriptive budget summary, not a formal financial statement or tax calculation."};
}
function tasks(raw){
 const rows=limit(raw).replace(/\r/g,"").split("\n").filter(Boolean);
 if(rows.length>500)throw Error("Maximum 500 tasks.");
 const priorities={high:0,medium:1,low:2};
 const items=rows.map((line,i)=>{
  const parts=line.split("|").map(s=>s.trim());
  if(parts.length!==3)throw Error("Task line "+(i+1)+" must be status | priority | task.");
  const [status,priority,title]=parts;
  if(!["todo","doing","done"].includes(status.toLowerCase()))throw Error("Status must be todo, doing or done.");
  if(!(priority.toLowerCase() in priorities))throw Error("Priority must be high, medium or low.");
  if(!title)throw Error("Task title required.");
  return {status:status.toLowerCase(),priority:priority.toLowerCase(),title:clean(title)};
 });
 const sorted=items.slice().sort((a,b)=>priorities[a.priority]-priorities[b.priority]||a.title.localeCompare(b.title));
 return {count:items.length,progress:{todo:items.filter(x=>x.status==="todo").length,doing:items.filter(x=>x.status==="doing").length,done:items.filter(x=>x.status==="done").length},
  board:sorted.map(x=>(x.status==="done"?"- [x] ":"- [ ] ")+x.title+" ("+x.status+", "+x.priority+")").join("\n")};
}
function cards(raw){
 const rows=limit(raw).replace(/\r/g,"").split("\n").filter(Boolean);
 if(rows.length>150)throw Error("Maximum 150 flashcards.");
 const deck=rows.map((line,i)=>{
  const sep=line.indexOf("::");if(sep<1)throw Error("Card "+(i+1)+" must use Question :: Answer");
  const question=clean(line.slice(0,sep)),answer=clean(line.slice(sep+2));
  if(!question||!answer)throw Error("Each card needs question and answer");
  return {question,answer};
 });
 return {count:deck.length,deck};
}
function agenda(raw,goal=""){
 const rows=limit(raw).replace(/\r/g,"").split("\n").filter(Boolean);
 if(rows.length>100)throw Error("Maximum 100 agenda topics.");
 let minute=0;
 const topics=rows.map((line,i)=>{
  const parts=line.split("|").map(x=>x.trim());if(parts.length!==2)throw Error("Topic "+(i+1)+" must be Topic | minutes.");
  const duration=Number(parts[1]);if(!Number.isInteger(duration)||duration<1||duration>240)throw Error("Duration must be integer 1-240 minutes");
  const start=minute;minute+=duration;
  return {topic:clean(parts[0]),duration_minutes:duration,start_minute:start,end_minute:minute};
 });
 return {goal:clean(goal),total_minutes:minute,topics,
   markdown:"# Meeting plan"+(goal?" — "+clean(goal):"")+"\n\n"+topics.map(t=>"- "+t.start_minute+"–"+t.end_minute+" min: "+t.topic).join("\n")};
}
function palette(raw){
 const input=limit(raw).trim();if(!/^#[\da-fA-F]{6}$/.test(input))throw Error("Use six-digit hex #rrggbb.");
 const arr=[1,3,5].map(i=>parseInt(input.slice(i,i+2),16));
 const complement=arr.map(x=>255-x);
 const tint=arr.map(x=>Math.round((x+255)/2));
 const shade=arr.map(x=>Math.round(x/2));
 const hx=a=>"#"+a.map(x=>x.toString(16).padStart(2,"0")).join("");
 return {base:input.toLowerCase(),complement:hx(complement),tint:hx(tint),shade:hx(shade),
  css:"--color-base: "+input.toLowerCase()+";\n--color-complement: "+hx(complement)+";\n--color-tint: "+hx(tint)+";\n--color-shade: "+hx(shade)+";"};
}
const catalog=[
 {id:"invoice",name:"Invoice Draft Builder",category:"Business",format:"JSON",sample:JSON.stringify({issuer:"Example Studio",customer:"Example Buyer",invoice_number:"DEMO-001",currency:"USD",tax_percent:0,items:[{description:"Data cleanup",quantity:2,unit_price:"5.00"}]},null,2),run:invoice},
 {id:"budget",name:"Income & Expense Summary",category:"Money",format:"CSV",sample:"type,category,amount\nincome,Sales,300.00\nexpense,Supplies,125.25\nexpense,Transport,20.00",run:ledger},
 {id:"tasks",name:"Project Task Board Export",category:"Productivity",format:"Lines",sample:"todo | high | Write tests\ndoing | medium | Improve website\ndone | low | Share source",run:tasks},
 {id:"cards",name:"Flashcard Study Deck",category:"Education",format:"Lines",sample:"What is HTML? :: HyperText Markup Language\nWhat is JSON? :: JavaScript Object Notation",run:cards},
 {id:"agenda",name:"Meeting Agenda Planner",category:"Productivity",format:"Lines",sample:"Updates | 10\nDemonstration | 20\nNext actions | 10",run:agenda},
 {id:"palette",name:"Color Palette Generator",category:"Design",format:"Hex",sample:"#2375c9",run:palette}
];
return {catalog,run(id,raw,second){const item=catalog.find(x=>x.id===id);if(!item)throw Error("Unknown mini app");return item.run(raw,second);},invoice,ledger,tasks,cards,agenda,palette};
});
