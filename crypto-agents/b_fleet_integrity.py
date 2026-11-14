"""Fail closed if B1 and B2 workforce pace or payment director split drifts.

This is a config audit, not a claim of completed model inferences or income.
No external dependencies, accounts, keys or transaction initiation.
"""
import json
import re
from pathlib import Path

R = Path(".github/workflows")
C = json.loads(Path("crypto-agents/b_collection_assignments.json").read_text(encoding="utf-8"))
S = json.loads(Path("crypto-agents/shared_understanding.json").read_text(encoding="utf-8"))
F = C["fleets"]
assert set(F) == {"transferexperiment", "BountyScoutAI"}
assert C["director_operations"]["payment_director_id"] == "D10"
assert C["director_operations"]["other_directors"] == [
    "D%02d" % n for n in range(1, 10)
]
assert C["hierarchy"]["chief_director"] == "D"
assert C["hierarchy"]["top_level_executive_count"] == 1
assert C["hierarchy"]["distinct_local_director_count"] == 20
assert S["organization_governance"]["chief_director"] == "D"
assert S["director_operating_split"]["chief_director"].startswith("Only ONE Chief Director D")
assert S["director_mandates"]["D10"].startswith("FLEET-LOCAL PAYMENTS DIRECTOR")
all_local_ids = []
for fleet in ("transferexperiment", "BountyScoutAI"):
    board = C["hierarchy"]["companies"][fleet]
    expected = [fleet + "/D%02d" % i for i in range(1,11)]
    assert board["local_director_ids"] == expected
    assert board["directors"] == 10
    assert board["local_payment_director"] == fleet+"/D10"
    assert board["reports_to"] == "D"
    all_local_ids += board["local_director_ids"]
assert len(all_local_ids) == len(set(all_local_ids)) == 20
for f in F.values():
    assert f["network"] == "Bitcoin mainnet"
    assert f["asset"] == "BTC"
    assert f["address"].startswith("bc1q")
    assert "INDEPENDENT board of 10 directors" in f["director_mandate"]

pair = {
    "transferexperiment": ("crypto-directors.yml", "real-ai-workers.yml"),
    "BountyScoutAI": ("bountyscoutai-workforce.yml", "bountyscoutai-real-ai-workers.yml"),
}
by_fleet = {}
for fleet, (research, model) in pair.items():
    res = (R/research).read_text(encoding="utf-8")
    ai = (R/model).read_text(encoding="utf-8")
    assert re.search(r"(?m)^\s*WORKFORCE_ID: " + re.escape(fleet) + r"\s*$", res)
    assert re.search(r"(?m)^\s*WORKFORCE_ID: " + re.escape(fleet) + r"\s*$", ai)
    rs = re.findall(r"cron: '([^']+)'", res)
    ms = re.findall(r"cron: '([^']+)'", ai)
    assert len(rs) == 1 and len(ms) == 1
    assert rs[0].split()[1:] == ["*", "*", "*", "*"], "Research must be hourly"
    assert ms[0].split()[1:] == ["4", "*", "*", "*"], "AI workers must run daily at UTC 04"
    max_parallel = int(re.search(r"max-parallel:\s*(\d+)", ai).group(1))
    model_attempts = int(re.search(r"REAL_AI_PROCESSES_PER_DIRECTOR: '(\d+)'", ai).group(1))
    budget = int(re.search(r"MAX_BATCH_SECONDS: '(\d+)'", ai).group(1))
    assert model_attempts > 0 and max_parallel > 0
    assert "director: [D01, D02, D03, D04, D05, D06, D07, D08, D09, D10]" in ai
    by_fleet[fleet] = {
        "research_cron_utc": rs[0],
        "actual_model_cron_utc": ms[0],
        "model_attempts_per_director": model_attempts,
        "directors": 10,
        "max_parallel": max_parallel,
        "max_batch_seconds": budget,
        "configured_daily_model_attempt_cap": model_attempts * 10,
    }
base = list(by_fleet.values())
for field in ("model_attempts_per_director","max_parallel","max_batch_seconds",
              "configured_daily_model_attempt_cap"):
    assert len({x[field] for x in base}) == 1, field + " mismatch"
assert by_fleet["transferexperiment"]["research_cron_utc"] == "31 * * * *"
assert by_fleet["BountyScoutAI"]["research_cron_utc"] == "46 * * * *"
assert by_fleet["transferexperiment"]["actual_model_cron_utc"] == "7 4 * * *"
assert by_fleet["BountyScoutAI"]["actual_model_cron_utc"] == "21 4 * * *"
assert by_fleet["transferexperiment"]["configured_daily_model_attempt_cap"] == 200
print("B_FLEET_PARITY", json.dumps({
    "integrity": "PASS",
    "chief_director": "D",
    "company_local_payment_directors": ["transferexperiment/D10","BountyScoutAI/D10"],
    "independent_company_directors": 20,
    "earning_directors": 9,
    "fleets": by_fleet,
    "limit": "Scheduled capacity is not completed AI output, permanent model hosting, payer contact or cryptocurrency earnings.",
}, sort_keys=True))
