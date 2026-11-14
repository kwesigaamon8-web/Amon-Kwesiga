"""Safely read bounded public SOURCE EVIDENCE for a B worker's second task.

No clone, install, execute, scrape of private APIs, user auth, archive download,
license grant, source code copying, wallet connection or third-party account.
Fixed allowlisted URLs only. Cached once per director across sequential workers.
"""
from __future__ import annotations
import base64
import hashlib
import html
import json
import re
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from secondary_software_study import ALL_REFERENCES

CACHE=Path("source-learning")
CACHE.mkdir(exist_ok=True)
PUBLIC={x[1] for x in ALL_REFERENCES}
MAX_BYTES=24576
HEAD={"User-Agent":"BOpenSourceReadOnlyLearning/1.0",
      "Accept":"application/vnd.github+json,application/json,text/html;q=0.6"}
class TextHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tokens=[]
        self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ("script","style"):self.skip+=1
    def handle_endtag(self,tag):
        if tag in ("script","style") and self.skip:self.skip-=1
    def handle_data(self,data):
        if not self.skip and data.strip():
            self.tokens.append(data.strip())
def readable(t):
    if t.lstrip().startswith("<"):
        p=TextHTML();p.feed(t);t=" ".join(p.tokens)
    return " ".join(html.unescape(str(t)).split())[:3400]
def api_for(url):
    if url.startswith("https://github.com/"):
        part=url[len("https://github.com/"):]
        return "https://api.github.com/repos/"+part+"/readme"
    if url=="https://gitlab.com/gitlab-org/gitlab":
        return "https://gitlab.com/api/v4/projects/gitlab-org%2Fgitlab"
    if url=="https://codeberg.org/forgejo/forgejo":
        return "https://codeberg.org/api/v1/repos/forgejo/forgejo"
    if url=="https://pypi.org/project/requests/":
        return "https://pypi.org/pypi/requests/json"
    if url=="https://www.npmjs.com/package/bitcoinjs-lib":
        return "https://registry.npmjs.org/bitcoinjs-lib/latest"
    return url
def load(url):
    if url not in PUBLIC:raise ValueError("Public source is not allowlisted")
    key=hashlib.sha256(url.encode()).hexdigest()[:28]
    fp=CACHE/(key+".json")
    if fp.exists():
        try:
            d=json.loads(fp.read_text())
            if d.get("original_url")==url and d.get("source_check_status") in ("PUBLIC_SOURCE_READ","PUBLIC_SOURCE_UNAVAILABLE"):
                return d
        except (ValueError,OSError):pass
    evidence={"original_url":url,"api_url":api_for(url),"source_check_status":"PUBLIC_SOURCE_UNAVAILABLE",
        "read_only_excerpt":"","listed_license_not_verified_for_specific_file":True,
        "actual_source_code_copied":False,"actual_software_run":False,
        "error":"not_attempted"}
    try:
        req=urllib.request.Request(evidence["api_url"],headers=HEAD)
        with urllib.request.urlopen(req,timeout=6) as r:
            data=r.read(MAX_BYTES)
            content_type=str(r.headers.get("Content-Type",""))
        raw=data.decode("utf-8","replace")
        if "json" in content_type or raw.lstrip().startswith("{"):
            d=json.loads(raw)
            if not isinstance(d,dict):raise ValueError("Unexpected JSON")
            if d.get("encoding")=="base64" and d.get("content"):
                raw=base64.b64decode(d["content"]).decode("utf-8","replace")
            elif url=="https://pypi.org/project/requests/":
                raw="PyPI metadata: "+str(d.get("info",{}).get("summary",""))+". "+str(d.get("info",{}).get("description",""))[:2000]
            elif url=="https://www.npmjs.com/package/bitcoinjs-lib":
                raw="npm package metadata: "+str(d.get("description",""))+". "+str(d.get("readme",""))[:2000]
            else:
                raw=("Read-only official project metadata: "+str(d.get("description",""))+"; "+
                  "project "+str(d.get("name",""))+"; homepage "+str(d.get("web_url") or d.get("html_url") or ""))
        excerpt=readable(raw)
        if len(excerpt)<20:raise ValueError("Insufficient public source excerpt")
        evidence.update({"source_check_status":"PUBLIC_SOURCE_READ",
                         "read_only_excerpt":excerpt,"error":None})
    except (ValueError,TimeoutError,urllib.error.URLError,OSError) as exc:
        evidence["error"]=type(exc).__name__+":"+str(exc)[:180]
    fp.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n")
    return evidence

def selftest():
    assert len(PUBLIC)>=12
    assert len({x.split("/")[2] for x in PUBLIC})>=7
    try:
        load("http://localhost:8080/private")
        raise AssertionError("Untrusted source unexpectedly allowed")
    except ValueError:pass
    assert api_for("https://github.com/bitcoin/bitcoin")=="https://api.github.com/repos/bitcoin/bitcoin/readme"
    print("PUBLIC_CODE_READER_WHITELIST_TEST_PASS",json.dumps({
      "allowlisted_public_sources":len(PUBLIC),"domains":len({x.split("/")[2] for x in PUBLIC}),
      "untrusted_source_rejected":True,"network_access_in_test":False}))
if __name__=="__main__":
    selftest()
