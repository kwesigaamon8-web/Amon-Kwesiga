"""Fifty distinct additional source-checking scouts for the B1/B2 fleet.
Separate matrix runners, bounded read-only verified-public-issue checks; no email,
wallet signing, unsolicited contact, paid commitments, or invented receipts.
"""
import argparse
import sys
from pathlib import Path
import ten_agent_fleet as fleet

FIFTY_AGENTS = {
    "B1-26": ("Database migration tools", "database migration bounty is:issue is:open"),
    "B1-27": ("PostgreSQL issue fixes", "postgres bounty is:issue is:open"),
    "B1-28": ("SQLite tooling", "sqlite bounty is:issue is:open"),
    "B1-29": ("Financial CSV importer", "csv import bounty is:issue is:open"),
    "B1-30": ("Expense categorization", "expense categorization bounty is:issue is:open"),
    "B1-31": ("Receipt parsing tools", "receipt parser bounty is:issue is:open"),
    "B1-32": ("Bank feed integrations", "bank api bounty is:issue is:open"),
    "B1-33": ("API error reporting", "api error bounty is:issue is:open"),
    "B1-34": ("Django maintenance", "django bounty is:issue is:open"),
    "B1-35": ("Flask services", "flask bounty is:issue is:open"),
    "B1-36": ("FastAPI testing", "fastapi bounty is:issue is:open"),
    "B1-37": ("Linux tools", "linux cli bounty is:issue is:open"),
    "B1-38": ("Packaging fixes", "python packaging bounty is:issue is:open"),
    "B1-39": ("Open-source grants tasks", "open source grant issue paid is:issue is:open"),
    "B1-40": ("Data quality tests", "data quality bounty is:issue is:open"),
    "B1-41": ("Financial data export", "financial export bounty is:issue is:open"),
    "B1-42": ("Exchange-rate API", "exchange rate api bounty is:issue is:open"),
    "B1-43": ("Digital invoice formats", "invoice xml bounty is:issue is:open"),
    "B1-44": ("Business reporting", "business intelligence bounty is:issue is:open"),
    "B1-45": ("Python performance", "python performance bounty is:issue is:open"),
    "B1-46": ("Open-source bug reproduction", "reproducible bug paid is:issue is:open"),
    "B1-47": ("Financial schema mapping", "accounting schema bounty is:issue is:open"),
    "B1-48": ("Local-first web tools", "offline app bounty is:issue is:open"),
    "B1-49": ("Command documentation", "readme documentation bounty is:issue is:open"),
    "B1-50": ("BTC payment proof checks", "btc transaction verification bounty is:issue is:open"),
    "B2-26": ("Base network integrations", "base network bounty is:issue is:open"),
    "B2-27": ("EVM blockchain explorer tools", "evm explorer bounty is:issue is:open"),
    "B2-28": ("USDC payment proofs", "usdc payment verifier bounty is:issue is:open"),
    "B2-29": ("Ethereum SDK documentation", "ethereum sdk bounty is:issue is:open"),
    "B2-30": ("Web3 API test coverage", "web3 api test bounty is:issue is:open"),
    "B2-31": ("Agent benchmarking", "agent benchmark bounty is:issue is:open"),
    "B2-32": ("AI red-team evaluation (authorized)", "llm evaluation bounty is:issue is:open"),
    "B2-33": ("Data annotation tooling", "annotation tool bounty is:issue is:open"),
    "B2-34": ("Python notebook cleanup", "jupyter notebook bounty is:issue is:open"),
    "B2-35": ("Documentation localization", "documentation localization bounty is:issue is:open"),
    "B2-36": ("NPM package fixes", "npm package bounty is:issue is:open"),
    "B2-37": ("Rust CLI bug fixes", "rust cli bounty is:issue is:open"),
    "B2-38": ("Go module bug fixes", "golang bounty is:issue is:open"),
    "B2-39": ("CI pipeline issue fixes", "github actions bounty is:issue is:open"),
    "B2-40": ("Docker tooling maintenance", "docker bounty is:issue is:open"),
    "B2-41": ("Browser extension bug fixes", "browser extension bounty is:issue is:open"),
    "B2-42": ("Accessibility audits", "wcag bounty is:issue is:open"),
    "B2-43": ("Markdown parser fixes", "markdown parser bounty is:issue is:open"),
    "B2-44": ("Open-source testing utilities", "test automation bounty is:issue is:open"),
    "B2-45": ("Public data APIs", "open data api bounty is:issue is:open"),
    "B2-46": ("Type definitions fixes", "typescript types bounty is:issue is:open"),
    "B2-47": ("SDK sample apps", "sdk example bounty is:issue is:open"),
    "B2-48": ("CLI release fixes", "release automation bounty is:issue is:open"),
    "B2-49": ("ETL data processing", "etl pipeline bounty is:issue is:open"),
    "B2-50": ("Technical tutorial work", "tutorial bounty is:issue is:open"),
}
assert len(FIFTY_AGENTS) == 50 and len(set(FIFTY_AGENTS)) == 50
fleet.AGENTS = FIFTY_AGENTS
fleet.OUT = Path("fifty-agent-reports")


def test():
    assert len([x for x in FIFTY_AGENTS if x.startswith("B1-")]) == 25
    assert len([x for x in FIFTY_AGENTS if x.startswith("B2-")]) == 25
    assert all("is:issue is:open" in q for _, q in FIFTY_AGENTS.values())
    sample = {
        "id": 2, "number": 10, "state": "open", "title": "Funded Python bounty",
        "body": "Buyer will assess original work before payment",
        "updated_at": fleet.now().isoformat(),
        "html_url": "https://github.com/example/another/issues/10",
        "repository_url": "https://api.github.com/repos/example/another",
    }
    assert fleet.classify(sample)["payout_amount_verified"] is False
    assert fleet.classify({**sample, "body": "Send me a fee first"}) is None
    print("PASS: fifty additional B1/B2 search workers have distinct jobs and safe classification")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=sorted(FIFTY_AGENTS))
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        test()
    elif args.audit is not None:
        sys.exit(fleet.audit(args.audit))
    elif args.agent:
        sys.exit(fleet.run_agent(args.agent))
    else:
        parser.error("Choose --agent, --audit or --self-test")
