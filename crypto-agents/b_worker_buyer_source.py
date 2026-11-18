"""Give actual B workers a CURRENT original GitHub issue to investigate, read only.

This is never evidence that a reward is escrowed, that owner is eligible, or
that any external contact or payment occurred. A source is only a prospect.
"""
from __future__ import annotations
import hashlib,json,os,re,urllib.request
from pathlib import Path
from bounty_eligibility_audit import evaluate as evaluate_eligibility

ISSUE=re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/issues/(\d+)$")
FLEETS=("transferexperiment","BountyScoutAI")

# A live ORIGINAL marketplace fallback, never a granted contract or a payout.
# These are explicit, approved-by-publication payout *offers*, not issues
# posted by freelancing claimants or mirrored directories. Keep each endpoint
# on a closed exact HTTPS allowlist. Never sign wallets or submit automatically.
MARKETPLACE_PAGES=(
    {
        "url":"https://elgora.ai/bounties/3",
        "title":"ElgoraHub Escrow Security Bounty — local Foundry proof",
        "reward_claim":"36 USDC escrow advertised on Base",
        "asset":"USDC","network":"Base",
        "markers":("ElgoraHub Escrow Security Bounty","36.00 USDC","Funded escrow"),
        "avoid_markers":("Timed out","Awarded","No valid Submission"),
        "last_day":"2026-11-21",
        "terms":"Offline reproducible local Foundry exploit against specifically pinned escrow contracts, submit with registered compatible solver identity before deadline; first qualifying entry wins; no live exploit, wallet fees or signing by this worker.",
    },
    {
        "url":"https://www.actiontokens.org/bounties/b8d50db5-a3ce-495a-9b33-c5537a8ba5d9",
        "title":"Action Tokens authorized security bug report",
        "reward_claim":"Up to 50 USDC on Stellar, review and severity dependent",
        "asset":"USDC","network":"Stellar",
        "markers":("Find a security bug","1 of 5 claims left","50 USDC"),
        "avoid_markers":("Fully claimed","Submissions are now closed"),
        "last_day":None,
        "terms":"Find and privately disclose a real reproducible vulnerability with screenshot. No unauthorized access, harm, public exposure, or claim without verified Stellar USDC trustline.",
    },
)

def marketplace_source(fleet,worker_id,fetch_html=None,now=None):
    """One verified public LIVE market page per worker; no external claiming.

    This is research-only evidence that an offer's page currently advertises
    a reward and appears open. It does not prove on-chain escrow, owner account
    eligibility, accepted original work, or a credited incoming payment.
    """
    import datetime as dt
    from html.parser import HTMLParser
    now=now or dt.datetime.now(dt.timezone.utc)
    if fleet not in FLEETS:raise ValueError("Invalid B fleet")
    if worker_id.startswith("D10-"):
        return {"status":"LOCAL_D10_PAYMENT_ONLY_NO_SPECULATIVE_BOUNTY","source_item":None}
    class Plain(HTMLParser):
        def __init__(self):
            super().__init__();self.parts=[]
        def handle_data(self,data):self.parts.append(data)
    seed=hashlib.sha256((fleet+"/"+worker_id).encode()).digest()
    item=MARKETPLACE_PAGES[int.from_bytes(seed[:4],"big")%len(MARKETPLACE_PAGES)]
    if item["last_day"] and now.date()>dt.date.fromisoformat(item["last_day"]):
        return {"status":"MARKETPLACE_BOUNTY_EXPIRED","source_item":None}
    def default_fetch(url):
        if url not in (x["url"] for x in MARKETPLACE_PAGES):
            raise ValueError("Unapproved marketplace URL")
        req=urllib.request.Request(url,headers={"User-Agent":"B1B2ReadOnlyMarketOfferCheck/1.0","Accept":"text/html"})
        with urllib.request.urlopen(req,timeout=8) as resp:
            return resp.read(850000).decode("utf-8","replace")
    try:
        html=fetch_html(item["url"]) if fetch_html else default_fetch(item["url"])
        if not isinstance(html,str):raise ValueError("Marketplace reply not text")
        parser=Plain();parser.feed(html)
        visible=" ".join(parser.parts)
        # Check text actually rendered to users, not a hidden JSON blob or a
        # script prompt. Include only our fixed safe one-paragraph task summary.
        markers_ok=all(x.casefold() in visible.casefold() for x in item["markers"])
        unclaimed=not any(x.casefold() in visible.casefold() for x in item["avoid_markers"])
        if not markers_ok or not unclaimed:
            return {"status":"MARKETPLACE_OFFER_NOT_CONFIRMED_OPEN_AT_THIS_CHECK","source_item":None,
                    "source_checked":item["url"]}
    except Exception as e:
        return {"status":"MARKETPLACE_READ_UNAVAILABLE","source_item":None,
                "error":type(e).__name__,"source_checked":item["url"]}
    return {
        "status":"ORIGINAL_MARKETPLACE_ADVERTISED_OPEN_NOT_BUYER_ACCEPTANCE",
        "source_item":{
            "title":item["title"],"url":item["url"],
            "status":"public_reward_offer_read_only_not_accepted_or_submitted",
            "payment_funding_accepted":False,
            "reward_advertised":item["reward_claim"],
            "payout_asset":item["asset"],"payout_network":item["network"],
            "original_source_read_only":True,
            "public_issue_body_excerpt":item["terms"],
            "eligibility_screener_status":"NEEDS_AUTHENTICATED_SUBMISSION_AND_OWNER_RECEIVER_CHECK",
            "commercial_terms_independently_agreed":False,
        },
        "buyer_acceptance":False,"payout_verified":False,
        "external_contact_sent":False,
        "next_action":"Use only safe original offline/public research. Do not claim, submit, reveal a non-BTC receiving route, sign or spend without authorized platform and compatible wallet. Confirm source freshness and actual sponsor payout acceptance.",
    }

