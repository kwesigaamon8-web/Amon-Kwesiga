"""Fail-closed Bitcoin receiving-address safety for B1/B2.

Uses a VERBATIM vendored MIT-licensed reference by Pieter Wuille from the
Bitcoin BIPs repository (bip-0352/bech32m.py). Validates Bitcoin native
SegWit Bech32 (v0) and Bech32m (v1+) checksum, padding and witness version
before requesting public chain evidence or presenting a payment link.

No private key generation, wallet signing, transaction broadcast, or mining.
"""
from __future__ import annotations
from vendor.bitcoin_bip352_bech32m import (
    bech32_decode, bech32_encode, convertbits, Encoding
)

B1="bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z"
B2="bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9"
OWNER_MAINNET_RECEIVERS={
    "transferexperiment": B1,
    "BountyScoutAI": B2,
}


def parse_mainnet_receiver(address: str) -> dict:
    if (not isinstance(address, str) or not 14 <= len(address) <= 90
            or address != address.lower() or any(ord(c) < 33 or ord(c) > 126
                                                 for c in address)):
        raise ValueError("BTC_MAINNET_INVALID_CASE_LENGTH_OR_CHARACTERS")
    hrp, words, scheme = bech32_decode(address)
    if hrp != "bc" or not isinstance(words, list) or len(words) < 2:
        raise ValueError("BTC_MAINNET_NETWORK_OR_CHECKSUM_INVALID")
    version = words[0]
    if version < 0 or version > 16:
        raise ValueError("BTC_MAINNET_WITNESS_VERSION_INVALID")
    if scheme != (Encoding.BECH32 if version == 0 else Encoding.BECH32M):
        raise ValueError("BTC_MAINNET_WRONG_CHECKSUM_SCHEME_FOR_VERSION")
    program = convertbits(words[1:], 5, 8, False)
    if program is None or not 2 <= len(program) <= 40:
        raise ValueError("BTC_MAINNET_WITNESS_PROGRAM_OR_PADDING_INVALID")
    if version == 0 and len(program) not in (20, 32):
        raise ValueError("BTC_MAINNET_V0_PROGRAM_WRONG_LENGTH")
    if bech32_encode("bc", words, scheme) != address:
        raise ValueError("BTC_MAINNET_NONCANONICAL_ADDRESS")
    return {
        "network": "bitcoin-mainnet",
        "address": address,
        "witness_version": version,
        "witness_program_bytes": len(program),
        "checksum_scheme": scheme.name,
        "is_receiving_address_valid": True,
        "wallet_control_verified": False,
        "received_payment_verified": False,
    }


def require_approved_receiver(fleet: str, address: str) -> dict:
    if fleet not in OWNER_MAINNET_RECEIVERS:
        raise ValueError("BTC_MAINNET_UNKNOWN_FLEET")
    if address != OWNER_MAINNET_RECEIVERS[fleet]:
        raise ValueError("BTC_MAINNET_ADDRESS_NOT_APPROVED_FOR_FLEET")
    return parse_mainnet_receiver(address)


def require_all_owner_receivers() -> dict:
    if len(OWNER_MAINNET_RECEIVERS) != 2 or len(set(OWNER_MAINNET_RECEIVERS.values())) != 2:
        raise ValueError("BTC_MAINNET_OWNER_WALLET_REFERENCE_DUPLICATED")
    return {fleet: require_approved_receiver(fleet, addr)
            for fleet,addr in OWNER_MAINNET_RECEIVERS.items()}
