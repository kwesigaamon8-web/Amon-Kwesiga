"""JSON Key Collision Review — offline interoperability preflight.
18 Nov 2026 Kampala. Proposed 15,000-sat review of one authorized JSON export
(up to 1 MB), including duplicate-member report and original regression fixture.
Market: GitHub API maintainers and BitcoinTalk Services integration buyers.
No funded buyer, accepted fee, regional eligibility or mainnet payout confirmed.
No data changes, external requests, wallet operations or payment inference.

Problem: RFC8259 section4 recommends unique object names; duplicate handling
varies between consumers: https://www.rfc-editor.org/rfc/rfc8259#section-4
Alternative: jq is a broader transformation tool https://jqlang.org/manual/ .
This narrow preflight preserves pairs before any dictionary collapse. Not a
schema/security certification or novel algorithm. Report names can be sensitive:
only publish reports for public/authorized data. Unlike existing CSV converter,
this identifies ambiguity in original JSON, including nested objects.
"""
import json,sys,unittest
class Pairs(list): pass

def inspect(text):
    if not isinstance(text,str) or len(text.encode("utf-8"))>1000000:
        raise ValueError("UTF-8 text up to 1 MB required")
    def reject(x): raise ValueError("nonstandard numeric constant")
    root=json.loads(text,object_pairs_hook=Pairs,parse_constant=reject)
    findings=[]
    object_number=0
    def walk(value,depth=0):
        nonlocal object_number
        if depth>100: raise ValueError("nesting limit exceeded")
        if isinstance(value,Pairs):
            object_number+=1
            number=object_number
            counts={}
            for name,child in value: counts[name]=counts.get(name,0)+1
            for name,count in counts.items():
                if count>1: findings.append({"object_index":number,"name":name,"occurrences":count})
            for _,child in value: walk(child,depth+1)
        elif isinstance(value,list):
            for child in value: walk(child,depth+1)
    walk(root)
    return {"duplicate_members":findings,"schema_verified":False,
            "status":"REVIEW_REQUIRED" if findings else "NO_DUPLICATE_NAMES_FOUND"}

class Tests(unittest.TestCase):
    def test_root(self):
        self.assertEqual(inspect('{"x":1,"x":2}')["duplicate_members"][0]["occurrences"],2)
    def test_nested_array(self):
        self.assertEqual(inspect('[{"a":{"x":0,"x":1}}]')["duplicate_members"][0]["object_index"],2)
    def test_separate_objects(self):
        self.assertEqual(inspect('[{"x":1},{"x":2}]')["duplicate_members"],[])
    def test_escaped_equal(self):
        self.assertEqual(len(inspect('{"a":1,"\\u0061":2}')["duplicate_members"]),1)
    def test_invalid(self):
        for x in ('{"a":','NaN','Infinity'):
            with self.assertRaises(ValueError): inspect(x)
    def test_empty_object_array(self):
        self.assertEqual(inspect('[{},[]]')["duplicate_members"],[])
    def test_limit(self):
        with self.assertRaises(ValueError): inspect(" "*1000001)

if __name__=="__main__":
    if sys.argv[1:]==["--test"]: unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv)==2:
        with open(sys.argv[1],encoding="utf-8") as f: print(json.dumps(inspect(f.read(1000001)),indent=2))
    else: raise SystemExit("Use --test or authorized JSON path")
