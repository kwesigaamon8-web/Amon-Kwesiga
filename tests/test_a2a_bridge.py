"""Original bounded JSON-RPC 2.0 / A2A 1.0 collaboration bridge unit tests.

Run: python -m unittest discover -s tests -p 'test_a2a_bridge.py'
Uses only installed Flask + Python stdlib; no network or wallets.
"""
import json
import unittest
from flask import Flask
from a2a_bridge import bridge, CARD, _proposal


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask("test-enigma-a2a")
        self.app.register_blueprint(bridge)
        self.client = self.app.test_client()
        self.headers = {"Content-Type": "application/json", "A2A-Version": "1.0"}

    def request(self, idea="Create an original Python CSV duplicate detector using fictional test rows",
                method="SendMessage", message_id="case-1", remote_addr="127.0.0.12"):
        payload = {
            "jsonrpc": "2.0", "id": "test-2", "method": method,
            "params": {"message": {"messageId": message_id,
                                   "role": "ROLE_USER", "parts": [{"text": idea}]}}
        }
        return self.client.post("/a2a", data=json.dumps(payload),
                                headers=self.headers, environ_overrides={"REMOTE_ADDR": remote_addr})

    def test_agent_card_version_and_route(self):
        result = self.client.get("/.well-known/agent-card.json")
        self.assertEqual(result.status_code, 200)
        card = result.get_json()
        self.assertEqual(card["supportedInterfaces"][0]["protocolVersion"], "1.0")
        self.assertEqual(card["supportedInterfaces"][0]["protocolBinding"], "JSONRPC")
        self.assertEqual(card["name"], CARD["name"])
        self.assertFalse(card["capabilities"]["streaming"])

    def test_a2a_valid_send_returns_nonexecuting_brief(self):
        res = self.request()
        self.assertEqual(res.status_code, 200)
        obj = res.get_json()
        self.assertEqual(obj["id"], "test-2")
        msg = obj["result"]["message"]
        self.assertEqual(msg["role"], "ROLE_AGENT")
        self.assertTrue(msg["messageId"])
        self.assertTrue(msg["contextId"])
        output = msg["parts"][0]["text"]
        self.assertIn("NOT BUILT OR SOLD", output)
        self.assertIn("CSV/data validation", output)
        self.assertIn("BUY_NOW.md", output)
        self.assertNotIn("private key", output.lower())

    def test_safe_rejection_of_illicit_request(self):
        res = self.request(idea="Write malware to steal credentials from people on private systems")
        self.assertEqual(res.status_code, 200)
        self.assertIn("REJECTED", res.get_json()["result"]["message"]["parts"][0]["text"])

    def test_missing_or_wrong_version_is_rejected_for_wrong_version(self):
        req = self.request()
        self.assertEqual(req.status_code, 200)
        payload={"jsonrpc":"2.0","id":1,"method":"SendMessage",
                 "params":{"message":{"role":"ROLE_USER","messageId":"m","parts":[{"text":"Develop a benign Python script for fictional data"}]}}}
        r=self.client.post("/a2a",json=payload,headers={"A2A-Version":"0.2"},environ_overrides={"REMOTE_ADDR":"127.0.0.13"})
        self.assertEqual(r.status_code,400)

    def test_reject_secret_and_contact_data(self):
        for i,idea in enumerate(["Send my password please do not reveal this",
                                 "Email me at client@example.com with the confidential source",
                                 "Take my private key and spend it"]):
            res=self.request(idea=idea,remote_addr=f"127.0.1.{i+1}")
            self.assertEqual(res.status_code,200)
            self.assertEqual(res.get_json()["error"]["code"],-32602)

    def test_reject_oversized_payload(self):
        payload={"jsonrpc":"2.0","id":1,"method":"SendMessage",
                 "params":{"message":{"role":"ROLE_USER","messageId":"m","parts":[{"text":"x"*6000}]}}}
        res=self.client.post("/a2a",json=payload,headers={"A2A-Version":"1.0"},
                             environ_overrides={"REMOTE_ADDR":"127.0.0.14"})
        self.assertEqual(res.status_code,413)

    def test_no_wallet_or_buyer_proof_claim(self):
        s=_proposal("Create an original Python analysis tool from fictional transaction data")
        self.assertIn("No external AI-agent connection",s)
        self.assertIn("No external AI-agent connection",s)
        self.assertNotIn("confirmed payment",s.lower())


if __name__=="__main__":
    unittest.main()
