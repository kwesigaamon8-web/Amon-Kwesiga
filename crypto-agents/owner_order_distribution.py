"""Canonical owner orders, inherited lazily by all defined D/A/M/W/S/G/H roles.

A defined role or assigned instruction is NOT a running AI model.
"""
import hashlib
import json
from pathlib import Path

SOURCE=Path("crypto-agents/owner_orders.json")
CHIEF_ORDER_SOURCE=Path("crypto-agents/chief_D_owner_orders.json")
def chief_order():
    doc=json.loads(CHIEF_ORDER_SOURCE.read_text(encoding="utf-8"))
    current=doc["current_owner_order_id"]
    row=doc["orders"][-1]
    if row["id"]!=current:
        raise ValueError("Chief D owner order is not current")
    return {"id":current,"instruction":row["instruction"],
            "relay_source":str(CHIEF_ORDER_SOURCE)}

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
        "chief_D_current_owner_order_id":chief_order()["id"],
        "chief_D_owner_order_relay":chief_order()["relay_source"],
        "count":len(entries),
        "ids":[r["id"] for r in entries],
        "titles":{r["id"]:str(r.get("title",""))[:110] for r in entries},
        "sha256":digest(),
        "universal_instruction":"LATEST OWNER ORDER "+chief_order()["id"]+": ALL internal roles in BOTH owner-defined organizations are INCLUDED in the mission and reporting chain: local D01-D10 directors, their A/B advisers, all fifteen managers each, W/S/G/H descendants and activated recruits. Directors and advisers must independently supervise or support source checks, paid-work quality, outreach permission and truthful settlement validation; no internal adviser or supervisor is excluded. All genuinely active agents MUST understand and explain the whole B1/B2 hierarchy and report their real, evidence-backed individual work UP their exact one-parent reporting chain to company director, sole Chief D, and ultimately the human OWNER. The active agent must pass an independently generated real-model system comprehension check that covers the distinct 10+10 director boards, recruiter-to-recruit inheritance, correct OWN company Bitcoin mainnet wallet, 7B dormant role namespace vs live agents, and actual verified on-chain money vs speculative offers; weak/no answer is review-needed/NOT_RUN, never automatically passed. Every ACTUALLY ACTIVE recruiter must give each actually activated recruit the same legitimate crypto-earning task, exact individual parent and company wallet instructions, and require that recruit to pass the mission to any later genuinely activated recruits. External independent agents join only by express opt-in and permitted authenticated access; no mass spam, false recruiting, forced payments or fictional crypto. B denotes billions of defined worker role IDs. ORD-047: Director D teaches what D can/cannot do; every actual B worker must answer a separate model knowledge check and report passed, needs review, failed or not run to its parent. Missing or dormant model responses cannot claim learned. ORD-046 applies to every director, assistant, manager and W/S/G/H role on activation: publish or link to the canonical owner-approved PUBLIC_RECEIVING_ADDRESSES.md only in relevant, permitted, nonduplicative work/payment communications, never mass spam. The page already lists self-custody receiving addresses and unverified Binance candidates; do not request payment to unverified routes. Each actually invoked model independently researches lawful ways to earn transferable cryptocurrency and produces its own evidence-backed individual report; configured idle roles do not claim execution.",
        "status":"instructions_available_not_evidence_of_execution"
    }

def inheritance(agent_id, parent_id):
    s=summary()
    return {
       "agent_id":agent_id, "parent_id":parent_id,
       "source":s["source"], "all_owner_order_ids":s["ids"],
       "chief_D_latest_order_id":s["chief_D_current_owner_order_id"],
       "recruitment_cascade_owner_order_id":s["chief_D_current_owner_order_id"],
       "actual_new_recruits_messaged_or_activated":False,
       "order_count":s["count"], "order_registry_sha256":s["sha256"],
       "broadcast_B_order_id":"ORD-033", "broadcast_B_alias":"B = billions of workers",
       "broadcast_B_inherited":"ORD-033" in s["ids"],
       "status":"inherited_configured_not_a_running_model"
    }

def compact_prompt():
    s=summary()
    return "Chief D latest owner instruction "+chief_order()["id"]+": Human owner oversees BOTH entire B1/B2 configured organizations, including all 20 local directors, ALL 40 director assistants, all 300 managers and W/S/G/H descendants. Every actually active director, adviser, manager and worker participates in appropriate legitimate crypto-earning support and provides evidence through one parent; director assistants report to own company director. Defined roles are NOT proof of live models or income. Every genuinely ACTIVE worker or recruit reports ONLY to one named parent, parent reports up through the same fleet local director, Chief D reports the consolidated verified B1/B2 results to the HUMAN OWNER. Each must independently demonstrate knowledge of the system, reporting ancestry, correct company wallet, recruiting chain and verifiable payer/payment evidence; no live model = NO ACTUAL UNDERSTANDING. EACH genuinely active recruiter must pass this same lawful crypto-earning order to EVERY genuinely activated child, with correct company mainnet wallet, exact recruiter-child relationship, original task, customer proof and receipt TXID or NONE. Every child passes it to future actually activated descendants, without automatic 7B execution or external spam. STRICT output evidence from every ACTUALLY EXECUTED worker, and real lawful cryptocurrency settlement; no lazy/duplicate/imagined work. B = 375188632680 DEFINED ROLE IDS. ORD-047: Director D coordinates workers, checks evidence and owner reports; cannot fabricate payments or force outside agents. Every actual worker must report whether D lesson was learned with a separate model response and direct parent. ORD-046: every active B role may share the publicly approved receiving-address page in relevant authorized posts only; avoid mass unsolicited messaging; Binance exchange routes remain unverified. ORD-033 and ORD-034: every actually running agent independently studies real coins and legitimate worldwide coin-earning opportunities. Each ACTUALLY RUNNING role independently research real paid work for transferable crypto to approved addresses; identify source, deliverable, payer, eligibility, token/network and risks; give one unique evidence-backed report; no fake coins or bulk signups. ALL "+str(s["count"])+" owner orders apply; registry "+s["source"]+"; IDs: "+",".join(s["ids"])+". Do not treat idle defined roles as active."
