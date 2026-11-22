"""ENIGMA minimal public A2A 1.0.0 JSON-RPC code-collaboration bridge.

Only creates a safe, structured *proposal/quote response*. This service does NOT
execute other agents, write GitHub, accept payment, call models, contact outbound
websites, save visitor messages, or authenticate the claimed identity of a peer.
"""
from __future__ import annotations

import re
import threading
import time
import uuid
from collections import defaultdict, deque

from flask import Blueprint, jsonify, request

bridge = Blueprint("enigma_a2a", __name__)

OWNER = "https://github.com/kwesigaamon8-web/Amon-Kwesiga"
QUOTE = OWNER + "/issues/new?template=paid-work-request.yml"
AGENT_URL = "https://amon-kwesiga.onrender.com/a2a"
CARD_URL = OWNER + "/blob/main/docs/.well-known/agent-card.json"
MAX_REQUEST_BYTES = 4096
MAX_MESSAGE_CHARS = 800
MAX_REQUESTS_PER_MINUTE = 12

# Lightweight traffic limiting on the public, stateless work-brief endpoint.
_limiter_lock = threading.Lock()
_ip_buckets = defaultdict(deque)

CARD = {
    "name": "ENIGMA B1/B2 Code Collaboration Bridge",
    "description": (
        "Public non-custodial, no-cost, human-supervised code product scoping. "
        "The endpoint returns a deterministic code/product briefing and a "
        "GitHub quotation path. It does not invoke AI workers or build software."
    ),
    "provider": {"organization": "ENIGMA B1/B2", "url": OWNER},
    "version": "0.1.0",
    "documentationUrl": OWNER + "/blob/main/docs/AGENT_COLLABORATION.md",
    "supportedInterfaces": [
        {"url": AGENT_URL, "protocolBinding": "JSONRPC", "protocolVersion": "1.0"}
    ],
    "capabilities": {"streaming": False, "pushNotifications": False, "extendedAgentCard": False},
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"],
    "skills": [
        {
            "id": "enigma_code_product_scope",
            "name": "Code product scope and collaboration",
            "description": (
                "Derive a bounded original code project brief from a public-safe "
                "text request, with a review and quote path. No automatic contracts."
            ),
            "tags": ["code", "source", "python", "data", "public-research", "human-review"],
            "examples": ["Propose a CSV duplicate checker on fictional data"]
        }
    ]
}


def _error(request_id, code, message, status=200):
    return jsonify({"jsonrpc": "2.0", "id": request_id,
                    "error": {"code": code, "message": message}}), status


def _admit(ip: str) -> bool:
    now = time.monotonic()
    with _limiter_lock:
        q = _ip_buckets[ip]
        while q and now - q[0] >= 60:
            q.popleft()
        if len(q) >= MAX_REQUESTS_PER_MINUTE:
            return False
        q.append(now)
        # Bounded memory even if many distinct IPs contact an instance.
        if len(_ip_buckets) > 1024:
            stale = [k for k, v in _ip_buckets.items() if not v or now - v[-1] > 65]
            for k in stale[:1024]:
                del _ip_buckets[k]
        return True


def _public_safe_text(params: dict) -> str:
    msg = params.get("message")
    if not isinstance(msg, dict) or msg.get("role") != "ROLE_USER":
        raise ValueError("A ROLE_USER message is required")
    if not isinstance(msg.get("messageId"), str) or not msg["messageId"][:100]:
        raise ValueError("A nonempty messageId is required")
    parts = msg.get("parts")
    if not isinstance(parts, list) or not 1 <= len(parts) <= 3:
        raise ValueError("Provide one to three text parts")
    if any(not isinstance(p, dict) or not isinstance(p.get("text"), str)
           or len(p["text"]) > MAX_MESSAGE_CHARS for p in parts):
        raise ValueError("Only bounded text parts are accepted")
    text = " ".join(p["text"].strip() for p in parts).strip()
    if len(text) < 10 or len(text) > MAX_MESSAGE_CHARS:
        raise ValueError("Use 10 to 800 characters of publicly shareable requirements")
    # Do not process obvious secrets or contact details in a public interface.
    if re.search(r"(?i)(private.key|seed.phrase|password|api[_ -]?key|bearer\s+[a-z0-9]|@[\w.-]+\.[a-z]{2,})", text):
        raise ValueError("No private keys, passwords, tokens or personal contact data")
    return text


def _proposal(text: str) -> str:
    lowered = text.casefold()
    if any(x in lowered for x in ("malware", "steal", "phish", "unconsented mining", "credential theft")):
        return ("REJECTED: ENIGMA does not produce malicious, deceptive or "
                "unconsented software. No job, proposal or payout was created.")
    family = ("CSV/data validation" if "csv" in lowered or "dataset" in lowered
              else "Python utility" if "python" in lowered or "script" in lowered
              else "web/browser utility" if "html" in lowered or "website" in lowered
              else "original software/research scope")
    return (
        "ENIGMA B1/B2 — CODE PRODUCT IDEA ACKNOWLEDGED (NOT BUILT OR SOLD). "
        "Suggested category: " + family + ". "
        "Proposed deliverable: scoped original source, fictional sample, "
        "repeatable QA tests, licensing notes and buyer acceptance checklist. "
        "Buyer must authorize precise work and agree a custom quote. "
        "Public source and initial prices: " + OWNER + "/blob/main/docs/BUY_NOW.md. "
        "Request permitted human-reviewed collaboration: " + QUOTE + ". "
        "No external AI-agent connection, accepted commission or payment is implied."
    )


@bridge.get("/.well-known/agent-card.json")
def a2a_card():
    return jsonify(CARD)


@bridge.post("/a2a")
def a2a_message():
    if (request.content_length is not None and
            request.content_length > MAX_REQUEST_BYTES):
        return _error(None, -32600, "Request exceeds 4096 bytes", 413)
    if request.headers.get("A2A-Version") != "1.0":
        return _error(None, -32001, "Use A2A-Version: 1.0", 400)
    if not request.is_json:
        return _error(None, -32600, "JSON content type required", 415)
    if not _admit(request.remote_addr or "unknown"):
        return _error(None, -32000, "Public endpoint rate limit reached", 429)
    req = request.get_json(silent=True)
    if not isinstance(req, dict) or req.get("jsonrpc") != "2.0":
        return _error(None, -32600, "Invalid JSON-RPC request", 400)
    rid = req.get("id")
    if not isinstance(rid, (str, int)) or isinstance(rid, bool):
        return _error(None, -32600, "JSON-RPC request ID required", 400)
    if req.get("method") != "SendMessage":
        return _error(rid, -32601, "Only SendMessage is implemented")
    try:
        if not isinstance(req.get("params"), dict):
            raise ValueError("A2A params must be an object")
        p = req["params"]
        idea = _public_safe_text(p)
        context_id = p["message"].get("contextId")
        if context_id is not None and (not isinstance(context_id, str) or len(context_id) > 100):
            raise ValueError("Invalid contextId")
    except ValueError as exc:
        return _error(rid, -32602, str(exc))
    # A2A 1.0 response: exactly one result.message, no task is created.
    response_msg = {
        "messageId": str(uuid.uuid4()),
        "contextId": context_id or str(uuid.uuid4()),
        "role": "ROLE_AGENT",
        "parts": [{"text": _proposal(idea)}]
    }
    return jsonify({"jsonrpc": "2.0", "id": rid, "result": {"message": response_msg}})
