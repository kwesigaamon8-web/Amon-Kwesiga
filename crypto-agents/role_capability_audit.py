"""Real per-role capability inspection and bounded executable proof.

Reports tools actually available to this process. The role's *advertised*
capabilities must be verified by a concrete local test, not inferred from
a massive virtual role count or from its title.

No network, email, account login, wallet transfer, financial commitment or
third-party outreach is conducted by this module.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

BASE=Path("crypto-agents")
SOURCE=BASE/"customer-acquisition"/"2026-11-20-public-customer-prospects.json"
PROGRAMS=BASE/"hierarchy_command_core.py"
REQUIRED={"D","A","M","W","S","G","H"}
CATALOGUE={
"D":("evaluate_direct_reports","audit_lead_application_states","report_unverified_deals"),
"A":("inspect_public_lead_record_completeness","deduplicate_source_urls"),
"M":("construct_50_configured_child_ids","validate_supervisor_assignment"),
"W":("validate_local_public_lead_urls","report_unknown_buyer_identity"),
"S":("check_duplicate_public_lead_urls","verify_local_ledger_structure"),
"G":("audit_external_application_proof_flags","reject_unverified_sales"),
"H":("audit_accepted_work_and_payment_evidence","report_missing_transaction_proof"),
}
# Capabilities without an authenticated external tool/account are NOT granted.
NOT_AVAILABLE_WITHOUT_ADDITIONAL_PERMISSION=(
 "authenticated_social_media_account_search",
 "permitted_external_bid_submission",
 "unapproved_direct_customer_messages",
 "gmail_or_email_access",
 "private_wallet_signing_or_spending",
 "mining_on_other_peoples_devices",
 "independent_model_comprehension_without_actual_model_invocation",
 "independent_payment_confirmation_without_blockchain_or_payer_evidence",
)

def digest(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=False).encode("utf-8")).hexdigest()

def source():
    raw=SOURCE.read_bytes()
    doc=json.loads(raw.decode("utf-8"))
    rows=doc.get("leads")
    if not isinstance(rows,list):raise ValueError("No public lead records")
    return {"file":str(SOURCE),"sha256":hashlib.sha256(raw).hexdigest(),"rows":rows}

def run_trial(tier,role_id,immediate_parent,order_id):
    if tier not in REQUIRED:raise ValueError("Invalid role tier")
    if not isinstance(role_id,str) or not role_id:raise ValueError("Role missing")
    if not isinstance(immediate_parent,str) or not immediate_parent:raise ValueError("Parent missing")
    if not str(order_id).startswith("OWNER-"):raise ValueError("Untrusted order ID")
    src=source()
    leads=src["rows"]
    urls=[str(x.get("url") or "") for x in leads]
    valid=[u for u in urls if u.startswith("https://")]
    duplicates=len(urls)-len(set(urls))
    unverified_submission=sum(
        not str(x.get("platform_submission_status") or "").startswith("SENT_VERIFIED")
        for x in leads
    )
    accepted=sum(x.get("scope_commitment_accepted") is True for x in leads)
    verified_flag=sum(x.get("payment_verified") is True for x in leads)
    base={"task_source":src["file"],"task_source_sha256":src["sha256"],
          "rows_processed":len(leads),"urls_present":len(valid),
          "unique_urls":len(set(urls)),"duplicate_urls":duplicates}
    if tier=="D":
        action={"test":"director_local_supervision_and_application_state",
            "local_evidence":{**base,"unverified_proposal_rows":unverified_submission,
              "accepted_contract_flags":accepted,"verified_payment_flags":verified_flag,
              "real_manager_acknowledgments_in_this_test":0},
            "conclusion":"Review actual manager receipts and original payer sources; this local ledger cannot prove customer acquisition."}
    elif tier=="A":
        action={"test":"assistant_source_record_completeness",
            "local_evidence":{**base,"all_urls_have_https_shape":len(valid)==len(urls),
              "rows_missing_external_source":len(urls)-len(valid)},
            "conclusion":"Report missing or duplicate source fields to director; do not treat one ledger field as real buyer proof."}
    elif tier=="M":
        # A manager may be loaded at any root but its assigned direct worker IDs
        # are always based on its own unique role identifier.
        children=[role_id+f"-W{i:02d}" for i in range(1,51)]
        action={"test":"manager_child_coverage_and_parent_validation",
            "local_evidence":{**base,"children_configured":len(children),
              "distinct_child_ids":len(set(children)),
              "first_child":children[0],"last_child":children[-1],
              "actual_child_processes_verified_in_this_test":0},
            "conclusion":"These are 50 assignable role IDs, not 50 active independent children; require their own run receipts."}
    elif tier=="W":
        action={"test":"worker_original_url_syntax_and_missing_identity",
            "local_evidence":{**base,"invalid_url_rows":len(urls)-len(valid),
              "independently_verified_buyers_in_this_test":0},
            "conclusion":"Source URLs have only a syntactic check; authenticate individual buyers before submitting."}
    elif tier=="S":
        action={"test":"specialist_source_duplicates_and_ledger_data_integrity",
            "local_evidence":{**base,"duplicate_source_entries":duplicates,
              "records_with_public_platform":sum(bool(x.get("platform")) for x in leads)},
            "conclusion":"Maintain a deduplicated lead list; no platform bid is sent by data QA."}
    elif tier=="G":
        action={"test":"group_lead_submission_claims_vs_evidence",
            "local_evidence":{**base,"submissions_without_evidence":unverified_submission,
              "verified_sent_submissions_by_flag":len(leads)-unverified_submission},
            "conclusion":"Do not count drafts as actual bids; independently inspect permitted platform proof."}
    else:
        action={"test":"final_H_contract_and_payment_claims",
            "local_evidence":{**base,"accepted_contract_flags":accepted,
              "payment_verified_flags":verified_flag,
              "independently_checked_blockchain_transactions":0},
            "conclusion":"Do not report cash or coins without accepted work and independent transaction evidence."}
    return {"schema":"CENTRAL_ORDER_REAL_CAPABILITY_TRIAL_V1",
      "current_owner_order_id":order_id,"worker_role":role_id,
      "actual_immediate_parent":immediate_parent,"tier":tier,
      "available_with_existing_local_code":list(CATALOGUE[tier]),
      "cannot_prove_with_available_permissions":list(NOT_AVAILABLE_WITHOUT_ADDITIONAL_PERMISSION),
      "self_selected_paying_customer_without_authenticated_access":False,
      "bounded_test_executed":True,
      "bounded_test_pass":len(leads)>0 and len(valid)==len(urls),
      "evidence":action,"evidence_sha256":digest(action),
      "actually_completed_external_buyer_assignment":False,
      "actual_model_inference":False,
      "understanding_verified":False,
      "verified_payment":False,
    }

def audit(receipt,expected_order,expected_parent,expected_tier):
    if not isinstance(receipt,dict):return False,["no_receipt"]
    errors=[]
    if receipt.get("current_owner_order_id")!=expected_order:errors.append("stale_order")
    if receipt.get("actual_immediate_parent")!=expected_parent:errors.append("wrong_parent")
    if receipt.get("tier")!=expected_tier:errors.append("wrong_tier")
    if receipt.get("available_with_existing_local_code")!=list(CATALOGUE[expected_tier]):
        errors.append("capability_catalogue_mismatch")
    if receipt.get("bounded_test_executed") is not True:errors.append("no_executed_task")
    if receipt.get("bounded_test_pass") is not True:errors.append("task_test_failed")
    evidence=receipt.get("evidence")
    if not isinstance(evidence,dict) or receipt.get("evidence_sha256")!=digest(evidence):
        errors.append("invalid_task_hash")
    src=source()
    if isinstance(evidence,dict):
        e=evidence.get("local_evidence") or {}
        if e.get("task_source_sha256")!=src["sha256"]:errors.append("changed_task_input")
        if e.get("rows_processed")!=len(src["rows"]):errors.append("incorrect_rows_examined")
    if receipt.get("actually_completed_external_buyer_assignment") is not False:
        errors.append("unsupported_external_assignment")
    if receipt.get("actual_model_inference") is not False:errors.append("unsupported_model_inference")
    if receipt.get("verified_payment") is not False:errors.append("unsupported_payment")
    return len(errors)==0,errors

def self_test():
    order="OWNER-20261120-EXAMPLE"
    report=run_trial("H","ORIGINAL/transferexperiment/D01-M01-W01-S001-G001-H001",
                     "ORIGINAL/transferexperiment/D01-M01-W01-S001-G001",order)
    assert audit(report,order,report["actual_immediate_parent"],"H")[0]
    forged=dict(report,evidence_sha256="0"*64)
    assert "invalid_task_hash" in audit(forged,order,report["actual_immediate_parent"],"H")[1]
    stale=dict(report,current_owner_order_id="OLDER")
    assert "stale_order" in audit(stale,order,report["actual_immediate_parent"],"H")[1]
    return {"role_tiers_with_shared_capability_catalogue":len(CATALOGUE),
            "synthetic_pass_and_two_negative_tests":True,
            "actual_external_customers_contacted":0}
if __name__=="__main__":
    print("ROLE_CAPABILITY_SELF_TEST "+json.dumps(self_test()))
