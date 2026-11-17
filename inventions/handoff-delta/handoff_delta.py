"""HandoffDelta: offline delivery-version change report. No acceptance or payment inference."""
import hashlib
import json
import sys
import unittest

def manifest(files):
    """Map explicit public deliverable names to bytes; never scans folders."""
    if not isinstance(files, dict):
        raise ValueError("files must be a mapping")
    result = {}
    for name, data in files.items():
        if not isinstance(name, str) or not name.strip() or not isinstance(data, bytes):
            raise ValueError("nonempty names and bytes required")
        result[name] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    return result

def compare(before, after):
    return {
        "added": sorted(after.keys() - before.keys()),
        "removed": sorted(before.keys() - after.keys()),
        "changed": sorted(k for k in before.keys() & after.keys() if before[k] != after[k]),
        "unchanged": sorted(k for k in before.keys() & after.keys() if before[k] == after[k]),
        "buyer_acceptance_verified": False,
        "payment_verified": False,
        "warning": "Digest equality checks bytes only. It does not prove authorship, quality, agreement or payment."
    }

class Tests(unittest.TestCase):
    def test_known_digest(self):
        self.assertEqual(manifest({"a": b"abc"})["a"]["sha256"], "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
    def test_changes(self):
        r = compare(manifest({"a": b"x", "b": b"y", "c": b"z"}), manifest({"a": b"xx", "c": b"z", "d": b"q"}))
        self.assertEqual([r[k] for k in ("added", "removed", "changed", "unchanged")], [["d"], ["b"], ["a"], ["c"]])
    def test_empty(self):
        self.assertEqual(compare({}, {})["changed"], [])
    def test_unicode(self):
        self.assertEqual(manifest({"guide": "BTC →".encode()})["guide"]["bytes"], 7)
    def test_invalid(self):
        for x in ({"": b"a"}, {"a": "text"}, []):
            with self.assertRaises(ValueError): manifest(x)
    def test_no_inferred_acceptance(self):
        r = compare(manifest({"a": b"x"}), manifest({"a": b"x"}))
        self.assertFalse(r["buyer_acceptance_verified"])
        self.assertFalse(r["payment_verified"])

if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        unittest.main(argv=[sys.argv[0]])
    else:
        print(json.dumps(compare(manifest({"guide.md": b"synthetic draft"}), manifest({"guide.md": b"synthetic revised draft"})), indent=2))
