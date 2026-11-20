"""B1/B2 zero-dependency HTTP status service + SQLite evidence queue.

No remote writes, wallet keys, mining, external outreach, or perpetual jobs.
An HTTP server is only live while the host process is running. DB on free
ephemeral hosts must be mounted on durable storage for persistence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = os.environ.get("B1B2_DB_PATH", "/tmp/b1b2-worker-evidence.sqlite3")
CHIEF = ROOT / "crypto-agents/chief_D_owner_orders.json"
PUBLIC = ROOT / "crypto-agents/PUBLIC_AGENT_COMMAND.json"
ROUTES = ROOT / "crypto-agents/public_payment_routes.json"

SEEDS = (
    ("order-integrity", "command_integrity", "Check latest Chief D/public command mirror and cascade", str(CHIEF)),
    ("btc-routes", "btc_routes_audit", "Check B1/B2 published receiving routes without any transactions", str(ROUTES)),
    ("tor-paid-work", "external_research", "Investigate authentic Tor/privacy-security BTC-paying opportunities", "https://www.torproject.org/"),
    ("mining-profitability", "external_research", "Find an expressly consenting ASIC operator and verify economics", "https://mempool.space/"),
)

def timestamp():
    return datetime.now(timezone.utc).isoformat()

def digest(text):
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()

def connect(path):
    conn = sqlite3.connect(str(path), timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def initialize(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS tasks(
            id TEXT PRIMARY KEY, kind TEXT NOT NULL, title TEXT NOT NULL,
            source TEXT NOT NULL, status TEXT NOT NULL,
            updated_utc TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS receipts(
            id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL,
            status TEXT NOT NULL, evidence TEXT NOT NULL,
            evidence_sha256 TEXT NOT NULL, created_utc TEXT NOT NULL);
        """)
        for task_id, kind, title, source in SEEDS:
            db.execute(
                "INSERT OR IGNORE INTO tasks VALUES (?,?,?,?,?,?)",
                (task_id, kind, title, source, "QUEUED", timestamp())
            )

def command_check():
    chief = json.loads(CHIEF.read_text(encoding="utf-8"))
    public = json.loads(PUBLIC.read_text(encoding="utf-8"))
    last = chief["orders"][-1]
    order_id = chief["current_owner_order_id"]
    consistent = (
        last["id"] == order_id
        and public["command_id"] == order_id
        and last["instruction"] == public["owner_command"]
        and chief.get("owner_prompt_cascade", {}).get("owner_order_id") == order_id
        and public.get("owner_prompt_cascade", {}).get("owner_order_id") == order_id
    )
    return {
        "status": "PASS" if consistent else "FAIL",
        "order_id": order_id,
        "instruction_sha256": digest(last["instruction"]),
        "mirror_and_cascade_match": consistent,
        "independent_ai_comprehension_proved": False,
    }

def routes_check():
    doc = json.loads(ROUTES.read_text(encoding="utf-8"))
    records = {x["route_id"]: x for x in doc["self_custody_candidate_routes"]}
    wanted = {
        "BTC-01": "bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z",
        "BTC-02": "bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9",
    }
    checks = {}
    for route_id, expected in wanted.items():
        x = records.get(route_id, {})
        checks[route_id] = (
            x.get("receiving_address") == expected
            and x.get("chain") == "bitcoin-mainnet"
            and x.get("asset") == "BTC"
            and x.get("direction") == "RECEIVE_ONLY"
            and x.get("allowed_to_send") is False
        )
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "wallet_ownership_independently_verified": False,
        "blockchain_receipts_checked": False,
        "bitcoin_earned_or_mined_by_this_test": 0,
    }

def run_once(path):
    """Execute ONE actual, finite local validation, no fabricated external task."""
    initialize(path)
    with connect(path) as db:
        row = db.execute(
            "SELECT * FROM tasks WHERE status='QUEUED' AND kind!='external_research' "
            "ORDER BY CASE id WHEN 'order-integrity' THEN 0 ELSE 1 END LIMIT 1"
        ).fetchone()
        if row is None:
            return {"status": "NO_ELIGIBLE_LOCAL_TASK", "note": "External research requires separate authenticated, source-backed work."}
        db.execute("UPDATE tasks SET status='RUNNING',updated_utc=? WHERE id=?",
                   (timestamp(), row["id"]))
        try:
            result = command_check() if row["kind"] == "command_integrity" else routes_check()
            status = "PASS" if result["status"] == "PASS" else "FAIL"
        except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
            status = "BLOCKED"
            result = {"status": status, "reason": type(exc).__name__, "detail": str(exc)[:180]}
        evidence = json.dumps(result, sort_keys=True, separators=(",", ":"))
        db.execute("INSERT INTO receipts(task_id,status,evidence,evidence_sha256,created_utc) "
                   "VALUES(?,?,?,?,?)", (row["id"], status, evidence, digest(evidence), timestamp()))
        db.execute("UPDATE tasks SET status=?,updated_utc=? WHERE id=?",
                   (status, timestamp(), row["id"]))
        return {"task_id": row["id"], "status": status, "evidence": result,
                "evidence_sha256": digest(evidence)}

def snapshot(path, table):
    initialize(path)
    if table not in ("tasks", "receipts"):
        raise ValueError("Unsupported table")
    with connect(path) as db:
        rows = db.execute(
            ("SELECT id,kind,title,source,status,updated_utc FROM tasks ORDER BY id LIMIT 50"
             if table == "tasks" else
             "SELECT id,task_id,status,evidence_sha256,created_utc FROM receipts "
             "ORDER BY id DESC LIMIT 50")
        ).fetchall()
        return [dict(row) for row in rows]

def handler_for(path):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, code, payload):
            raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            route = urlsplit(self.path).path
            if route == "/health":
                self.reply(200, {"status": "ok", "service": "b1b2-evidence",
                                 "mode": "READ_ONLY", "wallet_signing": False})
            elif route == "/command":
                try:
                    value = command_check()
                    self.reply(200 if value["status"] == "PASS" else 503, value)
                except (OSError, ValueError, KeyError) as exc:
                    self.reply(503, {"status": "BLOCKED", "reason": type(exc).__name__})
            elif route in ("/tasks", "/receipts"):
                self.reply(200, {"rows": snapshot(path, route[1:])})
            else:
                self.reply(404, {"error": "NOT_FOUND"})

        def log_message(self, fmt, *args):
            pass  # no visitor IPs in public error artifacts

    return Handler

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=DEFAULT_DB)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("run-once")
    sub.add_parser("status")
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8080")))
    args = parser.parse_args()
    initialize(args.db)
    if args.command == "init":
        print(json.dumps({"status": "initialized", "tasks": len(snapshot(args.db, "tasks"))}))
    elif args.command == "run-once":
        print(json.dumps(run_once(args.db), sort_keys=True))
    elif args.command == "status":
        print(json.dumps({"tasks": snapshot(args.db, "tasks"),
                          "receipts": snapshot(args.db, "receipts"),
                          "command": command_check()}, sort_keys=True))
    else:
        print("Serving read-only B1/B2 evidence API (no worker mining)", flush=True)
        ThreadingHTTPServer((args.host, args.port), handler_for(args.db)).serve_forever()

if __name__ == "__main__":
    main()
