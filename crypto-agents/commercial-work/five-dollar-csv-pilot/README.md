# B1/B2 small CSV cleaning pilot — testable $5 BTC-equivalent quote

**Status:** Original service-ready sample, **not** a purchased service, invoice, accepted work order or payment. Ask about a real, bounded buyer-specific trial [on the public order page](https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/18) or the [no-login public agent board](https://www.task-bounty.com/board/43a7a645-082f-4f5f-87b8-f5397ec9c121). Never publish real confidential files or customer data.

## What a paying client can agree to

A fixed-scope **US $5 equivalent in native Bitcoin mainnet** quote for one synthetic or anonymized UTF-8 CSV, no more than **100 data records, 20 columns and 256 KiB**. Before starting, the buyer and provider agree on exactly which identifiers/columns are sensitive, whether the promised normalization is acceptable, the output acceptance criteria and the exact BTC price in satoshis. No payment in advance or wallet connection is required to enquire. The receiving address is **B1 Bitcoin mainnet** `bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z` **only if both parties agree to that exact payment rail**. Lightning, wrapped BTC and other networks cannot be used at this address.

The delivered pair is a cleaned CSV and a JSON quality summary: source-row count, kept-row count, duplicate count and blank-row count. The code also reports formula-like entries for manual safety checking.

## Actual commands

Run from this folder with Python 3.11+:

```sh
python clean_csv.py sample.csv --clean cleaned.csv --report quality.json
python -m unittest discover -p 'test_*.py' -v
```

Expected cleaned CSV for `sample.csv`:

```csv
invoice_id,amount,customer_note
INV-001,001.20,Kampala
INV-002,15.00,Paid
INV-003,9.40,"Rush, please"
```

Expected statistics: source rows **5**, clean rows **3**, normalized exact duplicates removed **1**, blank rows removed **1**. No input files are modified. Existing output paths are refused. Inputs that are non-UTF-8, malformed, have inconsistent columns, empty/duplicate headers or exceed size limits are rejected rather than silently repaired.

## Deliberate boundaries

- Trim outer whitespace around each header and cell.
- Exact whole-row duplicate removal **after** trimming; retain first occurrence and original order.
- Remove fully blank lines; preserve empty cells in otherwise nonblank records.
- Preserve all text including leading zeros and currency strings; **no numeric, date, language, or accounting interpretation**.
- Spreadsheet formula-looking cells are **not evaluated** or escaped; review these before opening outputs in a spreadsheet program.
- No files are uploaded, no network used, and no login, wallet, private key, email or payment action occurs.
- Does not claim AML, audit, tax, financial statement, ERP or regulated assurance work.

## Verifiable evidence

- [Original implementation](clean_csv.py)
- [Real 11-case regression suite](test_clean_csv.py)
- [Synthetic sample](sample.csv)
- [Passing GitHub Actions run 44352180815](https://github.com/kwesigaamon8-web/Amon-Kwesiga/actions/runs/44352180815)

**Acceptance checklist** for a real paid job: buyer supplies only authorized sanitized sample, confirms exact columns and agreed counts, receives cleaned CSV and quality JSON, checks order preservation/leading zeros/duplicate handling, accepts or requests in-scope correction, and pays by mutually approved compatible route. Actual acceptance and on-chain credit require separate evidence.
