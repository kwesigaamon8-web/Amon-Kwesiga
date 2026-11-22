"""ENIGMA evidence-first virtual assignment router.

11,255,658,980,400 is a virtual role namespace, not an active AI fleet.
Emit only bounded assignment packets. Real execution must be logged separately.
No network calls, mining, unauthorized access, wallet signing or mass posting.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

POSITION_COUNT = 11_255_658_980_400
STEP = 1_201  # relatively prime to namespace; enables non-repeating position walk
MAX_PACKETS_PER_RUN = 32
COUNTRIES = tuple("""AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW""".split())
LANES = (
    ("economic-indicators", "Country and sector economic indicators", "Country/sector evidence brief"),
    ("agriculture-trade", "Crop and food trade indicators", "Agricultural market comparison"),
    ("public-tenders", "Open public procurement notices and deadlines", "Tender eligibility report"),
    ("competitors", "Published competitor products and prices", "Competitor price and feature scan"),
    ("suppliers", "Publicly identified commercial suppliers", "Supplier landscape report"),
    ("software-reviews", "Published software license and feature evidence", "Software due diligence note"),
    ("energy", "Published energy and electricity indicators", "Energy market factsheet"),
    ("transport", "Public transport, trade and logistics indicators", "Logistics market factsheet"),
    ("urban-development", "Public housing and construction indicators", "Construction market fact sheet"),
    ("tourism", "Public tourism and hospitality statistics", "Tourism demand context brief"),
    ("education", "Education and skills aggregate statistics", "Workforce/education brief"),
    ("blockchain", "Public read-only blockchain network indicators", "Non-custodial blockchain evidence report"),
)
ORDER_ID = "OWNER-20261122-WORLD-OPEN-DATA-REPORTS-SELL-ALL"
SOURCE_POLICY = (
    "Only accessible, lawful, attributable, commercially suitable public-source "
    "material. Check each dataset license and freshness; no personal dossier, "
    "copyrighted raw-data resale, restricted scraping or classified data."
)
PAYMENT_POLICY = (
    "No wallet signing/spending or transfer. Only verified incoming native BTC "
    "mainnet or explicitly validated native Circle USDC on Base may count as receipt, "
    "after actual buyer agreement and independent blockchain verification."
)

def address(seed: str, k: int) -> int:
    """Unique within each seed's 11T-cycle using O(1) arithmetic."""
    if k < 0 or k >= POSITION_COUNT:
        raise ValueError("role index outside virtual namespace")
    origin = int.from_bytes(hashlib.sha256(seed.encode("utf-8")).digest()[:8], "big") % POSITION_COUNT
    return (origin + STEP * k) % POSITION_COUNT

def packet(seed: str, k: int) -> dict:
    ix = address(seed, k)
    work_number = k // 2
    company = "B1" if k % 2 == 0 else "B2"
    lane_id, focus, sale = LANES[work_number % len(LANES)]
    country = COUNTRIES[(work_number // len(LANES)) % len(COUNTRIES)]
    return {
        "schema": "ENIGMA_VIRTUAL_ROLE_ASSIGNMENT_V1",
        "order_id": ORDER_ID,
        "virtual_position": ix,
        "virtual_role_id": f"VROLE-{ix:014d}",
        "company": company,
        "hierarchy_parent": "OWNER/CHIEF_D/" + company,
        "task_pair_id": f"{seed}:{work_number}",
        "country_iso_3166_alpha2": country,
        "lane": lane_id,
        "research_focus": focus,
        "buyer_service_proposal": sale,
        "assigned_action": ("Find a single verified buyer need, budget, and permitted contact path"
            if company == "B1" else
            "Build original cited public-data brief only after sources, licenses, and buyer question are validated"),
        "source_policy": SOURCE_POLICY,
        "payment_policy": PAYMENT_POLICY,
        "execution_state": "VIRTUAL_ASSIGNMENT_ONLY_NOT_INVOKED",
        "runtime_execution_receipt": None,
        "original_report_url": None,
        "actual_buyer_url": None,
        "buyer_acceptance": None,
        "verified_incoming_txid": None,
        "financial_status": "NO_RECEIPT_VERIFIED",
    }

def make_manifest(seed: str, count: int) -> dict:
    if not isinstance(seed, str) or not seed or len(seed) > 128:
        raise ValueError("seed must be a nonempty identifier <=128 chars")
    if not 1 <= count <= MAX_PACKETS_PER_RUN:
        raise ValueError("max 32 source-safe assignments per genuine run")
    assignments = [packet(seed, k) for k in range(count)]
    if len({p["virtual_position"] for p in assignments}) != count:
        raise AssertionError("virtual role collision")
    return {
        "schema": "ENIGMA_BOUNDED_ASSIGNMENT_MANIFEST_V1",
        "order_id": ORDER_ID,
        "role_namespace": POSITION_COUNT,
        "covered_country_codes": len(COUNTRIES),
        "available_research_lanes": len(LANES),
        "generated_virtual_assignments": count,
        "activated_independent_ai_agents": 0,
        "completed_independent_worker_reports": 0,
        "accepted_paid_engagements": 0,
        "on_chain_receipts_verified": 0,
        "execution_rule": "Only later verifiable process logs and original outputs can change actual execution status",
        "seed": seed,
        "assignments": assignments,
    }

def self_test() -> None:
    assert POSITION_COUNT == 11_255_658_980_400
    assert math.gcd(STEP, POSITION_COUNT) == 1
    assert len(COUNTRIES) == 249 and len(set(COUNTRIES)) == 249
    assert len(LANES) == 12 and len({lane[0] for lane in LANES}) == 12
    test = make_manifest("pilot-2026-11-22", 32)
    assert test["generated_virtual_assignments"] == 32
    assert test["activated_independent_ai_agents"] == 0
    assert all(p["financial_status"] == "NO_RECEIPT_VERIFIED" for p in test["assignments"])
    assert len({p["virtual_position"] for p in test["assignments"]}) == 32
    for pair in range(16):
        b1, b2 = test["assignments"][pair*2:pair*2+2]
        assert b1["company"] == "B1" and b2["company"] == "B2"
        assert b1["task_pair_id"] == b2["task_pair_id"]
        assert b1["country_iso_3166_alpha2"] == b2["country_iso_3166_alpha2"]
        assert b1["lane"] == b2["lane"]
    for n in (0, 33, 1000):
        try:
            make_manifest("pilot", n)
        except ValueError:
            pass
        else:
            raise AssertionError("unbounded packet count passed")
    for n in (-1, POSITION_COUNT):
        try:
            address("pilot", n)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid virtual position passed")
    assert make_manifest("pilot", 4) == make_manifest("pilot", 4)
    print("ROLE_ROUTER_PASS: 11.25T namespace, 249 ISO codes, 12 lanes, 16 B1/B2 pairs, 5 negative guards, no false income")

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--seed", default="owner-20261122-research")
    p.add_argument("--count", type=int, default=24)
    p.add_argument("--output", default="out/enigma_virtual_work_packets.json")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        self_test()
        return
    x = make_manifest(a.seed, a.count)
    f = Path(a.output)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(x, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "ASSIGNMENT_PACKETS_CREATED_NOT_WORKER_EXECUTION",
        "file": str(f),
        "virtual_roles_addressed": x["generated_virtual_assignments"],
        "active_independent_agents_verified": 0,
        "verified_receipts": 0,
    }))

if __name__ == "__main__":
    main()
