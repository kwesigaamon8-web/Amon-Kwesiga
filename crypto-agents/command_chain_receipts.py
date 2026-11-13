"""Deterministic one-parent owner-command routing and truthful acknowledgements.

Owner -> director -> manager -> W -> S -> G -> H.
D-A/D-B are direct director assistants, not required intermediate supervisors.
A route is AVAILABLE to all defined descendants, not evidence of delivery.
"""
import json
import re
from datetime import datetime,timezone
from pathlib import Path

from owner_order_distribution import summary

D=re.compile(r"^D(?:0[1-9]|10)$")
A=re.compile(r"^D(?:0[1-9]|10)-[AB]$")
M=re.compile(r"^D(?:0[1-9]|10)-M(?:0[1-9]|1[0-5])$")
W=re.compile(r"^D(?:0[1-9]|10)-M(?:0[1-9]|1[0-5])-W(?:0[1-9]|[1-4]\d|50)$")
S=re.compile(W.pattern[:-1]+r"-S(?:00[1-9]|0[1-9]\d|1[0-4]\d|150)$")
G=re.compile(S.pattern[:-1]+r"-G(?:00[1-9]|0[1-9]\d|[1-4]\d\d|500)$")
H=re.compile(G.pattern[:-1]+r"-H(?:00[1-9]|0[1-9]\d|[1-5]\d\d|6[0-5]\d|66[0-6])$")
PATTERNS=((D,"D"),(A,"A"),(M,"M"),(W,"W"),(S,"S"),(G,"G"),(H,"H"))
CHILDREN={"OWNER":10,"D":17,"A":0,"M":50,"W":150,"S":500,"G":666,"H":0}

def level(role_id):
    for pattern,tag in PATTERNS:
        if pattern.fullmatch(str(role_id)):return tag
    raise ValueError("Unrecognized role identity: "+str(role_id)[:120])

def parent(role_id):
    tag=level(role_id)
    if tag=="D":return "OWNER"
    if tag=="A":return role_id[:3]
    return role_id.rsplit("-",1)[0]

def route(role_id):
    if role_id=="OWNER":return ["OWNER"]
    result=[role_id]
    while result[-1]!="OWNER":
        result.append(parent(result[-1]))
        if len(result)>8:raise ValueError("Cycle in command chain")
    return result[::-1]

def configured_assignment(role_id):
    r=route(role_id)
    orders=summary()
    return {
      "role_id":role_id,"direct_supervisor":r[-2] if len(r)>1 else None,
      "owner_to_role_route":r,"level":level(role_id),
      "owner_orders_count":orders["count"],
      "owner_order_registry_sha256":orders["sha256"],
      "owner_orders_all_inherited":True,
      "subordinates_configured":CHILDREN[level(role_id)],
      "instruction_at_each_ancestor":"configured_inheritance_only_unverified_agent_ack",
      "role_instruction_status":"assigned_not_executed",
      "individual_acknowledgement_status":"not_received",
      "own_next_task":"Independently research real lawful crypto-paying opportunities worldwide, verify evidence and report to one parent.",
      "warning":"This record is a mathematical instruction chain, not a message delivered to live processes at every tier."
    }

def understanding_receipt(role_id,model_text,model_status,source_url=""):
    assign=configured_assignment(role_id)
    replied=model_status=="model_completed" and bool(str(model_text or "").strip())
    body=str(model_text or "").strip()[:1300]
    lower=body.lower()
    money=any(x in lower for x in ("bitcoin","btc","crypto","coins","coin","usdc","token","wallet","payment","payout"))
    action=any(x in lower for x in ("research","source","verify","paid","work","bounty","job","task","contract","next","check","payer"))
    status=("model_response_has_mission_and_action" if replied and money and action else
            "model_response_needs_parent_review" if replied else "model_not_completed_no_acknowledgement")
    return {
      "order":"ORD-035","role_id":role_id,
      "direct_parent":assign["direct_supervisor"],
      "route":assign["owner_to_role_route"],
      "all_owner_orders_sha256":assign["owner_order_registry_sha256"],
      "all_owner_orders_received_as_prompt":replied,
      "model_inference_status":model_status,
      "model_generated_own_words":body if replied else "",
      "understanding_status":status,
      "understanding_verified":False,
      "parent_review_required":True,
      "evidence_url":str(source_url or "")[:300],
      "created_at_utc":datetime.now(timezone.utc).isoformat(),
      "configured_uncharged_children":assign["subordinates_configured"],
      "children_live_acknowledgements_received":0,
      "explanation":"Heuristic markers do not prove comprehension. A child is not acknowledged until it runs a separate real model call and leaves an inspectable receipt."
    }

def structural_check():
    ids=["D01","D10-B","D05-M09","D10-M15-W50",
         "D01-M01-W01-S150","D05-M09-W29-S075-G500",
         "D10-M15-W50-S150-G500-H666"]
    expected=["OWNER","D10","D10-M15","D10-M15-W50",
              "D10-M15-W50-S150","D10-M15-W50-S150-G500",
              "D10-M15-W50-S150-G500-H666"]
    chain=route(ids[-1])
    if chain!=expected:raise AssertionError("H-tier owner chain mismatch: "+str(chain))
    for item in ids:
        obj=configured_assignment(item)
        assert obj["owner_to_role_route"][-1]==item
        assert obj["individual_acknowledgement_status"]=="not_received"
        assert obj["role_instruction_status"]=="assigned_not_executed"
    assert summary()["count"]>=35
    return {"status":"PASS","routes_checked":ids,"final_H_route":chain,
            "defined_roles_total":375188632680,
            "verified_understanding_replies":0,
            "structural_only_not_live_delivery":True}

if __name__=="__main__":
    print(json.dumps(structural_check(),indent=2))
