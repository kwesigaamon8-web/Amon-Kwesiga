"""Generate and regression-test an original Lateralus LQL parser patch.

Fetches a pinned public upstream revision; no external repository writes.
Maintainer acceptance and Bitcoin payment are NOT implied by a passing CI job.
"""
from __future__ import annotations
import difflib, hashlib, json, os, subprocess, sys, tempfile, urllib.request
from pathlib import Path

REV = "d078809df3f5db544b7efa7b0979c7a43ebb25e6"
URL = "https://raw.githubusercontent.com/bad-antics/lateralus-lang/" + REV + "/lateralus_lang/query_engine.py"
OLD = """    # Try AND / OR splitting (simple, not nested)
    if " AND " in expr.upper():
        parts = re.split(r'\\bAND\\b', expr, flags=re.IGNORECASE)
        preds = [_parse_condition(p) for p in parts]
        return lambda r, ps=preds: all(p(r) for p in ps)

    if " OR " in expr.upper():
        parts = re.split(r'\\bOR\\b', expr, flags=re.IGNORECASE)
        preds = [_parse_condition(p) for p in parts]
        return lambda r, ps=preds: any(p(r) for p in ps)
"""
NEW = """    # Respect quoted literals and nested groups; AND binds more tightly than OR.
    pieces = _split_outside_literals(expr, "OR")
    if len(pieces) > 1:
        preds = [_parse_condition(p) for p in pieces]
        return lambda row, ps=preds: any(p(row) for p in ps)

    pieces = _split_outside_literals(expr, "AND")
    if len(pieces) > 1:
        preds = [_parse_condition(p) for p in pieces]
        return lambda row, ps=preds: all(p(row) for p in ps)

    if _is_one_parenthesized_group(expr):
        return _parse_condition(expr[1:-1])
"""
HELPERS = '''def _split_outside_literals(expr: str, word: str) -> list[str]:
    """Split only on top-level standalone boolean words, never inside strings."""
    parts = []
    quote = None
    escape = False
    depth = 0
    start = i = 0
    k = len(word)
    while i < len(expr):
        char = expr[i]
        if quote:
            if escape:
                escape = False
            elif char == "\\\\":
                escape = True
            elif char == quote:
                quote = None
        elif char in ("'", '"'):
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise QueryError("Unmatched closing parenthesis in WHERE")
        elif (depth == 0 and expr[i:i+k].upper() == word
              and (i == 0 or expr[i-1].isspace())
              and (i+k == len(expr) or expr[i+k].isspace())):
            before = expr[start:i].strip()
            if not before:
                raise QueryError("Missing condition before " + word)
            parts.append(before)
            start = i + k
            i = start
            continue
        i += 1
    if quote or depth:
        raise QueryError("Unclosed quote or parentheses in WHERE")
    if parts:
        last = expr[start:].strip()
        if not last:
            raise QueryError("Missing condition after " + word)
        parts.append(last)
        return parts
    return [expr]


def _is_one_parenthesized_group(expr: str) -> bool:
    if len(expr) < 2 or not expr.startswith("(") or not expr.endswith(")"):
        return False
    quote = None
    escape = False
    depth = 0
    for i, char in enumerate(expr):
        if quote:
            if escape:
                escape = False
            elif char == "\\\\":
                escape = True
            elif char == quote:
                quote = None
        elif char in ("'", '"'):
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0 and i != len(expr) - 1:
                return False
    return depth == 0 and quote is None


'''
TESTS = '''import unittest
from lateralus_lang.query_engine import Query, QueryError, lql

class TestQuotedConditions(unittest.TestCase):
    def setUp(self):
        self.users = [
            {"id":1, "status":"Research AND Development", "active":True},
            {"id":2, "status":"Sales OR Support", "active":False},
            {"id":3, "status":"A", "active":True},
            {"id":4, "status":"B", "active":False},
        ]
    def query(self, where):
        return lql("SELECT id FROM users WHERE " + where, {"users":self.users})
    def test_literal_and(self):
        self.assertEqual(self.query("status == 'Research AND Development'"), [{"id":1}])
    def test_literal_or(self):
        self.assertEqual(self.query('status == "Sales OR Support"'), [{"id":2}])
    def test_real_and(self):
        self.assertEqual(self.query("status == 'Research AND Development' AND active == true"), [{"id":1}])
    def test_real_or(self):
        self.assertEqual(self.query("status == 'Research AND Development' OR status == 'Sales OR Support'"), [{"id":1},{"id":2}])
    def test_precedence(self):
        self.assertEqual(self.query("status == 'A' OR status == 'B' AND active == true"), [{"id":3}])
    def test_grouping(self):
        self.assertEqual(self.query("(status == 'A' OR status == 'B') AND active == false"), [{"id":4}])
    def test_nested_grouping(self):
        self.assertEqual(self.query("((status == 'A' OR status == 'B') AND active == false)"), [{"id":4}])
    def test_direct_python_query(self):
        self.assertEqual(Query().from_(self.users).where(lambda x:x["id"]==1).select("id").execute(), [{"id":1}])
    def test_unterminated_quote(self):
        with self.assertRaises(QueryError):
            self.query("status == 'A OR B")

if __name__ == "__main__":
    unittest.main(verbosity=2)
'''

