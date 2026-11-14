"""A real, reusable read-only bounty eligibility audit; no claims of payment.

Useful B1/B2 paid-task work product. A price label alone is not sponsor
approval, eligibility, escrow, signed contract or on-chain receipt.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import urllib.request
from urllib.error import HTTPError,URLError

RESTRICTED=re.compile(r"(?i)(?:must be (?:a )?(?:core team member|collaborator|administrator)|only (?:collaborators|core team|maintainers|invited)|reserved for an invited contributor|unsolicited (?:claims|pull requests).*(?:closed|rejected)|not open to external contributors)")
SUBMITTED=re.compile(r"(?i)(?:PR submitted|pull requests? (?:submitted|opened|merged)|clean, tested fix ready|existing (?:PR|pull request))")
RISK=re.compile(r"(?i)(?:pay to claim|fee before apply|deposit to start|private key|seed phrase|stake required)")
PRICE=re.compile(r"(?i)(?:\bPrice:\s*\d+(?:\.\d+)?\s*USD|\b(?:bounty|reward|payment|pays?)\b[^\n]{0,50}?\$\s*\d+(?:\.\d+)?|\[\$\d+(?:\.\d+)?\])")
DISPUTE=re.compile(r"(?i)(?:payment not received|bounty not paid|unable to pay|fake bounty|scam bounty)")
ISSUE_URL=re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/issues/(\d+)$")
ZERO_BOUNTY=re.compile(r"(?i)(?:\bzero[- ]bounty\b|\[\$0\]|\b(?:bounty|reward|payment|price|worker price)\s*[:=]?\s*\$\s*0(?:\b|\D)|\b(?:no payout|unpaid|no monetary reward)\b)")
FILLED_OR_DELIVERED=re.compile(r"(?i)(?:\bstatus\s*:\s*(?:delivered|completed|paid|awarded)\b|\bslots?\s*:\s*\d+\s*\(filled\)|\bslots?\s*:\s*0\b|\bno slots available\b)")

def evaluate(issue,comments,repo=None):
    repo=repo or {}
    title=str(issue.get("title") or "")
    body=str(issue.get("body") or "")[:30000]
    labels=[x.get("name","") if isinstance(x,dict) else str(x) for x in issue.get("labels") or []]
    issue_text="\n".join((title,body,*labels))
    bot_comments="\n".join(str(c.get("body") or "")[:8000] for c in comments if str((c.get("user") or {}).get("login") or "").lower().endswith("[bot]"))
    all_comments="\n".join(str(c.get("body") or "")[:8000] for c in comments)
    flags=[]
    if issue.get("state")!="open" or issue.get("pull_request") or repo.get("archived") is True:
        flags.append("NOT_OPEN_OR_ARCHIVED")
    if RESTRICTED.search(issue_text) or RESTRICTED.search(bot_comments):
        flags.append("EXPLICIT_EXTERNAL_CONTRIBUTOR_RESTRICTION")
    if ZERO_BOUNTY.search(issue_text) or any(str(x).lower() in ("zero-bounty","no-bounty","unpaid","no-payment") for x in labels):
        flags.append("ZERO_PAYMENT_EXPLICIT")
    if FILLED_OR_DELIVERED.search(issue_text) or any(str(x).lower() in ("delivered","filled","already-awarded","paid") for x in labels):
        flags.append("ALL_SLOTS_FILLED_OR_DELIVERED")
    if RISK.search(issue_text):
        flags.append("ADVANCE_FEE_OR_SECRET_RISK")
    if DISPUTE.search(issue_text) or DISPUTE.search(all_comments):
        flags.append("PAYMENT_DISPUTE_REVIEW_REQUIRED")
    if SUBMITTED.search(all_comments):
        flags.append("ALREADY_SUBMITTED_FIX_OR_PRS_IN_COMMENTS")
    if not PRICE.search(issue_text):
        flags.append("NO_EXPLICIT_REWARD_IN_SOURCE")
    if int(issue.get("comments") or 0)>len(comments):
        flags.append("SOME_COMMENTS_UNREAD")
    critical=any(x in flags for x in ("NOT_OPEN_OR_ARCHIVED","EXPLICIT_EXTERNAL_CONTRIBUTOR_RESTRICTION","ADVANCE_FEE_OR_SECRET_RISK","ZERO_PAYMENT_EXPLICIT","ALL_SLOTS_FILLED_OR_DELIVERED"))
    return {
      "schema":"B_COMMERCIAL_ELIGIBILITY_V1",
      "source_url":issue.get("html_url"),"issue_title":title,
      "eligibility":"BLOCKED_DO_NOT_CLAIM" if critical else "UNVERIFIED_CONFIRM_WITH_SPONSOR",
      "critical_blocker":critical,"flags":flags,"comments_inspected":len(comments),
      "reward_funded_verified":False,"external_worker_eligibility_verified":False,
      "accepted_paid_job_verified":False,"incoming_crypto_verified":False,
      "next_action":"Exclude from active paid queue" if critical else "Verify sponsor, actual funding, eligibility, delivery criteria and settlement before accepting work"
    }

def fetch_api(url):
    m=ISSUE_URL.fullmatch(url)
    if not m:raise ValueError("Source must be a full original GitHub issue URL")
    owner,repo,num=m.groups()
    base=f"https://api.github.com/repos/{owner}/{repo}"
    def get(u):
        headers={"User-Agent":"B1B2ReadOnlyEligibility/1.0","Accept":"application/vnd.github+json"}
        if os.environ.get("GH_TOKEN"):
            headers["Authorization"]="Bearer "+os.environ["GH_TOKEN"]
        with urllib.request.urlopen(urllib.request.Request(u,headers=headers),timeout=10) as r:
            return json.loads(r.read(900000))
    issue=get(f"{base}/issues/{num}")
    comments=get(f"{base}/issues/{num}/comments?per_page=100")
    metadata=get(base)
    if issue.get("html_url")!=url or not isinstance(comments,list):
        raise ValueError("Original issue URL or comments failed verification")
    return evaluate(issue,comments,metadata)

def self_test():
    i={"state":"open","title":"Fix bug $75 bounty","body":"Maintainer pays $75 after review","labels":[{"name":"Price: 75 USD"}],"comments":1}
    bot=[{"user":{"login":"ubiquity-os[bot]"},"body":"You must be a core team member, or an administrator to start this task"}]
    x=evaluate(i,bot)
    assert x["critical_blocker"] and "EXPLICIT_EXTERNAL_CONTRIBUTOR_RESTRICTION" in x["flags"]
    assert x["incoming_crypto_verified"] is False and x["accepted_paid_job_verified"] is False
    reserved={**i,"body":"Reserved for an invited contributor. Unsolicited pull requests will be closed."}
    assert evaluate(reserved,[])["critical_blocker"]
    ordinary=evaluate(i,[{"user":{"login":"bob"},"body":"What is the payment process?"}])
    assert ordinary["eligibility"]=="UNVERIFIED_CONFIRM_WITH_SPONSOR"
    assert ordinary["reward_funded_verified"] is False
    closed={**i,"state":"closed","title":"General question","body":"Unpaid help","labels":[]}
    assert evaluate(closed,[])["critical_blocker"]
    fake={**i,"body":"Pay to claim $75 reward"}
    assert evaluate(fake,[])["critical_blocker"]
    submitted=evaluate(i,[{"user":{"login":"dev"},"body":"PR submitted #138"}])
    assert "ALREADY_SUBMITTED_FIX_OR_PRS_IN_COMMENTS" in submitted["flags"]
    zero={**i,"body":"This is a zero-bounty task: $0. Real reward requires /reward funding.","labels":[{"name":"bounty"},{"name":"zero-bounty"}]}
    z=evaluate(zero,[])
    assert z["critical_blocker"] and "ZERO_PAYMENT_EXPLICIT" in z["flags"]
    filled={**i,"body":"Worker price: $10\\nSlots: 1 (filled)\\nStatus: delivered","labels":[{"name":"bounty"},{"name":"funded"},{"name":"delivered"}]}
    z=evaluate(filled,[])
    assert z["critical_blocker"] and "ALL_SLOTS_FILLED_OR_DELIVERED" in z["flags"]
    price_only={**i,"title":"[$250] New paid issue","body":"Code task with no buyer acceptance evidence","comments":0}
    z=evaluate(price_only,[])
    assert not z["reward_funded_verified"] and not z["accepted_paid_job_verified"]
    print("PAID_BOUNTY_ELIGIBILITY_TEST_PASS: nine independent checks including zero-payout, filled slots, prior submitted PR and bot permission failures")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("issue_url",nargs="?")
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--file")
    a=p.parse_args()
    if a.self_test:self_test();return
    try:
        if a.file:
            with open(a.file,encoding="utf-8") as f:r=json.load(f)
            result=evaluate(r["issue"],r["comments"],r.get("repo"))
        elif a.issue_url:result=fetch_api(a.issue_url)
        else:p.error("provide issue_url or --file")
        print(json.dumps(result,indent=2))
    except (HTTPError,URLError,ValueError,KeyError,TimeoutError) as e:
        print(json.dumps({"eligibility":"SOURCE_UNAVAILABLE_CANNOT_CLAIM","error":type(e).__name__}))
if __name__=="__main__":main()
