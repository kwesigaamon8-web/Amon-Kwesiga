/** Private key-authenticated relay to the ALREADY authorized specialist Flask backend.
 *  It cannot mint new AI keys, connect strangers' accounts, mine, or accept money.
 *  Caller-supplied domains are ignored; the owner configures exactly one HTTPS
 *  BOT_BACKEND_ORIGIN in the deployed edge environment.
 */
function failure(error,status) {
 return new Response(JSON.stringify({error,model_invocation_completed:false}),{
  status,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store",
  "x-content-type-options":"nosniff"}});
}
export function validatedOrigin(env) {
 if(typeof env?.BOT_BACKEND_ORIGIN!=="string") return null;
 try {
  const u=new URL(env.BOT_BACKEND_ORIGIN);
  if(u.protocol!=="https:" || u.username || u.password || u.search ||
    u.hash || u.pathname!=="/" || u.port && u.port!=="443") return null;
  if(["localhost","127.0.0.1","0.0.0.0","[::1]"].includes(u.hostname) ||
     u.hostname.endsWith(".local") || u.hostname.endsWith(".internal") ||
     !u.hostname.includes(".")) return null;
  return u.origin;
 } catch {return null}
}
export async function relayChat(req,env,resolveRole,doFetch=fetch) {
 if(req.method!=="POST")return failure("POST required",405);
 const origin=validatedOrigin(env);
 if(!origin) return failure("Paid chat is not deployed: configure a verified HTTPS model backend",503);
 const bearer=req.headers.get("authorization")||"";
 if(!/^Bearer [A-Za-z0-9._~-]{24,250}$/.test(bearer))
  return failure("Provisioned customer bearer key required",401);
 if(req.headers.get("content-type")?.split(";")[0].toLowerCase()!=="application/json")
  return failure("Use application/json",415);
 const expectedMax=12500;
 const size=Number(req.headers.get("content-length")||"0");
 if(size>expectedMax)return failure("Request too large",413);
 let total=0,bytes=[];
 try{
  if(req.body){
   const reader=req.body.getReader();
   while(true){
    const {done,value}=await reader.read();
    if(done)break;
    total+=value.byteLength;
    if(total>expectedMax){await reader.cancel();return failure("Request too large",413);}
    bytes.push(value);
   }
  }
 }catch {return failure("Request body unreadable",400)}
 const buffer=new Uint8Array(total);
 let pos=0;for(const part of bytes){buffer.set(part,pos);pos+=part.byteLength}
 let data;
 try{data=JSON.parse(new TextDecoder("utf-8",{fatal:true}).decode(buffer))}catch{return failure("Invalid JSON",400)}
 if(!data||typeof data!=="object"||Array.isArray(data)||
    !["B1","B2"].includes(data.company)||!resolveRole(data.company,data.role))
  return failure("Unknown customer assistant company or role",404);
 if(!Array.isArray(data.messages)||data.messages.length<1||data.messages.length>8)
  return failure("Requires 1–8 customer chat messages",422);
 for(const x of data.messages) {
  if(!x || !["user","assistant"].includes(x.role) ||
     typeof x.content!=="string"||x.content.length<1||x.content.length>1400)
    return failure("Message role/length invalid",422);
 }
 if(data.messages.at(-1).role!=="user")return failure("Last turn must be a user",422);
 const fleet=data.company==="B1"?"transferexperiment":"BountyScoutAI";
 const payload=JSON.stringify({fleet,role_id:data.role,messages:data.messages});
 let upstream;
 try{
  upstream=await doFetch(origin+"/api/bots/chat",{
   method:"POST",
   headers:{"authorization":bearer,"content-type":"application/json","accept":"application/json"},
   body:payload,
   redirect:"error"
  });
 }catch{return failure("Configured bot service unavailable",502)}
 // Never reflect arbitrary upstream HTML/headers, credentials or provider error internals.
 let result;
 try {
  const text=await upstream.text();
  if(text.length>10000) return failure("Upstream response exceeded safe size",502);
  result=JSON.parse(text);
 }catch {return failure("Unusable bot service response",502)}
 if(!upstream.ok)return failure(
   typeof result.error==="string"?result.error.slice(0,160):"Chat service refused request",
   [400,401,403,413,415,422,429,503].includes(upstream.status)?upstream.status:502
 );
 if(result.model_invocation_completed!==true||typeof result.answer!=="string")
  return failure("Model completion was not verified",502);
 return new Response(JSON.stringify({
   fleet,role_id:data.role,answer:result.answer.slice(0,7000),
   assistant:typeof result.assistant==="string"?result.assistant.slice(0,100):"B Agent",
   model_invocation_completed:true,
   externally_earned_payment_verified:false,
   automatic_bitcoin_mining_performed:false,
   actual_model_response_from_configured_backend:true
 }),{status:200,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store",
   "x-content-type-options":"nosniff"}});
}
