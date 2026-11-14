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
    if not items:return {"status":"NO_MATCHING_ORIGINAL_TASK_CANDIDATES","source_item":None}
    # Work on real paying-origin issues, not automated mirrors, FAQ, or
    # "reward mentioned in discussion" pseudo-opportunities.
    def priority(row):
        pay=row.get("secondary_payment_channel")
        payer_history=row.get("secondary_payer_history_claim") is True
        title=str(row.get("title") or "").lower()
        if any(t in title for t in ("digest","bounty alert","eligibility question","referral reward","[radar]","site credit")):
            return 9
        if payer_history and pay=="crypto":return 0
        if payer_history and pay=="stripe":return 1
        if payer_history and pay=="upwork":return 2
        return 5
    items=sorted(items,key=lambda x:(priority(x),x["original_url"]))
    best_priority=priority(items[0])
    if best_priority>=9:
        return {"status":"NO_COMMERCIALLY_USABLE_ORIGINAL_ISSUES","source_item":None}
    top=[x for x in items if priority(x)==best_priority]
    seed=hashlib.sha256((fleet+"/"+worker_id).encode()).digest()
    initial=int.from_bytes(seed[:8],"big")%len(top)
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
    for step in range(min(5,len(top))):
        candidate=top[(initial+step)%len(top)]
        url=candidate["original_url"]
        match=ISSUE.fullmatch(url)
        api="https://api.github.com/repos/"+match.group(1)+"/"+match.group(2)+"/issues/"+match.group(3)
        try:
            issue=fetch(api)
            if issue.get("state")!="open" or issue.get("pull_request") or issue.get("html_url")!=url:
                skipped.append({"url":url,"reason":"NOT_OPEN_OR_SOURCE_URL_MISMATCH"})
                continue
            n=int(issue.get("comments") or 0)
            comments=[]
            # Comments reveal permission warnings, submitted fixes and payout
            # restrictions that search results and issue descriptions omit.
            if n>0:
                comments=fetch(api+"/comments?per_page=100")
                if not isinstance(comments,list):
                    skipped.append({"url":url,"reason":"COMMENTS_UNAVAILABLE"})
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

    print("PASS original task source fed to each real B only, no imaginary payer or D10 speculation")
if __name__=="__main__":self_test()
