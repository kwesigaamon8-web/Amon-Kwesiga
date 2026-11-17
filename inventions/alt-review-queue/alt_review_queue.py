"""Alt Review Queue: offline HTML image inventory; not an accessibility audit.
17 November 2026 service hypothesis: review up to 20 images in one public
educational guide and propose contextual alt text after viewing authorized
images and surrounding prose. Proposed fee 20,000 sats, not accepted.
Market: BitcoinTalk Services publishers and GitHub documentation sponsors.
No verified buyer, eligibility or BTC-mainnet payout willingness established.

W3C context guidance: https://www.w3.org/WAI/tutorials/images/decision-tree/
Competitor: https://www.deque.com/axe/ offers broader automated/manual testing.
Differentiator is a bounded editorial handoff, not a replacement for axe,
a new standard, legal compliance certification or proof of demand.
The queue never infers that empty alt is wrong or nonempty alt is correct.
Only static img tags are inventoried; no rendering, network or script execution.
"""
from html.parser import HTMLParser
import json,sys,unittest

class Queue(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items=[]
    def handle_starttag(self,tag,attrs):
        if tag!="img": return
        alts=[value for name,value in attrs if name=="alt"]
        if len(alts)>1: state="DUPLICATE_ALT_REVIEW"
        elif not alts: state="MISSING_ALT_REVIEW"
        elif alts[0] is None: state="VALUELESS_ALT_REVIEW"
        elif not alts[0].strip(): state="EMPTY_ALT_CONTEXT_REVIEW"
        else: state="TEXT_PRESENT_CONTEXT_REVIEW"
        self.items.append({"image_index":len(self.items)+1,"line":self.getpos()[0],
                           "state":state,"appropriateness_verified":False})

def inventory(html):
    q=Queue()
    q.feed(html)
    q.close()
    return {"images":q.items,"rendered_page_checked":False,
            "accessibility_conformance_verified":False}

class Tests(unittest.TestCase):
    def test_states(self):
        r=inventory('<img><img alt=""><img alt="A chart">')["images"]
        self.assertEqual([x["state"] for x in r],["MISSING_ALT_REVIEW","EMPTY_ALT_CONTEXT_REVIEW","TEXT_PRESENT_CONTEXT_REVIEW"])
    def test_case_selfclosing(self):
        self.assertEqual(len(inventory('<IMG ALT="x"/>')["images"]),1)
    def test_duplicates(self):
        self.assertEqual(inventory('<img alt="x" alt="y">')["images"][0]["state"],"DUPLICATE_ALT_REVIEW")
    def test_no_execution(self):
        self.assertEqual(inventory('<script>var s="<img>";</script>')["images"],[])
    def test_no_raw_content(self):
        self.assertNotIn("PRIVATE",json.dumps(inventory('<img src="PRIVATE" alt="PRIVATE">')))
    def test_no_false_conformance(self):
        self.assertFalse(inventory("")["accessibility_conformance_verified"])

if __name__=="__main__":
    if sys.argv[1:]==["--test"]: unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv)==2:
        with open(sys.argv[1],encoding="utf-8") as f: print(json.dumps(inventory(f.read()),indent=2))
    else: raise SystemExit("Use --test or an authorized HTML path")
