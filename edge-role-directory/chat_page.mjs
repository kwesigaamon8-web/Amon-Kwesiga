/** Static browser client for an explicitly provisioned customer. No key storage. */
export const CHAT_HTML=String.raw`<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>B Agent Assistants — Chat</title>
<style>body{font:16px system-ui,Arial,sans-serif;background:#f5f7fa;color:#182737;max-width:790px;margin:35px auto;padding:0 16px}
main{background:white;padding:24px;border:1px solid #dbe4ef;border-radius:14px}
input,select,textarea,button{font:inherit;border-radius:8px;border:1px solid #bbcadd;padding:11px;max-width:100%}
input,textarea{width:98%}textarea{min-height:120px}label{display:block;margin:13px 0 6px;font-weight:600}
button{background:#19559d;color:white;font-weight:700;cursor:pointer}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#eef3fa;padding:14px;border-radius:10px;min-height:80px}
p{line-height:1.5}.small{color:#526277;font-size:14px}a{color:#19559d}</style></head><body><main>
<h1>B Agent Assistants</h1>
<p class="small">Private on-demand specialized assistant pilot. Chat works only after the owner connects a legitimate model backend, provisions access and approves its usage budget. Not an official ChatGPT or OpenAI service.</p>
<label for="company">Company</label><select id="company"><option>B1</option><option>B2</option></select>
<label for="role">Valid role ID</label><input id="role" value="D01-M01-W01" maxlength="95" autocomplete="off">
<label for="key">Customer access key</label><input id="key" type="password" autocomplete="off" placeholder="Privately issued access key">
<label for="q">Your question</label><textarea id="q" maxlength="1400" placeholder="Help me draft a test plan…"></textarea>
<button id="send">Ask the specialist</button><p id="status" class="small">No money is transferred by this page.</p>
<pre id="answer" aria-live="polite">No chat response yet.</pre>
<p class="small">Browser does not store the key. This demo sends only your messages and access key to the configured protected backend. No mining, external research or financial transactions occur. <a href="/">Role directory</a></p>
</main><script>
let history=[],lastContext="";
document.getElementById("send").addEventListener("click",async()=>{
 const company=document.getElementById("company").value,role=document.getElementById("role").value.trim(),
 key=document.getElementById("key").value.trim(),content=document.getElementById("q").value.trim();
 const status=document.getElementById("status"),answer=document.getElementById("answer");
 if(!content||!key){status.textContent="Enter a message and provisioned access key.";return;}
 const context=company+"/"+role;
 if(context!==lastContext){history=[];lastContext=context;}
 const messages=[...history,{role:"user",content}].slice(-8);
 status.textContent="Checking access and bot backend…";
 try{
 const r=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json","Authorization":"Bearer "+key},body:JSON.stringify({company,role,messages})});
 const j=await r.json();
 if(!r.ok){status.textContent="Chat unavailable ("+r.status+")";answer.textContent=j.error||"No response";return;}
 history.push({role:"user",content},{role:"assistant",content:j.answer});
 history=history.slice(-8);
 answer.textContent=j.answer;
 status.textContent="Model answer received. This does not perform transactions.";
 }catch{status.textContent="Could not connect to configured bot server";answer.textContent="No model response recorded";}
});
</script></body></html>`;
