"""Read-only source-pinned minimal repro for a candidate $10 BTC/LN bug-report microbounty.

Tests the actual upstream Lateralus LQL query engine, without editing, bypassing,
or copying private code. Successful exit means the defect was actually reproduced,
NOT that a bounty was won or that money was received.
"""
from __future__ import annotations
import importlib.util
import json
import sys
import urllib.request
from pathlib import Path
from tempfile import TemporaryDirectory

UPSTREAM_SHA = "d078809df3f5db544b7efa7b0979c7a43ebb25e6"
UPSTREAM_URL = (
    "https://raw.githubusercontent.com/bad-antics/lateralus-lang/"
    + UPSTREAM_SHA + "/lateralus_lang/query_engine.py"
)

def main() -> None:
    with urllib.request.urlopen(UPSTREAM_URL, timeout=25) as response:
        source = response.read()
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "query_engine.py"
        path.write_bytes(source)
        spec = importlib.util.spec_from_file_location("ltl_quoted_boolean_test", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        try:
            users = [
                {"status": "Research AND Development", "id": 1},
                {"status": "Operations", "id": 2},
            ]
            # SQL string literals can contain AND / OR without being boolean clauses.
            query = "SELECT status FROM users WHERE status == 'Research AND Development'"
            exact_match = [{"status": "Research AND Development"}]
            direct = module.Query().from_(users).where(
                lambda item: item["status"] == "Research AND Development"
            ).select("status").execute()
            observed = module.lql(query, {"users": users})
            report = {
                "source_commit": UPSTREAM_SHA,
                "source_url": UPSTREAM_URL,
                "query": query,
                "direct_query": direct,
                "lql_actual": observed,
                "expected": exact_match,
                "bug_reproduced": direct == exact_match and observed != exact_match,
                "payment": "NOT_CLAIMED_OR_VERIFIED",
            }
            print(json.dumps(report, indent=2))
            if direct != exact_match:
                raise AssertionError("Control query failed; reproduction is inconclusive")
            if observed == exact_match:
                raise AssertionError("No bug at pinned upstream source; do not report")
            print("BUG_REPRODUCED: quoted AND text is split as a boolean keyword")
        finally:
            sys.modules.pop(spec.name, None)

if __name__ == "__main__":
    main()
