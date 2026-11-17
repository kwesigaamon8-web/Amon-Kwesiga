"""Synthetic-only regression tests. Does not need Odoo or real customer data."""
from __future__ import annotations
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

P=Path(__file__).with_name("duplicate_order_ids.py")
spec=importlib.util.spec_from_file_location("original_duplicate_checker",P)
mod=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

class DuplicateOrderTests(unittest.TestCase):
    def input_file(self,text):
        td=tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        p=Path(td.name)/"orders.csv"
        p.write_text(text,encoding="utf-8")
        return p

    def test_returns_all_row_positions_including_first(self):
        path=self.input_file("external_order_id,amount\nA01,30\nB10,20\nA01,15\nB10,1\n")
        data=mod.find_duplicates(path)
        self.assertEqual(data["duplicate_ids"],{"A01":[2,4],"B10":[3,5]})
        self.assertEqual(data["duplicate_id_count"],2)
        self.assertEqual(data["duplicate_row_count"],4)

    def test_source_file_not_modified(self):
        path=self.input_file("external_order_id,value\nx,1\nx,2\n")
        before=hashlib.sha256(path.read_bytes()).digest()
        mod.find_duplicates(path)
        self.assertEqual(hashlib.sha256(path.read_bytes()).digest(),before)

    def test_missing_required_column_rejected(self):
        path=self.input_file("order_id,amount\nA,2\n")
        with self.assertRaisesRegex(ValueError,"external_order_id"):
            mod.find_duplicates(path)

    def test_empty_values_are_not_duplicates(self):
        path=self.input_file("external_order_id,amount\n,1\n,2\nX,4\n")
        self.assertEqual(mod.find_duplicates(path)["duplicate_ids"],{})

    def test_whitespace_normalization(self):
        path=self.input_file("external_order_id,amount\n ABC ,1\nABC,2\n")
        self.assertEqual(mod.find_duplicates(path)["duplicate_ids"],{"ABC":[2,3]})

    def test_unicode_and_quoted_commas(self):
        path=self.input_file("external_order_id,comment\nORD-é,\"a,b\"\nORD-é,none\n")
        self.assertEqual(mod.find_duplicates(path)["duplicate_ids"],{"ORD-é":[2,3]})

    def test_utf8_bom(self):
        path=self.input_file("\ufeffexternal_order_id,amount\nA,1\nA,2\n")
        self.assertEqual(mod.find_duplicates(path)["duplicate_ids"],{"A":[2,3]})

    def test_no_duplicates(self):
        path=self.input_file("external_order_id,amount\nA,1\nB,2\n")
        self.assertEqual(mod.find_duplicates(path)["duplicate_id_count"],0)

if __name__=="__main__":
    unittest.main(verbosity=2)
