# Original Python CSV → JSON Work Sample

A dependency-free Python 3.10+ converter corresponding to the published **100-USDC CSV→JSON type of marketplace brief**. The buyer's specific task URL could not be fetched (404) and escrow or a contract was not independently verified. **Do not claim this code is paid, hired or delivered.**

## Run

```bash
python csv_to_json.py input.csv -o output.json
python csv_to_json.py input.tsv --delimiter tab -o output.json
python csv_to_json.py input.csv --delimiter ';' --json-lines -o output.jsonl
python -m pytest -q
```

CSV comma, semicolon, tab and pipe supported, autodetection, quoting, Unicode/BOM, missing values empty, custom 0–8-space indentation and JSON Lines. Duplicate/empty headers, bad quotes and too many columns fail clearly, rather than silently losing data. Text values stay strings to keep leading zeros. No dependency beyond Python standard library for runtime.

## Proof

15 tests independently passed in the local working environment before publishing. This is original useful work, **not buyer acceptance or cryptocurrency income**. Real paid use requires a confirmed genuine hiring contract, permitted authenticated customer contact, network-compatible payer agreement and independently verified wallet receipt.
