"""Build truthful, owner-approved draft introductions for real paid-work leads.

Drafts are NEVER sent automatically. No wallet full addresses or owner personal
data are printed. Quotes from external leads are treated as untrusted text.
"""
import re

def clean(s, cap=130):
    return re.sub(r"[\x00-\x1f<>]+"," ",str(s or "")).strip()[:cap]

def warm_pitch(lead, role="research", writer_id=""):
    if not isinstance(lead,dict) or not str(lead.get("url") or "").startswith("https://"):
        return {"status":"not_prepared_no_original_source"}
    title=clean(lead.get("title") or lead.get("assigned_role") or role,110)
    if not title:
        return {"status":"not_prepared_no_actual_scope"}
    message=(
        "Hello! I noticed your opportunity concerning \""+title+"\" and would be glad "
        "to explore whether I can help deliver the work to your expectations. "
        "Could you kindly confirm the specific deliverable, deadline, available budget, "
        "and how you review completed work? If we're a good fit, I can prepare a "
        "short proposal with the scope and milestones. BTC or genuine USDC could be "
        "discussed as payment options if you support them, using an agreed exact network. "
        "Thank you for your time!"
    )
    return {
        "status":"DRAFT_ONLY_NOT_SENT",
        "independent_researcher_id":clean(writer_id,60),
        "source_url":str(lead["url"]),
        "personalization_source":"observed publicly listed opportunity title; not verified client identity",
        "message":message,
        "next_action":"Verify original payer, scope, amount and eligibility before any authorized outreach. Never auto-send.",
        "payment_requested":False,
        "work_agreed":False,
        "money_received_verified":False
    }
