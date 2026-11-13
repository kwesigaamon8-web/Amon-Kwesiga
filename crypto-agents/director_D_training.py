"""Real per-worker lesson from Director D: distinguish taught, learned, and dormant.

No prefilled acknowledgements. A lesson is graded only if THIS worker executes
an actual model inference using the available model and produces its own answer.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

LESSON_PATH = Path("crypto-agents/DIRECTOR_D_LESSON_TO_B.md")
LESSON_SUMMARY = (
    "Director D coordinates 10 operating directors, reviews original-source worker "
    "evidence, finds failures, allocates legitimate work and sends ONE truthful "
    "report to the OWNER. D09 checks asset/network/payment proof; D10 checks "
    "execution and software reliability. D cannot force independent agents to "
    "work or pay, create cryptocurrency by prompts, confirm payment without "
    "chain/account evidence, use keys, spend funds or claim dormant roles ran. "
    "A B worker reports to its one direct parent, not directly to D. "
    "A job link is not a contract; a promise is not received money."
)
QUESTION = (
    "After studying the lesson, answer IN YOUR OWN WORDS with exactly three "
    "short lines: CAN: what Director D actually helps you do; "
    "CANNOT: one limitation Director D has; PARENT: your actual reporting parent. "
    "Do not copy the lesson verbatim, invent training, or claim money."
)

def grade_answer(text, parent):
    """Conservative, transparent heuristic. Failing this is review-needed, not proof of ignorance."""
    answer = str(text or "").strip()
    lower = answer.lower()
    markers = all(re.search(r"(?m)^\s*" + re.escape(tag) + r"\s*:", answer, re.I)
                  for tag in ("CAN", "CANNOT", "PARENT"))
    correct_parent = bool(re.search(r"(?m)^\s*PARENT\s*:\s*.*" + re.escape(parent), answer, re.I))
    capability = any(term in lower for term in (
        "coordinat", "organis", "organiz", "assign", "delegat", "audit",
        "review", "verify", "check", "report", "monitor", "improv"))
    cannot_line = re.search(r"(?mi)^\s*CANNOT\s*:\s*(.{6,})", answer)
    limit_ok = bool(cannot_line) and any(term in cannot_line.group(1).lower() for term in (
        "force", "guarantee", "create", "make", "coin", "payment", "money",
        "fund", "sign", "key", "transfer", "spend", "wallet", "control",
        "fabricat", "invent", "without", "cannot", "fake"))
    return {
        "structure_markers_present": bool(markers),
        "actual_parent_correct": bool(correct_parent),
        "valid_D_capability_mentioned": bool(capability),
        "real_D_limit_mentioned": bool(limit_ok),
        "passed": bool(markers and correct_parent and capability and limit_ok),
    }

def teach_and_assess(model, worker_id, parent_id):
    evidence = {
        "order": "ORD-047",
        "worker_id": worker_id,
        "parent_id": parent_id,
        "lesson_file": str(LESSON_PATH),
        "lesson_accessible": False,
        "lesson_sha256": None,
        "model_execution_status": "not_run",
        "answer": None,
        "knowledge_check": None,
        "assessment": "not_run",
        "reported_learned": False,
        "limitation": "Assigned curriculum does not establish learning or model execution.",
    }
    try:
        raw = LESSON_PATH.read_bytes()
    except OSError as exc:
        evidence["assessment"] = "not_run_lesson_missing"
        evidence["limitation"] = str(exc)[:180]
        return evidence
    evidence["lesson_accessible"] = True
    evidence["lesson_sha256"] = hashlib.sha256(raw).hexdigest()
    if model is None:
        evidence["assessment"] = "not_run_model_unavailable"
        return evidence
    prompt = [
        {"role":"system","content":
            "You are one genuinely invoked B worker. Answer one Director D lesson check "
            "from given facts. No imaginary peers, external activity, or earned coins."},
        {"role":"user","content":
            "Worker "+worker_id+"; direct parent "+parent_id+". LESSON: "+LESSON_SUMMARY+
            " QUESTION: "+QUESTION},
    ]
    try:
        output = model(prompt, max_new_tokens=105, do_sample=False,
                       return_full_text=False)
        answer = output[0].get("generated_text", "")
        if isinstance(answer, list):
            answer = answer[-1].get("content", "")
        answer = str(answer or "").strip()
        if not answer:
            raise ValueError("Model returned empty training answer")
        evidence["model_execution_status"] = "model_completed"
        evidence["answer"] = answer[:1250]
        check = grade_answer(answer, parent_id)
        evidence["knowledge_check"] = check
        evidence["assessment"] = "passed" if check["passed"] else "needs_parent_review"
        evidence["reported_learned"] = bool(check["passed"])
        evidence["limitation"] = (
            "Passed a simple model-answer knowledge check; does not imply human understanding."
            if check["passed"] else
            "Model answered but the evidence did not pass all checks; parent review needed."
        )
    except Exception as exc:
        evidence["model_execution_status"] = "model_failed"
        evidence["assessment"] = "failed_model_inference"
        evidence["limitation"] = type(exc).__name__ + ": " + str(exc)[:200]
    return evidence

if __name__ == "__main__":
    good = (
        "CAN: D coordinates directors and reviews source evidence.\n"
        "CANNOT: D cannot create coins or confirm payment without proof.\n"
        "PARENT: D03-M02"
    )
    assert grade_answer(good, "D03-M02")["passed"]
    assert not grade_answer(good, "D04-M02")["passed"]
    assert not grade_answer("I learned everything", "D03-M02")["passed"]
    assert not teach_and_assess(None, "D03-M02-W01", "D03-M02")["reported_learned"]
    print("DIRECTOR_D_TRAINING_SELF_TEST_PASS")
