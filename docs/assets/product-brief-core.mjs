// Original privacy-first ENIGMA prompt-to-product brief engine.

// Pure functions: no accounts, network calls, storage, spending, model inference or claims of worker execution.

export function clean(value,max=600){return String(value??"").trim().replace(/\r/g,"").replace(/[\u0000-\u001F\u007F]/g," ").slice(0,max)}

export function slug(text){const s=clean(text,160).toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"");return s.slice(0,55)||"new-product"}

export function stableId(text){let h=2166136261;for(const c of String(text)){h^=c.charCodeAt(0);h=Math.imul(h,16777619)}return(h>>>0).toString(16).padStart(8,"0")}

export function createBrief(input){
 if(!input||typeof input!=="object")throw Error("Input object required");
 const prompt=clean(input.prompt,1400),name=clean(input.name,100),audience=clean(input.audience,100),output=clean(input.output,150),acceptance=clean(input.acceptance,380);
 const kind=String(input.kind||"software").toLowerCase();
 const valid=["software","data","research","design","documentation"];
 if(!valid.includes(kind))throw Error("Unsupported product category");
 if(prompt.length<12)throw Error("Describe the product in at least 12 characters");
 const title=name || prompt.split(/[.!?]/)[0].slice(0,72);
 const id="EN-IDEA-"+stableId(kind+"|"+title+"|"+prompt);
 const checks={
  software:["Run a fictional example from input to expected output","Reject empty or invalid input with a clear explanation","Inspect source, dependencies and permissions before delivery"],
  data:["Agree input/output schema with buyer and use synthetic samples","Verify duplicates, blank values and the intended transformations","Record row counts and exceptions in a reproducible report"],
  research:["Name the original publisher, date and source URL for material claims","Check applicable data rights and distinguish facts from inference","Avoid private-person data and log uncertainty"],
  design:["Confirm dimensions, format and intended audience before production","Check legibility and contrast on desktop/mobile outputs","Record buyer-approved revisions and final export format"],
  documentation:["Confirm technical audience, scope and supported version","Reproduce all commands and links on safe sample inputs","Check that copy is original and sources are attributed"]
 };
 const tests=checks[kind].concat(acceptance?["Buyer-defined acceptance: "+acceptance]:[]);
 const buyer=audience||"A buyer with a matching real problem";
 const deliverable=output||({software:"Tested source code and instructions",data:"Cleaned sample dataset and exception log",research:"Source-cited original findings and evidence register",design:"Reviewed original design and editable source",documentation:"Original editable guide with verification steps"})[kind];
 const safeTitle=title.replace(/[\n\r]/g," ");
 const parts=[
 "# "+safeTitle,
 "",
 "Product brief ID: "+id,
 "Status: PROPOSED IDEA ONLY — not built, sold, posted by a worker or paid",
 "Audience: "+buyer,
 "Category: "+kind,
 "",
 "## Customer problem",
 prompt,
 "",
 "## Proposed original deliverable",
 deliverable,
 "",
 "## Acceptance and QA tests",
 ...tests.map((x,i)=>String(i+1)+". "+x),
 "",
 "## Distribution and sale gates",
 "- Produce original source or a source-cited report, then test and review it.",
 "- Publish only to a permitted, authenticated owner-controlled channel; preserve proof URL.",
 "- Existing free products remain free; price only agreed new customization/service work.",
 "- Contact a genuine opt-in buyer; agree price, acceptance, network and receiving address.",
 "- Count income only after independently verified correct-chain incoming transaction evidence.",
 "- No Gmail, subscriptions, paid compute, private keys, unauthorized mining or spam.",
 "",
 "Executor: NOT_ASSIGNED",
 "Run evidence: NOT_VERIFIED",
 "Buyer acceptance: NONE",
 "Incoming BTC / validated Base-native-USDC TXID: NOT_VERIFIED",
 ""
 ];
 return {schema:"ENIGMA_PRODUCT_BRIEF_V1",id,title:safeTitle,kind,audience:buyer,deliverable,tests,publication_status:"DRAFT_NOT_POSTED",buyer_status:"NOT_VERIFIED",payment_status:"NOT_VERIFIED",markdown:parts.join("\n")};
}
