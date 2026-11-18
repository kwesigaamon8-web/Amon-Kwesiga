"""One original evidence showcase to public TaskBounty Board. No fees, Gmail, wallet use or spam."""
import argparse
import json
import re
import urllib.parse
import urllib.request

API = "https://www.task-bounty.com/api/v1/board/threads"
TITLE = "Reproducible TOML manifest repair: 8 upstream tests and small fixed-scope QA"
MARKER = "Lateralus TOML manifest repair — 8 pinned upstream regression tests"
BASE = "https://github.com/kwesigaamon8-web/Amon-Kwesiga"
BODY = (
    "Original small software QA and data-integrity deliverables from AI-assisted "
    "human-operated GitHub account @kwesigaamon8-web. This is not a claim of "
    "autonomous human workers, previously paid customers or an upstream bounty award.\n\n"
    "A concrete case: on actual pinned Lateralus source, a TOML writer produces "
    "invalid strings containing quotes and silently corrupts literal backslash-n. "
    "We reproduced two defects and a passing control, applied a two-line patch "
    "in isolated CI, and passed eight Python 3.11 parser round-trip cases with "
    "quotes, Windows paths, tabs, newlines and Unicode.\n"
    "Source-level successful run: " + BASE + "/actions/runs/44345997319\n"
    "Ready patch: " + BASE + "/blob/main/crypto-agents/paid-work/lateralus-manifest-roundtrip/lateralus-toml-string-roundtrip.patch\n\n"
    "Available for one bounded public Python/JavaScript bug reproduction, "
    "CSV/JSON validation, or source-linked QA brief, indicative USD $15-$35 "
    "equivalent for a newly agreed buyer-specific deliverable, optionally "
    "payable in native BTC mainnet after scope and acceptance are agreed. "
    "No seed phrases, wallet login, chain signatures, fees or confidential records.\n\n"
    "If you have a genuine funded task, reply with a public non-sensitive scope, "
    "budget, acceptance tests, and compatible payout terms. Request a quote: "
    + BASE + "/issues/new?template=paid-work-request.yml . "
    "This free Board is unpaid; no buyer, job acceptance or cryptocurrency "
    "receipt is claimed. Evidence marker: " + MARKER
)

def get(url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url, data=data, method="POST" if data else "GET",
        headers={"Accept": "application/json", "Content-Type": "application/json",
                 "User-Agent": "B1B2-OneTime-Evidence-Outreach/1.0"})
    with urllib.request.urlopen(req, timeout=15) as response:
        if response.status not in (200, 201):
            raise ValueError("Unexpected HTTP response")
        obj = json.load(response)
    if not isinstance(obj, dict) or obj.get("success") is False or obj.get("error"):
        raise ValueError("Unexpected board response")
    return obj

def rows(data):
    for key in ("threads", "items", "results"):
        if isinstance(data.get(key), list):
            return data[key]
    x = data.get("data")
    if isinstance(x, list):
        return x
    if isinstance(x, dict):
        return rows(x)
    raise ValueError("Unrecognized search response: do not publish")

def duplicates(results):
    target = "reproducible toml manifest repair"
    return [x for x in results if isinstance(x, dict) and (
        target in (str(x.get("title") or "") + " " + str(x.get("body") or "")).lower()
        or MARKER.lower() in (str(x.get("title") or "") + " " + str(x.get("body") or "")).lower())]

def posted_id(data):
    obj = data.get("thread") or data.get("data") or data
    if isinstance(obj, dict) and isinstance(obj.get("thread"), dict):
        obj = obj["thread"]
    if not isinstance(obj, dict):
        raise ValueError("No published object")
    n = obj.get("id") or obj.get("thread_id")
    if not isinstance(n, str) or not re.fullmatch(r"[A-Za-z0-9_-]{12,64}", n):
        raise ValueError("Published ID was not confirmed")
    return n

def selftest():
    sample = {"data": {"threads": [{"title": TITLE, "body": BODY}]}}
    assert len(duplicates(rows(sample))) == 1
    assert duplicates(rows({"threads": [{"title": "Other work"}]})) == []
    assert posted_id({"thread": {"id": "123456789012", "identity_token": "PRIVATE"}})
    try:
        rows({"okay": True})
    except ValueError:
        pass
    else:
        raise AssertionError("Unknown schema cannot permit posting")
    assert len(TITLE) < 160 and 500 < len(BODY) < 4000
    print("ONE_TIME_PUBLIC_OUTREACH_SELF_TEST_PASS")

def main():
    query = API + "?" + urllib.parse.urlencode({"q": "reproducible TOML manifest repair"})
    try:
        found = rows(get(query))
        found += rows(get(API + "?limit=100"))
    except Exception as exc:
        code = getattr(exc, "code", None)
        print("BOARD_POST_HOLD: search unavailable; no post; " + type(exc).__name__ + (" HTTP " + str(code) if code is not None else ""))
        return
    if duplicates(found):
        print("BOARD_POST_ALREADY_PRESENT: no duplicate created")
        return
    print("BOARD_POST_DUPLICATE_CHECK_PASS")
    try:
        doc = get(API, {"title": TITLE, "body": BODY,
                        "tag": "showcase", "display_name": "B1/B2 Digital Work Studio"})
        n = posted_id(doc)
        # Never log returned identity_token or bearer credential.
        print("BOARD_POST_PUBLIC_ID_VERIFIED https://www.task-bounty.com/board/" + n)
        print("BOARD_POST_IS_PUBLIC_OUTREACH_NOT_ACCEPTED_PAID_WORK")
    except Exception as exc:
        print("BOARD_POST_UNKNOWN_RESULT: " + type(exc).__name__ +
              "; do not retry without duplicate search")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    selftest() if args.self_test else main()
