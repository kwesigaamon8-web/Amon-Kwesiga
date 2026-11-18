"""One actual CPU-model inference per bounded, evidence-led B1/B2 worker.

Source is a first-party public job record. Model writes one skeptical, original
job review for real commercial decision-making. Not an account or an application.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.request

SOURCE = "https://musedin.com/api/role/job-f180"
FLEETS = {
    "B1": {"name": "transferexperiment",
           "role": "e-invoice task acceptance and narrow free API testing",
           "wallet": "bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z"},
    "B2": {"name": "BountyScoutAI",
           "role": "sponsor payment and worker eligibility diligence",
           "wallet": "bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9"}
}
OUT = Path("bounded-paid-shift-evidence")
MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"

def fetch_role(url=SOURCE):
    req = urllib.request.Request(url, headers={
        "Accept": "application/json", "User-Agent": "B1B2-OneRealAgent-TaskReview/1.0"})
    with urllib.request.urlopen(req, timeout=16) as response:
        payload = response.read(100001)
    if len(payload) > 100000:
        raise ValueError("Excessive source size")
    doc = json.loads(payload)
    role = doc.get("role")
    if doc.get("ok") is not True or not isinstance(role, dict):
        raise ValueError("Missing authentic job role record")
    if role.get("slug") != "job-f180":
        raise ValueError("Wrong job ID")
    if role.get("status") != "open":
        raise ValueError("Not a currently open job")
    return {
        "title": str(role.get("title") or "")[:150],
        "slug": role.get("slug"),
        "status": role.get("status"),
        "seats": role.get("seats"),
        "applicants": role.get("applicants"),
        "verified_only": role.get("verified_only"),
        "budget": role.get("budget"),
        "budget_custody_status": role.get("worker_budget"),
        "payout_rail": role.get("rail"),
        "poster": (role.get("poster") or {}).get("name"),
        "poster_past_paid_jobs": (role.get("poster_stats") or {}).get("paid"),
        "done": str(role.get("done") or "")[:340],
    }

def selftest():
    assert len(FLEETS) == 2
    assert all(v["wallet"].startswith("bc1q") and len(v["wallet"]) == 42 for v in FLEETS.values())
    assert MODEL and SOURCE.startswith("https://musedin.com/api/role/")
    print("BOUNDED_REAL_AI_SHIFT_SELFTEST_PASS")

def main(fleet):
    start = time.monotonic()
    name = FLEETS[fleet]["name"]
    print("WORKER_REAL_INFERENCE_START", fleet, name, flush=True)
    result = {
        "fleet": fleet, "company": name,
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": SOURCE,
        "original_role": FLEETS[fleet]["role"],
        "actual_model_completed": False,
        "auth_or_submission_executed": False,
        "buyer_hired": False,
        "owner_crypto_payment_verified": False,
        "owner_wallet_receive_only": FLEETS[fleet]["wallet"],
    }
    try:
        evidence = fetch_role()
        result["live_first_party_role"] = evidence
        result["source_fetch_status"] = "CONFIRMED_FIRST_PARTY_PUBLIC_JSON"
        print("WORKER_LIVE_JOB_SOURCE_OK", json.dumps(evidence), flush=True)
    except Exception as exc:
        result["source_fetch_status"] = "FAILED_NO_PAYER_ELIGIBILITY_VERIFIED"
        result["source_error"] = type(exc).__name__ + ": " + str(exc)[:160]
        evidence = None
        print("WORKER_LIVE_JOB_SOURCE_FAILED", result["source_error"], flush=True)
    try:
        import torch
        from transformers import pipeline
        torch.set_num_threads(2)
        gen = pipeline("text-generation", model=MODEL, device=-1)
        contract = json.dumps(evidence or {"status": "unavailable"}, ensure_ascii=True)
        prompt = (
            "You are a cautious paid-work assistant. Give ONE original, short "
            "evaluation for role " + FLEETS[fleet]["role"] +
            ". Source facts: " + contract[:1050] +
            ". State eligibility and payout blockers. A declared unescrowed budget "
            "is NOT money received. Avoid invented buyers. "
            "No emails, wallet signatures or fees. Answer in short sentences:"
        )
        generated = gen([
            {"role": "system", "content": "You are a careful real paid-task eligibility reviewer. Never invent buyers, money or account actions."},
            {"role": "user", "content": prompt}
        ], max_new_tokens=96, do_sample=False, return_full_text=False)
        output = generated[0].get("generated_text", "")
        if isinstance(output, list):
            output = " ".join(str(x.get("content") or "") for x in output)
        output = str(output).strip()
        if not output:
            raise ValueError("Empty real-model response")
        result.update({"actual_model_completed": True,
                       "model_id": MODEL,
                       "model_output": output[:1300],
                       "model_output_sha256": hashlib.sha256(output.encode()).hexdigest(),
                       "worker_result": "ORIGINAL_DRAFT_NEEDS_INDEPENDENT_VERIFICATION",
                       "source_is_guaranteed_escrow": False,
                       "new_payment_receipts": []})
        print("WORKER_REAL_MODEL_COMPLETED", fleet, len(output), flush=True)
    except Exception as exc:
        result["model_status"] = "FAILED_NO_MODEL_COMPLETION"
        result["model_error"] = type(exc).__name__ + ": " + str(exc)[:240]
        print("WORKER_REAL_MODEL_FAILED", fleet, result["model_error"], flush=True)
    result["elapsed_seconds"] = round(time.monotonic() - start, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / (fleet + "-worker.json")).write_text(json.dumps(result, indent=2) + "\n")
    print("BOUNDED_SHIFT_RESULT", json.dumps({
        "fleet": fleet,
        "source_status": result["source_fetch_status"],
        "model_completed": result["actual_model_completed"],
        "buyer_hired": result["buyer_hired"],
        "owner_crypto_payment_verified": result["owner_crypto_payment_verified"],
        "elapsed_seconds": result["elapsed_seconds"],
    }), flush=True)
    if not result["actual_model_completed"]:
        raise SystemExit(1)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--fleet", choices=FLEETS.keys())
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        selftest()
    elif not a.fleet:
        p.error("--fleet required")
    else:
        main(a.fleet)
