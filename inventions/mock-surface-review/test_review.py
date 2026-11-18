import json
import unittest
import tempfile
import os
from pathlib import Path
from review import review, bounded_read

class ReviewTests(unittest.TestCase):
    def compare(self, source, methods=()):
        return review(source, json.dumps({'class': 'Fake', 'methods': list(methods)}))

    def test_reports_missing_and_extra(self):
        r = self.compare('class Fake:\n def sign(self): pass\n def multiply(self): pass', ['sign', 'verify'])
        self.assertEqual(r['extra_direct_methods'], ['multiply'])
        self.assertEqual(r['missing_direct_methods'], ['verify'])
        self.assertFalse(r['names_equal'])

    def test_equal_empty_and_async(self):
        self.assertTrue(self.compare('class Fake: pass')['names_equal'])
        self.assertTrue(self.compare('class Fake:\n async def sign(self): pass', ['sign'])['names_equal'])

    def test_does_not_execute(self):
        r = self.compare('raise RuntimeError("not executed")\nclass Fake:\n def sign(self): raise RuntimeError()', ['sign'])
        self.assertTrue(r['names_equal'])

    def test_unsupported_shapes(self):
        for source in ['class Fake(Base): pass', '@wrap\nclass Fake: pass', 'class Fake(metaclass=M): pass', 'class Fake:\n x = lambda: 1', 'class Fake:\n if True:\n  def x(self): pass', 'class Fake:\n @staticmethod\n def x(): pass', 'class Fake:\n def __getattr__(self,x): pass']:
            with self.subTest(source=source), self.assertRaises(ValueError):
                self.compare(source)

    def test_duplicate_classes_methods(self):
        for source in ['class Fake: pass\nclass Fake: pass', 'class Fake:\n def x(self): pass\n def x(self): pass']:
            with self.assertRaises(ValueError): self.compare(source)

    def test_invalid_manifest(self):
        for data in [[], {}, {'class':'Fake','methods':['x','x']}, {'class':'Fake','methods':[1]}, {'class':'Fake','methods':[],'extra':1}]:
            with self.assertRaises(ValueError): review('class Fake: pass', json.dumps(data))

    def test_limits_and_syntax(self):
        with self.assertRaises(ValueError): self.compare(' ' * 65537)
        with self.assertRaises(ValueError): self.compare('class Fake: pass', ['m'+str(i) for i in range(257)])
        with self.assertRaises(SyntaxError): self.compare('class Fake: !')

    def test_file_bounds_and_fifo(self):
        with tempfile.TemporaryDirectory() as folder:
            regular = Path(folder) / 'source'
            regular.write_text('class Fake: pass')
            self.assertEqual(bounded_read(regular), 'class Fake: pass')
            regular.write_bytes(b'x' * 65537)
            with self.assertRaises(ValueError): bounded_read(regular)
            fifo = Path(folder) / 'pipe'
            os.mkfifo(fifo)
            with self.assertRaises(ValueError): bounded_read(fifo)

    def test_deterministic_sort(self):
        self.assertEqual(self.compare('class Fake:\n def z(self): pass\n def a(self): pass')['extra_direct_methods'], ['a','z'])

if __name__ == '__main__': unittest.main()
