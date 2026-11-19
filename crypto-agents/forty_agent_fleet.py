"""Forty additional independent read-only B1/B2 scouts, above the original 10.
Each scout runs as one separate GitHub Actions matrix job using shared tested engine.
No inference-model claim, emails, wallet signing, outreach or asserted earnings.
"""
import argparse
import sys
from pathlib import Path
import ten_agent_fleet as fleet

EXTRA_AGENTS = {
    "B1-06": ("BTC Lightning integrations", "lightning network bounty is:issue is:open"),
    "B1-07": ("Bitcoin wallet user interface", "bitcoin wallet paid is:issue is:open"),
    "B1-08": ("Blockchain transaction parsers", "bitcoin transaction bounty is:issue is:open"),
    "B1-09": ("Open-source bug bounties", "bugfix bounty is:issue is:open"),
    "B1-10": ("Python API integrations", "python api paid is:issue is:open"),
    "B1-11": ("Command-line tool development", "cli tool bounty is:issue is:open"),
    "B1-12": ("Data transformation scripts", "data transformation bounty is:issue is:open"),
    "B1-13": ("JSON schema validation", "json schema bounty is:issue is:open"),
    "B1-14": ("Financial reporting tools", "finance reporting bounty is:issue is:open"),
    "B1-15": ("Invoice automation", "invoice automation bounty is:issue is:open"),
    "B1-16": ("CSV reconciliation tools", "reconciliation bounty is:issue is:open"),
    "B1-17": ("Accounting data import", "quickbooks bounty is:issue is:open"),
    "B1-18": ("Dashboard development", "dashboard bounty is:issue is:open"),
    "B1-19": ("Documentation fixes", "docs reward is:issue is:open"),
    "B1-20": ("TypeScript development", "typescript bounty is:issue is:open"),
    "B1-21": ("JavaScript browser utilities", "javascript bounty is:issue is:open"),
    "B1-22": ("Unit testing work", "unit test bounty is:issue is:open"),
    "B1-23": ("Security patching (defensive)", "security fix bounty is:issue is:open"),
    "B1-24": ("Open-source accessibility", "accessibility bounty is:issue is:open"),
    "B1-25": ("Developer SDK fixes", "sdk bug bounty is:issue is:open"),
    "B2-06": ("Base USDC paid work", "base usdc bounty is:issue is:open"),
    "B2-07": ("Stablecoin payment tooling", "stablecoin bounty is:issue is:open"),
    "B2-08": ("Smart-contract testing", "smart contract test bounty is:issue is:open"),
    "B2-09": ("Ethereum client integration", "ethereum integration bounty is:issue is:open"),
    "B2-10": ("Open-source agent evaluation", "agent evaluation bounty is:issue is:open"),
    "B2-11": ("Prompt quality evaluation", "prompt evaluation bounty is:issue is:open"),
    "B2-12": ("Machine-learning dataset quality", "dataset quality bounty is:issue is:open"),
    "B2-13": ("API testing automation", "api test bounty is:issue is:open"),
    "B2-14": ("Web scraping with permission", "data extraction bounty is:issue is:open"),
    "B2-15": ("Spreadsheet formatting automation", "spreadsheet automation bounty is:issue is:open"),
    "B2-16": ("Reproducible bug reports", "bug reproduction bounty is:issue is:open"),
    "B2-17": ("Release engineering support", "release tooling bounty is:issue is:open"),
    "B2-18": ("Dependency maintenance", "dependency update bounty is:issue is:open"),
    "B2-19": ("Technical translation", "translation bounty is:issue is:open"),
    "B2-20": ("Product feedback testing", "usability testing bounty is:issue is:open"),
    "B2-21": ("Test fixture creation", "test fixtures bounty is:issue is:open"),
    "B2-22": ("Data visualization", "data visualization bounty is:issue is:open"),
    "B2-23": ("Workflow scripting", "workflow automation bounty is:issue is:open"),
    "B2-24": ("CLI testing", "cli testing bounty is:issue is:open"),
    "B2-25": ("Open data cleaning", "open data bounty is:issue is:open"),
}
assert len(EXTRA_AGENTS) == 40 and len(set(EXTRA_AGENTS)) == 40
assert {key.split("-")[0] for key in EXTRA_AGENTS} == {"B1", "B2"}
# The base engine records verified source checks but NEVER fabricates buyer acceptance or deposits.
fleet.AGENTS = EXTRA_AGENTS
fleet.OUT = Path("forty-agent-reports")


def test():
    assert len([x for x in EXTRA_AGENTS if x.startswith("B1-")]) == 20
    assert len([x for x in EXTRA_AGENTS if x.startswith("B2-")]) == 20
    assert all("is:issue is:open" in query for _mission, query in EXTRA_AGENTS.values())
    issue = {
        "id": 90, "number": 8, "state": "open", "title": "Bounty funded",
        "body": "Original paid work after acceptance",
        "updated_at": fleet.now().isoformat(),
        "html_url": "https://github.com/example/work/issues/8",
        "repository_url": "https://api.github.com/repos/example/work",
    }
    assert fleet.classify(issue)["payer_verified"] is False
    assert fleet.classify({**issue, "body": "Please send us a deposit first"}) is None
    print("PASS: forty additional agents configured and safe classification tested")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=sorted(EXTRA_AGENTS))
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
