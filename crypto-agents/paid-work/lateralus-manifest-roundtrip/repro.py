#!/usr/bin/env python3
"""Pinned upstream TOML manifest round-trip investigation.

This probe performs no user-account access and no network calls itself.
The CI workflow fetches a public upstream source revision before invoking it.
A zero exit code means two regressions were reproduced AND a control passed;
it does NOT mean the program is fixed, a bounty was submitted, or money earned.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tomllib

UPSTREAM_SHA = "599cda9f9f4d18d9054e8f315d117d3cb74126b8"
UPSTREAM_PATH = "lateralus_lang/package_manager.py"


def run(path: Path) -> None:
    spec = importlib.util.spec_from_file_location("lateralus_pkg_under_test", str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load pinned upstream module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    cases = [
        ("simple_control", {"name": "OriginalName", "version": "0.1.0"}, False),
        ("embedded_quote", {"name": 'Company "North"', "version": "0.1.0"}, True),
        ("literal_backslash_n", {"name": r"src\new"}, True),
    ]
    report = {
        "schema": "LATERALUS_MANIFEST_ROUNDTRIP_REPRO_V1",
        "upstream_revision": UPSTREAM_SHA,
        "source_path": UPSTREAM_PATH,
        "results": [],
    }
    for label, value, expected_breakage in cases:
        serialized = module.write_toml(value)
        try:
            official = tomllib.loads(serialized)
            official_error = None
        except tomllib.TOMLDecodeError as e:
            official = None
            official_error = str(e).split("\n")[0]
        try:
            project = module.parse_toml(serialized)
            internal_error = None
        except Exception as e:
            project = None
            internal_error = type(e).__name__ + ": " + str(e)
        official_same = official == value
        internal_same = project == value
        broken = not (official_same and internal_same)
        if broken != expected_breakage:
            raise AssertionError(
                f"{label}: expected broken={expected_breakage}; "
                f"official={official!r} internal={project!r} TOML={serialized!r}"
            )
        report["results"].append({
            "case": label,
            "expected_breakage": expected_breakage,
            "broken_observed": broken,
            "original": value,
            "serialized": serialized,
            "tomllib_value": official,
            "tomllib_error": official_error,
            "internal_parser_value": project,
            "internal_parser_error": internal_error,
        })
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print("PINNED_UPSTREAM_TOML_BUG_REPRODUCED: two regressions, one passing control")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python repro.py /path/to/lateralus_lang/package_manager.py")
    run(Path(sys.argv[1]).resolve())
