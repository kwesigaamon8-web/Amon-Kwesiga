"""B1/B2 marketing-role dispatch over the owner's full 750,377,265,360
VIRTUAL role namespace. Exact deterministic O(1) lookup for any single role;
NOT actual AI execution, posting or network communication.
"""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone

FLEETS = ("transferexperiment", "BountyScoutAI")
COUNTS = (10, 20, 150, 7500, 1125000, 562500000, 374625000000)
PER_FLEET = sum(COUNTS)
ALL_ROLES = 2 * PER_FLEET
assert PER_FLEET == 375188632680
assert ALL_ROLES == 750377265360
REGIONS = (
    ("East Africa", "Kiswahili, English", "data cleaning"),
    ("West and Central Africa", "French, English", "developer tools"),
    ("North and Southern Africa", "English, Arabic", "free business apps"),
    ("Europe", "English, French, German", "privacy-first utilities"),
    ("North America", "English", "developer tools"),
    ("South America", "Spanish, Portuguese", "learning tools"),
    ("South and Central Asia", "English, Hindi", "data quality"),
    ("East and Southeast Asia", "English", "developer utilities"),
    ("Middle East", "Arabic, English", "business software"),
    ("Oceania and global communities", "English", "original open code"),
)
PRODUCTS = (
    ("55 browser utilities", "docs/free-toolbox.html"),
    ("6 mini applications", "docs/mini-apps.html"),
    ("6 business and marketing applications", "docs/market-lab.html"),
)
B1_TASKS = (
    "Research ONE developer community's actual posting rules; report source links before suggesting a post.",
    "Write ONE original help tutorial for a tested free product; use truthful sample outputs.",
    "Check ONE local language draft against software functionality, with human reviewer if possible.",
    "Research ONE suitable opt-in audience without extracting personal contact lists.",
    "Prepare ONE distinct education-first post, but keep it a draft pending connected platform permissions.",
    "Identify ONE relevant original open-source software listing directory and documented eligibility.",
    "Review existing website and report any broken demo or unclear call to action.",
    "Summarize actual GitHub release traffic or customer enquiries only if verifiable.",
)
B2_TASKS = (
    "Run ONE reproducible software smoke test and link to real test evidence.",
    "Find ONE genuine bug with steps to reproduce, expected result and actual output.",
    "Improve ONE developer example using original source, with test coverage.",
    "Check ONE privacy/accessibility concern and produce a documented fix suggestion.",
    "Verify ONE marketing feature claim against source/tests; reject unsupported claims.",
    "Review ONE dependency or third-party license before any external code reuse.",
    "Improve ONE error message or validation case in an original application.",
    "Draft ONE small original program that solves a real user problem and add tests.",
)
PAT_D = re.compile(r"^D(0[1-9]|10)$")
PAT_A = re.compile(r"^A(0[1-2])$")
PAT_M = re.compile(r"^M(0[1-9]|1[0-5])$")
PAT_W = re.compile(r"^W(0[1-9]|[1-4][0-9]|50)$")
PAT_S = re.compile(r"^S(00[1-9]|0[1-9][0-9]|1[0-4][0-9]|150)$")
PAT_G = re.compile(r"^G(00[1-9]|0[1-9][0-9]|[1-4][0-9][0-9]|500)$")
PAT_H = re.compile(r"^H(00[1-9]|0[1-9][0-9]|[1-5][0-9][0-9]|6[0-5][0-9]|66[0-6])$")
PATTERNS = (PAT_D, PAT_A, PAT_M, PAT_W, PAT_S, PAT_G, PAT_H)
WIDTHS = (2, 2, 2, 2, 3, 3, 3)
LABELS = ("D", "A", "M", "W", "S", "G", "H")
RADICES = (10, 2, 15, 50, 150, 500, 666)


