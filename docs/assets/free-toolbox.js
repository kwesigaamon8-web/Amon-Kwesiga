"use strict";
/* B1/B2 Free Toolbox — original, offline-by-default browser software.
   Pure functions are usable with Node's built-in test runner; no network calls. */
(function(root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  root.B1B2FreeToolbox = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function() {
  const LIMIT = 1024 * 1024;
  function input(s) {
    if (typeof s !== "string") s = String(s == null ? "" : s);
    if (s.length > LIMIT) throw Error("Input is over the 1 MB safety limit.");
    return s;
  }
  function lines(s) { return input(s).replace(/\r\n?/g, "\n").split("\n"); }
  function number(s, name) {
    if (String(s).trim() === "") throw Error(name + " is required.");
    const n = Number(s);
    if (!Number.isFinite(n)) throw Error(name + " must be a finite number.");
    return n;
  }
  function parseCSV(s) {
    s = input(s).replace(/^\uFEFF/, "");
    if (!s.trim()) return [];
    const result = []; let row = [], field = "", quoted = false, atStart = true, closed = false;
    for (let i=0;i<s.length;i++) {
      const ch=s[i];
      if (quoted) {
        if (ch === '"' && s[i+1] === '"') { field += '"'; i++; }
        else if (ch === '"') { quoted=false; closed=true; }
        else field += ch;
      } else if (ch === '"') {
        if (!atStart || closed) throw Error("Malformed CSV quote at position " + i);
        quoted=true; atStart=false;
      } else if (ch === ",") {
        row.push(field); field=""; atStart=true; closed=false;
      } else if (ch === "\r" || ch === "\n") {
        if (ch === "\r" && s[i+1] === "\n") i++;
        row.push(field); result.push(row);
        row=[];field="";atStart=true;closed=false;
      } else {
        if (closed) throw Error("Unexpected text after closing CSV quote.");
        field+=ch; atStart=false;
      }
    }
    if (quoted) throw Error("Unclosed CSV field.");
    if (row.length || field.length || !atStart || closed) {row.push(field);result.push(row);}
    return result;
  }
  function safeCsv(value) {
    const raw=String(value == null ? "" : value);
    // Prevent formula execution when CSV files are opened in spreadsheet apps.
    const guarded=/^[\s]*[=+\-@\t\r]/.test(raw) ? "'" + raw : raw;
    return /[",\r\n]/.test(guarded) ? '"' + guarded.replace(/"/g,'""') + '"' : guarded;
  }
  function csvWrite(rows) { return rows.map(r=>r.map(safeCsv).join(",")).join("\r\n"); }
  function csvToJSON(s) {
    const rows=parseCSV(s); if (!rows.length) return "[]";
    const headings=rows[0];
    if (!headings.length || headings.some(h=>!h.trim())) throw Error("CSV headings cannot be empty.");
    if (new Set(headings).size!==headings.length) throw Error("Duplicate CSV headings are not supported.");
    return JSON.stringify(rows.slice(1).map((r,i)=>{
      if (r.length!==headings.length) throw Error("Row " + (i+2) + " has an inconsistent number of columns.");
      const obj=Object.create(null);
      headings.forEach((h,j)=>Object.defineProperty(obj,h,{value:r[j],enumerable:true,configurable:true,writable:true}));
      return obj;
    }),null,2);
  }
  function jsonToCSV(s) {
    const a=JSON.parse(input(s)); if (!Array.isArray(a)) throw Error("JSON must be an array of flat objects.");
    if (!a.length) return "";
    if (a.some(x=>!x || typeof x!=="object" || Array.isArray(x))) throw Error("Array items must be objects.");
    const keys=Array.from(new Set(a.flatMap(x=>Object.keys(x))));
    if (!keys.length) return "";
    const rows=a.map(x=>keys.map(k=>{
      const v=x[k]; if (v!==null && typeof v==="object") throw Error("Nested JSON is not supported in flat CSV.");
      return v == null ? "" : String(v);
    }));
    return csvWrite([keys,...rows]);
  }
  function jsonFormat(s) { return JSON.stringify(JSON.parse(input(s)),null,2); }
  function jsonMinify(s) { return JSON.stringify(JSON.parse(input(s))); }
  function jsonKeys(s) {
    const x=JSON.parse(input(s)); const seen=[];
    function walk(v, p, depth) {
      if(depth>16) throw Error("JSON nesting exceeds 16 levels.");
      if(v && typeof v==="object") Object.keys(v).forEach(k=>{
        const next=p ? p+"."+k : k;
        seen.push(next); walk(v[k],next,depth+1);
      });
    }
    walk(x,"",0); return seen.join("\n");
  }
  function textStats(s) {
    s=input(s);const words=s.trim().match(/\S+/g)||[];
    return JSON.stringify({characters:[...s].length,words:words.length,lines:s ? lines(s).length : 0,unique_words:new Set(words.map(w=>w.toLowerCase())).size},null,2);
  }
  function slug(s) {
    return input(s).normalize("NFKD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"");
  }
  function titleCase(s) {return input(s).toLowerCase().replace(/\b[a-z]/g,x=>x.toUpperCase());}
  function uniqueLines(s) {const seen=new Set();return lines(s).filter(x=>{if(seen.has(x))return false;seen.add(x);return true;}).join("\n");}
  function sortedLines(s) {return lines(s).slice().sort((a,b)=>a.localeCompare(b,undefined,{numeric:true})).join("\n");}
  function reverseLines(s) {return lines(s).reverse().join("\n");}
  function numberedLines(s) {return lines(s).map((x,i)=>String(i+1).padStart(3," ")+"  "+x).join("\n");}
  function trimLines(s) {return lines(s).map(x=>x.trim()).join("\n");}
  function removeBlank(s) {return lines(s).filter(x=>x.trim()).join("\n");}
  function compareLines(a,b) {
    const left=new Set(lines(a).filter(Boolean)),right=new Set(lines(b).filter(Boolean));
    return JSON.stringify({only_first:[...left].filter(x=>!right.has(x)),only_second:[...right].filter(x=>!left.has(x)),in_both:[...left].filter(x=>right.has(x))},null,2);
  }
  function urlEncode(s) {return encodeURIComponent(input(s));}
  function urlDecode(s) {return decodeURIComponent(input(s));}
  function htmlEscape(s) {return input(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");}
  function base64Encode(s) {
    const b=new TextEncoder().encode(input(s));
    // Chunked binary conversion avoids argument length limits for large Unicode inputs.
    let bin="";for(let i=0;i<b.length;i+=8192) bin+=String.fromCharCode(...b.slice(i,i+8192));
    if(typeof btoa==="function") return btoa(bin);
    return Buffer.from(b).toString("base64");
  }
  function base64Decode(s) {
    s=input(s).replace(/\s/g,"");
    if(!/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(s)) throw Error("Invalid padded Base64.");
    const bytes=typeof atob==="function" ? Uint8Array.from(atob(s),c=>c.charCodeAt(0)) : Uint8Array.from(Buffer.from(s,"base64"));
    return new TextDecoder("utf-8",{fatal:true}).decode(bytes);
  }
  function percentageChange(a,b) {const first=number(a,"Original"),end=number(b,"New"); if(first===0) throw Error("Original must not be zero.");return (((end-first)/Math.abs(first))*100).toFixed(2)+"%";}
  function vatCalculator(a,b) {
    const amount=number(a,"Amount"),rate=number(b||"18","VAT rate");
    if(amount<0 || rate<0 || rate>100) throw Error("Amount must be nonnegative and VAT rate 0–100.");
    return JSON.stringify({net:amount,tax:Number((amount*rate/100).toFixed(2)),gross:Number((amount*(1+rate/100)).toFixed(2)),rate_percent:rate},null,2);
  }
  function timestamp(s) {const n=Date.parse(input(s));if(!Number.isFinite(n))throw Error("Provide an ISO-like date, for example 2026-11-20T00:00:00Z.");return JSON.stringify({iso_utc:new Date(n).toISOString(),unix_seconds:Math.trunc(n/1000)},null,2);}
  function colorContrast(a,b) {
    function luminance(hex) {
      hex=input(hex).trim().replace(/^#/,"");
      if(!/^[0-9a-fA-F]{6}$/.test(hex))throw Error("Use six-digit hex colors, such as #ffffff.");
      const rgb=[0,2,4].map(i=>parseInt(hex.slice(i,i+2),16)/255).map(v=>v<=0.04045?v/12.92:((v+0.055)/1.055)**2.4);
      return rgb[0]*0.2126+rgb[1]*0.7152+rgb[2]*0.0722;
    }
    let aL=luminance(a),bL=luminance(b);
    const ratio=(Math.max(aL,bL)+0.05)/(Math.min(aL,bL)+0.05);
    return JSON.stringify({contrast_ratio:Number(ratio.toFixed(2)),wcag_aa_normal:ratio>=4.5,wcag_aa_large:ratio>=3,wcag_aaa_normal:ratio>=7},null,2);
  }
  function hexToRgb(s) {let x=input(s).trim().replace(/^#/,"");if(!/^[0-9a-fA-F]{6}$/.test(x))throw Error("Provide a six-digit hex color.");return [0,2,4].map(i=>parseInt(x.slice(i,i+2),16)).join(", ");}
  function decimalToHex(s) {const x=input(s).trim();if(!/^-?\d+$/.test(x)||x.length>50)throw Error("Provide an integer up to 50 digits.");return "0x"+BigInt(x).toString(16);}
  function wordFrequency(s) {
    const words=input(s).toLowerCase().match(/[\p{L}\p{N}']+/gu)||[];
    const counts=new Map();words.forEach(x=>counts.set(x,(counts.get(x)||0)+1));
    return [...counts].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0])).slice(0,100).map(([w,n])=>w+": "+n).join("\n");
  }
  function checklist(s) {return lines(s).filter(Boolean).map(x=>"- [ ] "+x.trim()).join("\n");}
  function csvProfile(s) {
    const rows=parseCSV(s);if(!rows.length)return JSON.stringify({rows:0,columns:0},null,2);
    const width=rows[0].length;
    const mismatches=rows.slice(1).map((r,i)=>r.length!==width?i+2:null).filter(Boolean);
    const empties=rows.slice(1).reduce((n,r)=>n+r.filter(x=>!x.trim()).length,0);
    return JSON.stringify({data_rows:Math.max(0,rows.length-1),columns:width,headers:rows[0],empty_data_cells:empties,nonrectangular_row_numbers:mismatches},null,2);
  }
  const catalog=[
    ["csv-to-json","CSV → JSON","Data",csvToJSON,"CSV data with a header row"],
    ["json-to-csv","JSON → CSV","Data",jsonToCSV,"JSON array of flat objects"],
    ["csv-profile","CSV Data Profile","Data",csvProfile,"CSV contents"],
    ["json-format","JSON Formatter","Developer",jsonFormat,"Unformatted JSON"],
    ["json-minify","JSON Minifier","Developer",jsonMinify,"JSON text"],
    ["json-keys","JSON Key Paths","Developer",jsonKeys,"JSON text"],
    ["base64-encode","Base64 Encode (UTF-8)","Developer",base64Encode,"Text"],
    ["base64-decode","Base64 Decode (UTF-8)","Developer",base64Decode,"Padded Base64 text"],
    ["url-encode","URL Component Encode","Developer",urlEncode,"Text"],
    ["url-decode","URL Component Decode","Developer",urlDecode,"URL-encoded text"],
    ["html-escape","HTML Text Escape","Developer",htmlEscape,"Text"],
    ["decimal-to-hex","Integer → Hex","Developer",decimalToHex,"Integer"],
    ["text-stats","Text Statistics","Writing",textStats,"Text to count"],
    ["word-frequency","Word Frequency","Writing",wordFrequency,"Text"],
    ["slug","URL Slug Maker","Writing",slug,"Title or phrase"],
    ["title-case","Title Case","Writing",titleCase,"Text"],
    ["unique-lines","Remove Duplicate Lines","Writing",uniqueLines,"One line per item"],
    ["sort-lines","Sort Lines","Writing",sortedLines,"One line per item"],
    ["reverse-lines","Reverse Lines","Writing",reverseLines,"One line per item"],
    ["number-lines","Number Lines","Writing",numberedLines,"One line per item"],
    ["trim-lines","Trim Each Line","Writing",trimLines,"One line per item"],
    ["remove-blanks","Remove Blank Lines","Writing",removeBlank,"Text with blank lines"],
    ["checklist","Markdown Checklist Maker","Writing",checklist,"One task per line"],
    ["compare-lines","Compare Two Line Lists","Analysis",compareLines,"First line list","Second line list"],
    ["percentage","Percentage Change","Analysis",percentageChange,"Original number","New number"],
    ["vat","VAT Calculator","Analysis",vatCalculator,"Net amount","VAT rate (default 18)"],
    ["timestamp","Date & Unix Timestamp","Analysis",timestamp,"ISO date or date/time"],
    ["contrast","WCAG Color Contrast","Design",colorContrast,"Hex foreground (#000000)","Hex background (#ffffff)"],
    ["hex-rgb","Hex → RGB","Design",hexToRgb,"Hex color (#0088ff)"]
  ].map(([id,name,category,fn,first,second])=>({id,name,category,fn,first,second:second||null}));
  function run(id,a,b) {
    const t=catalog.find(x=>x.id===id);
    if(!t) throw Error("Unknown tool selection.");
    return t.fn(a,b);
  }
  return {catalog,run,parseCSV,csvWrite,safeCsv,csvToJSON,jsonToCSV,jsonFormat,jsonMinify,jsonKeys,textStats,slug,titleCase,uniqueLines,sortedLines,compareLines,base64Encode,base64Decode,percentageChange,vatCalculator,colorContrast,hexToRgb,csvProfile};
});
