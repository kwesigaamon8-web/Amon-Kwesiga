"""CSV Preview Guard: offline, non-mutating export preflight.
Service hypothesis (17 Nov 2026): one authorized CSV export review, <=10k rows,
proposed 15,000 sats, for BitcoinTalk Services software buyers or GitHub export
maintainers. No buyer, accepted price, eligibility or payout willingness verified.
BTC mainnet payment must be agreed separately; no alternative route assumed.

Alternatives: csvkit csvclean checks row structure:
https://csvkit.readthedocs.io/en/latest/changelog.html
OWASP describes spreadsheet formula interpretation risks:
https://community.owasp.org/attacks/CSV_Injection
This prototype reports coordinates without echoing cell contents, never opens
spreadsheets, executes formulas or rewrites data. Flagged negatives may be benign.
No claim of exhaustive detection or safe-to-open certification. A public report
must not include private data. Distinct from existing CSV conversion service.
"""
import csv, io, json, sys, unittest

def inspect(text):
    if not isinstance(text,str): raise ValueError("text required")
    issues=[]
    rows=0
    width=None
    try:
        for rows,row in enumerate(csv.reader(io.StringIO(text,newline=""),strict=True),1):
            if width is None: width=len(row)
            if len(row)!=width:
                issues.append({"record":rows,"kind":"width_mismatch"})
            for col,cell in enumerate(row,1):
                stripped=cell.lstrip(" \t\r\n\ufeff")
                if (stripped and stripped[0] in "=+-@＝＋－＠") or cell.startswith(("\t","\r","\n")):
                    issues.append({"record":rows,"column":col,"kind":"formula_like_prefix"})
    except csv.Error:
        return {"status":"PARSE_ERROR","records":rows,"issues":issues,"safe_to_open_verified":False}
    return {"status":"REVIEW_REQUIRED" if issues else "NO_FLAGS_IN_LIMITED_CHECK",
            "records":rows,"issues":issues,"safe_to_open_verified":False}

class Tests(unittest.TestCase):
    def test_benign(self):
        self.assertEqual(inspect("name,value\na,2\n")["issues"],[])
    def test_prefixes(self):
        self.assertEqual(len(inspect("=1,+2,-3,@x,＝1")["issues"]),5)
    def test_quoted(self):
        r=inspect('a,b\n"hello, world","=1"')
        self.assertEqual(r["issues"],[{"record":2,"column":2,"kind":"formula_like_prefix"}])
    def test_width(self):
        self.assertEqual(inspect("a,b\nx")["issues"][0]["kind"],"width_mismatch")
    def test_parse(self):
        self.assertEqual(inspect('"unterminated')["status"],"PARSE_ERROR")
    def test_no_data_leak(self):
        r=inspect("  =PRIVATE")
        self.assertNotIn("PRIVATE",json.dumps(r))
        self.assertFalse(r["safe_to_open_verified"])

if __name__=="__main__":
    if sys.argv[1:]==["--test"]: unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv)==2:
        with open(sys.argv[1],encoding="utf-8-sig",newline="") as f:
            print(json.dumps(inspect(f.read()),indent=2))
    else: raise SystemExit("Use --test or an authorized CSV path")
