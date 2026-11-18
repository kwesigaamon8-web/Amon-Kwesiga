"""Deterministic CSV invoice/payment reconciliation, standard library only."""
import csv
import decimal
import io
from collections import defaultdict

D = decimal.Decimal

def reconcile(invoices_csv: str, payments_csv: str):
    """Return sorted audit rows; preserve duplicates and exact decimal arithmetic.

    Both CSVs require reference,amount headers. A payment can be partial or
    multiple; blank refs and invalid amounts are rejected, not silently matched.
    """
    def parse(data, name):
        reader = csv.DictReader(io.StringIO(data))
        if not reader.fieldnames or not {'reference','amount'}.issubset(reader.fieldnames):
            raise ValueError(f'{name}: required headers reference,amount')
        totals = defaultdict(lambda: D('0'))
        counts = defaultdict(int)
        for n, row in enumerate(reader, 2):
            ref = (row['reference'] or '').strip()
            if not ref: raise ValueError(f'{name}: blank reference at row {n}')
            try: amount = D((row['amount'] or '').strip())
            except decimal.InvalidOperation: raise ValueError(f'{name}: invalid amount at row {n}') from None
            if not amount.is_finite(): raise ValueError(f'{name}: nonfinite amount at row {n}')
            totals[ref] += amount
            counts[ref] += 1
        return totals, counts
    invoices, ic = parse(invoices_csv, 'invoices')
    payments, pc = parse(payments_csv, 'payments')
    output = []
    for ref in sorted(invoices.keys() | payments.keys()):
        a, b = invoices[ref], payments[ref]
        status = ('payment_without_invoice' if not ic[ref] else
                  'unpaid' if not pc[ref] else 'matched' if a == b else
                  'underpaid' if b < a else 'overpaid')
        output.append(dict(reference=ref, invoice_amount=str(a), payment_amount=str(b),
                           difference=str(a-b), invoice_rows=ic[ref],
                           payment_rows=pc[ref], status=status))
    return output

if __name__ == '__main__':
    import argparse, json
    p = argparse.ArgumentParser()
    p.add_argument('invoices'); p.add_argument('payments')
    args = p.parse_args()
    with open(args.invoices, encoding='utf-8-sig') as a, open(args.payments, encoding='utf-8-sig') as b:
        print(json.dumps(reconcile(a.read(), b.read()), indent=2))
