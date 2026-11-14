"""Evaluate one genuinely model-generated acknowledgement of latest Chief D order.

An AI can repeat words without deeply understanding them; this gate therefore
records checkable self-reported comprehension, never a guarantee of competence,
external payment or child activation.
"""
from __future__ import annotations
import re

def evaluate(reply,worker_id,parent_id,owner_order_id):
    text=str(reply or "").strip()
    low=text.lower()
    id_evidenced=bool(owner_order_id and owner_order_id in text)
    parent_evidenced=bool(parent_id and parent_id in text)
    coin=any(x in low for x in ("bitcoin","btc","cryptocurrency","crypto","coin","wallet"))
    action=any(x in low for x in ("verify","check","research","find","complete","collect","deliver","work","payer","contract"))
    evidence=any(x in low for x in ("source","evidence","link","proof","txid","transaction","accepted","receipt","url"))
    status=("MODEL_SELF_REPORTED_COMMAND_ACK" if
      len(text)>=45 and id_evidenced and parent_evidenced and coin and action and evidence else
      "NEEDS_SUPERVISOR_REVIEW" if text else
      "NO_MODEL_ACKNOWLEDGEMENT")
    return {
      "status":status,
      "worker_id":worker_id,"parent_id":parent_id,
      "chief_D_owner_order_id":owner_order_id,
      "model_generated_reply":text[:1100],
      "order_id_repeated_in_own_model_reply":id_evidenced,
      "correct_direct_parent_in_model_reply":parent_evidenced,
      "crypto_mission_stated":coin,
      "concrete_action_stated":action,
      "source_or_payment_evidence_discussed":evidence,
      "understanding_independently_verified":False,
      "supervisor_model_review_status":"NOT_YET_EVIDENCED",
      "note":"A model response and format markers can support an acknowledgement, but cannot prove genuine competence, exact future compliance, contractual acceptance or cryptocurrency payment."
    }

if __name__=="__main__":
    good=evaluate("ORDER OWNER-20261114-073213. I report to D03-M02. Verify a public source and legitimate Bitcoin payer evidence, deliver qualified work before collecting coins.","D03-M02-W01","D03-M02","OWNER-20261114-073213")
    bad=evaluate("I received the command.","D03-M02-W01","D03-M02","OWNER-20261114-073213")
    assert good["status"]=="MODEL_SELF_REPORTED_COMMAND_ACK"
    assert bad["status"]=="NEEDS_SUPERVISOR_REVIEW"
    print("COMMAND_ACK_GATE_TEST_PASS")
