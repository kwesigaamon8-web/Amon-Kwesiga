"""Grounded paid-task scout for both AI worker fleets.
Reads Jobbi's public index at most hourly. Confirms original GitHub issue is
currently open; all payment claims remain unverified until separately checked.
Never auto-claims tasks, pays bonds, posts externally, or signs any wallet.
"""
import datetime as dt
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

OUT=Path("paid-opportunity-reports")
OUT.mkdir(exist_ok=True)
HEADERS={"User-Agent":"OwnerPaidWorkScout/1.0",
         "Accept":"text/plain, application/json"}
REPO=os.environ.get("GITHUB_REPOSITORY", "")
TOKEN=os.environ.get("GH_TOKEN", "")
ISSUE="https://api.github.com/repos/kwesigaamon8-web/Amon-Kwesiga/issues/9/comments"
SKILL=re.compile(r"\b(document|csv|excel|spreadsheet|report|test|quality|python|finance|reconcil|data|api|fix|vitest|svelte|database|bookkeep|research|audit|sql)\b",re.I)
EXCLUDE=re.compile(r"\b(USA ONLY|US-only|in.person|connect your wallet|seed phrase|private key|create.*account.*pay|verification fee|bond|stake|fund a.*bounty|pay first)\b",re.I)
LINK=re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/issues/(\d+)$")
def get(url,headers=None):
    req=urllib.request.Request(url,headers=headers or HEADERS)
    with urllib.request.urlopen(req,timeout=18) as resp:
        return resp.read(1_800_000).decode("utf-8","replace")

try:
    feed=get("https://jobbi.org/gigs.txt?lane=agent&limit=100")
except Exception as exc:
    report={"status":"feed_unavailable","error":type(exc).__name__+": "+str(exc)[:160],
            "verified_paid_work":[]}
    (OUT/"scout.json").write_text(json.dumps(report,indent=2)+"\n")
    print("PAID_SCOUT",json.dumps(report))
    raise SystemExit(0)

