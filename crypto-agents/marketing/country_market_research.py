"""Country-by-country evidence tasks for B1/B2 real processes or virtual role addresses.

249 ISO 3166-1 country/territory codes; not a list of 249 sovereign countries.
No country-specific market problem is asserted as a proven fact without
dated, local evidence. Zero network calls by default, zero external publishing.
"""
import argparse
import hashlib
import json

COUNTRY_CODES = ("AW AF AO AI AX AL AD AE AR AM AS AQ TF AG AU AT AZ BI BE BJ BQ BF BD BG BH BS BA BL BY BZ BM BO BR BB BN BT BV BW CF CA CC CH CL CN CI CM CD CG CK CO KM CV CR CU CW CX KY CY CZ DE DJ DM DK DO DZ EC EG ER EH ES EE ET FI FJ FK FR FO FM GA GB GE GG GH GI GN GP GM GW GQ GR GD GL GT GF GU GY HK HM HN HR HT HU ID IM IN IO IE IR IQ IS IL IT JM JE JO JP KZ KE KG KH KI KN KR KW LA LB LR LY LC LI LK LS LT LU LV MO MF MA MC MD MG MV MX MH MK ML MT MM ME MN MP MZ MR MS MQ MU MW MY YT NA NC NE NF NG NI NU NL NO NP NR NZ OM PK PA PN PE PH PW PG PL PR KP PT PY PS PF QA RE RO RU RW SA SD SN SG GS SH SJ SB SL SV SM SO PM RS SS ST SR SK SI SE SZ SX SC SY TC TD TG TH TJ TK TM TL TO TT TN TR TV TW TZ UG UA UM UY US UZ VA VC VE VG VI VN VU WF WS YE ZA ZM ZW").split()
# Frozen ISO-3166 jurisdiction code catalogue, including territories.
COUNTRY_CODES = tuple(COUNTRY_CODES)
SECTORS = (
    "farm and produce operations", "local shops and inventory",
    "construction and maintenance", "schools and learning",
    "delivery and logistics", "community health administration",
    "tourism and accommodation", "independent digital services",
    "nonprofits and community projects", "digital infrastructure and Bitcoin",
)
EVIDENCE_REQUIREMENTS = (
    "Verify whether jurisdiction is inhabited, independent or a territory; do not label all as sovereign states.",
    "Collect ONE recent official local statistic or primary study with source link, date, scope and limitations.",
    "Interview or consult willing actual local users ONLY through permissioned channels; no cold spam or private contact scraping.",
    "Identify one narrow, documented customer need; avoid unsupported market conclusions.",
    "Review accessibility, country languages, payment restrictions and local software laws before outreach.",
    "Test a relevant free app and document a real user problem or reproducible software defect.",
    "Draft locally useful content; publish only with an authorized platform account and rule-compliant original post.",
    "Capture real link, qualified inquiry, agreement, accepted deliverable and on-chain payment separately.",
)
OWNER_BASE = "https://amon-kwesiga.onrender.com/studio/"
COUNTRY_INDICATORS = ("IT.NET.USER.ZS", "EG.ELC.ACCS.ZS", "SP.POP.TOTL")


def research_assignment(code):
    code = str(code).upper()
    if code not in COUNTRY_CODES:
        raise ValueError("Unsupported ISO country or territory code")
    data = code.encode("ascii")
    h = ord(code[0]) * 67 + ord(code[1]) * 43
    sector_idx = h % 10
    app_number = (h % 1000) + 1
    return {
        "country_or_territory_code": code,
        "jurisdiction_type": "UNVERIFIED_CHECK_LOCAL_CLASSIFICATION",
        "candidate_issue_to_investigate": "Do local users in " + SECTORS[sector_idx] +
                 " need a lighter no-sign-up browser calculator, planner or original custom software?",
        "candidate_software": "SW-%03d" % app_number,
        "candidate_software_url": OWNER_BASE + "global-1000.html?tool=SW-%03d" % app_number,
        "free_software_page": OWNER_BASE + "global-1000.html",
        "reference_data": [
            "https://api.worldbank.org/v2/country/" + code +
                "/indicator/" + indicator + "?format=json&per_page=3"
            for indicator in COUNTRY_INDICATORS
        ],
        "note": "World Bank availability varies by territory and indicator. No research values have been fetched or verified by this plan.",
        "verified_local_problem": False,
        "actual_market_interviews": 0,
        "verified_competitor_review": False,
        "authorized_external_posts": 0,
        "actual_leads": 0,
        "customer_agreements": 0,
        "actual_accepted_work": 0,
        "independently_confirmed_crypto_payment": False,
        "required_steps": list(EVIDENCE_REQUIREMENTS),
        "payment_route": OWNER_BASE + "payment.html",
        "payment_terms": "Free apps never require payment; custom deliverables require buyer agreement; optional native BTC mainnet only.",
    }


def worker_country(global_index):
    if isinstance(global_index, bool) or not isinstance(global_index, int):
        raise ValueError("Worker address must be integer")
    if not (0 <= global_index < 750377265360):
        raise ValueError("Virtual role address outside valid range")
    # all 249 codes reached repeatedly; no need to allocate 750B objects.
    code = COUNTRY_CODES[global_index % len(COUNTRY_CODES)]
    result = research_assignment(code)
    result["virtual_worker_global_index"] = global_index
    result["worker_is_a_real_process"] = False
    return result


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--code")
    g.add_argument("--global-index", type=int)
    g.add_argument("--all", action="store_true", help="Produce 249 bounded research ASSIGNMENTS, not findings")
    options = p.parse_args()
    if options.code:
        records = [research_assignment(options.code)]
    elif options.global_index is not None:
        records = [worker_country(options.global_index)]
    else:
        records = [research_assignment(c) for c in COUNTRY_CODES]
    print(json.dumps({
        "iso_countries_and_territories": len(COUNTRY_CODES),
        "requested_briefs": len(records),
        "verified_country_findings_produced": 0,
        "actual_publishing_performed": 0,
        "workers_started": 0,
        "briefs": records,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
