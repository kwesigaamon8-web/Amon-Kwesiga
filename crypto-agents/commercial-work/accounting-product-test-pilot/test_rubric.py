"""Synthetic-only independent regression tests for bookkeeping test pilot."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().with_name("rubric.py")
spec=importlib.util.spec_from_file_location("bookkeeping_platform_rubric",SCRIPT)
rubric=importlib.util.module_from_spec(spec)
spec.loader.exec_module(rubric)

class RubricTests(unittest.TestCase):
    def test_36_platforms_generate_180_unscored_tasks(self):
        rows=rubric.init_rows([f"UNASSIGNED_PROVIDER_{i:02d}" for i in range(1,37)])
        self.assertEqual(len(rows),180)
        self.assertTrue(rubric.validate_rows(rows)["valid"])
        self.assertEqual(rubric.validate_rows(rows)["platforms_actually_completed"],0)
        self.assertTrue(all(r["score_1_to_5"]=="" and not r["evidence_screenshot"] for r in rows))

    def test_all_five_tasks_and_no_real_bank_records(self):
        rows=rubric.init_rows(["FAKE_PRODUCT"])
        self.assertEqual([r["task"] for r in rows],[t[1] for t in rubric.TASKS])
        self.assertTrue(all(r["test_data_class"]=="SYNTHETIC_DATA_ONLY" for r in rows))

    def test_roundtrip_read_write_valid(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"rubric.csv"
            rows=rubric.init_rows(["TEST_ONLY"])
            rubric.write_csv(rows,path)
            self.assertEqual(rows,rubric.read_csv(path))
            self.assertTrue(rubric.validate_rows(rubric.read_csv(path))["valid"])

    def test_refuses_overwrite_to_preserve_customer_data(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"rubric.csv"
            rubric.write_csv(rubric.init_rows(["ONE"]),path)
            with self.assertRaises(FileExistsError):
                rubric.write_csv(rubric.init_rows(["TWO"]),path)

    def test_completed_task_requires_proof_and_real_date(self):
        r=rubric.init_rows(["FAKE"])
        r[0]["test_status"]="COMPLETED"
        bad=rubric.validate_rows(r)
        self.assertFalse(bad["valid"])
        self.assertIn("evidence_screenshot"," ".join(bad["errors"]))
        r[0].update({"test_date":"2026-11-17","minutes_elapsed":"8.5","score_1_to_5":"4",
                     "observed_behavior":"Synthetic demonstration only",
                     "evidence_screenshot":"synthetic-example-only.png"})
        self.assertTrue(rubric.validate_rows(r)["valid"])
        self.assertEqual(rubric.validate_rows(r)["platforms_actually_completed"],0)

    def test_invalid_score_rejected(self):
        r=rubric.init_rows(["FAKE"])
        r[0]["score_1_to_5"]="10"
        self.assertFalse(rubric.validate_rows(r)["valid"])

    def test_unfinished_rows_cannot_claim_screenshots(self):
        r=rubric.init_rows(["FAKE"])
        r[0]["evidence_screenshot"]="madeup.png"
        self.assertFalse(rubric.validate_rows(r)["valid"])

    def test_duplicate_and_missing_task_rejected(self):
        r=rubric.init_rows(["FAKE"])
        r[0]=dict(r[1])
        self.assertFalse(rubric.validate_rows(r)["valid"])

    def test_excessive_elapsed_time_rejected(self):
        r=rubric.init_rows(["FAKE"])
        r[0]["minutes_elapsed"]="-1"
        self.assertFalse(rubric.validate_rows(r)["valid"])

    def test_duplicate_provider_names_rejected(self):
        with self.assertRaises(ValueError):
            rubric.init_rows(["A","A"])

if __name__=="__main__":
    unittest.main(verbosity=2)
