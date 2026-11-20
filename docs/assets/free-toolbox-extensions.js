"use strict";
(function(root){
const api=root.B1B2FreeToolbox;if(!api)throw Error("Requires base toolbox");
const str=x=>String(x==null?"":x),limited=x=>{const s=str(x);if(s.length>1048576)throw Error("Input limit 1MB");return s;};
const obj=s=>JSON.parse(limited(s));const pretty=x=>JSON.stringify(x,null,2);
const numeric=(x,name)=>{if(!str(x).trim()||!Number.isFinite(Number(x)))throw Error(name+" must be a number");return Number(x);};
function parseUrl(s){let u=new URL(limited(s));if(!["https:","http:"].includes(u.protocol))throw Error("Only HTTP(S) URLs allowed");return pretty({protocol:u.protocol,host:u.host,path:u.pathname,fragment:u.hash,params:Object.fromEntries(u.searchParams),contains_credentials:!!(u.username||u.password)});}
function queryToJSON(s){let p=new URLSearchParams(limited(s).replace(/^\?/,"")),o=Object.create(null);for(const [k,v] of p){if(Object.hasOwn(o,k)){o[k]=Array.isArray(o[k])?[...o[k],v]:[o[k],v];}else o[k]=v;}return pretty(o);}
function jsonToQuery(s){const v=obj(s);if(!v||Array.isArray(v)||typeof v!=="object")throw Error("Expected JSON object");let p=new URLSearchParams();for(const [k,val] of Object.entries(v)){for(const x of (Array.isArray(val)?val:[val])){if(x===null)continue;if(typeof x==="object")throw Error("Only flat values allowed");p.append(k,String(x));}}return p.toString();}
function rot13(s){return limited(s).replace(/[A-Za-z]/g,c=>String.fromCharCode(c.charCodeAt(0)+(c.toLowerCase()<"n"?13:-13)));}
function hexEncode(s){return Array.from(new TextEncoder().encode(limited(s)),v=>v.toString(16).padStart(2,"0")).join("");}
function hexDecode(s){const a=limited(s).replace(/\s/g,"");if(a.length%2||!/^[0-9a-fA-F]*$/.test(a))throw Error("Invalid hex");let bytes=Uint8Array.from(a.match(/.{2}/g)||[],h=>parseInt(h,16));return new TextDecoder("utf-8",{fatal:true}).decode(bytes);}
function binaryDecimal(s){let a=limited(s).trim();if(!/^[01]{1,512}$/.test(a))throw Error("1-512 binary digits expected");return BigInt("0b"+a).toString();}
function decimalBinary(s){let a=limited(s).trim();if(!/^-?[0-9]{1,80}$/.test(a))throw Error("Integer up to 80 digits expected");return BigInt(a).toString(2);}
function byteCount(s){let a=limited(s);return pretty({codepoints:Array.from(a).length,utf8_bytes:new TextEncoder().encode(a).length});}
function jwtInspect(s){const parts=limited(s).trim().split(".");if(parts.length!==3)throw Error("Three-part JWT required");function part(p){const b=p.replace(/-/g,"+").replace(/_/g,"/");if(!/^[a-zA-Z0-9+/]*$/.test(b)||b.length%4===1)throw Error("Invalid Base64URL");const b64=b+"=".repeat((4-b.length%4)%4);let raw=typeof atob==="function"?atob(b64):Buffer.from(b64,"base64").toString("binary");return JSON.parse(new TextDecoder("utf-8",{fatal:true}).decode(Uint8Array.from(raw,c=>c.charCodeAt(0))));}return pretty({warning:"UNVERIFIED: no signature/issuer/expiry verification; never paste real secrets",header:part(parts[0]),payload:part(parts[1])});}
function regexEscape(s){return limited(s).replace(/[$.*+?^{}()|[\]\\]/g,"\\$&");}
function jsonSort(s){function go(v,d){if(d>24)throw Error("JSON too deeply nested");if(Array.isArray(v))return v.map(x=>go(x,d+1));if(v&&typeof v==="object"){const x=Object.create(null);for(const k of Object.keys(v).sort())Object.defineProperty(x,k,{value:go(v[k],d+1),enumerable:true});return x;}return v;}return pretty(go(obj(s),0));}
function jsonDiff(a,b){let x=obj(a),y=obj(b),change=[];function walk(l,r,path,d){if(change.length>=100)return;if(d>20){change.push({path,change:"depth_limit"});return;}if(Object.is(l,r))return;if(l&&r&&typeof l==="object"&&typeof r==="object"&&Array.isArray(l)===Array.isArray(r)){for(const k of [...new Set([...Object.keys(l),...Object.keys(r)])].sort()){const p=path+"/"+k.replace(/~/g,"~0").replace(/\//g,"~1");if(!Object.hasOwn(l,k))change.push({path:p,change:"added",value:r[k]});else if(!Object.hasOwn(r,k))change.push({path:p,change:"removed",value:l[k]});else walk(l[k],r[k],p,d+1);if(change.length>=100)break;}return;}change.push({path:path||"/",change:"changed",before:l,after:r});}walk(x,y,"",0);return pretty({differences:change,truncated:change.length>=100});}
function jsonPointer(a,b){let v=obj(a),p=limited(b);if(!p)return pretty(v);if(!p.startsWith("/"))throw Error("JSON pointer must start /");for(const item of p.slice(1).split("/")){let k=item.replace(/~1/g,"/").replace(/~0/g,"~");if(v===null||typeof v!=="object"||!Object.hasOwn(v,k))throw Error("Not found: "+p);v=v[k];}return pretty(v);}
function jsonTS(s){let o=obj(s);if(!o||typeof o!=="object"||Array.isArray(o))throw Error("Sample must be a JSON object");function typ(v,d){if(d>8)return "unknown";if(v===null)return "null";if(Array.isArray(v))return "("+[...new Set(v.slice(0,20).map(x=>typ(x,d+1)))].join(" | ")+")[]";if(typeof v==="object")return "{ "+Object.entries(v).slice(0,50).map(([k,x])=>JSON.stringify(k)+": "+typ(x,d+1)+";").join(" ")+" }";return typeof v==="number"?"number":typeof v==="boolean"?"boolean":"string";}return "export interface DataRecord {\n"+Object.entries(o).slice(0,80).map(([k,v])=>"  "+JSON.stringify(k)+": "+typ(v,0)+";").join("\n")+"\n}";}
function linesJSON(s){return pretty(limited(s).replace(/\r/g,"").split("\n").filter(Boolean));}
function jsonLines(s){let a=obj(s);if(!Array.isArray(a)||a.some(x=>x!==null&&typeof x==="object"))throw Error("Flat JSON array expected");return a.map(x=>x==null?"":String(x)).join("\n");}
function csvUnique(s){let rows=api.parseCSV(s),seen=new Set();return api.csvWrite(rows.filter((r,i)=>{if(i===0)return true;let key=JSON.stringify(r);if(seen.has(key))return false;seen.add(key);return true;}));}
function csvColumn(a,b){let rows=api.parseCSV(a),head=rows[0]||[],idx=head.indexOf(limited(b).trim());if(idx<0)throw Error("Column not found");if(rows.some(r=>r.length!==head.length))throw Error("Inconsistent rows");return api.csvWrite(rows.map(r=>[r[idx]]));}
function csvSort(a,b){let rows=api.parseCSV(a),head=rows[0]||[],idx=head.indexOf(limited(b).trim());if(idx<0)throw Error("Column not found");if(rows.some(r=>r.length!==head.length))throw Error("Inconsistent rows");return api.csvWrite([head,...rows.slice(1).sort((x,y)=>x[idx].localeCompare(y[idx],undefined,{numeric:true}))]);}
function daysBetween(a,b){function date(x){const t=limited(x);if(!/^\d{4}-\d{2}-\d{2}$/.test(t))throw Error("Use YYYY-MM-DD");let d=new Date(t+"T00:00:00Z");if(!Number.isFinite(d.getTime())||d.toISOString().slice(0,10)!==t)throw Error("Invalid calendar date");return d.getTime();}return Math.round((date(b)-date(a))/86400000)+" days";}
function discount(a,b){let p=numeric(a,"Price"),d=numeric(b,"Discount");if(p<0||d<0||d>100)throw Error("Invalid price or discount");return pretty({original:p,discount_percent:d,savings:Number((p*d/100).toFixed(2)),after_discount:Number((p*(1-d/100)).toFixed(2))});}
function vatIncluded(a,b){let gross=numeric(a,"Gross"),rate=numeric(b,"Rate");if(gross<0||rate<0||rate>100)throw Error("Invalid gross or rate");let net=gross/(1+rate/100);return pretty({gross,rate_percent:rate,net:Number(net.toFixed(2)),included_vat:Number((gross-net).toFixed(2))});}
function rgbHex(s){let m=limited(s).trim().match(/^(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})$/);if(!m||m.slice(1).some(x=>Number(x)>255))throw Error("Use R,G,B 0-255");return "#"+m.slice(1).map(x=>Number(x).toString(16).padStart(2,"0")).join("");}
function uuid(){if(!root.crypto||!root.crypto.randomUUID)throw Error("Requires secure browser context");return root.crypto.randomUUID();}
function password(a){let n=a?Number(limited(a)):20;if(!Number.isInteger(n)||n<8||n>128)throw Error("Length must be 8-128");if(!root.crypto||!root.crypto.getRandomValues)throw Error("Secure browser required");const chars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%_-",result=[];while(result.length<n){const bytes=new Uint8Array(n);root.crypto.getRandomValues(bytes);for(const b of bytes){if(b<Math.floor(256/chars.length)*chars.length)result.push(chars[b%chars.length]);if(result.length>=n)break;}}return result.join("");}
const entries=[
["url-parse","HTTP URL Parser","Developer",parseUrl,"HTTP or HTTPS URL"],["query-to-json","Query → JSON","Developer",queryToJSON,"URL query"],
["json-to-query","JSON → URL Query","Developer",jsonToQuery,"Flat JSON object"],["rot13","ROT13 Text","Writing",rot13,"Text"],
["hex-encode","UTF-8 → Hex","Developer",hexEncode,"Text"],["hex-decode","Hex → UTF-8","Developer",hexDecode,"Hex bytes"],
["binary-decimal","Binary → Decimal","Analysis",binaryDecimal,"Binary digits"],["decimal-binary","Decimal → Binary","Analysis",decimalBinary,"Integer"],
["utf8-byte-count","UTF-8 Byte Counter","Writing",byteCount,"Text"],["jwt-inspect","JWT Inspector (Unverified)","Developer",jwtInspect,"JWT text"],
["regex-escape","Escape Regex Literal","Developer",regexEscape,"Text"],["json-sort","Sort JSON Object Keys","Developer",jsonSort,"JSON"],
["json-diff","Diff Two JSON Values","Developer",jsonDiff,"First JSON","Second JSON"],["json-pointer","JSON Pointer Lookup","Developer",jsonPointer,"JSON","Pointer e.g. /name"],
["json-to-typescript","JSON → TypeScript","Developer",jsonTS,"Sample object JSON"],["lines-to-json","Lines → JSON List","Data",linesJSON,"Lines"],
["json-to-lines","JSON List → Lines","Data",jsonLines,"Flat JSON array"],["csv-unique","CSV Remove Duplicate Rows","Data",csvUnique,"CSV"],
["csv-column","CSV Extract Column","Data",csvColumn,"CSV","Header name"],["csv-sort","CSV Sort By Column","Data",csvSort,"CSV","Header name"],
["days-between","Days Between Dates","Analysis",daysBetween,"Start YYYY-MM-DD","End YYYY-MM-DD"],
["discount","Discount Calculator","Analysis",discount,"Original price","Percent"],
["vat-included","VAT Included Calculator","Analysis",vatIncluded,"Gross amount","Percent"],
["rgb-to-hex","RGB → Hex","Design",rgbHex,"R,G,B"],["uuid-v4","Secure UUID v4","Developer",uuid,"Ignored"],
["password-gen","Secure Password Generator","Developer",password,"Length 8-128"]
];
for(const [id,name,category,fn,first,second] of entries){if(api.catalog.some(x=>x.id===id))throw Error("Duplicate id");api.catalog.push({id,name,category,fn,first,second:second||null});}
root.B1B2FreeToolboxExtensions=Object.freeze({count:entries.length});
})(typeof globalThis!=="undefined"?globalThis:this);
