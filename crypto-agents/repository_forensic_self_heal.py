"""Finite B1/B2 repository-wide forensic audit, safe repair and proof loop.

Protects owner order, payments, secrets, business logic, and external systems.
Parses all tracked source files using real parsers where supported, classifies
risks, applies ONLY a no-semantics final-newline fix to allowlisted files, then
rechecks every repaired file. Outputs machine-readable evidence on every run.

It NEVER changes any owner directive, wallet, credentials, payment ledgers,
workflow permissions, user accounts or source code logic. Unsafe defects stay
in the report pending actual unit-tested and human-reviewed fixes.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "self-correction-evidence"
CODE_TYPES = {".py", ".js", ".mjs", ".cjs", ".json", ".yml", ".yaml",
              ".toml", ".sh", ".ps1", ".html", ".css"}
PARSED_TYPES = {".py", ".js", ".mjs", ".cjs", ".json", ".yml", ".yaml",
                ".toml", ".sh", ".html"}
FIX_TYPES = PARSED_TYPES | {".css", ".ps1"}
MAX_SAFE_CHANGES = 12
MAX_TEXT_BYTES = 1_500_000
OWNER = "crypto-agents/chief_D_owner_orders.json"
MIRROR = "crypto-agents/PUBLIC_AGENT_COMMAND.json"
SAFE_DIRS = ("crypto-agents/", "docs/")
PROTECTED = re.compile(
    r"(?i)(owner|command|directive|wallet|key|token|secret|receiv|"
    r"payment|invoice|balance|ledger|fund|account|transaction|"
    r"checkout|payout|sponsor|claim|private|credentials|address)"
)
LEAKS = (
    ("PRIVATE_KEY_PEM", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("CREDENTIAL_LIKE", re.compile(r"(?<![A-Za-z0-9_])(?:ghp_[A-Za-z0-9]{30,}|"
                                  r"github_pat_[A-Za-z0-9_]{50,}|xox[baprs]-[A-Za-z0-9-]{15,})")),
)
RISK_RULES = (
    ("UNVERIFIED_SCRIPT_PIPE", re.compile(r"\bcurl\b[^\n]{0,180}\|\s*(?:bash|sh)\b")),
    ("UNVERIFIED_WGET_PIPE", re.compile(r"\bwget\b[^\n]{0,180}\|\s*(?:bash|sh)\b")),
    ("SHELL_REMOTE_EXEC", re.compile(r"\b(?:subprocess|os)\.(?:Popen|system)\([^\n]{0,140}shell\s*=\s*True")),
)


def tracked_files(root: Path) -> list[str]:
    p = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True,
                       timeout=20, check=True)
    return sorted(s.decode("utf-8") for s in p.stdout.split(b"\x00") if s)


def parse_file(path: str, contents: str, *, node: str | None,
               yaml_available: bool) -> tuple[str, str | None]:
    suffix = Path(path).suffix.lower()
    try:
        if suffix == ".py":
            compile(contents, path, "exec")
        elif suffix == ".json":
            json.loads(contents)
        elif suffix in (".yml", ".yaml"):
            if not yaml_available:
                return "TOOL_MISSING", "PyYAML cannot parse YAML"
            import yaml
            yaml.compose(contents)
        elif suffix == ".toml":
            tomllib.loads(contents)
        elif suffix in (".js", ".mjs", ".cjs"):
            if not node:
                return "TOOL_MISSING", "Node runtime unavailable"
            # stdin supports browser ES module syntax without executing code.
            mode = "commonjs" if suffix == ".cjs" else "module"
            c = subprocess.run(
                [node, "--check", "--input-type=" + mode], input=contents,
                encoding="utf-8", capture_output=True, timeout=8,
                check=False)
            if c.returncode:
                return "SYNTAX_ERROR", "Node syntax check failed"
        elif suffix == ".sh":
            c = subprocess.run(["bash", "-n"], input=contents, encoding="utf-8",
                               capture_output=True, timeout=5, check=False)
            if c.returncode:
                return "SYNTAX_ERROR", "Bash syntax check failed"
        elif suffix == ".html":
            parser = HTMLParser(convert_charrefs=True)
            parser.feed(contents)
            parser.close()
        else:
            return "SCANNED_STATIC_ONLY", None
    except (SyntaxError, json.JSONDecodeError, ValueError, UnicodeError,
            OverflowError, Exception) as e:
        # Never log snippets containing possible secrets.
        return "SYNTAX_ERROR", type(e).__name__
    return "PARSED", None


def invariant_issues(root: Path) -> list[dict]:
    """Fail closed on contradictory authoritative and public owner commands."""
    try:
        c = json.loads((root / OWNER).read_text(encoding="utf-8"))
        p = json.loads((root / MIRROR).read_text(encoding="utf-8"))
        ident = c["current_owner_order_id"]
        latest = c["orders"][-1]
        checks = {
            "canonical_last_id": latest["id"] == ident,
            "public_id": p["command_id"] == ident,
            "exact_owner_instruction": latest["instruction"] == p["owner_command"],
            "chief_cascade": c["owner_prompt_cascade"]["owner_order_id"] == ident,
            "public_cascade": p["owner_prompt_cascade"]["owner_order_id"] == ident,
            "owner_authorship_mark": latest.get("origin") == "explicit_human_owner_conversation",
            "no_email_hard_guard": bool(p.get("strict_worker_customer_execution", {}).get("no_email")),
            "no_spend_hard_guard": bool(p.get("strict_worker_customer_execution", {}).get("no_spend_or_sign")),
        }
        return [{"category": "OWNER_COMMAND_INTEGRITY", "check": k,
                 "status": "PASS" if v else "BLOCKED_MANUAL_REVIEW"}
                for k,v in checks.items()]
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        return [{"category": "OWNER_COMMAND_INTEGRITY", "check": "read_canonical_pair",
                 "status": "BLOCKED_MANUAL_REVIEW"}]


def static_findings(path: str, contents: str) -> list[dict]:
    findings = []
    for label, regex in LEAKS + RISK_RULES:
        if regex.search(contents):
            findings.append({"type": label, "severity": "HIGH" if label in
                {"PRIVATE_KEY_PEM", "CREDENTIAL_LIKE"} else "REVIEW",
                "snippet_exposed": False})
    if path.startswith(".github/workflows/"):
        if "permissions:" not in contents:
            findings.append({"type": "WORKFLOW_PERMISSIONS_NOT_EXPLICIT",
                             "severity": "REVIEW", "snippet_exposed": False})
    return findings


def is_safe_newline_target(path: str, text: str, status: str) -> bool:
    return (
        status == "PARSED" and not text.endswith("\n")
        and Path(path).suffix.lower() in FIX_TYPES
        and any(path.startswith(x) for x in SAFE_DIRS)
        and not PROTECTED.search(path)
        and not path.startswith("crypto-agents/forensic/")
        and not path.startswith("crypto-agents/commercial-work/")
        and ".github/" not in path
    )


def audit(root: Path, do_safe_repair: bool = False, cap: int = MAX_SAFE_CHANGES):
    paths = tracked_files(root)
    node = shutil.which("node")
    try:
        import yaml
        yaml_available = True
    except ImportError:
        yaml_available = False
    rows = []
    candidates = []
    for rel in paths:
        full = root / rel
        if not full.is_file():
            continue
        suffix = full.suffix.lower()
        if suffix not in CODE_TYPES:
            continue
        raw = full.read_bytes()
        if len(raw) > MAX_TEXT_BYTES:
            rows.append({"path": rel, "parse": "TOO_LARGE", "byte_count": len(raw)})
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeError:
            rows.append({"path": rel, "parse": "NOT_UTF8", "byte_count": len(raw)})
            continue
        status, error = parse_file(rel, text, node=node, yaml_available=yaml_available)
        row = {"path": rel, "parse": status, "sha256_before": sha256(raw).hexdigest(),
               "findings": static_findings(rel, text), "safe_newline_candidate": False}
        if error:
            row["error_type"] = error
        if is_safe_newline_target(rel, text, status) and not row["findings"]:
            candidates.append(rel)
            row["safe_newline_candidate"] = True
        rows.append(row)
    changed = []
    repair_status = ("DRY_RUN" if not do_safe_repair
                     else "BLOCKED_TOO_MANY_CANDIDATES" if len(candidates) > cap
                     else "NO_CHANGE_NEEDED")
    if do_safe_repair and len(candidates) <= cap:
        indexed = {r["path"]: r for r in rows}
        for rel in candidates:
            p = root / rel
            initial = p.read_text(encoding="utf-8")
            if initial.endswith("\n"):
                continue
            final = initial + "\n"
            after, _ = parse_file(rel, final, node=node, yaml_available=yaml_available)
            if after != "PARSED":
                indexed[rel]["repair_retest"] = "BLOCKED"
                continue
            p.write_text(final, encoding="utf-8", newline="")
            changed.append(rel)
            indexed[rel]["repair_retest"] = "PASS"
            indexed[rel]["sha256_after"] = sha256(p.read_bytes()).hexdigest()
        if changed:
            repair_status = "SAFE_FINAL_NEWLINE_FIXED_AND_RETESTED"
    issues = invariant_issues(root)
    counts = dict(Counter(r["parse"] for r in rows))
    defects = [r for r in rows if r["parse"] in
               ("SYNTAX_ERROR", "TOOL_MISSING", "NOT_UTF8", "TOO_LARGE") or r.get("findings")]
    result = {
        "schema": "B1B2_REPOSITORY_FORENSIC_SELF_HEAL_V1",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "tracked_files_total": len(paths),
        "code_and_config_files_scanned": len(rows),
        "parse_status_counts": counts,
        "findings_count": len(defects),
        "defects": defects,
        "owner_command_checks": issues,
        "owner_command_guard_passed": all(x["status"] == "PASS" for x in issues),
        "safe_repair_candidates": candidates,
        "safe_repair_count": len(changed),
        "safe_repair_paths": changed,
        "safe_repair_state": repair_status,
        "semantic_rewrites_attempted": 0,
        "secrets_or_wallets_changed": False,
        "emails_or_external_posts_sent": False,
        "mining_or_crypto_transactions_performed": False,
        "actual_live_ai_workers_proven_by_code_audit": False,
        "real_crypto_income_proven_by_code_audit": False,
        "code_review_needed_for_nonmechanical_defects": True,
    }
    return result


def self_test():
    assert parse_file("test.py", "x=1\n", node=None, yaml_available=False)[0] == "PARSED"
    assert parse_file("test.py", "def = bad\n", node=None, yaml_available=False)[0] == "SYNTAX_ERROR"
    assert parse_file("test.json", '{"x":1}', node=None, yaml_available=False)[0] == "PARSED"
    assert parse_file("bad.json", '{"x":', node=None, yaml_available=False)[0] == "SYNTAX_ERROR"
    assert not is_safe_newline_target(OWNER, "{}", "PARSED")
    assert not is_safe_newline_target("crypto-agents/wallet_signer.py", "pass", "PARSED")
    assert is_safe_newline_target("crypto-agents/ordinary_source_test.py", "pass", "PARSED")
    assert not is_safe_newline_target(".github/workflows/deploy.yml", "x", "PARSED")
    assert not is_safe_newline_target("docs/example.html", "x\n", "PARSED")
    assert static_findings("some.py", "ghp_" + "a"*36)[0]["snippet_exposed"] is False
    assert len(static_findings("normal.py", "print('safe')")) == 0
    print("B1B2_FORENSIC_SELF_HEAL_REGRESSION_TESTS_PASS")


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--self-test", action="store_true")
    cli.add_argument("--repair-safe", action="store_true")
    args = cli.parse_args()
    self_test()
    if args.self_test:
        return
    result = audit(ROOT, do_safe_repair=args.repair_safe)
    OUT.mkdir(exist_ok=True, parents=True)
    (OUT / "repository-audit.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# B1/B2 source-wide self-correcting forensic review",
        "",
        "Scope: " + str(result["tracked_files_total"]) + " tracked files; "
        + str(result["code_and_config_files_scanned"]) + " code/config files scanned.",
        "Parser results: " + json.dumps(result["parse_status_counts"], sort_keys=True),
        "Owner order and mirror guards: "
        + ("PASS" if result["owner_command_guard_passed"] else "BLOCKED"),
        "Files with warnings/parse issues: " + str(result["findings_count"]),
        "Safe exact-last-newline corrections: " + str(result["safe_repair_count"]),
        "Repair state: " + result["safe_repair_state"],
        "",
        "## Source defects needing actual code review",
    ]
    for row in result["defects"][:80]:
        types = ",".join(f["type"] for f in row.get("findings", []))
        lines.append("- " + row["path"] + " — " + row["parse"] +
                     (" / " + types if types else "") +
                     " (no secret contents disclosed)")
    if len(result["defects"]) > 80:
        lines.append("- Additional flagged files are listed in repository-audit.json")
    lines.extend([
        "",
        "## Stop conditions",
        "- Never execute unknown source code while auditing; compile/parse only.",
        "- Never modify owner instructions, signing keys, payment routes, financial files or workflows automatically.",
        "- Never auto-fix semantic or security defects without a reviewed, reproducible test.",
        "- Never treat a passing source audit as real AI activity, customers, mining, or funds.",
        "- Safe fixes are additive final newlines only; each was parsed again, independently.",
    ])
    (OUT / "AUDIT_SUMMARY.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print("B1B2_REPOSITORY_SELF_HEAL", json.dumps({
        "scanned": result["code_and_config_files_scanned"],
        "findings": result["findings_count"],
        "guard_pass": result["owner_command_guard_passed"],
        "newlines_repaired": result["safe_repair_count"],
        "state": result["safe_repair_state"], "actual_paid_receipts_verified": False
    }))


if __name__ == "__main__":
    main()
