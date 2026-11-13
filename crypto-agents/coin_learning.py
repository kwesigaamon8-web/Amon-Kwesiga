"""Official-coin learning research for a single genuinely executed role.

Provides a bounded, read-only HTTPS check. No account, mining or payment claim.
"""
import hashlib
import json
from datetime import datetime,timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,urlopen

CATALOG=json.loads(Path("crypto-agents/global_coin_learning.json").read_text(encoding="utf-8"))

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__();self.parts=[];self.skip_depth=0
    def handle_starttag(self,tag,attrs):
        if tag in ("style","script","svg","noscript"):self.skip_depth+=1
    def handle_endtag(self,tag):
        if tag in ("style","script","svg","noscript") and self.skip_depth:self.skip_depth-=1
    def handle_data(self,s):
        if not self.skip_depth and s.strip():self.parts.append(" ".join(s.split())[:120])

def study(agent_id):
    now=datetime.now(timezone.utc)
    h=int(hashlib.sha256((agent_id+now.date().isoformat()).encode()).hexdigest()[:12],16)
    coin=CATALOG["coins"][h%len(CATALOG["coins"])]
    earn=CATALOG["earning_channels"][(h//len(CATALOG["coins"]))%len(CATALOG["earning_channels"])]
    result={
      "order":"ORD-034",
      "role_id":agent_id,
      "coin":coin["name"],"network":coin["network"],
      "official_source_url":coin["url"],"question":coin["question"],
      "earning_channel":earn["name"],"earning_source_url":earn["url"],
      "earning_question":earn["question"],"checked_utc":now.isoformat(),
      "source_status":"not_checked","source_http_status":None,
      "source_excerpt":"","error":None,"verified_receipts":[]
    }
    url=urlsplit(coin["url"])
    if url.scheme!="https" or not url.hostname:
        result["source_status"]="invalid_url";return result
    try:
        req=Request(coin["url"],headers={"User-Agent":"AmonWorldwideCoinEducation/1.0",
             "Accept":"text/html,text/plain;q=0.9"},method="GET")
        with urlopen(req,timeout=6) as response:
            if urlsplit(response.geturl()).scheme!="https":
                raise ValueError("Redirected to non-HTTPS")
            result["source_http_status"]=response.status
            ctype=response.headers.get("Content-Type","").lower()
            if "text" not in ctype and "html" not in ctype:
                raise ValueError("Unsupported non-text content")
            data=response.read(22000).decode("utf-8",errors="replace")
        p=VisibleText();p.feed(data)
        result["source_excerpt"]=" ".join(p.parts)[:900]
        result["source_status"]="source_checked" if result["source_excerpt"] else "empty_page"
    except Exception as exc:
        result["source_status"]="source_unavailable"
        result["error"]=f"{type(exc).__name__}: {str(exc)[:170]}"
    return result
