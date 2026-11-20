"""Local, offline tests for B1/B2 actual database and web-server operation."""
from __future__ import annotations
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app import command_check, initialize, routes_check, run_once, snapshot, handler_for

class ServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.temp.name) / "evidence.sqlite3")
        initialize(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_no_fake_payment_and_real_local_work(self):
        order = command_check()
        self.assertEqual(order["status"], "PASS")
        self.assertTrue(order["mirror_and_cascade_match"])
        self.assertFalse(order["independent_ai_comprehension_proved"])
        self.assertEqual(routes_check()["status"], "PASS")
        first = run_once(self.path)
        second = run_once(self.path)
        third = run_once(self.path)
        self.assertEqual([first["status"], second["status"]], ["PASS", "PASS"])
        self.assertEqual(third["status"], "NO_ELIGIBLE_LOCAL_TASK")
        self.assertEqual(len(snapshot(self.path, "receipts")), 2)
        self.assertEqual(len([x for x in snapshot(self.path, "tasks")
                              if x["status"] == "QUEUED"]), 2)
        self.assertFalse(routes_check()["blockchain_receipts_checked"])

    def test_server_read_only_api(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(self.path))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = "http://127.0.0.1:" + str(server.server_port)
        try:
            for endpoint in ("/health", "/command", "/tasks", "/receipts"):
                with urllib.request.urlopen(base + endpoint, timeout=3) as response:
                    self.assertEqual(response.status, 200)
                    doc = json.load(response)
                    self.assertIsInstance(doc, dict)
            with self.assertRaises(urllib.error.HTTPError) as exc:
                urllib.request.urlopen(
                    urllib.request.Request(base + "/tasks", data=b"{}",
                                           method="POST"), timeout=3)
            self.assertEqual(exc.exception.code, 501)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=4)

if __name__ == "__main__":
    unittest.main()
