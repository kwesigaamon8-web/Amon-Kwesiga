"""B1/B2 expanded fleet: 900 individually executed, finite OS research processes.
Thirty separate scheduled shard jobs each fetch ONE source snapshot, then spawn 30
distinct bounded child processes to classify a different GitHub issue/search slot.
This is honest deterministic source triage, NOT 900 live LLMs or paid work.
No email, external posting, paid commitment, wallet signing or financial transfers.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

SHARDS = [f"{company}-S{i:02d}" for company in ("B1", "B2") for i in range(1, 16)]
# The 30 scheduled worker shards now screen explicit buyer/service demand,
# not generic issue traffic. Matches remain unverified prospects until source/payer checks.
KEYWORDS = [
    "csv", "data cleaning", "invoice", "reconciliation", "python",
    "automation", "testing", "bugfix", "api", "website",
    "javascript", "documentation", "software", "data migration", "blockchain",
]
SPECIALTIES = [
    "payer evidence", "payment terms", "Uganda eligibility", "original scope",
    "acceptance criteria", "reproducible testing", "copyright and licensing",
    "source freshness", "scam warnings", "next lawful action",
]
TYPES = ["source triage", "risk review", "acceptance review"]
LIMIT = datetime.now(timezone.utc) - timedelta(days=120)
REWARD = re.compile(r"\b(bounty|reward|paid|payment|funded|compensation|usdc|btc|\$[0-9]+)\b", re.I)
SCAM = re.compile(
    r"(seed phrase|private key|send (?:(?:us|me) )?(?:a )?(?:deposit|fee)(?: first)?|"
    r"pay (?:a |the )?(?:fee|deposit) first|connect your wallet to claim|"
    r"guaranteed (?:profit|income))", re.I)
ROOT = Path("thousand-fleet-evidence")

def current_owner_order():
    """Only the user-controlled, authenticated repository files issue commands."""
    public = json.loads(Path("crypto-agents/PUBLIC_AGENT_COMMAND.json").read_text(encoding="utf-8"))
    chief = json.loads(Path("crypto-agents/chief_D_owner_orders.json").read_text(encoding="utf-8"))
    ident = public.get("command_id")
    if not ident or ident != chief.get("current_owner_order_id"):
        raise ValueError("Chief D order disagrees with public worker order")
    if not chief.get("orders") or chief["orders"][-1].get("id") != ident:
        raise ValueError("Most recent owner instruction is missing or stale")
    if "NO_EMAILS_OF_ANY_KIND_FOR_THIS_CRYPTO_WORKFLOW" not in public.get("hard_constraints", []):
        raise ValueError("Email restriction missing from authenticated owner order")
    strict = public.get("strict_worker_customer_execution")
    # The customer-conversion protocol is a standing signed owner instruction.
    # It remains enforceable after a NEW owner order (e.g. BTC research).
    # Do not require the protocol's originating order to be the latest order;
    # authenticate its ID against the actual historical Chief D owner ledger.
    historic_owner_ids = {x.get("id") for x in chief["orders"]}
    if (not strict or strict.get("owner_order_id") not in historic_owner_ids
            or not strict.get("no_email")
            or not strict.get("duplicate_prevention")
            or not strict.get("no_spend_or_sign")):
        raise ValueError("Standing buyer protocol not authenticated to an owner order")
    path = Path(strict.get("prompt_path", ""))
    if not path.is_file():
        raise ValueError("Strict buyer execution protocol file is missing")
    prompt = path.read_text(encoding="utf-8")
    for required in ("ONE LEAD, ONE OWNER, ONE PROPOSAL", "NO GMAIL", "TXID", "NOT_SENT"):
        if required not in prompt.upper():
            raise ValueError("Strict work protocol missing requirement: " + required)
    return ident


def utc():
    return datetime.now(timezone.utc).isoformat()

def parse_date(raw):
    try:
        d = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None

def issue_assessment(issue, worker):
    """Independent deterministic assessment, never an LLM or payer confirmation."""
    title = str(issue.get("title") or "")[:200]
    body = str(issue.get("body") or "")[:4000]
    url = str(issue.get("html_url") or "")
    updated = parse_date(issue.get("updated_at"))
    signal = title + "\n" + body
    issues = []
    if issue.get("state") != "open" or issue.get("pull_request"):
        issues.append("not_open_issue")
    if not url.startswith("https://github.com/"):
        issues.append("not_original_github_link")
    # The previous fleet counted our own coordination issue as a possible buyer.
    # Suppress internal owner issues and third-party bounty mirrors before any lead tally.
    if re.match(r"^https://github\.com/kwesigaamon8-web/Amon-Kwesiga/issues/", url, re.I):
        issues.append("owner_repository_not_external_buyer")
    if re.search(r"/(?:bounty-plaza|bounty-bot)/issues/", url, re.I):
        issues.append("aggregated_repost_not_original_buyer")
    if not updated or updated < LIMIT:
        issues.append("stale_or_missing_date")
    if not REWARD.search(signal):
        issues.append("no_explicit_payment_language")
    if SCAM.search(signal):
        issues.append("scam_warning")
    if not issue.get("number") or not issue.get("repository_url"):
        issues.append("missing_original_source_fields")
    potential = not issues
    return {
        "issue_id": issue.get("id"),
        "source_url": url if url.startswith("https://github.com/") else "",
        "title": title,
        "source_last_updated": issue.get("updated_at"),
        "unique_specialty": worker["specialty"],
        "review_type": worker["review_type"],
        "visible_payment_language": bool(REWARD.search(signal)),
        "exclusion_reasons": issues,
        "possible_paid_lead_unverified": potential,
        "payer_verified": False,
        "payment_amount_verified": False,
        "owner_eligibility_verified": False,
        "customer_acceptance_verified": False,
        "incoming_crypto_verified": False,
        "original_issue_refetched": False,
        "next_action": "Verify original open issue, payer, exact reward, eligibility, acceptance terms and asset/network before any external claim",
    }

def role(shard, number):
    if shard not in SHARDS or number < 1 or number > 30:
        raise ValueError("Invalid shard/ordinal")
    return {
        "id": f"{shard}-W{number:02d}",
        "shard": shard,
        "specialty": SPECIALTIES[(number-1) % len(SPECIALTIES)],
        "review_type": TYPES[(number-1) // len(SPECIALTIES)],
        "slot": number,
        "reports_to": shard,
    }

def execute_specific_ordered_task(issue, snapshot, worker):
    """Actually compute a per-role result from source evidence, not just echo a role ID.
    A missing source triggers real diagnostic work, never a fake customer review.
    """
    if issue is None:
        err = snapshot.get("error") or (
            "NO_MATCHING_ISSUE_IN_WORKER_SLOT" if snapshot.get("fetch_status") == "ok"
            else "NO_SOURCE_ERROR_CAPTURED")
        data = {
            "action": "SOURCE_FAILURE_DIAGNOSIS", "worker_specialty": worker["specialty"],
            "source_query_examined": snapshot.get("source_query", ""),
            "observed_fetch_status": snapshot.get("fetch_status", "absent"),
            "observed_error": err, "work_result": "BLOCKED_NO_ORIGINAL_CUSTOMER_SOURCE",
            "corrective_action": ("Retry an authorized public source with bounded response size, "
                                  "check original issue URL, do not claim contacted customers"),
            "verified_external_customer": False, "contact_authorized": False,
        }
    else:
        title = str(issue.get("title") or "")
        body = str(issue.get("body") or "")[:4000]
        signal = title + "\n" + body
        checks = {
            "open_issue": issue.get("state") == "open" and not issue.get("pull_request"),
            "original_url_is_github": str(issue.get("html_url") or "").startswith("https://github.com/"),
            "payment_phrase_present": bool(REWARD.search(signal)),
            "scam_phrase_detected": bool(SCAM.search(signal)),
            "scope_or_deliverable_mentioned": bool(re.search(r"\b(scope|deliverable|requirements?|implement|fix|csv|code|test)\b", signal, re.I)),
            "acceptance_criteria_mentioned": bool(re.search(r"\b(acceptance|accept|verify|verification|tests?|reproduce|expected)\b", signal, re.I)),
            "public_deadline_mentioned": bool(re.search(r"\b(deadline|closing|due date|expires?)\b", signal, re.I)),
        }
        speciality = worker["specialty"]
        review = worker["review_type"]
        special_check = {
            "payer evidence": checks["payment_phrase_present"],
            "payment terms": bool(re.search(r"\b(escrow|reward|payment|paid|bounty)\b", signal, re.I)),
            "Uganda eligibility": bool(re.search(r"\b(global|worldwide|Uganda|remote|anywhere)\b", signal, re.I)),
            "original scope": checks["scope_or_deliverable_mentioned"],
            "acceptance criteria": checks["acceptance_criteria_mentioned"],
            "reproducible testing": bool(re.search(r"\b(test|reproducible|fixture|pytest|unittest)\b", signal, re.I)),
            "copyright and licensing": bool(re.search(r"\b(licen[cs]e|MIT|Apache|GPL|copyright)\b", signal, re.I)),
            "source freshness": bool(parse_date(issue.get("updated_at")) and parse_date(issue.get("updated_at")) >= LIMIT),
            "scam warnings": checks["scam_phrase_detected"],
            "next lawful action": bool(issue.get("number") and issue.get("repository_url")),
        }.get(speciality, False)
        data = {
            "action": "SPECIFIC_PUBLIC_BUYER_SOURCE_ASSESSMENT",
            "source_url_reviewed": issue.get("html_url", ""),
            "source_issue_id_reviewed": issue.get("id"),
            "assigned_review_type": review, "worker_specialty": speciality,
            "actual_rule_checks_executed": checks,
            "individual_specialty_rule_result": special_check,
            "work_result": ("UNVERIFIED_CANDIDATE_NEEDS_ORIGINAL_PAYER_CHECK"
                            if checks["payment_phrase_present"] and not checks["scam_phrase_detected"]
                            else "NOT_A_QUALIFIED_BUYER_REQUEST"),
            "verified_external_customer": False, "contact_authorized": False,
            "next_evidence_gate": ("Inspect original request and payer evidence and current platform terms; "
                                   "no direct messages, no self-assigned paid work"),
        }
    data["evidence_sha256"] = hashlib.sha256(
        json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    return data


def child(shard, number, root):
    worker = role(shard, number)
    snapshot_file = root / shard / "snapshot.json"
    snapshot = json.loads(snapshot_file.read_text(encoding="utf-8"))
    items = snapshot.get("items") or []
    # Unique issue slot in each shard, never pretend an absent issue exists.
    issue = items[number-1] if len(items) >= number else None
    # Read the complete authoritative owner instruction, not merely the order ID.
    public = json.loads(Path("crypto-agents/PUBLIC_AGENT_COMMAND.json").read_text(encoding="utf-8"))
    prompt = Path("crypto-agents/customer-acquisition/OWNER_STRICT_CUSTOMER_WORKER_PROMPT.md").read_text(encoding="utf-8")
    if snapshot.get("owner_order_id", "self-test-only") not in ("self-test-only", public["command_id"]):
        raise ValueError("Worker received stale or mismatched order")
    owner_instruction = str(public["owner_command"])
    if (not owner_instruction.strip()
            or public.get("command_id") != current_owner_order()):
        raise ValueError("Child received unauthenticated or blank current owner order")
    actual_task = execute_specific_ordered_task(issue, snapshot, worker)
    result = {
        "owner_instruction_sha256": hashlib.sha256(owner_instruction.encode("utf-8")).hexdigest(),
        "strict_prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "order_text_actually_read": True,
        "actual_distinct_ordered_task": actual_task,
        "worker_id": worker["id"],
        "shard": shard,
        "company": shard[:2],
        "pid": os.getpid(),
        "parent_pid": os.getppid(),
        "execution": "separate real Python OS subprocess",
        "ai_inference_completed": False,
        "task": worker,
        "source_query": snapshot["source_query"],
        "snapshot_search_success": snapshot["fetch_status"] == "ok",
        "owner_order_id": snapshot.get("owner_order_id", "self-test-only"),
        "original_issue_source_independently_refetched": False,
        "source_issue_seen": bool(issue),
        "strict_owner_customer_prompt_source": "crypto-agents/customer-acquisition/OWNER_STRICT_CUSTOMER_WORKER_PROMPT.md",
        "customer_contact_status": "NOT_SENT",
        "external_paid_proposals_submitted": 0,
        "assessment": issue_assessment(issue, worker) if issue else None,
        "worker_status": "reviewed_snapshot_issue" if issue else "no_issue_for_slot",
        "verified_paid_work": 0,
        "new_wallet_receipts_verified": 0,
        "emails_read_or_sent": 0,
        "external_applications_or_posts": 0,
        "wallet_transactions": 0,
        "executed_utc": utc(),
    }
    path = root / shard / f"{worker['id']}.json"
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"worker": worker["id"], "status": result["worker_status"]}))
    return 0

def fetch_snapshot(shard):
    company = shard[:2]
    num = int(shard[-2:])
    keyword = KEYWORDS[num-1]
    # GitHub's native OR search has been checked for customer-demand vocabulary.
    # One original-source snapshot per shard; no unsolicited contact is sent.
    query = f'{keyword} (paid OR bounty OR reward) is:issue is:open'
    if company == "B2" and num in (1, 2, 6, 10, 15):
        query += " usdc"
    # Each shard requires only 30 records. The previous 50-record JSON response
    # was cut at 900,000 bytes, causing JSONDecodeError and 360 no-source workers.
    url = "https://api.github.com/search/issues?" + urllib.parse.urlencode({
        "q": query, "per_page": 30, "sort": "updated", "order": "desc"
    })
    header = {
        "User-Agent": "B1B2-nine-hundred-process-fleet/1.0",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GH_TOKEN", "")
    if token:
        header["Authorization"] = "Bearer " + token
    snap = {
        "shard": shard,
        "source_query": query,
        "fetch_status": "error",
        "error": None,
        "items": [],
        "source_type": "GitHub search snapshot; NOT independently fetched original issue",
        "timestamp_utc": utc(),
    }
    try:
        request = urllib.request.Request(url, headers=header)
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = response.read(8_000_001)
        if len(payload) > 8_000_000:
            raise ValueError("github_search_response_over_8MB")
        data = json.loads(payload)
        if not isinstance(data.get("items"), list):
            raise ValueError("github_search_missing_items")
        snap["items"] = [
            {k: i.get(k) for k in ("id", "title", "body", "html_url", "number",
                                    "repository_url", "updated_at", "state", "pull_request")}
            for i in data.get("items", []) if isinstance(i, dict)
        ][:50]
        snap["fetch_status"] = "ok"
        snap["payload_bytes"] = len(payload)
    except (OSError, ValueError, urllib.error.HTTPError, urllib.error.URLError) as ex:
        snap["error"] = type(ex).__name__ + (
            f":{ex.code}" if isinstance(ex, urllib.error.HTTPError) else "")
    return snap

def run_shard(shard, root):
    if shard not in SHARDS:
        raise ValueError("Unrecognized shard")
    target = root / shard
    target.mkdir(parents=True, exist_ok=True)
    owner_order_id = current_owner_order()
    snap = fetch_snapshot(shard)
    snap["owner_order_id"] = owner_order_id
    (target / "snapshot.json").write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
    executions = []
    # Spawn a separate OS process for every individual role and capture its exit code.
    # Keep max concurrency to 4 per runner rather than 30.
    def spawn(i):
        cmd = [sys.executable, str(Path(__file__).resolve()), "child",
               "--shard", shard, "--worker", str(i), "--root", str(root.resolve())]
        try:
            run = subprocess.run(cmd, capture_output=True, text=True, timeout=12, check=False)
            return {"worker": role(shard, i)["id"], "exit_code": run.returncode,
                    "stdout": run.stdout[-250:], "stderr": run.stderr[-350:]}
        except subprocess.TimeoutExpired:
            return {"worker": role(shard, i)["id"], "exit_code": -1, "error": "child_timeout"}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        executions = list(pool.map(spawn, range(1, 31)))
    all_success = all(x["exit_code"] == 0 for x in executions)
    manifest = {
        "shard": shard, "source_fetch": snap["fetch_status"],
        "owner_order_id": owner_order_id,
        "source_error": snap["error"], "snapshot_issue_count": len(snap["items"]),
        "worker_attempts": 30,
        "child_process_successes": sum(x["exit_code"] == 0 for x in executions),
        "child_process_failures": sum(x["exit_code"] != 0 for x in executions),
        "child_statuses": executions,
        "finish_utc": utc(),
        "all_30_subprocesses_finished": all_success,
    }
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "child_statuses"}))
    return 0 if all_success else 1

def audit(root):
    owner_order_id = current_owner_order()
    records = []
    errors = []
    for shard in SHARDS:
        base = root / shard
        manifest = base / "manifest.json"
        if not manifest.exists():
            errors.append(f"missing_manifest:{shard}")
            continue
        info = json.loads(manifest.read_text(encoding="utf-8"))
        if info.get("owner_order_id") != owner_order_id:
            errors.append(f"wrong_owner_order:{shard}")
        if info.get("child_process_successes") != 30:
            errors.append(f"missing_subprocess:{shard}")
        for idx in range(1, 31):
            wid = role(shard, idx)["id"]
            file = base / (wid + ".json")
            if not file.is_file():
                errors.append(f"missing_report:{wid}")
                continue
            data = json.loads(file.read_text(encoding="utf-8"))
            if data.get("owner_order_id") != owner_order_id:
                errors.append(f"worker_missed_owner_order:{wid}")
            if data.get("worker_id") != wid or not isinstance(data.get("pid"), int):
                errors.append(f"invalid_identity:{wid}")
            if data.get("verified_paid_work") or data.get("new_wallet_receipts_verified"):
                errors.append(f"unsupported_payment_claim:{wid}")
            if data.get("emails_read_or_sent") or data.get("external_applications_or_posts") or data.get("wallet_transactions"):
                errors.append(f"unauthorized_external_action:{wid}")
            records.append(data)
    # Dedupe possible prospects across company/shard overlaps so a buyer does not
    # become 30 invented clients or receive repeated solicitations.
    prospect_urls = {}
    for record in records:
        assessment = record.get("assessment") or {}
        url = assessment.get("source_url")
        if assessment.get("possible_paid_lead_unverified") and url:
            prospect_urls.setdefault(url, {
                "source_url": url,
                "title": assessment.get("title", ""),
                "first_screening_worker": record["worker_id"],
                "payer_verified": False,
                "buyer_contact_authorized": False,
                "payment_received_verified": False,
            })
    report = {
        "distinct_preliminary_prospect_urls": len(prospect_urls),
        "preliminary_prospects_NOT_verified_customers": list(prospect_urls.values())[:20],
        "owner_order_id": owner_order_id,
        "expected_new_workers": 900,
        "independent_child_reports": len(records),
        "independent_completed_processes": len(records),
        "unique_worker_ids": len({r["worker_id"] for r in records}),
        "roles_by_company": {
            code: sum(r.get("company") == code for r in records)
            for code in ("B1", "B2")
        },
        "snapshot_issues_inspected": sum(r.get("source_issue_seen", False) for r in records),
        "source_snapshot_failures": sum(
            (not r.get("snapshot_search_success", False)) for r in records),
        "models_executed": 0,
        "paid_jobs_verified_by_this_fleet": 0,
        "crypto_deposits_verified_by_this_fleet": 0,
        "audited_utc": utc(),
        "errors": errors[:100],
        "pass": len(records) == 900 and len({r["worker_id"] for r in records}) == 900 and not errors,
        "truth_in_reporting": "Distinct executed child OS processes; NOT 900 live LLMs, not confirmed paid opportunities, no original-source refetch",
    }
    root.mkdir(parents=True, exist_ok=True)
    (root / "audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return 0 if report["pass"] else 1

def self_test():
    assert current_owner_order() == json.loads(
        Path("crypto-agents/PUBLIC_AGENT_COMMAND.json").read_text(encoding="utf-8")
    )["command_id"]
    assert len(SHARDS) == 30 and len({role(s,i)["id"] for s in SHARDS for i in range(1,31)}) == 900
    assert all(role(s,i)["reports_to"] == s for s in SHARDS for i in range(1,31))
    example = {
        "id": 4, "number": 7, "state": "open", "title": "Paid Python bounty",
        "body": "Bounty paid after work accepted",
        "html_url": "https://github.com/example/public/issues/7",
        "repository_url": "https://api.github.com/repos/example/public",
        "updated_at": utc(),
    }
    check = issue_assessment(example, role("B1-S01", 1))
    assert check["possible_paid_lead_unverified"] and not check["payer_verified"]
    assert "owner_repository_not_external_buyer" in issue_assessment(
        {**example, "html_url": "https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/9"},
        role("B1-S01", 1))["exclusion_reasons"]
    assert "aggregated_repost_not_original_buyer" in issue_assessment(
        {**example, "html_url": "https://github.com/alfrexo95/bounty-bot/issues/27"},
        role("B2-S01", 1))["exclusion_reasons"]
    assert "scam_warning" in issue_assessment(
        {**example, "body": "Bounty, send a deposit first"},
        role("B2-S01", 1))["exclusion_reasons"]
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        d = folder / "B1-S01"
        d.mkdir()
        snap = {"shard": "B1-S01", "source_query": "test bounty",
                "fetch_status": "ok", "items": [example]}
        (d / "snapshot.json").write_text(json.dumps(snap))
        assert child("B1-S01", 1, folder) == 0
        saved = json.loads((d / "B1-S01-W01.json").read_text())
        assert saved["source_issue_seen"] and saved["pid"] > 0
        assert saved["order_text_actually_read"]
        assert saved["actual_distinct_ordered_task"]["action"] == "SPECIFIC_PUBLIC_BUYER_SOURCE_ASSESSMENT"
        assert saved["actual_distinct_ordered_task"]["evidence_sha256"]
    print("PASS: 900 unique role allocations, independent child execution, and truthful screening")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("self-test", "shard", "child", "audit"))
    parser.add_argument("--shard", choices=SHARDS)
    parser.add_argument("--worker", type=int)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    if args.mode == "self-test":
        self_test()
    elif args.mode == "shard":
        if not args.shard:
            parser.error("--shard required")
        sys.exit(run_shard(args.shard, args.root))
    elif args.mode == "child":
        if not args.shard or args.worker is None:
            parser.error("--shard and --worker required")
        sys.exit(child(args.shard, args.worker, args.root))
    elif args.mode == "audit":
        sys.exit(audit(args.root))
