"""Ten accountable coin-earning idea avenues per B role.

Evidence-first idea *assignment*, not ten autonomous model-generated thoughts,
a real buyer, payment, miner, or cryptocurrency transfer. A worker may use the
ten avenues to draft 10 original independent ideas and should be separately
graded on the actual model-generated response, not menu assignment.
"""
from __future__ import annotations
import hashlib
import json
import re

BANK=[
 ("Specific paid open-source bugfix","Fix a documented sponsored issue and submit passing tests","Software maintainer with confirmed bounty","Original maintainer must confirm reward remains funded and claimable","Check original issue, prior claims and acceptance requirements"),
 ("Paid documentation improvement","Deliver well-tested tutorials or API docs","Open-source sponsor or paying developer","Confirm actual contract/price and documented acceptance","Propose one focused documentation sample"),
 ("Spreadsheet cleanup microcontract","Deduplicate and reconcile sample spreadsheet rows","Business client or verified remote buyer","Verify client ownership, quote and pay-out method","Prepare anonymized sample transformation"),
 ("Public-data research memo","Source and summarize lawful public data for a buyer","Research sponsor or paid task platform","Check commercial request and source usage restrictions","Draft a referenced one-page sample"),
 ("API integration support","Implement/test one authorized API connector","Verified developer or startup","Establish written scope, acceptance test and coin settlement","Find issue specifying precise API behavior"),
 ("Accessibility testing service","Audit public website interface and deliver a bug list","Website owner purchasing QA","Verify owner authorization and fee before invasive tests","Prepare an example public accessibility checklist"),
 ("Unit-test and CI repair","Repair a test suite with reproducible failure","Software team offering scoped paid work","Confirm issue author controls payout and code contribution allowed","Draft an isolated reproducible failure case"),
 ("Data-label QA service","Check permitted annotation quality and deliver quality metrics","Authorized dataset owner","Confirm privacy rules, lawful data rights and payout","Build sample scoring checklist"),
 ("Public blockchain analysis","Produce accurate read-only on-chain dashboard or CSV","Authorized analytics customer","Verify scope and do not imply owner controls third-party wallet","Build a sample from public chain explorer data"),
 ("Legitimate crypto conference research","Compile sourced event/grant calendar for interested buyer","Event researcher or commissioned customer","Need a real commissioning client and eligibility","Deliver a sample verified event index"),
 ("Translation and localization work","Translate permitted text with bilingual quality review","Localization customer or open-source sponsor","Confirm language competence and explicit budget","Find a small funded localization issue"),
 ("Transcription correction service","Correct consented transcripts with timestamps","Media producer who supplies authorized recordings","Confirm recording consent and payout terms","Prepare a timestamped sample with supplied material"),
 ("Software QA bug reproduction","Write useful reproducible bug steps and patches","Software owner with authentic funded bug bounty","Respect scope and avoid unauthorized security probing","Locate one current bug-reproduction offer"),
 ("Sales data reporting","Produce an anonymized sales-analytics sample dashboard","Paying business with relevant permission","Confirm client authorization, source data rights and reward","Prepare a generic dashboard sample"),
 ("Website content maintenance","Update authorized content or markdown and pass review","Website maintainer hiring paid help","Confirm paid scope and access without soliciting credentials","Produce a sample content diff"),
 ("Structured market comparison","Compare current publicly listed prices with dated references","Buyer requesting market research","Confirm external sponsor and no prohibited scraping","Create a cited side-by-side table"),
 ("Permission-based paid AI evaluation","Test authorized model outputs for accuracy and report failures","AI model tester with budget","Confirm approved test data and genuinely payable program","Make a task-specific evaluation rubric"),
 ("Earned microservice subscription","Offer ongoing low-cost public-data reporting under contract","Direct client willing to subscribe","Requires genuine buyer and written recurring terms","Pitch a fixed weekly deliverable to consenting buyer"),
 ("Opt-in independent miner collaboration","Provide a volunteer miner accurate public BTC pool-address instructions","Mining operator volunteering owned hashrate","No miner is committed; solo or pooled shares give no guaranteed income","Verify pool mode and ask for explicit consent, never keys"),
 ("Voluntary agent contribution for useful research","Offer useful source-backed service to independent operator; invite tip only if wanted","Independent agent's authorized human/operator","No bot account or funding inferred; authentic consent required","Publish a precise sample deliverable on an allowed forum"),
 ("Open design/document asset commission","Produce editable, licensed digital design or technical template","Customer authorizing commission","Copyright, asset rights and fee must be verified","Create a small original template sample"),
 ("Cash-prize competition entry","Submit eligible original artifact to public prize contest","Verified competition sponsor","Confirm date, residency eligibility, payout network and award judging","Read current sponsor rules, identify one feasible deliverable"),
]
assert len(BANK)==22
FLEETS=("transferexperiment","BountyScoutAI")
def role_menu(fleet,role_id,parent,specialty):
    if fleet not in FLEETS or not role_id or not parent:
        raise ValueError("Fleet, worker and direct parent required")
    salt=int.from_bytes(hashlib.sha256((fleet+"/"+role_id).encode()).digest()[:8],"big")
    # 22 choices and a stride coprime to 22 give exactly 10 different
    # hypotheses without constructing any millions/billions of records.
    selected=[BANK[(salt+i*5)%len(BANK)] for i in range(10)]
    items=[]
    for i,(title,deliverable,payer,proof,step) in enumerate(selected,1):
        items.append({
            "number":i,"idea_title":title,
            "worker_specialty_context":str(specialty)[:100],
            "possible_deliverable":deliverable,
            "potential_payer_or_consenter_category":payer,
            "required_original_evidence":proof,
            "concrete_first_step":step,
            "estimated_reward":"unknown",
            "verified_payer":False,
            "verified_funding":False,
            "verified_contract":False,
            "verified_wallet_receipt":False,
            "requires_upfront_funds":False,
            "status":"BRAINSTORMING_PROPOSAL_NOT_AUTHENTICATED_JOB",
        })
    return {
        "fleet":fleet,"worker_id":role_id,"globally_unique_role_id":fleet+"/"+role_id,
        "parent_id":parent,
        "latest_owner_order":"OWNER-20261114-075553",
        "count":len(items),
        "candidate_ideas":items,
        "idea_origin":"DETERMINISTIC_MENU_NOT_MODEL_GENERATED",
        "actual_model_ideation":"NOT_YET_EVIDENCED",
        "actual_paid_work":"NOT_YET_EVIDENCED",
        "limitations":"10 different opportunity hypotheses assigned to an eligible role are NOT 10 real AI-generated ideas, paying clients, contracts, mining machines or earned crypto."
    }

