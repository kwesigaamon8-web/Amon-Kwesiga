"""Read-only cross-source candidate scan for legitimate crypto-paid jobs.

No automatic bounty claims, wallet signatures, mass messaging, mining or
invented payouts. This expands the original Jobbi feed by independently
checking a bounded set of recent open GitHub sponsorship opportunities.
GitHub's search is an index, not proof of payer legitimacy or reward funding.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

OUT=Path("paid-opportunity-reports")
OUT.mkdir(exist_ok=True)
REPO="kwesigaamon8-web/Amon-Kwesiga"
TOKEN=os.environ.get("GH_TOKEN","")
T=dt.datetime.now(dt.timezone.utc)
SINCE=(T-dt.timedelta(days=21)).date().isoformat()
MAX_CANDIDATES_PER_SEARCH=25
HEADERS={"Accept":"application/vnd.github+json","User-Agent":"TwoCompanyAuthenticPaidWorkScout/1.0"}
if TOKEN:HEADERS["Authorization"]="Bearer "+TOKEN

SEARCHES=[
 f'is:issue is:open bounty reward created:>={SINCE} -repo:{REPO}',
 f'is:issue is:open "BTC" "reward" created:>={SINCE} -repo:{REPO}',
 f'is:issue is:open "USDC" bounty created:>={SINCE} -repo:{REPO}',
 f'is:issue is:open "paid" "fix" created:>={SINCE} -repo:{REPO}',
]
MONEY=re.compile(r'(?i)(?:[$€£]\s?\d+(?:[.,]\d+)?|(?:\d+(?:\.\d+)?)\s?(?:BTC|USDC|USD|sats?|satoshis)\b|\bbounty\s*(?:amount|pool|reward)\s*[:=]\s?\d+)')
SCOPE=re.compile(r'(?i)\b(?:fix|implement|write|docs|test|issue|build|patch|data|audit|research|bug|feature|script|code|review|integration|translate|spreadsheet|documentation)\b')
RISK=re.compile(r'(?i)\b(?:deposit|prepay|send funds|send crypto first|connect your wallet|verification fee|stake required|bond required|private key|seed phrase|pay to claim)\b')
FINISHED=re.compile(r'(?i)\b(?:already awarded|claimed and paid|bounty closed|winner chosen|no longer available|work complete|payment issued)\b')

# Filter misleading low-quality discovery hits before assigning scarce real
# LLM inference. Open GitHub issues often contain unrelated monetary figures,
# automated digests, third-party mirrors, disputes and reward questions.
STRONG_REWARD=re.compile(r'(?i)(?:\b(?:bounty|reward|payout|compensation|payment|prize|paid)\s*(?:[:=\-]|is|of|worth)?\s*(?:USD\s*)?(?:[$€£]\s*\d+(?:[.,]\d+)?|\d+(?:\.\d+)?\s*(?:USD|USDC|BTC|sats?|satoshis))\b|(?:[$€£]\s*\d+(?:[.,]\d+)?|\d+(?:\.\d+)?\s*(?:BTC|USDC|USD|sats?))\s*(?:\b(?:bounty|reward|payout|compensation|payment|prize)\b))')
ZERO_OFFER=re.compile(r'(?i)(?:\b(?:bounty|reward|compensation|payment|price)\s*[:=]?\s*\$0(?:\D|$)|\[\$0\]|\b(?:unpaid|volunteer-only|no reward|no payout)\b)')
SECONDARY_SOURCE=re.compile(r'(?i)(?:\b(?:digest|roundup|alert|scanner|mirror|aggregat(?:or|ion)|newsletter|vote:|discussion only|not (?:reviewed|accepted) on this mirror|no manual pull requests)\b|(?:^\s*###\s*(?:original link|source url)\s*$))')
UNRELATED_MONEY=re.compile(r'(?i)(?:\b(?:state|sales)[ -]?tax\b|\b(?:taxable|income tax|payroll|vat)\b|\b\$[\d.,]+\s*(?:sale|purchase|invoice)\b)')
QUESTIONS_ONLY=re.compile(r'(?i)(?:\b(?:could the current docs|clarify|question routes|request for information|eligibility question|is the bounty|vote:|how to claim)\b)')
AUTO_USERNAME=re.compile(r'(?i)(?:\[bot\]$|^github-actions(?:\[bot\])?$|^dependabot(?:\[bot\])?$)')
EXCLUDED_ORIGIN_REPOS=("bountyscout","bounty-plaza")


def github_get(url):
    request=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(request,timeout=14) as response:
        return json.loads(response.read(1_500_000))

def normalize(issue):
    title=str(issue.get("title") or "")[:170]
    body=str(issue.get("body") or "")[:12000]
    full=title+"\n"+body
    url=str(issue.get("html_url") or "")
    from_user=issue.get("user") or {}
    original_repo=str(issue.get("repository_url") or "").split("/repos/")[-1]
    repo_name=original_repo.split("/")[-1].lower()
    # Empty repository_url occurs in simple unit fixtures: do not assert
    # provenance from a stub; a real search result must supply its own repo.
    mirror_or_digest=(bool(SECONDARY_SOURCE.search(title)) or
        "not reviewed on this mirror" in body.lower() or
        any(name in repo_name for name in EXCLUDED_ORIGIN_REPOS))
    checks={
       "open_issue":issue.get("state")=="open" and not issue.get("pull_request"),
       "original_link":url.startswith("https://github.com/"),
       "mentions_specific_reward_amount":bool(MONEY.search(full)),
       "explicit_paid_work_reward":bool(STRONG_REWARD.search(full)) and not bool(ZERO_OFFER.search(full)),
       "describes_actual_work":bool(SCOPE.search(full)),
       "not_automated_digest_or_secondary_mirror":not mirror_or_digest,
       "author_not_obvious_bot":not bool(AUTO_USERNAME.search(str(from_user.get("login") or ""))),
       "not_a_money_question_or_unrelated_sales_figure":not bool(QUESTIONS_ONLY.search(title)) and
          not (bool(UNRELATED_MONEY.search(title)) and not STRONG_REWARD.search(title)),
       "no_obvious_deposit_or_key_request":not bool(RISK.search(full)),
       "not_marked_already_awarded_in_description":not bool(FINISHED.search(full)),
    }
    status=("POSSIBLE_PAID_TASK_UNVERIFIED" if all(checks.values())
            else "REVIEW_OR_REJECT")
    return {
      "original_url":url,
      "title":title,
      "created_at":issue.get("created_at"),
      "updated_at":issue.get("updated_at"),
      "original_repo":(issue.get("repository_url") or "").split("/repos/")[-1],
      "source":"GitHub public issues: original repository",
      "checks":checks,
      "status":status,
      "reward_funded":False,
      "claim_eligible_for_owner":None,
      "payout_network_accepted":None,
      "external_payer_contact_sent":False,
      "work_completed":False,
      "verified_paid_receipt":False,
      "next_step":"Read current issue AND current comments, confirm sponsor authority, funding, exact deliverable, eligibility and payout network before claiming, doing work, or requesting BTC.",
    }

def assign_company_review(candidate):
    digest=hashlib.sha256(candidate["original_url"].encode("utf-8")).digest()
    fleet=("transferexperiment","BountyScoutAI")[digest[0]%2]
    director=f"D{1+digest[1]%9:02d}" # D10 is local payment recovery, not new speculative leads
    return {**candidate,
      "assigned_fleet":fleet,
      "assigned_company_director":fleet+"/"+director,
      "reports_to":"D",
      "owner_order_id":"OWNER-20261114-074258",
      "assignment_status":"ASSIGNED_FOR_FUTURE_VALIDATION_NOT_CONTACTED",
      "accepted_client_job":False,
      "payment_recovery_handoff":fleet+"/D10 only after sponsor acceptance and funds due",
    }

def scan():
    selected={}
    rejected=0
    source_errors=[]
    for q in SEARCHES:
        url=("https://api.github.com/search/issues?"+
          urllib.parse.urlencode({"q":q,"per_page":MAX_CANDIDATES_PER_SEARCH,"sort":"created","order":"desc"}))
        try:items=github_get(url).get("items",[])
        except Exception as e:
            source_errors.append({"query":q,"error":type(e).__name__+": "+str(e)[:100]})
            continue
        for item in items:
            candidate=normalize(item)
            if candidate["status"]!="POSSIBLE_PAID_TASK_UNVERIFIED":
                rejected+=1
                continue
            if candidate["original_url"] in selected:continue
            selected[candidate["original_url"]]=assign_company_review(candidate)
    return {
      "checked_utc":T.isoformat(),
      "companies":["transferexperiment","BountyScoutAI"],
      "status":"CANDIDATES_REQUIRE_ORIGINAL_SPONSOR_VALIDATION",
      "queries":SEARCHES,
      "source_errors":source_errors,
      "rejected_nonmatching_or_risky_issues":rejected,
      "candidate_count":len(selected),
      "candidates":list(selected.values())[:45],
      "independent_director_review_queues":{
        fleet:[a for a in list(selected.values())[:45] if a["assigned_fleet"]==fleet]
        for fleet in ("transferexperiment","BountyScoutAI")
      },
      "director_assignments_are_not_authenticated_external_contacts":True,
      "mining_collaboration":{
          "opt_in_only":True,
          "official_pool":"https://web.public-pool.io/",
          "solo_accepted_endpoint":"stratum+tls://public-pool.io:4333",
          "shared_pplns_endpoint":"stratum+tls://public-pool.io:14333",
          "correct_bitcoin_username_format":"BTC_RECEIVING_ADDRESS.optional_worker_name",
          "miner_hardware_or_signing_access":"not_available",
          "third_party_miner_verified":"not_verified",
          "hasrate_or_actual_shares_verified":"not_verified",
          "actual_mined_coins_received":"not_verified",
          "warning":"Solo mining pays only if a valid block is found; PPLNS pays according to actual eligible share/pool performance. BTC CPU and language-model processes cannot be assumed profitable ASIC miners. Pool mode, payout identity, self-custody and miner consent must be verified, no deposits or hardware financing assumed."
      },
      "payment_status":"No real transaction has been established by candidate discovery.",
      "limits":"This samples bounded public GitHub searches plus the separate Jobbi scout; it is not an exhaustive scan of every paid job or AI agent worldwide. No payouts or external messages are inferred."
    }

def selftest():
    issue={"title":"$50 bounty fix CSV import for a Python library","body":"Implement a test and source code fix, PR accepted by maintainers.","state":"open","html_url":"https://github.com/sample/repo/issues/44"}
    assert normalize(issue)["status"]=="POSSIBLE_PAID_TASK_UNVERIFIED"
    assert assign_company_review(normalize(issue))["assigned_company_director"].split("/")[-1]!="D10"
    issue["body"]+=" Send funds for a verification fee."
    assert normalize(issue)["status"]=="REVIEW_OR_REJECT"
    issue["body"]="The bounty was already awarded. Fix code."
    assert normalize(issue)["status"]=="REVIEW_OR_REJECT"
    issue={"title":"Docs: current referral reward eligibility and review timing",
           "body":"The docs advertise $50 in BTC for referrals. Can you clarify eligibility?",
           "state":"open","html_url":"https://github.com/aib/landing/issues/9",
           "repository_url":"https://api.github.com/repos/aib/landing","user":{"login":"aria"}}
    assert normalize(issue)["status"]=="REVIEW_OR_REJECT"
    issue={"title":"YouTube digest — 2026-11-14",
           "body":"Financial video: $35.5 billion debt and audits",
           "state":"open","html_url":"https://github.com/r/trading/issues/3",
           "repository_url":"https://api.github.com/repos/r/trading","user":{"login":"github-actions[bot]"}}
    assert normalize(issue)["status"]=="REVIEW_OR_REJECT"
    issue={"title":"[Bounty] [Escrowed $600 USDC] fix 64 shards",
           "body":"Automated mirror; no manual pull requests reviewed on this mirror",
           "state":"open","html_url":"https://github.com/r/bounty-plaza/issues/3",
           "repository_url":"https://api.github.com/repos/r/bounty-plaza","user":{"login":"author"}}
    assert normalize(issue)["status"]=="REVIEW_OR_REJECT"
    issue={"title":"$0 i18n bounty: translate README",
           "body":"Create docs PR. Reward $0.", "state":"open",
           "html_url":"https://github.com/owner/repo/issues/4",
           "repository_url":"https://api.github.com/repos/owner/repo","user":{"login":"maintainer"}}
    assert normalize(issue)["status"]=="REVIEW_OR_REJECT"
    issue={"title":"$50 bounty: fix CSV import on project",
           "body":"Maintainer offers $50 reward after reviewed PR, test required",
           "state":"open","html_url":"https://github.com/owner/repo/issues/5",
           "repository_url":"https://api.github.com/repos/owner/repo","user":{"login":"maintainer"}}
    assert normalize(issue)["status"]=="POSSIBLE_PAID_TASK_UNVERIFIED"
    print("PAID_CANDIDATE_QUALITY_TESTS_PASS — reject digest, reward FAQ, mirror and zero-bounty; retain real scoped paid issue")

if __name__=="__main__":
    selftest()
    out=scan()
    (OUT/"new-earning-lanes.json").write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    lines=["# Independent paid jobs and opt-in mining cooperation","",
      "Checked UTC: "+out["checked_utc"],
      "Recent original-source *candidate* issues: "+str(out["candidate_count"]),
      "Rejected nonmatching/risky issues: "+str(out["rejected_nonmatching_or_risky_issues"]),
      "Source query errors: "+str(len(out["source_errors"])),"",
      "Candidate listings are NOT verified paid jobs or promises of compensation.",
      "No mining hardware, hashrate, miner consent, mining shares or wallet receipts are proved.",
      "Official Public Pool solo and PPLNS have DIFFERENT payout mechanisms; opt-in collaboration only.",
      ""]
    for item in out["candidates"][:20]:
        lines.append("- "+item["assigned_company_director"]+" to check "+
           item["title"]+" — "+item["original_url"]+" (sponsor and reward UNVERIFIED)")
    lines += ["", "## Two separate D-board assignments"]
    for fleet,queue in out["independent_director_review_queues"].items():
        lines.append("- "+fleet+": "+str(len(queue))+" leads needing independent sponsor verification; local D10 handles only genuine accepted unpaid claims")
    (OUT/"new-earning-lanes.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print("NEW_EARNING_LANES",json.dumps({"candidates":out["candidate_count"],"rejected":rejected if False else out["rejected_nonmatching_or_risky_issues"],"source_errors":len(out["source_errors"]),"verified_paid_receipts":0}))
