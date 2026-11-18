#!/usr/bin/env python3
"""Check an independently applied change to pinned Lateralus upstream.

Requires Python 3.11+ tomllib and the actual upstream source module.
No network, account, payment or wallet operations.
"""
from __future__ import annotations
import importlib.util
import json
import pathlib
import sys
import tomllib

def main(source: pathlib.Path) -> None:
    spec = importlib.util.spec_from_file_location("lateralus_patched_pkg", str(source))
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load pinned upstream package manager")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    cases = {
        "plain": {"name": "OriginalName", "version": "0.1.0"},
        "quoted": {"name": 'Company "North"', "version": "0.1.0"},
        "backslash_n": {"name": r"src\new"},
        "windows_path": {"main": r"C:\new\tools\main.ltl"},
        "multiline": {"description": "first line\nsecond line"},
        "unicode": {"author": "Kampala — café 🇺🇬"},
        "escaped_tab": {"description": "name\tvalue"},
        "escaped_quote_backslash": {"name": 'Memo \\"quoted"'},
    }
    results = []
    for name, obj in cases.items():
        raw = module.write_toml(obj)
        official = tomllib.loads(raw)
        own = module.parse_toml(raw)
        if official != obj:
            raise AssertionError(f"{name}: tomllib changed input: {official!r} vs {obj!r}")
        if own != obj:
            raise AssertionError(f"{name}: internal parser changed input: {own!r} vs {obj!r}")
        results.append({"case": name, "standards_parser": "PASS", "internal_parser": "PASS"})
    print(json.dumps({"schema": "LATERALUS_UPSTREAM_PATCH_TEST_V1",
                      "cases": len(results), "results": results}, indent=2))
    print("LATERALUS_TOML_PATCH_PASS: eight actual upstream round trips")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: test_patched.py path/to/package_manager.py")
    main(pathlib.Path(sys.argv[1]).resolve())