def fleet_for_global_index(index):
    if isinstance(index, bool) or not isinstance(index, int) or not (0 <= index < ALL_ROLES):
        raise ValueError("Global role index outside 0..750377265359")
    return FLEETS[index // PER_FLEET], index % PER_FLEET


def role_from_local_index(index):
    if isinstance(index, bool) or not isinstance(index, int) or not (0 <= index < PER_FLEET):
        raise ValueError("Local role index outside company range")
    level = 0
    local = index
    while local >= COUNTS[level]:
        local -= COUNTS[level]
        level += 1
    if level == 0:
        return "D%02d" % (local + 1)
    if level == 1:
        return "D%02d-A%02d" % ((local // 2) + 1, (local % 2) + 1)
    # Manager -> first-tier W -> subagent S -> micro G -> branch H
    multipliers = [15, 50, 150, 500, 666][:level - 1]
    divs = list(reversed(multipliers))
    parts = []
    cur = local
    for radix in divs:
        cur, remainder = divmod(cur, radix)
        parts.append(remainder + 1)
    indices = [cur + 1] + list(reversed(parts))
    return "D%02d-" % indices[0] + "-".join(
        ("%s%0*d" % (symbol, width, value))
        for symbol, width, value in zip(("M", "W", "S", "G", "H"), (2, 2, 3, 3, 3), indices[1:])
    )


def local_index_from_role(role):
    parts = role.split("-")
    if not parts or len(parts) > 6 or not PAT_D.fullmatch(parts[0]):
        raise ValueError("Invalid director prefix")
    director = int(parts[0][1:]) - 1
    if len(parts) == 1:
        return director
    if PAT_A.fullmatch(parts[1]) and len(parts) == 2:
        return COUNTS[0] + director * 2 + int(parts[1][1:]) - 1
    tags = ("M", "W", "S", "G", "H")
    widths = (2, 2, 3, 3, 3)
    maxvals = (15, 50, 150, 500, 666)
    if not (2 <= len(parts) <= 6):
        raise ValueError("Invalid role depth")
    value = director
    for i, s in enumerate(parts[1:]):
        if not re.fullmatch(tags[i] + r"\d{" + str(widths[i]) + "}", s):
            raise ValueError("Invalid role level")
        number = int(s[1:])
        if not (1 <= number <= maxvals[i]):
            raise ValueError("Role slot outside valid range")
        value = value * maxvals[i] + number - 1
    return sum(COUNTS[:len(parts)]) + value


def assignment(fleet, role):
    if fleet not in FLEETS:
        raise ValueError("Unknown fleet")
    local_index = local_index_from_role(role)
    if role_from_local_index(local_index) != role:
        raise ValueError("Noncanonical role ID")
    director = int(role[1:3]) - 1
    global_index = FLEETS.index(fleet) * PER_FLEET + local_index
    digest = int.from_bytes(hashlib.blake2b(
        (fleet + "/" + role + "|20261120").encode(), digest_size=8).digest(), "big")
    focus = "B1_MARKET" if fleet == FLEETS[0] else "B2_QUALITY"
    tasks = B1_TASKS if focus == "B1_MARKET" else B2_TASKS
    product = PRODUCTS[(digest // len(tasks)) % len(PRODUCTS)]
    parent = "CHIEF_D" if len(role.split("-")) == 1 else role.rsplit("-", 1)[0]
    region, languages, topic = REGIONS[director]
    return {
        "campaign": "B1B2_FREE_SOFTWARE_RELEASE_20261120",
        "global_index_zero_based": global_index,
        "fleet": fleet,
        "fleet_agent": "B1" if fleet == FLEETS[0] else "B2",
        "role_id": role,
        "virtual_role_not_live_worker": True,
        "task_execution_verified": False,
        "parent_id": parent,
        "director_id": role[:3],
        "region_research_assignment": region,
        "suggested_languages": languages,
        "specialty": topic,
        "software_focus": product[0],
        "source_path": product[1],
        "assignment_type": focus,
        "work_order": tasks[digest % len(tasks)],
        "posting": "DRAFT_ONLY_NO_EXTERNAL_PUBLICATION",
        "platform_permission_verified": False,
        "verified_public_post_url": None,
        "verified_customer_acceptance": False,
        "payment_verification": "NOT_ASSESSED",
        "report_path": "worker -> parent -> director -> local B agent -> Chief D",
        "note": "A virtual role assignment is not an operating AI agent, online account, publication or receipt."
    }


def main():
    p = argparse.ArgumentParser(description="O(1) addressable task instructions for the full virtual B1/B2 role namespace")
    args = p.add_mutually_exclusive_group(required=True)
    args.add_argument("--global-index", type=int)
    args.add_argument("--role", help="Canonical role ID e.g. D01-M01-W01-S001-G001-H001")
    args.add_argument("--sample", type=int, help="Return at most 40 evenly spread example assignments")
    p.add_argument("--fleet", choices=FLEETS)
    opt = p.parse_args()
    if opt.global_index is not None:
        fleet, local = fleet_for_global_index(opt.global_index)
        records = [assignment(fleet, role_from_local_index(local))]
    elif opt.role:
        if not opt.fleet:
            p.error("--fleet required with --role")
        records = [assignment(opt.fleet, opt.role)]
    else:
        amount = opt.sample
        if amount < 1 or amount > 40:
            p.error("--sample must be 1..40")
        records = []
        for k in range(amount):
            index = (k * (ALL_ROLES - 1)) // max(1, amount - 1)
            fleet, local = fleet_for_global_index(index)
            records.append(assignment(fleet, role_from_local_index(local)))
    doc = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "total_configured_virtual_roles": ALL_ROLES,
        "total_actually_deployed_by_this_script": 0,
        "actual_publications_made_by_this_script": 0,
        "entries_generated": len(records),
        "assignments": records
    }
    print(json.dumps(doc, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
