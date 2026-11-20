"""Real, finite, permission-safe parent-to-child task queue pilot.

Uses vendored Apache-2.0 unkloud/liteq (SQLite claim/ACK/retry/DLQ),
MIT python-jsonschema (strict command-envelope validation),
and Apache-2.0 tenacity (bounded SQLite transient-error retries).

SOURCE/VERSION/LICENCES: see crypto-agents/vendor/OPEN_SOURCE_NOTICES.md.
This script is new B1/B2 integration code; only the queue module is copied.

The queue is LOCAL to this GitHub runner. It does NOT transmit to all
virtual worker IDs, provide permanent 24/7 compute, contact buyers or prove
model understanding. One actually spawned Python subprocess per task.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_none
from vendor.liteq import LiteQueue

from b_certified_agent_service_router import role_index
from directive_cascade import read_owner
from hierarchy_command_core import execute, task_context

SCHEMA={
    "$schema":"https://json-schema.org/draft/2020-12/schema",
    "type":"object","additionalProperties":False,
    "required":["command_id","owner_sha256","fleet","role","role_index",
                "parent","task_type","message_version"],
    "properties":{
      "command_id":{"type":"string","pattern":"^OWNER-[A-Za-z0-9-]+$","maxLength":180},
      "owner_sha256":{"type":"string","pattern":"^[0-9a-f]{64}$"},
      "fleet":{"type":"string","enum":["transferexperiment","BountyScoutAI"]},
      "role":{"type":"string","pattern":"^D(0[1-9]|10)(-(M(0[1-9]|1[0-5])|A|B)(-W(0[1-9]|[1-4][0-9]|50)(-S[0-9]{3}(-G[0-9]{3}(-H[0-9]{3})?)?)?)?)?$","maxLength":90},
      "role_index":{"type":"integer","minimum":0},
      "parent":{"type":"string","minLength":2,"maxLength":180},
      "task_type":{"type":"string","const":"READ_ONLY_SOURCE_LEDGER_QA"},
      "message_version":{"type":"integer","const":1}
    }
}
VALIDATOR=Draft202012Validator(SCHEMA)

def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def init_receipts(db):
    with sqlite3.connect(db,timeout=8) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS owner_job_receipts(
            command_id TEXT NOT NULL, role_id TEXT NOT NULL,
            parent_id TEXT NOT NULL, action_sha256 TEXT NOT NULL,
            result_json TEXT NOT NULL,
            PRIMARY KEY(command_id,role_id)
        )""")

def envelope(fleet,role):
    authority=read_owner()
    idx=role_index(fleet,role)
    assignment=task_context(idx)
    return {
      "command_id":authority["owner_order_id"],
      "owner_sha256":authority["owner_sha256"],
      "fleet":fleet,"role":role,"role_index":idx,
      "parent":assignment["parent"],
      "task_type":"READ_ONLY_SOURCE_LEDGER_QA","message_version":1
    }

def check_envelope(item):
    errors=list(VALIDATOR.iter_errors(item))
    if errors:raise ValueError("TASK_SCHEMA_INVALID: "+str(errors[0])[:150])
    auth=read_owner()
    if item["command_id"]!=auth["owner_order_id"] or item["owner_sha256"]!=auth["owner_sha256"]:
        raise ValueError("REJECT_STALE_OR_ALTERED_HUMAN_OWNER_ORDER")
    if role_index(item["fleet"],item["role"])!=item["role_index"]:
        raise ValueError("REJECT_ROLE_INDEX_MISMATCH")
    ctx=task_context(item["role_index"])
    if ctx["role_id"]!="ORIGINAL/"+item["fleet"]+"/"+item["role"]:
        raise ValueError("REJECT_WRONG_TARGET_COMPANY_OR_LEAF")
    if ctx["parent"]!=item["parent"]:
        raise ValueError("REJECT_WRONG_IMMEDIATE_PARENT")
    return ctx

@retry(retry=retry_if_exception_type(sqlite3.OperationalError),
       stop=stop_after_attempt(3),wait=wait_none(),reraise=True)
def store_receipt(db,item,record):
    result=json.dumps(record,sort_keys=True,ensure_ascii=False)
    with sqlite3.connect(db,timeout=8) as con:
        row=con.execute("""SELECT action_sha256 FROM owner_job_receipts
            WHERE command_id=? AND role_id=?""",
            (item["command_id"],record["role_id"])).fetchone()
        if row:
            if row[0]!=record["task_evidence_sha256"]:
                raise ValueError("REJECT_INCONSISTENT_DUPLICATE_ROLE_RESULT")
            return False
        con.execute("""INSERT INTO owner_job_receipts
             (command_id,role_id,parent_id,action_sha256,result_json)
             VALUES (?,?,?,?,?)""",
             (item["command_id"],record["role_id"],record["supervisor"],
              record["task_evidence_sha256"],result))
        return True