candidates=[]
watchlist=[]
for line in feed.splitlines():
    p=[x.strip() for x in line.split("|")]
    if len(p)!=9 or not p[0] or not p[8].startswith("https://"):
        continue
    gig_id,title,board,lane,reward,payment,acceptance,grade,url=p
    if lane!="agent" or payment!="escrowed" or not SKILL.search(title+" "+acceptance):
        continue
    if EXCLUDE.search(" ".join((title,acceptance))):
        continue
    m=LINK.fullmatch(url)
    if not m:
        continue
    amount=re.search(r"\$\s*(\d+(?:\.\d+)?)",reward)
    if not amount or float(amount.group(1))<10:
        continue
    # Only source-check concrete GitHub issues, never treat index flag alone as open.
    api=f"https://api.github.com/repos/{m.group(1)}/{m.group(2)}/issues/{m.group(3)}"
    h={"User-Agent":"OwnerPaidWorkScout/1.0","Accept":"application/vnd.github+json"}
    if TOKEN:h["Authorization"]="Bearer "+TOKEN
    try:
        sponsor=json.loads(get(api,h))
        if sponsor.get("state")!="open" or sponsor.get("pull_request"):
            continue
        # Some bounty sponsors retain a nominally open GitHub issue after awarding;
        # do not call this claimable unless its latest sponsor comments are checked.
        count=int(sponsor.get("comments",0))
        # Fetch the actual final comment page, not Github's first comment page.
        last_page=max(1,(count+99)//100)
        comments=json.loads(get(api+"/comments?per_page=100&page="+str(last_page),h))[-15:]
        closed_claim=re.compile(r"\b(bounty (?:is )?claimed|already awarded|winner announced|bounty paid|no longer available|reward.*paid|task completed|no more submissions)\b",re.I)
        if any(closed_claim.search(str(msg.get("body") or "")[:1800]) for msg in comments):
            continue
        created=str(sponsor.get("created_at") or "")[:10]
        owner_recent=any(
            str(msg.get("author_association") or "").upper() in ("OWNER","MEMBER","COLLABORATOR")
            and str(msg.get("created_at") or "")[:10]>="2026-10-14"
            and re.search(r"still (?:available|open|payable)|reward.*available|accepting (?:new )?submissions",
                          str(msg.get("body") or ""),re.I)
            for msg in comments
        )
        if created < "2026-08-01" and not owner_recent:
            watchlist.append({"original_url":url,
                "reason":"old listing without current original-sponsor confirmation",
                "issue_created":created,"last_comments_checked":len(comments)})
            continue
        claim_mentions=sum(bool(re.search(r"/claim\b|/attempt\b",str(msg.get("body") or ""),re.I))
                           for msg in comments)
        if claim_mentions>=3 and not owner_recent:
            watchlist.append({"original_url":url,
                "reason":"several claimed attempts, payer has not re-confirmed reward",
                "issue_created":created,"last_comments_checked":len(comments)})
            continue
    except Exception:
        continue
    candidates.append({
        "title":title[:125],"original_url":url,"board":board,
        "advertised_reward":reward,"advertised_payment_state":payment,
        "github_original_issue_open":True,"reviewed_recent_comments":len(comments[-15:]),
        "verified_funding":False,"claim_available":None,
        "ugandan_eligibility":None,"authenticated_submission":False,
        "status":"source_open_payment_and_claim_unverified",
        "recommended_next_step":"Read original issue, confirm maintainer still accepts work, payout method and Uganda eligibility; draft a specific solution before any authenticated application."
    })
    if len(candidates)>=8:
        break

report={"checked_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
        "source":"https://jobbi.org/gigs.txt?lane=agent&limit=100",
        "status":"source_checked","not_claimed_or_paid":True,
        "shortlisted_unverified_paid_work":candidates,
        "stale_or_contested_watchlist":watchlist,
        "verified_paid_work":[],"verified_wallet_deposits":[]}
(OUT/"scout.json").write_text(json.dumps(report,indent=2)+"\n")
print("PAID_SCOUT",json.dumps({"candidates":len(candidates),"stale_or_contested":len(watchlist),"verified_paid":0,
                             "source_urls":[c["original_url"] for c in candidates]}))

if not candidates or not TOKEN or REPO!="kwesigaamon8-web/Amon-Kwesiga":
    raise SystemExit(0)
today=dt.datetime.now(dt.timezone.utc).date().isoformat()
marker="<!-- paid-gig-scout:"+today+" -->"
h={"User-Agent":"OwnerPaidWorkScout/1.0","Accept":"application/vnd.github+json",
   "Authorization":"Bearer "+TOKEN}
try:
    comments=json.loads(get(ISSUE+"?per_page=100",h))
    if any(marker in c.get("body","") for c in comments):
        print("Report already shared today")
        raise SystemExit(0)
    lines=[marker,"## Concrete paid-task scout — "+today,"",
      "**Verification:** original GitHub issues still open and recent issue comments screened. Sponsor acceptance, Uganda eligibility, payout and escrow have NOT been independently proven. **Nothing has been claimed, submitted or earned.**",""]
    for c in candidates[:6]:
        lines.append("- ["+c["title"].replace("]","") +"]("+c["original_url"]+") — "+c["advertised_reward"]+" indexed as escrowed via "+c["board"]+". **Next:** request maintainer confirmation that the bounty is still available and check required submission workflow.")
    lines += ["","**D action:** select a single technically feasible open issue, check maintainer's newest statements, then prepare a working fix or documentation response. Never pay upfront, auto-claim, spoof receipts or market speculative funds as income.",
              "**Source:** "+report["source"]]
    body=json.dumps({"body":"\n".join(lines)}).encode()
    req=urllib.request.Request(ISSUE,data=body,headers=h,method="POST")
    with urllib.request.urlopen(req,timeout=20) as resp:
        x=json.load(resp)
    print("PAID_SCOUT_POST",x.get("html_url"))
except Exception as exc:
    print("PAID_SCOUT_POST_BLOCKED",type(exc).__name__,str(exc)[:190])
