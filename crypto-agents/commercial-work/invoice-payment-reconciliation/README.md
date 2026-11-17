# B1/B2 original invoice–payment matching microservice

**Working product demonstration, not a customer contract.** This original Python 3.10+ script reconciles anonymized invoice records against payment reference IDs. It is a candidate service for a real merchant who asks for custom reconciliation or workbook cleanup.

## Run locally

Provide **two synthetic or authorized anonymized** CSV files.

`invoices.csv`:

```csv
invoice_id,customer,amount
INV-01,Demo Shop,100.00
INV-02,Sample Cafe,50.00
INV-03,Example School,40.00
```

`payments.csv`:

```csv
payment_id,invoice_id,amount
P-1,INV-01,35.00
P-2,INV-01,65.00
P-3,INV-02,60.00
P-4,NOT_FOUND,5.00
```

Run:

```sh
python reconcile.py invoices.csv payments.csv -o report.json
python -m unittest -q test_reconcile
```

**Output:** Per-invoice unpaid, partial, fully paid or overpaid status, outstanding amounts, unmatched payments, aggregated invoiced/paid/unmatched balances. Handles multiple payments per invoice. Rejects duplicate invoice and payment IDs and non-finite, negative, or over-precise decimal amounts. Requires all monetary amounts in **the same agreed currency** and uses `Decimal` not floating-point math. No network access, API keys or external dependencies.

## Revenue experiment

Proposed **US$35 fixed-scope** implementation pilot for a buyer-specific schema, matching rules and accepted testing sample. **Not a confirmed sale or universal quote.** B1 should validate a willing buyer's real need and permitted contact. B2 should test/QA and customize when the buyer has agreed on exact terms. An authorized human must approve binding customer commitments and payment arrangements.

To discuss scope, use the owner-operated [commercial intake issue](https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/18). Public replies must not contain private financial documents, bank account numbers, customer records, email lists, secrets or identifying payment histories.

**Truthfulness:** A payment reference in a CSV file is NOT evidence of bank settlement, cryptocurrency receipt, wallet ownership, a live buyer, or a successfully accepted contract. No earned money is claimed from this demo. Crypto receiving instructions only belong in a relevant agreed payer context, with the exact token and network confirmed.

## Current demonstration evidence

Nine unit tests passed in the creator's local environment before publishing, using fabricated samples. The repository CI should independently rerun them. This demonstration is original and may be tailored to genuinely authorized customer data if and only if a real client requests it.
