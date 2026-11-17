"""ClaimSourceMap: offline editorial evidence checklist (not fact verification).

Validation: six local tests passed on 17 November 2026.
Prototype 17 November 2026. Service hypothesis: source-map QA for one public
Bitcoin educational guide, up to 20 author-selected claims; proposed 20,000 sats.
Market: BitcoinTalk Services guide publishers and GitHub documentation sponsors.
No verified buyer, accepted fee, regional eligibility or buyer payout willingness.
Only separately agreed BTC mainnet payout is eligible; no Lightning assumed.

Alternatives checked:
https://docs.vale.sh/ (prose linting)
https://www.zotero.org/support/creating_bibliographies (citation formatting)
This tool maps explicit claim IDs to source URLs and review dates. It does not
replace either, extract every claim, fetch links or verify truth. Distinct from
BriefGate (contract terms), HandoffDelta (file versions) and payment evidence.
Human source checking is the proposed paid deliverable. No novelty claim.

Run python claim_source_map.py --test, or pass a JSON file containing a claims
array and review_date (YYYY-MM-DD). Only use public/authorized material.
"""
import datetime as dt
import json
import sys
import unittest
from urllib.parse import urlsplit

def review(claims, review_date, max_age_days=30):
    today=dt.date.fromisoformat(review_date)
    if type(max_age_days) is not int or max_age_days < 0:
        raise ValueError("max_age_days must be a nonnegative integer")
    if not isinstance(claims,list): raise ValueError("claims must be a list")
    seen=set()
    findings=[]
    for claim in claims:
        if not isinstance(claim,dict): raise ValueError("each claim must be an object")
        cid=claim.get("id")
        if not isinstance(cid,str) or not cid.strip() or cid in seen:
            raise ValueError("claim IDs must be unique nonempty strings")
        seen.add(cid)
        gaps=[]
        if not isinstance(claim.get("text"),str) or not claim["text"].strip():
            gaps.append("missing_claim_text")
        sources=claim.get("sources",[])
        if not isinstance(sources,list): raise ValueError("sources must be a list")
        if not sources: gaps.append("no_sources")
        for i,source in enumerate(sources):
            if not isinstance(source,dict): raise ValueError("source must be an object")
            url=source.get("url","")
            try:
                p=urlsplit(url) if isinstance(url,str) else None
                valid=p and p.scheme=="https" and p.hostname and not p.username and not p.password
            except ValueError: valid=False
            if not valid: gaps.append("source_%d_invalid_https_url"%i)
            try:
                checked=dt.date.fromisoformat(source.get("checked_on",""))
                age=(today-checked).days
                if age<0: gaps.append("source_%d_future_review"%i)
                elif age>max_age_days: gaps.append("source_%d_stale_review"%i)
            except (ValueError,TypeError): gaps.append("source_%d_missing_or_invalid_review_date"%i)
        findings.append({"id":cid,"gaps":gaps,"truth_verified":False})
    return {"claims":findings,"coverage_scope":"author-selected claims only",
            "all_claims_identified":False,"buyer_accepted":False,"payment_verified":False}

class Tests(unittest.TestCase):
    def test_complete_stays_unverified(self):
        r=review([{"id":"c1","text":"Example","sources":[{"url":"https://example.org","checked_on":"2026-11-17"}]}],"2026-11-17")
        self.assertEqual(r["claims"][0]["gaps"],[])
        self.assertFalse(r["claims"][0]["truth_verified"])
    def test_missing(self):
        self.assertEqual(review([{"id":"a"}],"2026-11-17")["claims"][0]["gaps"],["missing_claim_text","no_sources"])
    def test_stale_future(self):
        r=review([{"id":"a","text":"x","sources":[{"url":"https://example.org","checked_on":"2026-01-01"},{"url":"https://example.org","checked_on":"2027-01-01"}]}],"2026-11-17")
        self.assertEqual(r["claims"][0]["gaps"],["source_0_stale_review","source_1_future_review"])
    def test_duplicate(self):
        with self.assertRaises(ValueError): review([{"id":"a"},{"id":"a"}],"2026-11-17")
    def test_url_and_date(self):
        r=review([{"id":"a","text":"x","sources":[{"url":"javascript:alert(1)"}]}],"2026-11-17")
        self.assertEqual(len(r["claims"][0]["gaps"]),2)
    def test_empty_is_not_coverage(self):
        self.assertFalse(review([],"2026-11-17")["all_claims_identified"])

if __name__=="__main__":
    if sys.argv[1:]==["--test"]: unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv)==2:
        with open(sys.argv[1],encoding="utf-8") as f: data=json.load(f)
        print(json.dumps(review(data["claims"],data["review_date"]),indent=2))
    else: raise SystemExit("Use --test or path to public claims JSON")
