"""Canonical owner orders, inherited lazily by all defined D/A/M/W/S/G/H roles.

A defined role or assigned instruction is NOT a running AI model.
"""
import hashlib
import json
from pathlib import Path

SOURCE=Path("crypto-agents/owner_orders.json")

def rows():
    records=json.loads(SOURCE.read_text(encoding="utf-8"))["orders"]
    ids=[r["id"] for r in records]
    if not ids or len(ids)!=len(set(ids)):
        raise ValueError("Owner order register invalid or duplicated")
    return records

def order_ids():
    return [r["id"] for r in rows()]

def digest():
    return hashlib.sha256(SOURCE.read_bytes()).hexdigest()

def summary():
    entries=rows()
    return {
        "source":str(SOURCE),
        "count":len(entries),
        "ids":[r["id"] for r in entries],
        "titles":{r["id"]:str(r.get("title",""))[:110] for r in entries},
        "sha256":digest(),
        "universal_instruction":"All current owner orders apply to every role, when activated; independently choose lawful authorized paid-work research and deliver a truthful individual report.",
        "status":"instructions_available_not_evidence_of_execution"
    }

def inheritance(agent_id, parent_id):
    s=summary()
    return {
       "agent_id":agent_id, "parent_id":parent_id,
       "source":s["source"], "all_owner_order_ids":s["ids"],
       "order_count":s["count"], "order_registry_sha256":s["sha256"],
       "status":"inherited_configured_not_a_running_model"
    }

def compact_prompt():
    s=summary()
    return "ALL "+str(s["count"])+" owner orders apply; canonical order file "+s["source"]+"; IDs: "+",".join(s["ids"])+". Focus: lawful crypto-paid work, independent evidence, no fees, correct chain, no invented receipts, your own report."
