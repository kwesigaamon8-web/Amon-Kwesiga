"""Standard-library tests; no paying buyer, bank data, or network calls."""
import unittest
from reconcile import amount, reconcile


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.invoices = [
            {"invoice_id": "INV-01", "customer": "Demo Shop", "amount": "100.00"},
            {"invoice_id": "INV-02", "customer": "Sample Cafe", "amount": "50"},
            {"invoice_id": "INV-03", "customer": "Example School", "amount": "40"},
        ]

    def test_totals_and_statuses(self):
        payments = [
            {"payment_id": "P-1", "invoice_id": "INV-01", "amount": "35"},
            {"payment_id": "P-2", "invoice_id": "INV-01", "amount": "65"},
            {"payment_id": "P-3", "invoice_id": "INV-02", "amount": "60"},
            {"payment_id": "P-4", "invoice_id": "MISSING", "amount": "5"},
        ]
        x = reconcile(self.invoices, payments)
        self.assertEqual([i["status"] for i in x["invoices"]], ["paid", "overpaid", "unpaid"])
        self.assertEqual([i["overpayment"] for i in x["invoices"]], ["0.00", "10.00", "0.00"])
        self.assertEqual(x["totals"], {
            "invoiced": "190.00", "allocated_paid": "160.00",
            "unmatched_paid": "5.00", "outstanding": "40.00"
        })

    def test_partial(self):
        x = reconcile(self.invoices, [
            {"payment_id": "P", "invoice_id": "INV-01", "amount": "19"}
        ])
        self.assertEqual(x["invoices"][0]["status"], "partial")
        self.assertEqual(x["invoices"][0]["outstanding"], "81.00")

    def test_duplicate_invoice_rejected(self):
        with self.assertRaises(ValueError):
            reconcile(self.invoices + [self.invoices[0]], [])

    def test_duplicate_payment_rejected(self):
        p = {"payment_id": "P", "invoice_id": "INV-01", "amount": "5"}
        with self.assertRaises(ValueError):
            reconcile(self.invoices, [p, p])

    def test_unknown_payment_retained(self):
        x = reconcile(self.invoices, [
            {"payment_id": "P", "invoice_id": "NOPE", "amount": "5"}
        ])
        self.assertEqual(x["unmatched_payments"][0]["invoice_id"], "NOPE")

    def test_invalid_decimals_rejected(self):
        for value in ("nan", "-3", "5.001", "abc", "inf"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                amount(value, "test")

    def test_empty_invoice_id_rejected(self):
        with self.assertRaises(ValueError):
            reconcile([{"invoice_id": "", "customer": "A", "amount": "10"}], [])

    def test_empty_invoices(self):
        self.assertEqual(reconcile([], [])["totals"]["invoiced"], "0.00")

    def test_zero_invoice(self):
        row = {"invoice_id": "X", "customer": "A", "amount": "0"}
        self.assertEqual(reconcile([row], [])["invoices"][0]["status"], "paid")


if __name__ == "__main__":
    unittest.main()
