"""Director-grade independent effort for every ACTUALLY invoked B1/B2 worker.

D01–D10 remain designated directors and D10 remains payment verifier.
This gives other W/S/G/H workers the same work standards, not new privileges,
fictional running agents, extra buyer contact rights or spending power.
"""
from __future__ import annotations
import argparse
import json
import re

FLEETS = ("transferexperiment", "BountyScoutAI")
DUTIES = (
    ("D01", "Find a genuine paying customer and exact useful task"),
    ("D02", "Verify sponsor legitimacy, active funding and eligibility"),
    ("D03", "Agree deliverable, fee, deadline, coin and network"),
    ("D04", "Produce original payer-specific useful work"),
    ("D05", "Test, challenge, fix and rerun independent checks"),
    ("D06", "Package evidence, clear acceptance tests and delivery"),
    ("D07", "Use only permissioned approved no-email submission channels"),
    ("D08", "Verify actual buyer feedback, acceptance or revision request"),
    ("D09", "Audit originality, licenses, facts, duplicate work and claims"),
    ("D10", "Verify genuine correct-chain income by payer, TXID and amount"),
)
LANE_DUTY = {
    "BUYER_SOURCE":"D01", "PAYER_VALIDATE":"D02",
    "BUILD_ORIGINAL":"D04", "QA_REVIEW":"D05",
    "BUYER_CONTACT":"D07", "PAYMENT_EVIDENCE":"D10",
    "ASIC_PARTNER":"D02", "HOST_RESEARCH":"D09",
    "PROOF_AUDIT":"D09", "REPAIR_AND_SUPPORT":"D05",
}
ROLE = re.compile(
    r"^D(?:0[1-9]|10)-M(?:0[1-9]|1[0-5])-W(?:0[1-9]|[1-4][0-9]|50)"
    r"(?:-S[0-9]{3}(?:-G[0-9]{3}(?:-H[0-9]{3})?)?)?$"
)

def assign(fleet: str, worker: str, parent: str, lane: str) -> dict:
    if fleet not in FLEETS: raise ValueError("Unknown B company")
    if not ROLE.fullmatch(worker): raise ValueError("Unknown W/S/G/H role")
    if worker.rsplit("-", 1)[0] != parent: raise ValueError("Parent mismatch")
    if lane not in LANE_DUTY: raise ValueError("Unknown paid-work lane")
    lead = LANE_DUTY[lane]
    responsibilities = dict(DUTIES)
    return {
        "mode": "TEN_DIRECTOR_GRADE_WORK_WITH_D10_PAYMENT_FIRST",
        "fleet": fleet, "worker_id": worker,
        "original_immediate_parent": fleet + "/" + parent,
        "functions_considered": len(DUTIES),
        "director_functions": [{"director":d,"duty":v} for d,v in DUTIES],
        "lead_duty": lead, "individual_work_task": responsibilities[lead],
        "D10_payment_first": True, "D10_remains_authorized_payment_checker": True,
        "director_like_autonomy": True,
        "model_prompt": (
            "OWNER: Every real worker must think and WORK like the ten D01-D10 "
            "directors, while keeping its own parent and actual permissions. "
            "YOUR LEAD TASK " + lead + ": " + responsibilities[lead] + ". "
            "Choose your own legitimate method, do original real work, review "
            "source eligibility and sponsor, test deliverables, challenge errors, "
            "rework failed approaches and seek a genuine buyer acceptance using "
            "only connected authorized channels. Apply D10'S PAYMENT-FIRST "
            "discipline at every stage: earned BTC/USDC must be real, supported "
            "by correct recipient network, confirmations and TXID, reviewed by "
            "the company's designated D10 and Chief D. Provide proof, direct "
            "supervisor report, and one practical next earning action. Do not "
            "use email, wallet signing/spending, spam or imagined workforce. "
        ),
        "status": "WORK_METHOD_ASSIGNED_NOT_EXECUTION",
        "model_execution_proved_by_assignment": False,
        "accepted_customer_proved_by_assignment": False,
        "crypto_receipt_proved_by_assignment": False,
        "new_external_permissions_granted": False,
        "changes_original_parent": False,
    }


