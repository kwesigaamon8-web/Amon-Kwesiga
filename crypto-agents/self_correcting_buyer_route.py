"""B1/B2 self-correction of ONE public buyer route, not autonomous code rewriting.

Checks only allowlisted publicly published pages. If the preferred site fails a
real HTTPS check, automatically selects a *tested* backup. Never modifies the
canonical owner directive, wallets, permissions, secrets or arbitrary source.
A non-changing selection does not churn Git history. Evidence stays separate
from paid work and on-chain receipts.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

TEMP_PREVIEW = Path("docs/TEMP_PREVIEW.md")
PUBLISHED = Path("docs/BUYER_ENTRYPOINT.md")
EVIDENCE = Path("self-correction-evidence/public-buyer-route.json")
RENDER = "https://amon-kwesiga.onrender.com/studio/"
BACKUP = "https://cookie-ticket-dm9i1.ship.place/"
FALLBACK_INTAKE = (
    "https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/new"
    "?template=paid-work-request.yml"
)
B1 = "bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z"
B2 = "bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9"
REQUIRED_PATHS = ("software.html", "ai.html", "payment.html")
ALLOWED_HOSTS = {"amon-kwesiga.onrender.com", "cookie-ticket-dm9i1.ship.place"}
PREVIEW_HOST = re.compile(r"^[a-z0-9-]+\.ship\.place$", re.ASCII)


def allowed_url(url: str) -> bool:
    try:
        p = urllib.parse.urlsplit(url)
        return (p.scheme == "https" and p.username is None and p.password is None
                and p.port is None and p.fragment == ""
                and bool(p.hostname)
                and (p.hostname in ALLOWED_HOSTS or bool(PREVIEW_HOST.fullmatch(p.hostname))))
    except ValueError:
        return False


def choose_candidates(preview_file: Path = TEMP_PREVIEW) -> list[tuple[str, str]]:
    candidates = []
    if preview_file.is_file():
        content = preview_file.read_text(encoding="utf-8")
        match = re.search(r"\*\*Open the latest working digital service site:\*\*\s+"
                          r"(https://[a-z0-9-]+\.ship\.place/)", content)
        if match and allowed_url(match.group(1)):
            candidates.append(("renewed_preview", match.group(1)))
    candidates.extend((("tested_backup", BACKUP), ("render", RENDER)))
    seen = set()
    return [(name, url) for name, url in candidates if not (url in seen or seen.add(url))]


def public_fetch(url: str, timeout: int = 12) -> tuple[int, str, str]:
    """Reject redirects to an unapproved hostname to avoid leaking requests."""
    if not allowed_url(url):
        raise ValueError("Unapproved public URL")
    req = urllib.request.Request(url, headers={
        "User-Agent": "B1B2-SelfCorrect-BuyerRoute/1.0",
        "Accept": "text/html",
    })
    opener = urllib.request.build_opener(_StrictRedirect())
    with opener.open(req, timeout=timeout) as resp:
        final = resp.geturl()
        if not allowed_url(final):
            raise ValueError("Unapproved final URL")
        raw = resp.read(130_000)
        return int(resp.status), raw.decode("utf-8", "replace"), final


class _StrictRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not allowed_url(newurl):
            raise ValueError("Refuse redirect outside approved public hostnames")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def check_site(name: str, root: str, fetch=public_fetch) -> dict:
    result = {"name": name, "root": root, "status": "UNKNOWN", "pages": {}}
    if not allowed_url(root) or not root.endswith("/"):
        result["status"] = "UNSAFE_CONFIG"
        return result
    for page in REQUIRED_PATHS:
        url = root + page
        try:
            code, html, effective_url = fetch(url)
            ok = (code == 200 and "<html" in html.lower()
                  and allowed_url(effective_url)
                  and urllib.parse.urlsplit(effective_url).path.endswith("/" + page))
            if page == "payment.html":
                ok = ok and B1 in html and B2 in html and (
                    "Bitcoin mainnet" in html or "BTC" in html)
            elif page == "ai.html":
                ok = ok and any(x in html.lower() for x in ("hire", "services", "quote"))
            elif page == "software.html":
                ok = ok and any(x in html.lower() for x in ("software", "csv", "json"))
            result["pages"][page] = {"http": code, "verified": bool(ok)}
        except (urllib.error.URLError, OSError, TimeoutError, ValueError) as exc:
            result["pages"][page] = {
                "http": None, "verified": False, "error": type(exc).__name__,
            }
        if not result["pages"][page]["verified"]:
            result["status"] = "BLOCKED"
            result["failure_page"] = page
            break
    if len(result["pages"]) == len(REQUIRED_PATHS) and all(
        result["pages"][x]["verified"] for x in REQUIRED_PATHS
    ):
        result["status"] = "READY"
    return result


def decide(candidates: list[tuple[str, str]], fetch=public_fetch) -> dict:
    reviewed = []
    for name, root in candidates:
        finding = check_site(name, root, fetch)
        reviewed.append(finding)
        if finding["status"] == "READY":
            return {
                "status": "VERIFIED_LIVE_BUYER_ROUTE",
                "chosen": {"name": name, "root": root},
                "reviewed": reviewed,
                "buyer_inquiry_url": FALLBACK_INTAKE,
                "wallets_observed_in_payment_page": [B1, B2],
                "payment_received_verified": False,
                "code_files_automatically_rewritten": False,
            }
    return {
        "status": "ALL_PUBLIC_HOSTS_UNAVAILABLE",
        "chosen": None,
        "reviewed": reviewed,
        "buyer_inquiry_url": FALLBACK_INTAKE,
        "wallets_observed_in_payment_page": [],
        "payment_received_verified": False,
        "code_files_automatically_rewritten": False,
    }


def render_entrypoint(state: dict) -> str:
    chosen = state["chosen"]
    lines = [
        "# B1/B2 live buyer entrypoint — automatically health-checked",
        "",
        "This page is managed by a bounded read-only website checker. Only this "
        "buyer-route directory may be updated; owner orders, code, wallets and "
        "financial ledgers are never automatically changed.",
        "",
    ]
    if chosen is None:
        lines.extend([
            "**Live site status: NOT VERIFIED.** Do not redirect a buyer to an unavailable host.",
            "",
        ])
    else:
        url = chosen["root"]
        lines.extend([
            "**Live site status: independently checked HTTPS pages.**",
            "",
            f"- [Open tested B1/B2 software]({url}software.html)",
            f"- [Request AI-assisted services]({url}ai.html)",
            f"- [View Bitcoin-mainnet payment instructions]({url}payment.html)",
            "",
            "All three pages returned HTTP 200 and passed minimum content "
            "and public receiving-address checks when selected. Availability "
            "may change after this check; hosting is not a customer or payment.",
            "",
        ])
    lines.extend([
        "- [Request a fixed-scope quote through GitHub]("
        + FALLBACK_INTAKE + ") — always use non-sensitive examples",
        "- [Stable site directory](./TEMP_PREVIEW.md) — alternative rotating static preview",
        "",
        "**Not earned revenue:** these links do not confirm a buyer, invoice, "
        "wallet control, ASIC miner, or cryptocurrency receipt. "
        "Never send email or sign/spend wallets through this checker.",
        "",
    ])
    return "\n".join(lines)


def save_if_changed(text: str, path: Path) -> bool:
    # Only this approved generated Markdown file can be replaced in CLI mode.
    if path != PUBLISHED:
        raise ValueError("Output mutation outside allowlist")
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def self_test() -> None:
    healthy = {
        "software.html": "<html><h1>Original CSV software</h1></html>",
        "ai.html": "<html><h1>Hire AI services</h1></html>",
        "payment.html": "<html>Bitcoin mainnet " + B1 + " " + B2 + "</html>",
    }
    def fake(url):
        if "amon-kwesiga.onrender.com" in url:
            raise urllib.error.HTTPError(url, 503, "Unavailable", {}, None)
        return 200, healthy[url.rsplit("/", 1)[1]], url
    a = decide([("render", RENDER), ("backup", BACKUP)], fake)
    assert a["status"] == "VERIFIED_LIVE_BUYER_ROUTE"
    assert a["chosen"]["name"] == "backup" and a["reviewed"][0]["status"] == "BLOCKED"
    b = decide([("backup", BACKUP)], fake)
    assert b["chosen"]["name"] == "backup"
    def fake_bad_wallet(url):
        return 200, "<html>Bitcoin mainnet " + B1 + "</html>" if url.endswith("payment.html") else healthy[url.rsplit("/",1)[1]], url
    c = decide([("backup", BACKUP)], fake_bad_wallet)
    assert c["status"] == "ALL_PUBLIC_HOSTS_UNAVAILABLE"
    assert "NOT VERIFIED" in render_entrypoint(c)
    assert not allowed_url("https://evil.com/")
    assert not allowed_url("http://cookie-ticket-dm9i1.ship.place/")
    assert not allowed_url("https://user:password@cookie-ticket-dm9i1.ship.place/")
    assert not allowed_url("https://cookie-ticket-dm9i1.ship.place:8443/")
    assert "bitcoin" in render_entrypoint(a).lower()
    assert "won $100" not in render_entrypoint(a)
    with __import__("tempfile").TemporaryDirectory() as tmp:
        p = Path(tmp) / "TEMP_PREVIEW.md"
        p.write_text("**Open the latest working digital service site:** "
                     "https://harvest-elk-yfh74.ship.place/\n")
        assert choose_candidates(p)[0] == (
            "renewed_preview", "https://harvest-elk-yfh74.ship.place/")
    print("B1B2_SELF_CORRECTING_BUYER_FAILOVER_TESTS_PASS")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    self_test()
    state = decide(choose_candidates())
    state["checked_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    changed = save_if_changed(render_entrypoint(state), PUBLISHED)
    print("B1B2_SELF_CORRECTION", json.dumps({
        "status": state["status"],
        "chosen": state["chosen"],
        "failed_sources": [r["name"] for r in state["reviewed"]
                           if r["status"] != "READY"],
        "buyer_route_directory_changed": changed,
        "bitcoin_received_verified": False,
        "no_external_account_actions": True,
    }))


if __name__ == "__main__":
    main()
