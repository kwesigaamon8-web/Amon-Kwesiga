#!/usr/bin/env python3
"""Read-only reproduction of a public AUREN risk-score diagnostic mismatch.

Retrieves the exact public upstream engine/score.py file pinned to its
2026-11-18 commit, executes only the risk-score module (no secrets, wallet
or network transactions), and asserts actual contradictory output. This is
an EXISTING-bug regression demonstration, not a proposed merged fix.
"""
from __future__ import annotations

import urllib.request

UPSTREAM_COMMIT = "eef89475dece13ad243c6fc83d06f0ae1d1b0882"
UPSTREAM = (
    "https://raw.githubusercontent.com/Ayush441-python/AUREN/"
    + UPSTREAM_COMMIT + "/engine/score.py"
)


def reproduce() -> None:
    req = urllib.request.Request(
        UPSTREAM, headers={"User-Agent": "B1-B2-original-AUREN-bug-reproducer/1"}
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        source = response.read(100_000).decode("utf-8")
    # Specific known source only: don't execute arbitrary data or build on
    # text from a bounty comment. The pinned file should have this exact API.
    assert "def risk_score(conc: dict, vol: float, mdd: float, pairs: list, sector_max: float):" in source
    scope = {"__name__": "auren_score_readonly_repro"}
    exec(compile(source, UPSTREAM, "exec"), scope)
    risk_score = scope["risk_score"]

    concentration = {"top_weight": 0.304, "effective_assets": 5.0}
    score, level, hits = risk_score(concentration, .304, -.304, [], .504)
    actual = [reason for _, reason in hits]
    assert score == 70 and level == "High", (score, level)
    expected_current = [
        "Largest holding is 30% (over 30%)",
        "Volatility is 30% a year (over 30%)",
        "Worst past fall was -30% (deeper than -30%)",
        "50% sits in one sector",
    ]
    assert actual == expected_current, actual

    control_score, _, control_hits = risk_score(
        {"top_weight": 0.30, "effective_assets": 5.0}, .30, -.30, [], .50
    )
    assert control_score == 0 and not control_hits

    print("AUREN_RISK_DISPLAY_REPRO_PASS")
    print("Upstream commit:", UPSTREAM_COMMIT)
    print("Raw reproducible source:", UPSTREAM)
    print("Four threshold crossings are triggered but rounded below visibility:")
    for reason in actual:
        print(" -", reason)
    print("Negative control: exact 30% / 50% values trigger nothing.")


if __name__ == "__main__":
    reproduce()