def enforce_actual_parent_receipt(db,item,ctx):
    # The first director's parent is the fleet root. No fictitious Chief D
    # process receipt is asserted by this bounded pilot.
    if ctx["tier"]=="D":return
    with sqlite3.connect(db,timeout=8) as con:
        row=con.execute("""SELECT action_sha256 FROM owner_job_receipts
            WHERE command_id=? AND role_id=?""",
            (item["command_id"],ctx["parent"])).fetchone()
    if not row:raise ValueError("REQUIRE_REAL_PARENT_RECEIPT_BEFORE_CHILD_TASK")

def one_consumer(db):
    queue=LiteQueue(db,max_retries=2)
    with queue.consume(qname="owner-role-work",wait_seconds=0,invisible_on_receive=30) as msg:
        if msg is None:return {"no_more_jobs":True}
        item=json.loads(msg.data.decode())
        ctx=check_envelope(item)
        enforce_actual_parent_receipt(db,item,ctx)
        record=execute(item["role_index"],expected={ctx["tier"]})
        if record["owner_instruction_sha256"]!=item["owner_sha256"]:
            raise ValueError("CHILD_EXECUTED_DIFFERENT_OWNER_COMMAND")
        stored=store_receipt(db,item,record)
        return {"role":ctx["role_id"],"tier":ctx["tier"],
                "order_id":item["command_id"],
                "receipt_written":stored,"task_digest":record["task_evidence_sha256"],
                "actual_python_process_completed":True,
                "model_inference_completed":False}