def build(source):
    marker = "def _parse_condition(expr: str) -> Predicate:"
    if source.count(marker) != 1 or source.count(OLD) != 1:
        raise AssertionError("Pinned upstream version changed; refusing imprecise patch")
    return source.replace(marker, HELPERS + marker).replace(OLD, NEW)

def main():
    request = urllib.request.Request(URL, headers={"User-Agent":"LQL-original-bugfix-testing/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        source = response.read(150000).decode("utf-8")
    patched = build(source)
    root = Path("lateralus-fix-evidence")
    root.mkdir(exist_ok=True)
    diff = "".join(difflib.unified_diff(
        source.splitlines(keepends=True), patched.splitlines(keepends=True),
        fromfile="a/lateralus_lang/query_engine.py",
        tofile="b/lateralus_lang/query_engine.py"))
    (root/"quoted_boolean_fix.patch").write_text(diff, encoding="utf-8")
    with tempfile.TemporaryDirectory() as dirname:
        pkg = Path(dirname)/"lateralus_lang"
        pkg.mkdir()
        (pkg/"__init__.py").write_text("")
        (pkg/"query_engine.py").write_text(patched, encoding="utf-8")
        (Path(dirname)/"test_patch.py").write_text(TESTS, encoding="utf-8")
        env = dict(os.environ, PYTHONPATH=dirname)
        run = subprocess.run([sys.executable, "-m", "unittest", "discover",
            "-s", dirname, "-p", "test_patch.py", "-v"],
            capture_output=True, text=True, timeout=25, env=env)
        (root/"unit_test_results.txt").write_text(run.stdout+run.stderr, encoding="utf-8")
        result = {
            "upstream_commit":REV, "source_url":URL,
            "source_sha256":hashlib.sha256(source.encode()).hexdigest(),
            "patch_sha256":hashlib.sha256(diff.encode()).hexdigest(),
            "patch_generated":bool(diff),
            "unit_tests_passed":run.returncode == 0,
            "unit_test_exit_code":run.returncode,
            "third_party_submission_verified":False,
            "maintainer_acceptance_verified":False,
            "crypto_payment_verified":False,
        }
        (root/"evidence.json").write_text(json.dumps(result,indent=2)+"\n", encoding="utf-8")
        print("LATERALUS_ORIGINAL_PATCH",json.dumps(result))
        if run.returncode != 0:
            raise SystemExit("Regression tests failed; inspect unit_test_results.txt")

if __name__=="__main__":
    main()
