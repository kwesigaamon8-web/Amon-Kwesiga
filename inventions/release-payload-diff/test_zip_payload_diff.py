import contextlib
import io
import json
import os
from pathlib import Path
import stat
import struct
import tempfile
import unittest
from unittest import mock
import warnings
import zipfile

import zip_payload_diff as tool


class PayloadDiffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def archive(self, name, entries, timestamp=(2020, 1, 1, 0, 0, 0), comment=b""):
        path = self.root / name
        with warnings.catch_warnings(), zipfile.ZipFile(path, "w") as archive:
            warnings.simplefilter("ignore", UserWarning)
            archive.comment = comment
            for filename, data in entries:
                info = filename if isinstance(filename, zipfile.ZipInfo) else zipfile.ZipInfo(filename, timestamp)
                archive.writestr(info, data)
        return path

    def test_identical_archives(self):
        a = self.archive("a.zip", [("one.txt", b"one")])
        b = self.root / "b.zip"
        b.write_bytes(a.read_bytes())
        result = tool.compare_archives(a, b)
        self.assertTrue(result["payloads_equal"])
        self.assertTrue(result["archive_bytes_equal"])
        self.assertEqual(result["changed"], [])

    def test_same_payload_with_different_metadata(self):
        a = self.archive("a.zip", [("one.txt", b"one")])
        b = self.archive("b.zip", [("one.txt", b"one")], (2024, 2, 3, 4, 5, 6), b"release")
        result = tool.compare_archives(a, b)
        self.assertTrue(result["payloads_equal"])
        self.assertFalse(result["archive_bytes_equal"])
        self.assertEqual(result["metadata"]["changed_members"], ["one.txt"])
        self.assertTrue(result["metadata"]["archive_comment_changed"])

    def test_added_removed_changed_and_stable_order(self):
        a = self.archive("a.zip", [("same", b"same"), ("old", b"old"), ("edit", b"before")])
        b = self.archive("b.zip", [("z", b"z"), ("edit", b"after"), ("a", b"a"), ("same", b"same")])
        result = tool.compare_archives(a, b)
        self.assertEqual((result["added"], result["removed"], result["changed"]), (["a", "z"], ["old"], ["edit"]))
        self.assertFalse(result["payloads_equal"])
        self.assertEqual(json.dumps(result, sort_keys=True), json.dumps(tool.compare_archives(a, b), sort_keys=True))

    def test_member_order_and_empty_directory_are_separate(self):
        a = self.archive("a.zip", [("a", b"a"), ("b", b"b")])
        b = self.archive("b.zip", [("b", b"b"), ("a", b"a"), ("empty/", b"")])
        result = tool.compare_archives(a, b)
        self.assertTrue(result["payloads_equal"])
        self.assertTrue(result["metadata"]["member_order_changed"])
        self.assertEqual(result["metadata"]["directories_added"], ["empty"])

    def test_duplicate_path_and_file_directory_alias(self):
        for index, entries in enumerate([[("a", b"a"), ("a", b"b")], [("a", b"a"), ("a/", b"")]]):
            with self.subTest(entries=entries):
                a = self.archive(f"duplicate-{index}.zip", entries)
                with self.assertRaisesRegex(tool.ArchiveError, "duplicate"):
                    tool.compare_archives(a, a)

    def test_unsafe_paths(self):
        for index, name in enumerate(["../x", "/root", "a/../x", "C:/x", "a\\x", "./x", "a//b"]):
            with self.subTest(name=name):
                a = self.archive(f"unsafe-{index}.zip", [(name, b"x")])
                with self.assertRaisesRegex(tool.ArchiveError, "unsafe"):
                    tool.compare_archives(a, a)

    def test_symlink(self):
        info = zipfile.ZipInfo("link")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        a = self.archive("link.zip", [(info, b"target")])
        with self.assertRaisesRegex(tool.ArchiveError, "symlink"):
            tool.compare_archives(a, a)

    def test_all_limits(self):
        a = self.archive("large.zip", [("a", b"123456"), ("b", b"123456")])
        cases = {"archive_bytes": 10, "members": 1, "member_bytes": 5, "total_bytes": 10}
        for key, value in cases.items():
            with self.subTest(limit=key), self.assertRaisesRegex(tool.ArchiveError, "limit"):
                tool.compare_archives(a, a, tool.DEFAULT_LIMITS | {key: value})

    def test_central_directory_count_cannot_evade_limit(self):
        a = self.archive("lied-count.zip", [("a", b"1"), ("b", b"2")])
        data = bytearray(a.read_bytes())
        pos = data.rfind(b"PK\x05\x06")
        struct.pack_into("<HH", data, pos + 8, 1, 1)
        a.write_bytes(data)
        with self.assertRaisesRegex(tool.ArchiveError, "count limit"):
            tool.compare_archives(a, a, tool.DEFAULT_LIMITS | {"members": 1})

    def test_corrupt_crc_and_not_zip(self):
        a = self.archive("corrupt.zip", [("a", b"UNIQUE-PAYLOAD")])
        data = a.read_bytes().replace(b"UNIQUE-PAYLOAD", b"BROKEN-PAYLOAD")
        a.write_bytes(data)
        with self.assertRaisesRegex(tool.ArchiveError, "CRC"):
            tool.compare_archives(a, a)
        a.write_bytes(b"not a zip")
        with self.assertRaisesRegex(tool.ArchiveError, "ZIP end"):
            tool.compare_archives(a, a)

    def test_cli_failure_is_readable_and_nonzero(self):
        a = self.root / "bad.zip"
        a.write_bytes(b"invalid")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = tool.main([str(a), str(a)])
        self.assertEqual(code, 2)
        self.assertIn("error", json.loads(stderr.getvalue()))
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_deflated_members(self):
        info = zipfile.ZipInfo("data")
        info.compress_type = zipfile.ZIP_DEFLATED
        a = self.archive("deflated.zip", [(info, b"repeated " * 200)])
        b = self.archive("stored.zip", [("data", b"repeated " * 200)])
        result = tool.compare_archives(a, b)
        self.assertTrue(result["payloads_equal"])
        self.assertFalse(result["archive_bytes_equal"])

    def test_corrupt_deflate_has_readable_error(self):
        info = zipfile.ZipInfo("data")
        info.compress_type = zipfile.ZIP_DEFLATED
        a = self.archive("bad-deflate.zip", [(info, b"repeated " * 200)])
        data = bytearray(a.read_bytes())
        name_length, extra_length = struct.unpack_from("<HH", data, 26)
        offset = 30 + name_length + extra_length
        data[offset] = (data[offset] & 0xF8) | 7  # Reserved DEFLATE block type 3.
        a.write_bytes(data)
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = tool.main([str(a), str(a)])
        self.assertEqual(code, 2)
        self.assertIn("invalid block type", json.loads(stderr.getvalue())["error"])
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_growth_after_preflight_still_obeys_archive_limit(self):
        a = self.archive("growing.zip", [("a", b"a")])
        limit = a.stat().st_size + 1
        original = tool.preflight
        def append_after_preflight(stream, size, limits):
            original(stream, size, limits)
            with open(a, "ab") as writer:
                writer.write(b"x" * 100)
        with mock.patch.object(tool, "preflight", side_effect=append_after_preflight):
            with self.assertRaisesRegex(tool.ArchiveError, "archive byte limit.*reading"):
                tool.compare_archives(a, a, tool.DEFAULT_LIMITS | {"archive_bytes": limit})

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO unavailable on this OS")
    def test_fifo_rejected_before_open(self):
        fifo = self.root / "input-fifo"
        os.mkfifo(fifo)
        with self.assertRaisesRegex(tool.ArchiveError, "regular file"):
            tool.compare_archives(fifo, fifo)


if __name__ == "__main__":
    unittest.main()
