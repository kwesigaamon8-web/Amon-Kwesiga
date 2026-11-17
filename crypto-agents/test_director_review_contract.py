"""Offline regression: scheduled B1/B2 consolidation must accept current anonymous owner brief.

No network, paid API, personal records, or model invocation. Generates only synthetic
empty worker reports and verifies the director review no longer crashes.
"""
from __future__ import annotations
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix="chief-d-director-contract-") as temp:
    root=Path(temp)
    (root/"crypto-agents").mkdir(parents=True)
    (root/"combined-reports").mkdir()
    for name in ("owner_brief.json", "roles.json", "company_hierarchy.json"):
        shutil.copy2(BASE/name, root/"crypto-agents"/name)
    (root/"summary.json").write_text(
        json.dumps({"qualified_unverified_leads": []})+"\n", encoding="utf-8"
    )
    run=subprocess.run(
        [sys.executable, str(BASE/"director_review.py")],
        cwd=root, capture_output=True, text=True, timeout=20
    )
    assert run.returncode==0, (run.stdout, run.stderr)
    brief=json.loads((BASE/"owner_brief.json").read_text(encoding="utf-8"))
    reports=sorted((root/"director-reports").glob("D??.json"))
    assert len(reports)==10, "Expected ten independent local director reports"
    for report_path in reports:
        report=json.loads(report_path.read_text(encoding="utf-8"))
        assert report["owner_brief_version"]==brief["version"]
        assert report["owner_profile_understood"]==brief["visibility_note"]
        assert report["owner_objectives"]==brief["owner_mission"]
        assert report["owner_working_style"]==brief["approach"]
        assert report["own_research_report_present"] is False
        assert report["assistant_a_report_present"] is False
        assert report["assistant_b_report_present"] is False
        assert report["verified_earnings"]==[]
        assert report["outreach_capability"].startswith("Not available")
    d10=json.loads((root/"director-reports"/"D10.json").read_text())
    assert d10["teamwide_accountability"]["verified_payment_receipts"]==0
    assert (root/"director-reports"/"INDEX.md").exists()
    print("DIRECTOR_REVIEW_SCHEMA_PASS: 10 reports, current anonymous mission; "
          "zero fake workers, zero fake receipts")
