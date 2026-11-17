"""UnitPair QA: exact BTC/satoshi pair checking for educational copy.
18 Nov 2026 Kampala. Proposed service: audit up to 30 explicitly supplied
BTC/satoshi pairs in a public guide for 10,000 sats, subject to buyer agreement.
Market: BitcoinTalk Services educational publishers and GitHub docs sponsors.
No verified buyer, fee acceptance, region eligibility or payer mainnet support.
This is unit arithmetic, not accounting, tax, pricing or payment verification.

Alternatives: Python Decimal https://docs.python.org/3/library/decimal.html
and Bitcoin Core amount constants:
https://github.com/bitcoin/bitcoin/blob/master/src/consensus/amount.h
This constrained editor-facing checker rejects ambiguous formatting instead
of rounding. No novelty claim; ordinary exact calculators are alternatives.
No wallet, network, floating point, private data or transaction execution.
"""
import re,sys,unittest,json
def check(btc,sats):
    if not isinstance(btc,str) or not re.fullmatch(r"(0|[1-9][0-9]{0,7})(\.[0-9]{1,8})?",btc):
        raise ValueError("BTC requires plain nonnegative decimal text, at most 8 decimals")
    if type(sats) is not int or sats<0: raise ValueError("sats requires nonnegative integer")
    whole,_,fraction=btc.partition(".")
    expected=int(whole)*100000000+int(fraction.ljust(8,"0"))
    if expected>2100000000000000 or sats>2100000000000000:
        raise ValueError("outside supported monetary range")
    return {"matches":expected==sats,"expected_sats":expected,
            "difference_sats":sats-expected,"payment_verified":False}

class Tests(unittest.TestCase):
    def test_one_sat(self): self.assertTrue(check("0.00000001",1)["matches"])
    def test_mismatch(self): self.assertEqual(check("0.001",10000)["difference_sats"],-90000)
    def test_zero(self): self.assertTrue(check("0",0)["matches"])
    def test_max(self): self.assertTrue(check("21000000",2100000000000000)["matches"])
    def test_bad_format(self):
        for v in ("1e-8","0.000000001","1,000","-1","NaN","01"," 1",1.0):
            with self.assertRaises(ValueError): check(v,0)
    def test_bool(self):
        with self.assertRaises(ValueError): check("1",True)
    def test_not_payment(self): self.assertFalse(check("1",100000000)["payment_verified"])

if __name__=="__main__":
    if sys.argv[1:]==["--test"]: unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv)==3: print(json.dumps(check(sys.argv[1],int(sys.argv[2])),indent=2))
    else: raise SystemExit("Use --test or BTC_TEXT SATS_INTEGER")
