# Duplicate Odoo external-order-ID checker — original commission-ready sample

**What it does:** Safely reads an owner-supplied CSV with an `external_order_id` column and reports every nonempty duplicate ID plus the **CSV file row numbers (header is row 1)**. The input file is never written to, modified or uploaded. Standard Python 3.11+ only; works without Odoo login, Excel licenses or third-party libraries.

**Run:**

```sh
python duplicate_order_ids.py example_orders.csv
python duplicate_order_ids.py example_orders.csv --json
python -m unittest -v test_duplicate_order_ids.py
```

**Example**

Input `example_orders.csv`:
```csv
external_order_id,customer,amount
OD-101,Test Customer A,50
OD-102,Test Customer B,20
OD-101,Test Customer A,10
OD-103,Test Customer C,70
```

Output:
```text
Duplicate order IDs: 1
  OD-101 — CSV rows 2, 4
```

**Acceptance checks:** detects all repeated order IDs and their original CSV row numbers; does not change source bytes; reports errors when `external_order_id` is absent; ignores blank IDs but warns they should be separately reviewed. Eight unit tests use only synthetic examples.

**Commercial application:** This sample is relevant to a [$5 worldwide Odoo Python CSV order-ID job advertised November 16, 2026](https://www.upwork.com/freelance-jobs/apply/Quick-Python-Script-Find-Duplicate-Order-IDs-CSV-for-Odoo_~022122399417978516760/). **It is an independent public portfolio sample, not a submission, client-delivered artifact or paid contract.** The listing already showed one hire; verify additional buyer demand before applying through a genuinely authorized marketplace account.

**B1/B2 receiving policy:** Only quote a single owner-confirmed, compatible receiving address after a real customer agrees the job, network and currency. All routes are strictly **receive-only**. No wallet signatures or outgoing transactions.
