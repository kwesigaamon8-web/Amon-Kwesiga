# B1/B2 JSON-to-CSV converter — original customer work sample

Target: https://opentask.ai/tasks/cmpupoqmm0027kw04351wcfhz — advertised 50 USDC, not confirmed funded or agreed. A customer must hire/accept an offer before work becomes an assignment. No offer was actually sent using OpenTask.

## Three-step usage

1. Install Python 3.10+ and install pytest for testing: `python -m pip install pytest`.
2. Run `python json_to_csv.py input.json output.csv` (optional `--excel-safe`).
3. Run `python -m pytest -q` to check the 11 automated tests.

The JSON input must be an array of flat objects; missing keys produce blank CSV cells. Fields retain first-seen order. Quotes, commas, newlines, booleans and null values are handled. Nested structures are rejected before output writing. Runtime has no third-party dependencies.

## Commercial truth

- Original listing: sourced.
- Original script and tests: implemented.
- Tests: 11 passing locally in the current conversation.
- Authenticated OpenTask offer: NOT SENT / NOT VERIFIED.
- Customer acceptance: NOT VERIFIED.
- Earned USDC or BTC: NOT VERIFIED.
- No source-code licence is copied from an outside repository; this is a newly written work sample.
