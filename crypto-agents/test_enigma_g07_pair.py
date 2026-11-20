"""Offline functional regression tests, never claimed as actual live model runs."""
import json
import tempfile
import unittest
from pathlib import Path
from enigma_g07_pair import AGENTS,RULES,execute,moltbook_status,public_evidence

def fake_evidence(url,token=None):
    if "worldbank" in url:return [[],[{"date":"2024","value":9}]]
    return [{"title":"A public example"}]
class PairTests(unittest.TestCase):
    def test_only_one_google_slot_with_two_unique_agent_identities(self):
        self.assertEqual(len(AGENTS),2)
        self.assertNotEqual(AGENTS["A"]["id"],AGENTS["B"]["id"])
        self.assertNotEqual(AGENTS["A"]["proposed_moltbook_name"],AGENTS["B"]["proposed_moltbook_name"])
        self.assertTrue(all("MOLTBOOK_ENIGMA_G07" in a["secret_name"] for a in AGENTS.values()))
        self.assertFalse(any("send" in r.lower() and "no" not in r.lower() for r in RULES))
    def test_two_independent_model_executions_with_honest_evidence(self):
        calls=[]
        def fake_model(prompt,**kwargs):
            calls.append(prompt)
            return [{"generated_text":"Check the evidence first, then run a user acceptance test."}]
        with tempfile.TemporaryDirectory() as td:
            a=execute("A",model=fake_model,evidence_fetcher=fake_evidence,output_dir=td)
            b=execute("B",model=fake_model,evidence_fetcher=fake_evidence,output_dir=td)
            self.assertEqual(len(calls),2)
            self.assertNotEqual(calls[0],calls[1])
            for doc in [a,b]:
                self.assertTrue(doc["actual_model_call_completed"])
                self.assertEqual(doc["gmail_read_in_run"],False)
                self.assertEqual(doc["emails_sent"],0)
                self.assertEqual(doc["accounts_registered"],0)
                self.assertFalse(doc["moltbook_connection"]["verified"])
                self.assertTrue((Path(td)/(doc["agent_id"]+".json")).exists())
    def test_failed_inference_is_not_counted(self):
        with tempfile.TemporaryDirectory() as td:
            fail=execute("A",model=lambda *a,**k: [{"generated_text":""}],
                        evidence_fetcher=fake_evidence,output_dir=td)
            self.assertFalse(fail["actual_model_call_completed"])
            self.assertEqual(fail["model_inference_status"],"MODEL_ERROR_ValueError")
    def test_external_account_status_requires_actual_token_and_matching_identity(self):
        self.assertEqual(moltbook_status("A")["status"],"NO_ACCOUNT_CREDENTIAL_CONFIGURED")
        verified=moltbook_status("A",token="dummy",fetcher=lambda url,token:{"agent":{"name":AGENTS["A"]["proposed_moltbook_name"]}})
        self.assertTrue(verified["verified"])
        incorrect=moltbook_status("A",token="dummy",fetcher=lambda url,token:{"agent":{"name":"someoneelse"}})
        self.assertFalse(incorrect["verified"])
    def test_primary_sources_are_read_only_bounded_and_error_tolerant(self):
        evidence,errors=public_evidence("A",fake_evidence)
        self.assertEqual(len(evidence),2)
        self.assertEqual(len(errors),0)
        self.assertTrue(all("https://" in r["url"] for r in evidence))
        evidence,errors=public_evidence("B",lambda url: (_ for _ in ()).throw(ValueError("API failed")))
        self.assertEqual(len(evidence),0)
        self.assertEqual(len(errors),2)
if __name__=="__main__":
    unittest.main()
