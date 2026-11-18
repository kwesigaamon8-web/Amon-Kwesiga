"""Load the latest public owner WORK order into each real worker invocation.

This uses a read-only owner-controlled manifest. It does not start billions
of workers or grant external-account, email, wallet, or paid-spend permissions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_MANIFEST = Path(__file__).resolve().parent / "PUBLIC_AGENT_COMMAND.json"
EXPECTED_CONFIGURED_ROLES = 775_000_000_000


def load_work_contract(manifest_path: Path | str = DEFAULT_MANIFEST) -> dict:
    data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    order = data["work_shorthand_2026_11_18"]
    updated = order["owner_updated_exact_definition_2026_11_18_120915z"]
    method = order["owner_amendment_2026_11_18_120828z"]
    roles = updated["latest_requested_workforce_roles"]
    if roles != EXPECTED_CONFIGURED_ROLES:
        raise ValueError("Stale WORK definition: conceptual worker-role target changed")
    if not updated["no_email_and_wallet_restrictions_remain"]:
        raise ValueError("Owner no-email/no-wallet-signing constraints not inherited")
    if len(method.get("mandatory_per_task_checklist", [])) < 7:
        raise ValueError("Incomplete owner per-task careful-work instruction")
    if "NOT a count of active" not in updated["distinctions"]:
        raise ValueError("Role target is being confused with running processes")

    return {
        "owner_command": "WORK",
        "conceptual_role_target": roles,
        "owner_work_amendment": "2026-11-18T12:09:15Z",
        "manifest": str(manifest_path),
        "model_prompt": (
            "LATEST OWNER ORDER: WORK means TAKE THE TIME NEEDED FOR EACH TASK, "
            "first review available previous orders, actual failed attempts and "
            "public canonical context. Use the OWNER'S REQUESTED 775,000,000,000 "
            "CONFIGURED ROLE HIERARCHY to coordinate only genuinely executable "
            "B1/B2/Chief D workers. These are NOT 775B online AI agents or miners. "
            "Verify original payer/funding/eligibility and permitted submission "
            "before building, then make ORIGINAL tested work, independently QA "
            "the deliverable, use approved contact channels, seek acceptance, "
            "and attribute only independently proven owner-entitled correct-chain "
            "BTC or USDC receipts with TXID to income. If blocked, record the "
            "precise failure and change the source or strategy. NEVER use email, "
            "wallet signing/spending, unsafe mining, spam, invented payer claims "
            "or fabricated worker processes. Report actual evidence to your "
            "one parent, director and Chief D. "
        ),
        "actual_worker_execution_proven_by_reading": False,
        "confirmed_crypto_payment_proven_by_reading": False,
    }


def self_test():
    obj = load_work_contract()
    assert obj["conceptual_role_target"] == EXPECTED_CONFIGURED_ROLES
    assert "TAKE THE TIME" in obj["model_prompt"]
    assert "NOT 775B online" in obj["model_prompt"]
    assert "NEVER use email" in obj["model_prompt"]
    assert obj["confirmed_crypto_payment_proven_by_reading"] is False
    # Negative controls: stale role count or weakened no-email rule fail closed.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        data = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        d = data["work_shorthand_2026_11_18"]["owner_updated_exact_definition_2026_11_18_120915z"]
        d["latest_requested_workforce_roles"] = 750_377_265_360
        testfile = Path(tmp) / "stale.json"
        testfile.write_text(json.dumps(data), encoding="utf-8")
        try:
            load_work_contract(testfile)
        except ValueError as exc:
            assert "Stale WORK" in str(exc)
        else:
            raise AssertionError("Stale owner work target must fail")
        d["latest_requested_workforce_roles"] = EXPECTED_CONFIGURED_ROLES
        d["no_email_and_wallet_restrictions_remain"] = False
        testfile.write_text(json.dumps(data), encoding="utf-8")
        try:
            load_work_contract(testfile)
        except ValueError as exc:
            assert "no-email" in str(exc)
        else:
            raise AssertionError("Weak no-email restriction must fail")
    print("OWNER_WORK_CONTRACT_PASS 775000000000 configured; careful tasks; no email/wallet spending; no fake model counts")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    opts = parser.parse_args()
    if opts.self_test:
        self_test()
    else:
        print(json.dumps(load_work_contract(), indent=2))