LINE=re.compile(r"^\s*(?:[1-9]|10)[.)\:]\s*(\S.*)$")
def evaluate_generated_ten(text):
    lines=str(text or "").splitlines()
    found={}
    for raw in lines:
        m=LINE.match(raw.strip())
        if m:
            n=int(re.match(r"^\s*(\d+)",raw).group(1))
            proposal=m.group(1).strip()
            if 1<=n<=10 and n not in found and len(proposal)>=12:
                found[n]=proposal[:350]
    normalized={re.sub(r"\W+"," ",v.lower()).strip() for v in found.values()}
    good=(len(found)==10 and len(normalized)==10)
    return {
        "status":"TEN_MODEL_GENERATED_IDEAS_NEED_FACT_CHECK" if good else
                 "INCOMPLETE_OR_REPEATED_MODEL_IDEAS",
        "numbered_valid_unique_count":len(normalized),
        "has_all_ten_distinct_numbered_ideas":good,
        "model_generated_ideas":[{"number":n,"text":found[n]} for n in sorted(found)],
        "payer_verified_by_ideation":False,
        "income_verified_by_ideation":False,
        "next_step":"Independently check original source, payer/consent, eligibility, true acceptance and wallet network before any earnings claim."
    }

def self_test():
    all_ids=set()
    for fleet in FLEETS:
        for d in range(1,11):
            wid=f"D{d:02d}-M01-W01-S001-G001-H001"
            menu=role_menu(fleet,wid,wid.rsplit("-",1)[0],"QA and data")
            assert menu["count"]==10
            assert len(set(x["idea_title"] for x in menu["candidate_ideas"]))==10
            assert len(set(x["number"] for x in menu["candidate_ideas"]))==10
            assert menu["globally_unique_role_id"] not in all_ids
            all_ids.add(menu["globally_unique_role_id"])
    good="\n".join(f"{n}. A distinct authorized service option {n} with source verification" for n in range(1,11))
    assert evaluate_generated_ten(good)["has_all_ten_distinct_numbered_ideas"]
    assert not evaluate_generated_ten("1. Same idea\n2. Same idea")["has_all_ten_distinct_numbered_ideas"]
    assert not evaluate_generated_ten("")["has_all_ten_distinct_numbered_ideas"]
    return {"status":"PASS","roles_sampled":len(all_ids),"ten_distinct_menu_items_each":True,"generation_claimed":False}

if __name__=="__main__":
    print("TEN_IDEA_EXERCISE_SELFTEST",json.dumps(self_test()))