def choose(fleet,worker_id,feed_path,fetch_json=None):
    if fleet not in FLEETS:raise ValueError("Invalid B fleet")
    if worker_id.startswith("D10-"):
        return {"status":"LOCAL_D10_PAYMENT_ONLY_NO_SPECULATIVE_BOUNTY","source_item":None}
    path=Path(feed_path)
    try:feed=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError):
        return {"status":"NO_ORIGINAL_TASK_FEED_AVAILABLE","source_item":None}
    items=[x for x in feed.get("candidates",[]) if
           isinstance(x,dict) and x.get("assigned_fleet")==fleet and
           x.get("status")=="POSSIBLE_PAID_TASK_UNVERIFIED" and
           ISSUE.fullmatch(str(x.get("original_url","")))]
    if not items:
        return (marketplace_source(fleet,worker_id) if fetch_json is None else
                {"status":"NO_MATCHING_ORIGINAL_TASK_CANDIDATES","source_item":None})
    # Work on real paying-origin issues, not automated mirrors, FAQ, or
    # "reward mentioned in discussion" pseudo-opportunities.
    def priority(row):
        pay=row.get("secondary_payment_channel")
        payer_history=row.get("secondary_payer_history_claim") is True
        title=str(row.get("title") or "").lower()
        if any(t in title for t in ("digest","bounty alert","eligibility question","referral reward","[radar]","site credit","discussion about rewards","availability and scope")):
            return 9
        # An actual original GitHub-search result outranks a third-party
        # payout-history claim. The previous priority-0 directory cluster
        # repeatedly consumed all five checks on ineligible Ubiquity issues,
        # before any newly posted original source was reached.
        if row.get("source")=="GitHub public issues: original repository":return -1
        if payer_history and pay=="crypto":return 0
        if payer_history and pay=="stripe":return 1
        if payer_history and pay=="upwork":return 2
        return 5
    items=sorted(items,key=lambda x:(priority(x),x["original_url"]))
    if priority(items[0])>=9:
        return (marketplace_source(fleet,worker_id) if fetch_json is None else
                {"status":"NO_COMMERCIALLY_USABLE_ORIGINAL_ISSUES","source_item":None})
    # Independent workers were wasting real model executions on the SAME
    # top-ranked issue when its priority tier held only one entry. Rotate
    # across a meaningful source window, including secondary candidates.
    # Every selected source still needs a fresh original-issue eligibility
    # and latest-comment check. Determinism makes runs reproducible.
    eligible=[item for item in items if priority(item)<9]
    shortlist=eligible[:min(len(eligible),max(8,(len(eligible)+1)//2))]
    seed=hashlib.sha256((fleet+"/"+worker_id).encode()).digest()
    initial=int.from_bytes(seed[:8],"big")%len(shortlist)
    ordered=(shortlist[initial:]+shortlist[:initial]
             +eligible[len(shortlist):])
    def default_fetch(url):
        headers={"Accept":"application/vnd.github+json","User-Agent":"IndependentBReadOnlyTaskInspector/1.0"}
        token=os.environ.get("GH_TOKEN","")
        if token:headers["Authorization"]="Bearer "+token
        with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=9) as res:
            return json.loads(res.read(600000))
    fetch=fetch_json or default_fetch
    skipped=[]
    original=None
    chosen=None
    link=None
    eligibility=None
    # Bounded but deeper: the top five are often already claimed or core-team
    # restricted. Do not waste an entire model shift before testing other leads.
    for candidate in ordered[:min(len(ordered),12)]:
        url=candidate["original_url"]
        match=ISSUE.fullmatch(url)
        api="https://api.github.com/repos/"+match.group(1)+"/"+match.group(2)+"/issues/"+match.group(3)
        try:
            issue=fetch(api)
            if issue.get("state")!="open" or issue.get("pull_request") or issue.get("html_url")!=url:
                skipped.append({"url":url,"reason":"NOT_OPEN_OR_SOURCE_URL_MISMATCH"})
                continue
            # Most third-party search 'bounties' are actually submissions or
            # reservation questions posted by unaffiliated contributors.
            # Without an issuer relationship, a bounty is not a buyer order.
            relation=str(issue.get("author_association") or "").upper()
            if relation in ("NONE","CONTRIBUTOR","FIRST_TIME_CONTRIBUTOR","FIRST_TIMER"):
                skipped.append({"url":url,"reason":"UNVERIFIED_OUTSIDER_AUTHOR_NOT_SPONSOR",
                                "author_association":relation})
                continue
            n=int(issue.get("comments") or 0)
            comments=[]
            # Comments reveal permission warnings, submitted fixes and payout
            # restrictions that search results and issue descriptions omit.
            if n>0:
                # Inspect the latest page, not only the first 100 stale comments.
                page=(n-1)//100+1
                comments=fetch(api+"/comments?per_page=100&page="+str(page))
                if not isinstance(comments,list):
                    skipped.append({"url":url,"reason":"COMMENTS_UNAVAILABLE"})
                    continue
            # Multiple already-linked pull requests are evidence that a
            # first-merged paid fix may have been taken. Do not send model workers
            # into competing duplicate submissions without sponsor reconfirmation.
            text="\n".join(str(c.get("body") or "")[:2000] for c in comments if isinstance(c,dict))
            pr_numbers=set(re.findall(r"(?i)(?:/pull/|\bPR\s*#|\bpull request\s*#)\s*(\d+)",text))
            if len(pr_numbers)>=2:
                skipped.append({"url":url,"reason":"MULTIPLE_EXISTING_PR_CLAIMS_REQUIRES_SPONSOR_RECONFIRMATION",
                                "existing_pr_count_at_least":len(pr_numbers)})
                continue
            eligibility=evaluate_eligibility(issue,comments)
            if eligibility["critical_blocker"]:
                skipped.append({"url":url,"reason":"EXPLICIT_EXTERNAL_CONTRIBUTOR_RESTRICTION_OR_OTHER_CRITICAL","flags":eligibility["flags"]})
                continue
            original=issue; chosen=candidate; link=url
            break
        except Exception as exc:
            skipped.append({"url":url,"reason":"ORIGINAL_SOURCE_OR_COMMENT_READ_FAILED","error":type(exc).__name__})
    if original is None:
        if fetch_json is None:
            fallback=marketplace_source(fleet,worker_id)
            fallback["rejected_source_candidates"]=skipped
            if fallback.get("source_item"):
                return fallback
        return {"status":"NO_OPEN_ACCESSIBLE_PAID_ISSUE_FOUND_AFTER_ELIGIBILITY_CHECK",
                "source_item":None,"rejected_source_candidates":skipped}
    return {
        "status":"ORIGINAL_ISSUE_SCREENED_NO_OBVIOUS_ELIGIBILITY_BLOCKER_PAYER_UNVERIFIED",
        "source_item":{"title":str(original.get("title") or chosen.get("title") or "")[:155],
                       "url":link,
                       "status":"original_open_issue_check_only_not_verified_customer",
                       "payment_funding_accepted":False,
                       "company_director_assigned":chosen.get("assigned_company_director"),
                       "original_source_read_only":True,
                       "public_issue_body_excerpt":str(original.get("body") or "")[:650],
                       "public_issue_created_at":str(original.get("created_at") or "")[:35],
                       "public_issue_last_updated":str(original.get("updated_at") or "")[:35],
                       "public_issue_comment_count":int(original.get("comments") or 0),
                       "eligibility_risk_flags":eligibility["flags"],
                       "eligibility_screener_status":eligibility["eligibility"]},
        "rejected_source_candidates":skipped,
        "buyer_acceptance":False,"payout_verified":False,
        "external_contact_sent":False,
        "next_action":"Read terms and recent sponsor comments, verify real funding, eligibility and acceptance before preparing scoped work."
    }

def self_test():
    # Test the public-funding-page fallback offline. Never generate
    # acceptance or payer evidence from a page title or unverified contents.
    import datetime as dt
    now=dt.datetime(2026,11,18,tzinfo=dt.timezone.utc)
    def valid_page(url):
        item=next(x for x in MARKETPLACE_PAGES if x["url"]==url)
        return "<main>"+(" ".join(item["markers"]))+"</main>"
    hit=marketplace_source("BountyScoutAI","D01-M01-W01",fetch_html=valid_page,now=now)
    assert hit["source_item"] and hit["source_item"]["payment_funding_accepted"] is False
    assert hit["payout_verified"] is False and hit["external_contact_sent"] is False
    assert hit["source_item"]["url"].startswith("https://")
    empty=marketplace_source("BountyScoutAI","D01-M01-W01",fetch_html=lambda u:"<main>Closed</main>",now=now)
    assert empty["source_item"] is None
    assert marketplace_source("BountyScoutAI","D10-M01-W01",fetch_html=valid_page,now=now)["source_item"] is None
    with __import__("tempfile").TemporaryDirectory() as temp:
        f=Path(temp)/"candidate.json"
        f.write_text(json.dumps({"candidates":[
          {"status":"POSSIBLE_PAID_TASK_UNVERIFIED","assigned_fleet":"transferexperiment",
           "original_url":"https://github.com/example/repo/issues/12","title":"$30 bug fix"},
          {"status":"POSSIBLE_PAID_TASK_UNVERIFIED","assigned_fleet":"BountyScoutAI",
           "original_url":"https://github.com/example2/repo/issues/19","title":"$40 original report"}]}))
        good=choose("transferexperiment","D01-M01-W01",f,
                    lambda _:{"state":"open","title":"$30 bug fix","html_url":"https://github.com/example/repo/issues/12"})
        assert good["status"]=="ORIGINAL_ISSUE_SCREENED_NO_OBVIOUS_ELIGIBILITY_BLOCKER_PAYER_UNVERIFIED"
        assert good["source_item"]["payment_funding_accepted"] is False
        bad=choose("transferexperiment","D01-M01-W01",f,
                   lambda _:{"state":"closed","html_url":"https://github.com/example/repo/issues/12"})
        assert bad["source_item"] is None
        assert choose("BountyScoutAI","D10-M01-W01",f)["source_item"] is None
        assert choose("BountyScoutAI","D01-M01-W01",f,
                   lambda _:{"state":"open","html_url":"https://github.com/example2/repo/issues/19"})["source_item"]["url"].endswith("/19")
        with f.open("w") as out:
            json.dump({"candidates":[
              {"status":"POSSIBLE_PAID_TASK_UNVERIFIED","assigned_fleet":"transferexperiment",
               "original_url":"https://github.com/example/repo/issues/15","title":"Review discussion about rewards"},
              {"status":"POSSIBLE_PAID_TASK_UNVERIFIED","assigned_fleet":"transferexperiment",
               "original_url":"https://github.com/example/repo/issues/16","title":"Fix concrete bug",
               "secondary_payment_channel":"crypto","secondary_payer_history_claim":True}
            ]},out)
        q=choose("transferexperiment","D01-M01-W01",f,
                   lambda url:{"state":"open","html_url":"https://github.com/example/repo/issues/16"})
        assert q["source_item"]["url"].endswith("/16")
        denied_issue={"state":"open","html_url":"https://github.com/example/repo/issues/16",
                      "title":"$75 bounty fix","body":"Repair retry bug",
                      "comments":1}
        def restricted_fetch(url):
            if "comments?" in url:
                return [{"user":{"login":"github-actions[bot]"},
                         "body":"You must be a core team member or administrator to start this task"}]
            return denied_issue
        blocked=choose("transferexperiment","D01-M01-W01",f,restricted_fetch)
        assert blocked["source_item"] is None
        assert any("EXPLICIT_EXTERNAL_CONTRIBUTOR_RESTRICTION" in z.get("flags",[]) for z in blocked["rejected_source_candidates"])
        # A single older paid issue with several competing PRs must not
        # consume the fleet's real AI inference resources repeatedly.
        def contested_fetch(url):
            if "comments?" in url:
                return [{"body":"Implemented in PR #25 and PR #27; now PR #33 is active."}]
            return {"state":"open","html_url":"https://github.com/example/repo/issues/16",
                    "title":"$75 bounty fix","body":"Repair retry bug","comments":3}
        contested=choose("transferexperiment","D01-M01-W01",f,contested_fetch)
        assert contested["source_item"] is None
        assert contested["rejected_source_candidates"][0]["reason"]=="MULTIPLE_EXISTING_PR_CLAIMS_REQUIRES_SPONSOR_RECONFIRMATION"

        # An external claimant's submission is not a sponsor-issued paid task.
        f.write_text(json.dumps({"candidates":[{
            "status":"POSSIBLE_PAID_TASK_UNVERIFIED",
            "assigned_fleet":"transferexperiment",
            "original_url":"https://github.com/example/repo/issues/50",
            "title":"$25 API integration submission",
            "source":"GitHub public issues: original repository"},
            {"status":"POSSIBLE_PAID_TASK_UNVERIFIED",
             "assigned_fleet":"transferexperiment",
             "original_url":"https://github.com/example/repo/issues/51",
             "title":"$80 bug fix sponsor request",
             "source":"GitHub public issues: original repository"}]}))
        def outsider_then_maintainer(url):
            n=url.split("/issues/")[1].split("?")[0]
            return {"state":"open","title":"$80 repair test",
                    "html_url":"https://github.com/example/repo/issues/"+n,
                    "author_association":"NONE" if n=="50" else "OWNER",
                    "comments":0}
        verified_relation=choose("transferexperiment","D01-M01-W01",f,outsider_then_maintainer)
        assert verified_relation["source_item"]["url"].endswith("/51"),verified_relation
        assert any(x["reason"]=="UNVERIFIED_OUTSIDER_AUTHOR_NOT_SPONSOR"
                   for x in verified_relation["rejected_source_candidates"])

        # Bounded checks must reach a fresh original listing, even when a
        # secondary directory includes more than five unusable reward claims.
        primary={"status":"POSSIBLE_PAID_TASK_UNVERIFIED",
                 "assigned_fleet":"transferexperiment",
                 "original_url":"https://github.com/example/repo/issues/80",
                 "title":"$50 genuine maintainer task",
                 "source":"GitHub public issues: original repository"}
        secondaries=[{"status":"POSSIBLE_PAID_TASK_UNVERIFIED",
                      "assigned_fleet":"transferexperiment",
                      "original_url":f"https://github.com/example/repo/issues/{i}",
                      "title":"$300 old reward",
                      "secondary_directory_url":"https://example.org/directory",
                      "secondary_payment_channel":"crypto",
                      "secondary_payer_history_claim":True}
                     for i in range(81,93)]
        f.write_text(json.dumps({"candidates":secondaries+[primary]}))
        def many_restricted(url):
            n=url.split("/issues/")[1].split("?")[0]
            return {"state":"open","html_url":"https://github.com/example/repo/issues/"+n,
                    "title":"$50 paid task","comments":0,
                    "author_association":"OWNER" if n=="80" else "NONE"}
        chosen=choose("transferexperiment","D01-M01-W01",f,many_restricted)
        assert chosen["source_item"]["url"].endswith("/80"),chosen

        # Many active workers must not all process the first appealing issue.
        f.write_text(json.dumps({"candidates":[{
            "status":"POSSIBLE_PAID_TASK_UNVERIFIED",
            "assigned_fleet":"transferexperiment",
            "original_url":f"https://github.com/example/repo/issues/{n}",
            "title":f"$40 original patch {n}"}
            for n in range(21,33)]}))
        def all_open(url):
            n=url.split("/issues/")[1].split("?")[0]
            return {"state":"open","title":"$40 small Python fix",
                    "body":"Bounty $40 after accepted verified tests",
                    "html_url":"https://github.com/example/repo/issues/"+n,
                    "comments":0}
        choices={choose("transferexperiment",
                        f"D{n:02d}-M01-W01",f,all_open)["source_item"]["url"]
                 for n in range(1,10)}
        assert len(choices)>=3,choices


    print("PASS original task source fed to each real B only, no imaginary payer or D10 speculation")
if __name__=="__main__":self_test()
