"""Test Enigma 7x8 system isolation; mocks do not represent actual AI calls."""
import json
import tempfile
import unittest
from pathlib import Path
from enigma_seven_systems import SYSTEMS,ROLES,roles_for,run_system
class SevenPodTests(unittest.TestCase):
    def test_identity_count_and_mailbox_separation(self):
        self.assertEqual(len(SYSTEMS),7)
        self.assertEqual(len(ROLES),8)
        agents=[a for id_,*rest in SYSTEMS for a in roles_for(id_)]
        self.assertEqual(len(agents),56)
        self.assertEqual(len({x["agent_id"] for x in agents}),56)
        self.assertEqual(len({x["google_account_alias"] for x in agents}),7)
        self.assertTrue(all("@" not in json.dumps(x) for x in agents))
        self.assertTrue(all(x["emails_sent"]==0 for x in agents))
        self.assertTrue(all(not x["model_call_completed"] for x in agents))
        with self.assertRaises(ValueError):
            list(roles_for("G08"))
    def test_separate_calls_per_role(self):
        prompts=[]
        def fake(p,**kwargs):
            prompts.append(p)
            return [{"generated_text":"Check local facts; run tests; record gaps."}]
        with tempfile.TemporaryDirectory() as folder:
            for system,*_ in SYSTEMS:
                summary=run_system(system,True,fake,Path(folder)/system)
                self.assertEqual(summary["verified_model_calls_in_this_run"],8)
                self.assertEqual(summary["emails_sent"],0)
                self.assertFalse(summary["github_access_to_google_mailboxes"])
            self.assertEqual(len(prompts),56)
            self.assertEqual(len(set(prompts)),56)
    def test_do_not_claim_inference_without_actual_answer(self):
        with tempfile.TemporaryDirectory() as folder:
            s=run_system("G01",False,output_dir=folder)
            self.assertEqual(s["verified_model_calls_in_this_run"],0)
            self.assertEqual(len(list(Path(folder).glob("ENIGMA-*.json"))),8)
        with tempfile.TemporaryDirectory() as folder:
            s=run_system("G02",True,lambda p,**k:[{"generated_text":""}],folder)
            self.assertEqual(s["verified_model_calls_in_this_run"],0)
        with tempfile.TemporaryDirectory() as folder:
            def broken(*args,**kwargs):raise RuntimeError("provider failed")
            s=run_system("G03",True,broken,folder)
            self.assertEqual(s["verified_model_calls_in_this_run"],0)
            packet=json.loads((Path(folder)/"ENIGMA-G03-R01.json").read_text())
            self.assertEqual(packet["model_inference_status"],"MODEL_ERROR_RuntimeError")
if __name__=="__main__":
    unittest.main()
