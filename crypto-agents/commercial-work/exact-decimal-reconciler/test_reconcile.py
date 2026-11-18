import unittest
from reconcile import reconcile

class TestReconcile(unittest.TestCase):
    def test_reconcile(self):
        a='reference,amount\nA,0.10\nA,0.20\nB,20\nC,10\nD,3\n'
        b='reference,amount\nA,0.30\nB,15\nC,12\nE,4\n'
        rows={r['reference']:r for r in reconcile(a,b)}
        self.assertEqual({k:v['status'] for k,v in rows.items()},
                         {'A':'matched','B':'underpaid','C':'overpaid','D':'unpaid','E':'payment_without_invoice'})
        self.assertEqual(rows['A']['invoice_rows'],2)
        self.assertEqual(rows['A']['difference'],'0.00')
    def test_bad_data(self):
        for value in ['NaN','Infinity','abc']:
            with self.assertRaises(ValueError):
                reconcile('reference,amount\nA,'+value+'\n','reference,amount\n')
        with self.assertRaises(ValueError):
            reconcile('reference,amount\n,2\n','reference,amount\n')
        with self.assertRaises(ValueError):
            reconcile('ref,value\nA,2\n','reference,amount\n')

if __name__=='__main__': unittest.main()
