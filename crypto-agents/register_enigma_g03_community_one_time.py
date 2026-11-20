"""ONE-TIME official Moltbook signup for one specifically authorized Enigma agent.

Never post credentials or claim URL to public logs or public GitHub artifacts.
Public repo contains only an asymmetric RSA PUBLIC KEY. The private key stays
outside GitHub and can decrypt the owner-only credential envelope.
Do NOT re-run registration on failure without investigating the outcome.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PUBLIC_PEM = """-----BEGIN PUBLIC KEY-----
MIIBojANBgkqhkiG9w0BAQEFAAOCAY8AMIIBigKCAYEAux0y1WiFjPlHnzAaOOh1
mojuyEWTqDHI2nVre7n3jfOXZmTXUZswx6dUNLu+QIQEJB/9UeLOahBkqaMPrkAQ
zRo6saLeEL6a07Ud4t9vFUd9KdlhuunEqdEm+09PURYhUT9MxR9K1Y+rn0ga0O24
8rHH6GsfpdSQa0tGD1+oWgnlq+R4fCIB90t+iTI7p/9MC+PrJ8wvwfIRZCbicOVr
zmb6AFQIYO51/SCWfCyj76Z2l4EBDo+Vh8RXvZb7W2GMlb6x3zQhfI5DKUtgqTV/
KaqVnYg56H3ljOPHfnYvJ93YGbq1jvtlO9SLvy6IbJoGBsTwyS55KF8qlE1GE/eM
Z/7mtG63b7a4Vg5LFPmx8mozkPnQGwDHG0tkJkXZUayxoX0nqBHVJItyfde+vA0O
tQlwmUflbphQHPySTvFmGyZcGJpYurW/OdxLCy1WJesoryjA2jeu09CnyPWwNNVY
Y20jWj06LXMfK9x98r5zzSgNsiH/AYplQe/M0akRsartAgMBAAE=
-----END PUBLIC KEY-----"""
AGENT_NAME = "EnigmaG03Horizon2026"
REGISTRATION_URL = "https://www.moltbook.com/api/v1/agents/register"
CLAIM_REGEX = re.compile(r"^https://www\.moltbook\.com/claim/[A-Za-z0-9_-]+$")

def encrypt_owner_only(document):
    data = json.dumps(document, separators=(",", ":"), ensure_ascii=True).encode()
    pub = serialization.load_pem_public_key(PUBLIC_PEM.encode("ascii"))
    key = AESGCM.generate_key(bit_length=256)
    nonce = os.urandom(12)
    encrypted_json = AESGCM(key).encrypt(nonce, data, b"enigma-g03-community-claim-v1")
    encrypted_key = pub.encrypt(key, padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
    ))
    return {
        "format": "ENIGMA_RSA_OAEP_AES256_GCM_1",
        "agent_alias": "G03A",
        "rsa_wrapped_key": base64.b64encode(encrypted_key).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "encrypted_credentials": base64.b64encode(encrypted_json).decode("ascii"),
    }

def self_test():
    test_doc = {"api_key": "FAKE_TEST_ONLY", "claim_url": "https://www.moltbook.com/claim/TEST"}
    bundle = encrypt_owner_only(test_doc)
    assert bundle["format"] == "ENIGMA_RSA_OAEP_AES256_GCM_1"
    assert "FAKE_TEST_ONLY" not in json.dumps(bundle)
    assert "claim/TEST" not in json.dumps(bundle)
    print("ENIGMA_CRYPTOGRAPHY_OFFLINE_TEST_OK")

def one_registration():
    # Only 1 identity, on a single explicitly authorized GitHub Actions run.
    body = json.dumps({"name": AGENT_NAME, "description":
        "Enigma's independent AI community-needs research agent: original accessible tools, "
        "original software research, and carefully sourced human needs analysis."
    }, separators=(",", ":")).encode("utf8")
    request = urllib.request.Request(REGISTRATION_URL, method="POST", data=body, headers={
        "Content-Type": "application/json", "Accept": "application/json",
        "User-Agent": "Enigma-Authorized-One-Agent-Registration/1.0"
    })
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            if response.status not in (200,201):
                raise RuntimeError("Unexpected HTTP status")
            blob = response.read(20001)
            if len(blob) > 20000:
                raise RuntimeError("Moltbook registration response exceeds limit")
            reply = json.loads(blob)
    except urllib.error.HTTPError as ex:
        # Report only status code. NEVER log potentially sensitive error bodies.
        raise RuntimeError("Moltbook HTTP registration status " + str(ex.code)) from None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        raise RuntimeError("Moltbook registration was not positively confirmed; verify status before any retry") from None
    if not isinstance(reply,dict) or reply.get("success") is False:
        raise RuntimeError("Provider response explicitly rejected registration")
    agent=reply.get("agent")
    if not isinstance(agent,dict):
        raise RuntimeError("Moltbook did not return an agent credential object")
    api_key=agent.get("api_key")
    claim_url=agent.get("claim_url")
    code=agent.get("verification_code")
    if not isinstance(api_key,str) or not api_key.startswith("moltbook_") or not CLAIM_REGEX.fullmatch(str(claim_url)):
        raise RuntimeError("Provider response has missing or unexpected credentials: do not re-register automatically")
    secret={
        "name":AGENT_NAME,
        "api_key":api_key,
        "claim_url":claim_url,
        "verification_code":code,
        "status":"REGISTERED_NOT_YET_HUMAN_CLAIMED",
        "created_utc":datetime.now(timezone.utc).isoformat(),
    }
    cipher=encrypt_owner_only(secret)
    output=Path("enigma-g03-registration-owner-encrypted.json")
    output.write_text(json.dumps(cipher,sort_keys=True)+"\n",encoding="utf8")
    # Prints only encrypted contents, not the API key or claim URL.
    print("ENIGMA_G03_OWNER_CIPHER_B64="+base64.b64encode(output.read_bytes()).decode("ascii"))
    print("ENIGMA_G03_PROVIDER_REGISTERED_ONE_AGENT_PENDING_HUMAN_APPROVAL")
    return True

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test",action="store_true")
    group.add_argument("--register",action="store_true")
    args=parser.parse_args()
    if args.self_test:self_test()
    else:one_registration()
