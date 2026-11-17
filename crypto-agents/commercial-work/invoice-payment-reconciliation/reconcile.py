"""Original no-dependency invoice-to-payment reconciliation for small paid projects.

Invoice CSV columns: invoice_id,customer,amount
Payments CSV columns: payment_id,invoice_id,amount
Amounts must share the same agreed currency; no external transaction verification.
"""
import argparse
import csv
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


def amount(value, label):
    try:
        x = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError(f"{label}: invalid decimal amount") from exc
    if not x.is_finite() or x < 0 or x.as_tuple().exponent < -2:
        raise ValueError(f"{label}: amount must be nonnegative with up to 2 decimal places")
    return x


def read_csv(path, fields):
    with open(path, encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError(f"{path}: missing or duplicate header")
        if any(field not in reader.fieldnames for field in fields):
            raise ValueError(f"{path}: required columns: {', '.join(fields)}")
        rows = list(reader)
        if any(None in row for row in rows):
            raise ValueError(f"{path}: row contains extra columns")
        return rows


def reconcile(invoices, payments):
    by_id = {}
    for row in invoices:
        key = row["invoice_id"].strip()
        if not key or key in by_id:
            raise ValueError("Each invoice_id must be present and unique")
        if not row["customer"].strip():
            raise ValueError(f"Invoice {key}: customer is required")
        by_id[key] = {
            "invoice_id": key, "customer": row["customer"].strip(),
            "invoiced": amount(row["amount"], f"Invoice {key}"), "paid": Decimal("0")
        }
    seen_payments = set()
    unmatched = []
    for row in payments:
        payment_id = row["payment_id"].strip()
        if not payment_id or payment_id in seen_payments:
            raise ValueError("Each payment_id must be present and unique")
        seen_payments.add(payment_id)
        key = row["invoice_id"].strip()
        value = amount(row["amount"], f"Payment {payment_id}")
        if key not in by_id:
            unmatched.append({
                "payment_id": payment_id, "invoice_id": key,
                "amount": format(value, ".2f")
            })
        else:
            by_id[key]["paid"] += value
    lines = []
    for key, item in by_id.items():
        remaining = item["invoiced"] - item["paid"]
        status = (
            "unpaid" if item["paid"] == 0 and item["invoiced"] > 0 else
            "overpaid" if remaining < 0 else
            "paid" if remaining == 0 else "partial"
        )
        lines.append({
            "invoice_id": key, "customer": item["customer"],
            "invoiced": format(item["invoiced"], ".2f"),
            "paid": format(item["paid"], ".2f"),
            "outstanding": format(max(remaining, Decimal("0")), ".2f"),
            "overpayment": format(max(-remaining, Decimal("0")), ".2f"),
            "status": status
        })
    return {
        "invoices": lines, "unmatched_payments": unmatched,
        "totals": {
            "invoiced": format(sum((x["invoiced"] for x in by_id.values()), Decimal("0")), ".2f"),
            "allocated_paid": format(sum((x["paid"] for x in by_id.values()), Decimal("0")), ".2f"),
            "unmatched_paid": format(sum((Decimal(x["amount"]) for x in unmatched), Decimal("0")), ".2f"),
            "outstanding": format(sum((Decimal(x["outstanding"]) for x in lines), Decimal("0")), ".2f")
        },
        "note": "Synthetic demonstration. This output does not establish actual receipt, bank credit, customer acceptance or crypto TXIDs."
    }


def main():
    parser = argparse.ArgumentParser(description="Reconcile anonymized invoices and identified payments; no network calls")
    parser.add_argument("invoice_csv", type=Path)
    parser.add_argument("payment_csv", type=Path)
    parser.add_argument("-o", "--output", type=Path, help="JSON output path, otherwise stdout")
    args = parser.parse_args()
    result = reconcile(
        read_csv(args.invoice_csv, ("invoice_id", "customer", "amount")),
        read_csv(args.payment_csv, ("payment_id", "invoice_id", "amount"))
    )
    encoded = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