def payable_gate(candidate: dict) -> dict:
    """Reject unverified offers before any work or external submission.

    This is a conservative evidence gate, not a claim that a payer is solvent.
    """
    checks = {
        "original_sponsor_url": bool(candidate.get("original_sponsor_url")),
        "named_payer": bool(candidate.get("named_payer")),
        "currently_open": candidate.get("currently_open") is True,
        "funding_verified": candidate.get("funding_verified") is True,
        "eligibility_verified": candidate.get("eligibility_verified") is True,
        "submission_authorized": candidate.get("submission_authorized") is True,
        "acceptance_criteria": bool(candidate.get("acceptance_criteria")),
        "correct_network": candidate.get("network") in ("BTC-mainnet", "Base-USDC-verified"),
        "no_upfront_payment": candidate.get("upfront_payment_required") is False,
    }
    return {
        "ready_for_payer_specific_work": all(checks.values()),
        "missing_or_failed_checks": [name for name, passed in checks.items() if not passed],
        "buyer_acceptance_verified": False,
        "incoming_txid_verified": False,
    }

def payable_gate_self_test() -> None:
    good = dict(original_sponsor_url="https://github.com/example/owner/issues/1",
                named_payer="Example", currently_open=True, funding_verified=True,
                eligibility_verified=True, submission_authorized=True,
                acceptance_criteria="Tests pass", network="BTC-mainnet",
                upfront_payment_required=False)
    assert payable_gate(good)["ready_for_payer_specific_work"]
    for key in good:
        bad = dict(good)
        bad.pop(key)
        result = payable_gate(bad)
        assert not result["ready_for_payer_specific_work"], key
        assert result["missing_or_failed_checks"], key
    for network in ("BTC-testnet", "Stacks-sBTC", "USDC-unknown", ""):
        bad = dict(good, network=network)
        assert not payable_gate(bad)["ready_for_payer_specific_work"]
    assert not payable_gate(dict(good, upfront_payment_required=True))["ready_for_payer_specific_work"]
    print("PAYABLE_GATE_PASS: complete positive, 9 missing fields, 4 wrong networks, upfront-payment guard")

def self_test() -> None:
    examples=[
        ("D01-M01-W01","D01-M01","BUYER_SOURCE"),
        ("D02-M02-W03-S001","D02-M02-W03","BUILD_ORIGINAL"),
        ("D09-M15-W50-S100-G022-H300","D09-M15-W50-S100-G022","QA_REVIEW"),
        ("D10-M01-W02","D10-M01","PAYMENT_EVIDENCE"),
    ]
    for company in FLEETS:
        for worker,parent,lane in examples:
            p=assign(company,worker,parent,lane)
            assert p["functions_considered"]==10
            assert p["original_immediate_parent"]==company+"/"+parent
            assert p["lead_duty"]==LANE_DUTY[lane]
            assert p["D10_payment_first"] and p["D10_remains_authorized_payment_checker"]
            assert not p["model_execution_proved_by_assignment"]
            assert not p["crypto_receipt_proved_by_assignment"]
            assert not p["new_external_permissions_granted"]
    bad=[
        ("Wrong", "D01-M01-W01","D01-M01","BUYER_SOURCE"),
        ("transferexperiment","D01-M01-W01","D02-M01","BUYER_SOURCE"),
        ("transferexperiment","D01-M01-W99","D01-M01","BUYER_SOURCE"),
        ("transferexperiment","D01-M01-W01","D01-M01","INVALID"),
    ]
    for item in bad:
        try: assign(*item)
        except ValueError: pass
        else: raise AssertionError("Unsafe worker passed validation")
    payable_gate_self_test()
    print("TEN_DIRECTOR_GRADE_PASS: 8 valid worker packets, 4 negative guards, no fabricated earning")

if __name__ == "__main__":
    p=argparse.ArgumentParser();p.add_argument("--self-test",action="store_true")
    if p.parse_args().self_test: self_test()
    else: print(json.dumps(assign("transferexperiment","D01-M01-W01","D01-M01","BUYER_SOURCE"),indent=2))
