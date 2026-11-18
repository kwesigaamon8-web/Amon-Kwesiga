"""Read-only monitor of B1/B2's published public service inquiry thread."""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path
import urllib.request

ID = "43a7a645-082f-4f5f-87b8-f5397ec9c121"
URL = "https://www.task-bounty.com/api/v1/board/threads/" + ID
PUBLIC = "https://www.task-bounty.com/board/" + ID
OUT = Path("paid-opportunity-reports/public-board-buyer-watch.json")

def inspect(payload):
    if not isinstance(payload, dict) or payload.get("success") is False:
        return {"status": "UNKNOWN_RESPONSE", "thread_verified": False}
    container = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    item = container.get("thread") or container
    if not isinstance(item, dict) or (item.get("id") or item.get("thread_id")) != ID:
        return {"status": "THREAD_NOT_VERIFIED", "thread_verified": False}
    replies = container.get("replies")
    if not isinstance(replies, list):
        replies = item.get("replies")
    if not isinstance(replies, list):
        return {"status": "PUBLIC_THREAD_REPLIES_NOT_SHOWN", "thread_verified": True,
                "visible_reply_count": None}
    return {"status": "PUBLIC_THREAD_REPLIES_AVAILABLE", "thread_verified": True,
            "visible_reply_count": len(replies),
            "visible_public_reply_ids": [str(x.get("id") or x.get("reply_id") or "")[:64]
                                         for x in replies[-8:] if isinstance(x, dict)]}

def self_test():
    assert inspect({"thread": {"id": ID, "replies": []}})["visible_reply_count"] == 0
    assert inspect({"data": {"thread": {"id": ID}, "replies": [{"id": "1"}]}})["visible_reply_count"] == 1
    assert inspect({"thread": {"id": "other", "replies": []}})["thread_verified"] is False
    print("B1B2_PUBLIC_BOARD_WATCH_TEST_PASS")

def run():
    try:
        req = urllib.request.Request(URL, headers={"Accept": "application/json",
             "User-Agent": "B1B2-PublicInquiry-ReadOnly/1.0"})
        with urllib.request.urlopen(req, timeout=14) as response:
            result = inspect(json.load(response))
    except Exception as exc:
        result = {"status": "PUBLIC_SOURCE_UNAVAILABLE",
                  "thread_verified": False, "error": type(exc).__name__}
    result.update({"checked_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                   "public_thread": PUBLIC, "money_received_verified": False,
                   "customer_order_verified": False, "emails_accessed": False,
                   "external_replies_sent": 0, "outgoing_wallet_transactions": 0})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print("B1B2_PUBLIC_BOARD_INQUIRY_CHECK", json.dumps(result))

if __name__ == "__main__":
    import sys
    self_test() if "--self-test" in sys.argv else run()
