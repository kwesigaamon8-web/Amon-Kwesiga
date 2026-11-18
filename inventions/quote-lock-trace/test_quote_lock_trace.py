import copy
import json
import pathlib
import tempfile
import unittest

from quote_lock_trace import MAX_BYTES, load_document, review


def sample(**changes):
    result = dict(quote_id="synthetic", observed_at="2026-11-18T06:09:59Z",
                  expires_at="2026-11-18T06:10:00Z", locked_claim_visible=True,
                  pay_button_enabled=True)
    result.update(changes)
    return result


class TraceTests(unittest.TestCase):
    def check(self, *samples):
        return review({"snapshots": list(samples)})

    def test_before_expiry(self):
        self.assertEqual(self.check(sample())["status"], "UNKNOWN")
        self.assertFalse(self.check(sample())["at_or_after_expiry_observed"])

    def test_exact_boundary_locked_claim(self):
        r = self.check(sample(observed_at="2026-11-18T06:10:00Z", pay_button_enabled=False))
        self.assertEqual(r["status"], "REVIEW")
        self.assertEqual(r["events"][0]["flags"], ["LOCKED_CLAIM_AT_OR_AFTER_EXPIRY"])

    def test_enabled_button_is_separate(self):
        r = self.check(sample(observed_at="2026-11-18T06:12:00Z", locked_claim_visible=False))
        self.assertEqual(r["events"][0]["flags"], ["PAY_BUTTON_ENABLED_AT_OR_AFTER_EXPIRY"])
        self.assertEqual(r["backend_payment_acceptance"], "NOT_TESTED")

    def test_expired_without_claim_or_button(self):
        self.assertEqual(self.check(sample(observed_at="2026-11-18T06:12:00Z", locked_claim_visible=False, pay_button_enabled=False))["status"], "PASS")

    def test_timezone_boundary(self):
        self.assertTrue(self.check(sample(observed_at="2026-11-18T09:10:00+03:00"))["events"][0]["expired"])

    def test_timezone_midnight_and_fraction(self):
        r = self.check(sample(observed_at="2026-11-18T00:00:00+03:00", expires_at="2026-11-17T21:00:00.000001Z"))
        self.assertEqual(r["status"], "UNKNOWN")

    def test_duplicate_same_instant_different_offset(self):
        with self.assertRaises(ValueError):
            self.check(sample(), sample(observed_at="2026-11-18T09:09:59+03:00"))

    def test_out_of_order(self):
        with self.assertRaises(ValueError):
            self.check(sample(), sample(observed_at="2026-11-18T06:09:58Z"))

    def test_changing_quote_id(self):
        with self.assertRaises(ValueError):
            self.check(sample(), sample(quote_id="other", observed_at="2026-11-18T06:10:00Z"))

    def test_inconsistent_expiry(self):
        with self.assertRaises(ValueError):
            self.check(sample(), sample(observed_at="2026-11-18T06:10:01Z", expires_at="2026-11-18T06:11:00Z"))

    def test_equivalent_expiry_offsets(self):
        r = self.check(sample(), sample(observed_at="2026-11-18T06:10:01Z", expires_at="2026-11-18T09:10:00+03:00", locked_claim_visible=False, pay_button_enabled=False))
        self.assertEqual(r["status"], "PASS")

    def test_unknown_expiry_and_empty_trace(self):
        self.assertEqual(self.check(sample(expires_at=None))["status"], "UNKNOWN")
        self.assertIsNone(self.check(sample(expires_at=None))["events"][0]["expired"])
        self.assertEqual(self.check()["status"], "UNKNOWN")

    def test_review_retains_unknown(self):
        r = self.check(sample(expires_at=None), sample(observed_at="2026-11-18T06:10:00Z"))
        self.assertEqual(r["status"], "REVIEW")
        self.assertTrue(r["has_unknown_expiry"])

    def test_bad_timestamps(self):
        for value in ("2026-11-18T06:10:00", "bad", "2026-02-30T06:10:00Z", "2026-11-18T06:10:00+00:60", 123, None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.check(sample(observed_at=value))
        with self.assertRaises(ValueError): self.check(sample(expires_at=""))

    def test_schema_and_boolean(self):
        for value in ("true", 1, None):
            with self.assertRaises(ValueError): self.check(sample(locked_claim_visible=value))
        with self.assertRaises(ValueError): self.check(sample(extra="unexpected"))
        with self.assertRaises(ValueError): self.check(sample(quote_id=""))
        with self.assertRaises(ValueError): review({"snapshots": [sample()] * 1001})

    def test_input_unchanged(self):
        document = {"snapshots": [sample()]}
        original = copy.deepcopy(document)
        review(document)
        self.assertEqual(document, original)

    def test_file_limits_and_invalid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "input.json"
            for raw in (b"x" * (MAX_BYTES + 1), b'{"snapshots":[],"snapshots":[]}', b'{', b'{"x":NaN}', b'\xff'):
                path.write_bytes(raw)
                with self.assertRaises((ValueError, UnicodeError)): load_document(path)
            path.write_text(json.dumps({"snapshots": [sample()]}), encoding="utf-8")
            self.assertEqual(review(load_document(path))["status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
