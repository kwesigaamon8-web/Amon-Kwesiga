"""Continuous public social *lead discovery* for two company boards.

Searches at most two director themes per hour using existing Bluesky/Reddit
read-only search. Does not post, follow, send a DM, create accounts or sign
anything. No automatic hiring, buyer acceptance, or cash claims.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import pathlib
import re
import sys

ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from social_scan import scan_social, TOPICS
OUT=pathlib.Path("paid-opportunity-reports")
FLEETS=("transferexperiment","BountyScoutAI")
TAGS=("csv","python","excel","spreadsheet","quickbooks","bookkeep",
      "reconcil","invoice","accounting","data clean","api","paid","bounty")
INTENT=re.compile(
    r"(?i)\b(?:we['’]?re\s+(?:hiring|looking\s+for)|"
    r"i['’]m\s+(?:hiring|looking\s+for)|looking\s+to\s+hire|"
    r"seeking\s+(?:a|an|someone|developer|freelancer)|"
    r"need\s+(?:a|an|someone|help|developer|freelancer)|"
    r"paid\s+(?:gig|project|task|bounty)|bounty\s+(?:for|to)|"
    r"job\s+(?:opening|opportunity)|hiring)\b"
)
IGNORE=re.compile(
    r"(?i)\b(?:for\s+hire|available\s+for\s+hire|"
    r"hire\s+me|offering\s+my\s+services|"
    r"looking\s+for\s+(?:a\s+)?(?:job|work|clients|employment)|"
    r"i\s+offer|i\s+can\s+help\s+you|"
    r"wallet\s+connect|airdrop|presale|"
    r"send\s+(?:money|crypto|usdc|bitcoin)\s+first)\b"
)

def score(item, now):
    s=" ".join(str(item.get(x) or "") for x in ("title","excerpt"))
    if IGNORE.search(s) or not INTENT.search(s):
        return None
    ts=item.get("updated")
    try:
        t=dt.datetime.fromisoformat(str(ts).replace("Z","+00:00"))
        if not t.tzinfo:t=t.replace(tzinfo=dt.timezone.utc)
        if t>now+dt.timedelta(minutes=20) or now-t>dt.timedelta(days=14):
            return None
    except (ValueError,TypeError):
        return None
    tags=[x for x in TAGS if x in s.lower()]
    if not tags:return None
    source=item.get("social_platform")
    url=str(item.get("url") or "")
    if source=="Bluesky" and not url.startswith("https://bsky.app/profile/"):
        return None
    if source=="Reddit" and not url.startswith("https://www.reddit.com/r/"):
        return None
    if source not in ("Bluesky","Reddit"):
        return None
    return {
      "source":source,"public_post_url":url,"posted_at_utc":t.isoformat(),
      "text_excerpt":s[:300],
      "relevant_skills":tags[:6],
      "hiring_intent_heuristic_only":True,
      "actual_payer_and_hiring_not_verified":True,
      "uganda_eligibility_not_verified":True,
      "inbound_crypto_payment_not_verified":True,
      "external_contact_sent":False,
      "authenticated_social_account_connected":False,
      "recommended_next_step":"Read original human post, verify payer and legitimate terms, location eligibility and public venue rules; only contact through a genuinely authorized account where welcomed."
    }

def run(now=None,scanner=scan_social):
    now=now or dt.datetime.now(dt.timezone.utc)
    hour=int(now.timestamp()//3600)
    ids=tuple(sorted(TOPICS))
    # 10 different director themes in five hourly rotations.
    roleids=(ids[(2*(hour%5))%len(ids)],ids[(2*(hour%5)+1)%len(ids)])
    seen=set()
    selected=[]
    errors={}
    read_counts={}
    for did in roleids:
        rows,err=scanner({"id":did,"director":did})
        read_counts[did]=len(rows)
        if err:errors[did]=[str(x)[:140] for x in err]
        for item in rows:
            r=score(item,now)
            if r and r["public_post_url"] not in seen:
                seen.add(r["public_post_url"])
                r["assigned_B1_demand_review"]="transferexperiment/D03"
                r["assigned_B2_sample_QA"]="BountyScoutAI/D05"
                selected.append(r)
    selected.sort(key=lambda x:x["posted_at_utc"],reverse=True)
    return {
        "schema":"CHIEF_D_SOCIAL_READ_ONLY_HIRING_SCOUT_V1",
        "checked_at_utc":now.isoformat(),
        "source_domains_attempted":["bsky.app","reddit.com"],
        "role_themes_checked_this_hour":roleids,
        "raw_public_research_candidates":sum(read_counts.values()),
        "source_errors":errors,
        "social_accounts_authenticated_for_posting_by_this_scout":[],
        "posts_replies_and_DMs_sent_by_this_scout":0,
        "credible_payer_hired_or_contract_verified_by_this_scout":0,
        "coins_received_verified_by_this_scout":0,
        "read_only_incoming_wallets":True,
        "candidate_social_hiring_posts_UNVERIFIED":selected[:12],
        "actual_candidates_before_limit":len(selected),
        "source_outage_is_not_zero_opportunities":bool(errors),
        "recurrence":"This script runs in an actual scheduled GitHub Actions execution; configured billions of worker IDs are not active social accounts."
    }

def selftest():
    now=dt.datetime(2026,11,17,6,25,tzinfo=dt.timezone.utc)
    def fake(role):
        return ([
          {"title":"We are hiring a Python CSV cleanup freelancer",
           "excerpt":"Need a contractor for invoice spreadsheet project",
           "social_platform":"Bluesky",
           "url":"https://bsky.app/profile/test.example/post/abc",
           "updated":"2026-11-17T06:00:00Z"},
          {"title":"For hire: I can help with Excel",
           "excerpt":"My services","social_platform":"Reddit",
           "url":"https://www.reddit.com/r/forhire/comments/abc/job/",
           "updated":"2026-11-17T05:00:00Z"},
          {"title":"We are hiring an Excel consultant",
           "excerpt":"Posted 30 days ago","social_platform":"Reddit",
           "url":"https://www.reddit.com/r/forhire/comments/xyz/job/",
           "updated":"2026-10-01T05:00:00Z"}],[])
    d=run(now,fake)
    assert len(d["candidate_social_hiring_posts_UNVERIFIED"])==1
    assert d["actual_candidates_before_limit"]==1
    assert d["posts_replies_and_DMs_sent_by_this_scout"]==0
    assert d["read_only_incoming_wallets"] is True
    assert d["candidate_social_hiring_posts_UNVERIFIED"][0]["actual_payer_and_hiring_not_verified"]
    fail=run(now,lambda role: ([],["public endpoint 403"]))
    assert fail["source_outage_is_not_zero_opportunities"] and len(fail["source_errors"])==2
    assert fail["actual_candidates_before_limit"]==0
    print("CHIEF_D_SOCIAL_OPPORTUNITY_SCOUT_TEST_PASS",
          json.dumps({"candidate_test_count":1,"no_public_posting":True,"outages_explicit":True}))

def save(data):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"social-work.json").write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    lines=["# B1/B2 permission-based social hiring discovery",
           "Checked UTC: "+data["checked_at_utc"],"",
           "Platforms attempted: public Bluesky and Reddit (READ ONLY)",
           "Buyer contacts sent: 0, contracts accepted: 0, crypto deposits proven: 0.",
           "Themes: "+", ".join(data["role_themes_checked_this_hour"]),
           "Potential source errors: "+str(data["source_errors"]),"",
           "## Unverified direct social-hiring posts"]
    for item in data["candidate_social_hiring_posts_UNVERIFIED"]:
        lines.append("- ["+item["source"]+"]("+item["public_post_url"]+
          ") — "+item["text_excerpt"].replace("\n"," ").replace("|","/")[:165]+
          " (payer/permission/eligibility NOT verified)")
    lines.extend(["",
      "Only reply to posts asking for bids, through a connected authorized account, with individualized relevant details.",
      "No unsolicited bulk advertising, bot spam, impersonation, crypto-wallet sending or unverified payout claims.",
      "Bluesky/Reddit public search results are not social accounts or permission to post."])
    (OUT/"social-work.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    o=p.parse_args()
    if o.self_test:selftest()
    else:
        d=run();save(d)
        print("CHIEF_D_SOCIAL_WORK",json.dumps({
            "checked_at_utc":d["checked_at_utc"],
            "roles_checked":list(d["role_themes_checked_this_hour"]),
            "source_error_directors":len(d["source_errors"]),
            "possible_hiring_posts_unverified":len(d["candidate_social_hiring_posts_UNVERIFIED"]),
            "authenticated_contacts_sent":0,"contracts":0,"paid_receipts":0
        }))
