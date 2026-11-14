"""Prove strict cross-worker auditing with a small synthetic, no-network test."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

script=(Path(__file__).resolve().parent/"everyone_peer_audit.py")
fleet="transferexperiment"
def row(role,response,source,grade="QUALIFIED_SOURCE_BACKED_AI_RESEARCH"):
    return {
      "id":fleet+"/"+role,
      "director":"D01",
      "parent":"D01-M01",
      "grade":grade,
      "defects":[],
      "source_urls":[source],
      "independent_model_excerpt":response,
      "next_action":"Contact only genuine payer after verified acceptance, then verify any receipt.",
      "actual_source_check":"source_checked",
    }
with tempfile.TemporaryDirectory() as directory:
    root=Path(directory)
    (root/"strict-worker-accountability").mkdir()
    records=[
      row("D01-M01-W01","Investigate original open-source paid task then verify sponsor acceptance.",
          "https://github.com/demoA/project/issues/5"),
      row("D01-M01-W02","Investigate original open-source paid task then verify sponsor acceptance.",
          "https://github.com/demoB/project/issues/7"),
      row("D01-M01-W03","Independently inspect public terms of an eligible documented bounty.",
          "https://github.com/demoC/project/issues/9")
    ]
    f=root/"strict-worker-accountability"/("strict-"+fleet+".json")
    f.write_text(json.dumps({"individual_results":records}),encoding="utf-8")
    r=subprocess.run([sys.executable,str(script)],cwd=root,
       env={**os.environ,"WORKFORCE_ID":fleet},capture_output=True,text=True,timeout=15)
    assert r.returncode==0,r.stdout+"\n"+r.stderr
    data=json.loads((root/"peer-accountability"/("peer-everyone-"+fleet+".json")).read_text())
    assert data["attempted_actual_worker_reports"]==3
    assert data["total_deterministic_ordered_worker_vs_worker_comparisons"]==6
    assert data["engine_did_an_automated_check_on_every_distinct_pair"] is True
    assert data["actual_separate_model_generated_peer_reviews"]==0
    assert data["automated_checks"]["identical_response_pairs"]==2
    assert len(data["per_worker"])==3
    assert all(x["engine_checks_against_distinct_other_workers"]==2 for x in data["per_worker"])
    assert all(x["assigned_peer_reviewer_for_next_authorized_execution"]!=x["actual_worker_id"] for x in data["per_worker"])
    # The empty-list case must make no phantom claimed workers or peer activity.
    f.write_text(json.dumps({"individual_results":[]}),encoding="utf-8")
    r=subprocess.run([sys.executable,str(script)],cwd=root,
       env={**os.environ,"WORKFORCE_ID":fleet},capture_output=True,text=True,timeout=15)
    assert r.returncode==0,r.stdout+"\n"+r.stderr
    data=json.loads((root/"peer-accountability"/("peer-everyone-"+fleet+".json")).read_text())
    assert data["attempted_actual_worker_reports"]==0
    assert data["total_deterministic_ordered_worker_vs_worker_comparisons"]==0
print("EVERYONE_AUDIT_REGRESSION_PASS: 3 actual workers, 6 full checks, 2 repeated output directions, 0 fake reviewers; empty pass")