def main_self_test():
    with tempfile.TemporaryDirectory(prefix="b1b2-oss-queue-") as d:
        db=str(Path(d)/"actual-queue.sqlite3")
        init_receipts(db)
        queue=LiteQueue(db,max_retries=2)
        roles=("D01","D01-M01","D01-M01-W01","D01-M01-W01-S001",
               "D01-M01-W01-S001-G001","D01-M01-W01-S001-G001-H001")
        msgs=[envelope(fleet,role)
              for fleet in ("transferexperiment","BountyScoutAI")
              for role in roles]
        # Fault-injection: a leaf cannot run before an actually checked
        # parent has completed. A wrong/fake parent or owner hash is refused.
        child=msgs[3]
        cctx=check_envelope(child)
        try:enforce_actual_parent_receipt(db,child,cctx)
        except ValueError as e:assert "REQUIRE_REAL_PARENT_RECEIPT" in str(e)
        else:raise AssertionError("Unacknowledged parent was allowed")
        forged=dict(child,parent="ORIGINAL/other/D01-M01-W01")
        try:check_envelope(forged)
        except ValueError as e:assert "REJECT_WRONG_IMMEDIATE_PARENT" in str(e)
        else:raise AssertionError("Forged parent was allowed")
        stale=dict(child,owner_sha256="0"*64)
        try:check_envelope(stale)
        except ValueError as e:assert "REJECT_STALE_OR_ALTERED" in str(e)
        else:raise AssertionError("Altered command accepted")
        invalid=dict(child,task_type="SEND_GMAIL")
        try:check_envelope(invalid)
        except ValueError as e:assert "TASK_SCHEMA_INVALID" in str(e)
        else:raise AssertionError("Unauthorized Gmail task accepted")
        for item in msgs:
            queue.put(json.dumps(item,sort_keys=True).encode(),
                      qname="owner-role-work")
        assert queue.qsize("owner-role-work")==12
        records=[]
        for _ in range(12):
            result=subprocess.run([sys.executable,__file__,"--consume",db],
                capture_output=True,text=True,timeout=45,check=True)
            payload=json.loads(result.stdout.strip().split("OWNER_ROLE_EXECUTION ")[-1])
            assert payload["actual_python_process_completed"]
            assert not payload["model_inference_completed"]
            records.append(payload)
        assert queue.empty("owner-role-work")
        # Demonstrate that a task prohibited by the owner's instructions is
        # never ACKed as successful and is moved to a real dead-letter queue.
        bad=json.dumps(invalid,sort_keys=True).encode()
        # Set one-attempt policy for a forbidden (non-transient) instruction:
        # never retry unauthorized email access just to reach a retry count.
        unsafe_queue=LiteQueue(db,max_retries=1)
        unsafe_queue.put(bad,qname="rejected-owner-task")
        rejected_attempts=0
        try:
            with unsafe_queue.consume(qname="rejected-owner-task",wait_seconds=2) as msg:
                if msg is None:
                    raise AssertionError("Forbidden owner task never became visible")
                check_envelope(json.loads(msg.data.decode()))
        except ValueError as exc:
            assert "TASK_SCHEMA_INVALID" in str(exc)
            rejected_attempts+=1
        assert rejected_attempts==1
        assert unsafe_queue.empty("rejected-owner-task")
        # Retry utility is tested independently with a deterministic transient
        # OperationalError; do not claim a network failure was tested.
        transient_calls=[0]
        @retry(retry=retry_if_exception_type(sqlite3.OperationalError),
               stop=stop_after_attempt(3),wait=wait_none(),reraise=True)
        def transient_test():
            transient_calls[0]+=1
            if transient_calls[0]==1:
                raise sqlite3.OperationalError("synthetic temporary lock")
            return "recovered"
        assert transient_test()=="recovered" and transient_calls[0]==2
        with sqlite3.connect(db) as con:
            dead_letter_count=con.execute(
                "SELECT COUNT(*) FROM liteq_dlq WHERE queue_name='rejected-owner-task'").fetchone()[0]
        assert dead_letter_count==1
        with sqlite3.connect(db) as con:
            rr=con.execute("""SELECT command_id,role_id,parent_id,action_sha256,result_json
                     FROM owner_job_receipts ORDER BY role_id""").fetchall()
        assert len(rr)==12
        latest=read_owner()
        assert all(x[0]==latest["owner_order_id"] and len(x[3])==64 for x in rr)
        assert len({x[1] for x in rr})==12
        evidence={
            "order":latest["owner_order_id"],
            "two_real_original_company_roots":2,
            "real_python_worker_subprocesses":12,
            "unique_individual_accepted_local_task_receipts":len(rr),
            "hierarchy_tiers_tested":["D","M","W","S","G","H"],
            "queue_messages_acknowledged":12,
            "wrong_parent_refused":True,
            "stale_owner_order_refused":True,
            "unsafe_Gmail_type_refused":True,
            "unacknowledged_manager_refused":True,
            "disallowed_task_rejected_and_moved_to_dead_letter":dead_letter_count==1,
            "forbidden_task_retry_attempts":rejected_attempts,
            "transient_sqlite_error_retry_test_passed":True,
            "sqlite_backed_queue_source":"Apache-2.0 unkloud/liteq vendored",
            "schema_validation_source":"MIT python-jsonschema",
            "bounded_sqlite_retry_source":"Apache-2.0 tenacity",
            "actual_model_inferences":0,
            "external_customer_bids":0,
            "crypto_payments_confirmed":0,
            "not_a_globally_hosted_queue":True,
            "not_all_virtual_roles_running":True,
            "individual_process_receipts":records,
        }
        out=Path("opensource-worker-evidence")
        out.mkdir(exist_ok=True)
        (out/"QUEUE_EXECUTION_REPORT.json").write_text(json.dumps(evidence,indent=2)+"\n")
        lines=["# Permissive open-source queue integration — actual results","",
            "## Sources actually reused",
            "- Apache-2.0 single-file Liteq SQLite queue, pinned upstream and fully licensed",
            "- MIT jsonschema for fail-closed owner-order envelope and forbidden-task type validation",
            "- Apache-2.0 Tenacity for bounded SQLite transient retry",
            "",
            "## Independent demonstration",
            f"- **12/12 real finite Python role subprocesses** completed a task and gave verified SHA output.",
            "- **2 company roots × 6 tiers**: D→M→W→S→G→H",
            "- All 12 queue messages were acknowledged after completed work",
            "- Wrong parent, stale command, unsafe Gmail task, and child-before-parent rejected",
            "- An unsafe task was rejected without retry and placed in the dead-letter queue, never counted as work",
            "- A synthetic temporary SQLite error was successfully retried once",
            "- **0 independently proven AI-model comprehension or buyer payments**",
            "",
            "**Important limitation:** This is a **local SQLite queue on one ephemeral GitHub Actions runner**. Queue artifacts are evidence, not a 24/7 globally deployed messaging service. Running the code once does not notify trillions of virtual roles."]
        (out/"REPORT.md").write_text("\n".join(lines)+"\n")
        print("OSS_B1B2_PARENT_CHILD_QUEUE_PASS "+json.dumps({
            k:v for k,v in evidence.items() if k!="individual_process_receipts"},sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--consume",metavar="SQLITE_DB")
    args=p.parse_args()
    if args.self_test:main_self_test()
    elif args.consume:
        print("OWNER_ROLE_EXECUTION "+json.dumps(one_consumer(args.consume)))
    else:p.error("Use --self-test or --consume DB")
