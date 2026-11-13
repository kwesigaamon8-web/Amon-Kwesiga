"""Read-only public social opportunity discovery.

Bluesky and Reddit are searched without account credentials. If a provider
rejects public requests, record the failure and continue. Never post, DM,
follow, connect wallets or promise an outcome.
"""
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone

TOPICS = {
  "D01": ("bitcoin freelance hiring", "paid bitcoin bounty", "btc contract work"),
  "D02": ("USDC freelance job", "stablecoin bounty", "paid in USDC"),
  "D03": ("AI agent bounty", "AI agents hiring", "paid agent task"),
  "D04": ("remote bookkeeper hiring", "QuickBooks freelance work", "accounting contract remote"),
  "D05": ("open source paid bounty", "github bounty", "developer bounty"),
  "D06": ("AI data annotation paid", "paid AI microtask", "remote AI evaluator"),
  "D07": ("need a bookkeeper", "looking for an accountant", "QuickBooks cleanup contractor"),
  "D08": ("grant applications open", "cash prize competition", "paid hackathon"),
  "D09": ("USDC contractor payment", "crypto job scam", "paid bounty proof"),
  "D10": ("paid bookkeeping opportunity", "BTC contract job", "USDC paid work"),
}
ACTUAL_OPPORTUNITY = re.compile(r"(?i)\b(hir(?:e|ing)|hiring|looking for|seeking|need(?:ing)?|paid|paying|bounty|contract|freelance|job|gig|reward|grant|prize|work wanted)\b")
SPAM = re.compile(r"(?i)\b(airdrop|giveaway|presale|mint now|connect your wallet|guaranteed profit|send (?:me |us )?(?:btc|usdc|crypto))\b")

def _get(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "ResearchAgents/1.0 (public search, noninteractive)", "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read(1300000))

def scan_social(role):
    director = role["director"]
    if director not in TOPICS:
        return [], ["No social topic configured for " + director]
    topic_idx = 0 if role["id"] == director else (1 if role["id"].endswith("-A") else 2)
    term = TOPICS[director][topic_idx]
    items, errors = [], []

    # Bluesky's public search endpoint can change access or reject requests.
    try:
        url = "https://api.bsky.app/xrpc/app.bsky.feed.searchPosts?" + urllib.parse.urlencode(
            {"q": term, "sort": "latest", "limit": 25})
        data = _get(url)
        for post in data.get("posts", []):
            txt = str((post.get("record") or {}).get("text") or "").strip()
            if not txt or SPAM.search(txt) or not ACTUAL_OPPORTUNITY.search(txt):
                continue
            author = post.get("author") or {}
            handle = author.get("handle") or ""
            aturi = post.get("uri") or ""
            if not aturi.startswith("at://") or not handle:
                continue
            rkey = aturi.rsplit("/", 1)[-1]
            public_url = "https://bsky.app/profile/" + urllib.parse.quote(handle, safe=".-") + "/post/" + urllib.parse.quote(rkey, safe="")
            ts = (post.get("record") or {}).get("createdAt") or post.get("indexedAt") or ""
            items.append({"title": txt[:160], "url": public_url, "source": "Bluesky public post",
                          "excerpt": txt[:350], "updated": ts, "payment_verified": False,
                          "opportunity_verified": False, "social_platform": "Bluesky"})
    except Exception as exc:
        errors.append("Bluesky public search: " + str(exc)[:140])

    # Reddit may return a 403/rate-limit to unauthenticated searches; no workaround
    # using scraped mirrors or unauthorized account credentials is attempted.
    try:
        url = "https://www.reddit.com/search.json?" + urllib.parse.urlencode(
            {"q": term, "sort": "new", "limit": 20, "type": "link"})
        data = _get(url)
        for post in (data.get("data") or {}).get("children", []):
            p = post.get("data") or {}
            title = str(p.get("title") or "")
            body = str(p.get("selftext") or "")
            content = title + " " + body[:350]
            if not ACTUAL_OPPORTUNITY.search(content) or SPAM.search(content):
                continue
            link = p.get("permalink") or ""
            if not link.startswith("/r/"):
                continue
            created = p.get("created_utc")
            updated = datetime.fromtimestamp(float(created), timezone.utc).isoformat() if created else ""
            items.append({"title": title[:160], "url": "https://www.reddit.com" + link,
                          "source": "Reddit public post", "excerpt": content[:350],
                          "updated": updated, "payment_verified": False,
                          "opportunity_verified": False, "social_platform": "Reddit"})
    except Exception as exc:
        errors.append("Reddit public search: " + str(exc)[:140])
    return items, errors
