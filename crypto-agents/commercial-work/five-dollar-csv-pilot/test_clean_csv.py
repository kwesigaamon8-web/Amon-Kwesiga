"""Original regression suite for bounded, zero-dependency five-dollar CSV pilot."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("pilot_clean_csv", HERE / "clean_csv.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class CleanupContract(unittest.TestCase):
    def test_deduplicate_after_trim_preserves_order(self):
        output, s = mod.clean(b"ref, amount\n A, 001.20 \nA,001.20\nB, 2.00\n")
        self.assertEqual(output, "ref,amount\nA,001.20\nB,2.00\n")
        self.assertEqual((s["source_rows"], s["clean_rows"], s["exact_duplicate_rows_removed"]), (3, 2, 1))

    def test_utf8_bom_and_unicode(self):
        cleaned, s = mod.clean("\ufeffid,label\n01, Kampala café 🇺🇬 \n".encode("utf-8"))
        self.assertEqual(cleaned, "id,label\n01,Kampala café 🇺🇬\n")
        self.assertEqual(s["columns"], 2)

    def test_blank_row_removed_but_empty_cells_retained(self):
        cleaned, s = mod.clean(b"id,note\n1,\n\n  ,  \n2,done\n")
        self.assertEqual(cleaned, "id,note\n1,\n2,done\n")
        self.assertEqual(s["blank_rows_removed"], 2)

    def test_exact_rows_not_key_only(self):
        cleaned, s = mod.clean(b"ref,amount\nINV-1,10\nINV-1,20\n")
        self.assertEqual(s["clean_rows"], 2)
        self.assertIn("INV-1,20", cleaned)

    def test_quotes_embedded_newline_and_utf8(self):
        cleaned, s = mod.clean('id,note\n1,"He said ""yes"""\n2,"line1\nline2"\n'.encode())
        self.assertEqual(s["clean_rows"], 2)
        self.assertIn('"He said ""yes"""', cleaned)
        self.assertIn('"line1\nline2"', cleaned)

    def test_invalid_records_fail_closed(self):
        samples = [
            b"",
            b"col,col\na,b\n",
            b"col, col \na,b\n",
            b",other\na,b\n",
            b"a,b\n1\n",
            b"a,b\n1,2,3\n",
            b'a,b\n1,"unterminated\n',
            b"a,b\n1,\xff\n",
            b"a,b\n1,\x00\n",
            b"a," + b"c," * 20 + b"end\n",
        ]
        for input_bytes in samples:
            with self.subTest(input_bytes=input_bytes[:25]):
                with self.assertRaises(mod.InvalidCSV):
                    mod.clean(input_bytes)

    def test_100_records_maximum(self):
        one_hundred = b"id\n" + b"1\n" * 100
        clean, s = mod.clean(one_hundred)
        self.assertEqual(s["source_rows"], 100)
        with self.assertRaises(mod.InvalidCSV):
            mod.clean(one_hundred + b"2\n")

    def test_256_kib_limit(self):
        with self.assertRaises(mod.InvalidCSV):
            mod.clean(b"x" * (256 * 1024 + 1))

    def test_spreadsheet_formula_risks_flagged_without_running(self):
        output, s = mod.clean(b"a,b\n=2+2,-33.00\n+CMD,@cmd\n")
        self.assertEqual(s["formula_like_cells_not_evaluated"], 3)
        self.assertIn("=2+2", output)

    def test_readonly_source_and_no_overwrite_in_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            src, clean, report = (directory / x for x in ("input.csv", "clean.csv", "quality.json"))
            original = b"id,amount\na,10\na,10\n"
            src.write_bytes(original)
            args = [sys.executable, str(HERE / "clean_csv.py"), str(src),
                    "--clean", str(clean), "--report", str(report)]
            completed = subprocess.run(args, text=True, capture_output=True, timeout=10)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(src.read_bytes(), original)
            self.assertEqual(clean.read_text(), "id,amount\na,10\n")
            self.assertEqual(json.loads(report.read_text())["exact_duplicate_rows_removed"], 1)
            blocked = subprocess.run(args, text=True, capture_output=True, timeout=10)
            self.assertNotEqual(blocked.returncode, 0)
            self.assertIn("already exist", blocked.stderr)

    def test_no_side_effects_when_malformed_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, out, report = root / "input.csv", root / "clean.csv", root / "report.json"
            src.write_bytes(b"r,amt\n1,2,3")
            cmd = [sys.executable, str(HERE / "clean_csv.py"), str(src),
                   "--clean", str(out), "--report", str(report)]
            p = subprocess.run(cmd, text=True, capture_output=True, timeout=10)
            self.assertNotEqual(p.returncode, 0)
            self.assertFalse(out.exists())
            self.assertFalse(report.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
