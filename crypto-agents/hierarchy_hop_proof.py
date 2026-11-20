"""A real, finite per-hop command relay proof over 30 root divisions.

30 independent chains: a separate Python subprocess loads the exact *latest*
owner directive for each hop, verifies that its immediate parent has actually
acknowledged the same full instruction in this SQLite run, and records evidence.
This is a local prototype of a reliable queue, NOT real cloud models, individual
human managers, or 11.25 trillion permanently active workers.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0,"crypto-agents")
from directive_cascade import read_owner
from enigma_universal_owner_order import recipient,GRAND_TOTAL,PER_ROOT

def sha(text): return hashlib.sha256(str(text).encode("utf-8")).hexdigest()
def utc():return datetime.now(timezone.utc).isoformat()
def connect(db):
    conn=sqlite3.connect(db,timeout=20)
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def setup(db,selected):
    if Path(db).exists():raise ValueError("Refuse overwrite of prior audit DB")
    auth=read_owner()
    with connect(db) as con:
        con.execute("""CREATE TABLE hops (
            root_id INTEGER NOT NULL,
            hop INTEGER NOT NULL,
            recipient TEXT NOT NULL,
            immediate_parent TEXT,
            order_id TEXT NOT NULL,
            owner_instruction_sha256 TEXT NOT NULL,
            status TEXT NOT NULL,
            pid INTEGER,
            timestamp_utc TEXT,
            action_sha256 TEXT,
            action_result TEXT,
            PRIMARY KEY(root_id,hop)
        )""")
        for root in selected:
            index=(root+1)*PER_ROOT-1
            path=recipient(index)["owner_to_worker_path"]
            assert path[-1].endswith("-H666")
            for k,name in enumerate(path):
                con.execute("INSERT INTO hops VALUES (?,?,?,?,?,?,?,NULL,NULL,NULL,NULL)",
                    (root,k,name,path[k-1] if k else None,auth["owner_order_id"],auth["owner_sha256"],"PENDING"))
    return auth

def hop(db,root,k):
    auth=read_owner()
    with connect(db) as con:
        row=con.execute("SELECT recipient,immediate_parent,order_id,owner_instruction_sha256,status FROM hops WHERE root_id=? AND hop=?",
                        (root,k)).fetchone()
        if row is None:raise ValueError("Unrecognized hop")
        name,parent,oid,digest,status=row
        if oid!=auth["owner_order_id"] or digest!=auth["owner_sha256"] or status!="PENDING":
            raise ValueError("STALE_OR_REPLAYED_COMMAND_REJECTED")
        if k:
            previous=con.execute("SELECT recipient,status,order_id,owner_instruction_sha256,action_sha256 FROM hops WHERE root_id=? AND hop=?",
                (root,k-1)).fetchone()
            if not previous or previous[:4]!=(parent,"PROCESS_RECEIPT_ONLY",oid,digest) or not previous[4]:
                raise ValueError("PARENT_NOT_ACTUALLY_ACKNOWLEDGED_THIS_ORDER")
        complete_text=auth["full_owner_instruction"]+"\n"+auth["standard_prompt"]
        if sha(auth["full_owner_instruction"])!=digest:raise ValueError("Owner text altered")
        # This is a real, small deterministic task at EACH hop. Real AI
        # understanding requires a SEPARATE successful model inference and review.
        result={
            "actual_step":"READ_VERIFY_AND_RELAY_COMPLETE_OWNER_DIRECTIVE",
            "exact_recipient":name,"real_process_pid":os.getpid(),
            "acknowledged_parent":parent,
            "order_id":oid,"owner_instruction_sha256":digest,
            "standing_prompt_sha256":auth["standard_sha256"],
            "full_order_and_standing_prompt_read_chars":len(complete_text),
            "is_model_inference":False,"external_customer_contacted":False}
        if name.endswith("-H666"):
            # The final leaf has a concrete bounded data QA task with a real
            # input and output, rather than claiming it researched the internet.
            fp=Path("crypto-agents/customer-acquisition/2026-11-20-public-customer-prospects.json")
            leads=json.loads(fp.read_text(encoding="utf-8"))
            rows=leads.get("leads",[])
            urls=[x.get("url") for x in rows]
            result["actual_leaf_task"]="CHECK_ORIGINAL_CUSTOMER_SOURCE_LEDGER_FOR_DUPLICATES"
            result["ledger_rows_checked"]=len(rows)
            result["original_lead_urls_unique"]=len(set(urls))==len(rows)
            result["external_customer_proposals_proven_by_local_ledger"]=sum(
                x.get("platform_submission_status","").startswith("SENT_VERIFIED") for x in rows)
            result["task_pass"]=result["original_lead_urls_unique"] and bool(rows)
        sig=sha(json.dumps(result,sort_keys=True,ensure_ascii=False))
        con.execute("""UPDATE hops SET status=?,pid=?,timestamp_utc=?,action_sha256=?,action_result=?
                        WHERE root_id=? AND hop=? AND status='PENDING'""",
                    ("PROCESS_RECEIPT_ONLY",os.getpid(),utc(),sig,
                     json.dumps(result,ensure_ascii=False,sort_keys=True),root,k))
        if con.total_changes!=1:raise ValueError("Hop replay/duplicate")
    return result

def verify(db):
    auth=read_owner();roots={}
    with connect(db) as con:
        records=con.execute("SELECT root_id,hop,recipient,immediate_parent,order_id,owner_instruction_sha256,status,pid,action_sha256,action_result FROM hops ORDER BY root_id,hop").fetchall()
    for row in records:
        root,k,name,parent,oid,digest,status,pid,proof,raw=row
        roots.setdefault(root,[]).append(row)
        assert status=="PROCESS_RECEIPT_ONLY" and pid>0 and oid==auth["owner_order_id"] and digest==auth["owner_sha256"]
        actual=json.loads(raw)
        assert actual["real_process_pid"]==pid and sha(json.dumps(actual,sort_keys=True,ensure_ascii=False))==proof
        if k: assert parent==roots[root][-2][2]
    assert len(roots)==30
    assert all(rows[-1][2].endswith("-H666") for rows in roots.values())
    assert all(json.loads(rows[-1][-1]).get("task_pass") for rows in roots.values())
    return {
        "owner_order_id":auth["owner_order_id"],
        "root_divisions_with_full_real_per_hop_process_receipts":len(roots),
        "unique_relay_hops_completed_by_real_python_subprocesses":len(records),
        "actual_last_H_processes_with_original_source_ledger_qa":len(roots),
        "owner_sha_matched_every_step":True,
        "intermediate_parent_receipts_verified_in_sqlite":True,
        "actual_ai_model_understanding_verified":0,
        "genuinely_independent_permanent_directors_managers_or_trillions_live":False,
        "external_social_search_proven":0,
        "buyer_contacts_sent_or_payment_verified":0,
        "prototype_limit":"One bounded GitHub runner local SQLite queue; no persistent globally hosted broker, independent manager AI models or distributed service deployment.",
    }

def pilot(db,out):
    auth=setup(db,list(range(30)))
    # Negative test: a child cannot skip its parent. Rollback after rejecting.
    try:hop(db,0,1)
    except ValueError as exc:
        assert "PARENT_NOT_ACTUALLY_ACKNOWLEDGED" in str(exc)
    else:raise AssertionError("Unacknowledged parent accepted")
    root_paths=[]
    with connect(db) as con:
        for root in range(30):
            path=con.execute("SELECT hop,recipient FROM hops WHERE root_id=? ORDER BY hop",(root,)).fetchall()
            root_paths.append({"root":root+1,"hops":[name for _,name in path]})
    for root in range(30):
        count=len(root_paths[root]["hops"])
        for k in range(count):
            cmd=[sys.executable,str(Path(__file__).resolve()),"--hop",str(root),str(k),"--db",str(db)]
            subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,check=True,timeout=20)
    summary=verify(db)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/"HOP_BY_HOP_EVIDENCE.json").write_text(json.dumps({"summary":summary,"paths":root_paths},indent=2)+"\n")
    md=["# Real per-parent hop proof — 30 organizational root divisions","",
        f"Owner order: {summary['owner_order_id']}.", "",
        f"**{summary['unique_relay_hops_completed_by_real_python_subprocesses']}** separate finite Python hops across **30** root paths produced matched real-process evidence.",
        "**30/30** terminal H processes completed original-source ledger QA.",
        "A skipped-parent negative test was correctly rejected.",
        "",
        "This is ONLY a local SQLite prototype: separate Python subprocesses prove that a relay code path can be executed. They are NOT independent AI models, persistent globally hosted manager agents, authenticated social accounts or real customer contacts.",
        "",
        "**Real AI-model understanding demonstrated by this test: 0.**",
        "**Payment and buyer submissions demonstrated by this test: 0.**",
        "**All 11,255,658,980,400 virtual roles receiving commands: NOT PROVEN.**"]
    (out/"REPORT.md").write_text("\n".join(md)+"\n")
    print("HIERARCHY_REAL_PER_HOP_EXECUTION_PILOT "+json.dumps(summary,sort_keys=True))

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--pilot",action="store_true")
    cli.add_argument("--db",default="hierarchy-hop-evidence/command-relay.sqlite3")
    cli.add_argument("--out",default="hierarchy-hop-evidence")
    cli.add_argument("--hop",nargs=2,type=int)
    args=cli.parse_args()
    if args.hop is not None:print("HOP_PROCESS_ACK "+json.dumps(hop(args.db,*args.hop)))
    elif args.pilot:
        Path(args.db).parent.mkdir(parents=True,exist_ok=True)
        pilot(args.db,args.out)
    else:cli.error("Choose --pilot or --hop ROOT STEP")
