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
        "universal_instruction":"B=ORD-033 is a universal broadcast to all 375188632680 defined role IDs. Every actually invoked model independently researches lawful ways to earn transferable cryptocurrency and produces its own evidence-backed individual report; configured idle roles do not claim execution.",
        "status":"instructions_available_not_evidence_of_execution"
    }

def inheritance(agent_id, parent_id):
    s=summary()
    return {
       "agent_id":agent_id, "parent_id":parent_id,
       "source":s["source"], "all_owner_order_ids":s["ids"],
       "order_count":s["count"], "order_registry_sha256":s["sha256"],
       "broadcast_B_order_id":"ORD-033", "broadcast_B_alias":"B",
       "broadcast_B_inherited":"ORD-033" in s["ids"],
       "status":"inherited_configured_not_a_running_model"
    }

def compact_prompt():
    s=summary()
    return "B=ORD-033 BROADCAST TO ALL 375188632680 ROLE IDS. Each ACTUALLY RUNNING role independently research real paid work for transferable crypto to approved addresses; identify source, deliverable, payer, eligibility, token/network and risks; give one unique evidence-backed report; no fake coins or bulk signups. ALL "+str(s["count"])+" owner orders apply; registry "+s["source"]+"; IDs: "+",".join(s["ids"])+". Do not treat idle defined roles as active."
