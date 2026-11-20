"""Independent Bitcoin BIP173/BIP350 receipt safety and open-source license tests.

Source: https://github.com/bitcoin/bips/blob/master/bip-0352/bech32m.py
MIT copyright and permission notice is retained verbatim in vendored source.
Does not sign, mine, create TXs, or send funds.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vendor.bitcoin_bip352_bech32m import (
    Encoding, bech32_encode, convertbits,
)
from btc_receiver_safety import (
    B1, B2, OWNER_MAINNET_RECEIVERS,
    parse_mainnet_receiver, require_approved_receiver, require_all_owner_receivers,
)
import bitcoin_mainnet_receipt_probe as probe
import btc_public_address_snapshot as snapshot


def reject(fn, expected=None):
    try:
        fn()
    except (ValueError, TypeError) as e:
        if expected is not None and expected not in str(e):
            raise AssertionError("Unexpected rejection: " + str(e)) from e
    else:
        raise AssertionError("An invalid BTC receiving address was accepted")


def main():
    checked = require_all_owner_receivers()
    assert len(checked) == 2
    assert set(checked) == set(OWNER_MAINNET_RECEIVERS)
    for fleet, addr in OWNER_MAINNET_RECEIVERS.items():
        result = checked[fleet]
        assert result["address"] == addr
        assert result["network"] == "bitcoin-mainnet"
        assert result["witness_version"] == 0
        assert result["witness_program_bytes"] == 20
        assert result["checksum_scheme"] == "BECH32"
        assert result["wallet_control_verified"] is False
        assert result["received_payment_verified"] is False
        assert require_approved_receiver(fleet, addr) == result
        reject(lambda: parse_mainnet_receiver(addr.upper()), "INVALID_CASE")
        reject(lambda: parse_mainnet_receiver(addr[:5].upper()+addr[5:]), "INVALID_CASE")
        mutated = addr[:-1] + ("q" if addr[-1] != "q" else "p")
        reject(lambda: parse_mainnet_receiver(mutated), "NETWORK_OR_CHECKSUM_INVALID")
        reject(lambda: require_approved_receiver(fleet, mutated), "ADDRESS_NOT_APPROVED")
    reject(lambda: require_approved_receiver("BountyScoutAI", B1), "ADDRESS_NOT_APPROVED")
    reject(lambda: require_approved_receiver("transferexperiment", B2), "ADDRESS_NOT_APPROVED")
    reject(lambda: require_approved_receiver("UNKNOWN", B1), "UNKNOWN_FLEET")
    # The synthetic short testnet string is invalid by length first; the actual
    # valid BIP173 testnet address below proves network rejection.
    reject(lambda: parse_mainnet_receiver("https://mempool.space/"+B1))
    reject(lambda: parse_mainnet_receiver("bc1q"))
    reject(lambda: parse_mainnet_receiver(B1 + "\n"))

    # Official specification semantics: witness v0 must use Bech32 checksum,
    # witness v1+ Bech32m; never silently accept the other scheme.
    v0_words = [0] + convertbits(bytes([7]*20), 8, 5, True)
    valid_v0 = bech32_encode("bc", v0_words, Encoding.BECH32)
    assert parse_mainnet_receiver(valid_v0)["witness_version"] == 0
    reject(lambda: parse_mainnet_receiver(bech32_encode("bc", v0_words, Encoding.BECH32M)),
           "WRONG_CHECKSUM_SCHEME")
    v1_words = [1] + convertbits(bytes([8]*32), 8, 5, True)
    valid_v1 = bech32_encode("bc", v1_words, Encoding.BECH32M)
    assert parse_mainnet_receiver(valid_v1)["witness_version"] == 1
    reject(lambda: parse_mainnet_receiver(bech32_encode("bc", v1_words, Encoding.BECH32)),
           "WRONG_CHECKSUM_SCHEME")
    reject(lambda: parse_mainnet_receiver(bech32_encode("tb", v0_words, Encoding.BECH32)),
           "NETWORK_OR_CHECKSUM_INVALID")
    v0_wrong_size = bech32_encode("bc", [0]+convertbits(bytes([1]*18),8,5,True),Encoding.BECH32)
    reject(lambda: parse_mainnet_receiver(v0_wrong_size), "V0_PROGRAM_WRONG_LENGTH")
    reject(lambda: parse_mainnet_receiver(B1.replace("1","l",1)), "NETWORK_OR_CHECKSUM_INVALID")

    assert probe.ACCOUNTS == OWNER_MAINNET_RECEIVERS, "Bitcoin address registry drift"
    assert snapshot.ADDRESSES == {"B1": B1, "B2": B2}, "Bitcoin snapshot address registry drift"
    probe.self_test()
    snapshot.selftest()
    source = Path("crypto-agents/vendor/bitcoin_bip352_bech32m.py").read_text()
    assert "Copyright (c) 2017, 2020 Pieter Wuille" in source
    assert "Permission is hereby granted" in source
    assert "THE SOFTWARE IS PROVIDED" in source
    assert "class Encoding(Enum):" in source
    report={
        "schema":"B1B2_BIP173_BIP350_RECEIVER_SAFETY_V1",
        "official_upstream":"https://github.com/bitcoin/bips/blob/master/bip-0352/bech32m.py",
        "license":"MIT (verbatim notice retained)",
        "approved_fleets":list(checked),
        "approved_receiver_checksums_valid":True,
        "v0_v1_wrong_encoding_rejected":True,
        "mainnet_vs_testnet_separated":True,
        "B1_B2_cross_address_swap_rejected":True,
        "mutated_addresses_rejected":True,
        "public_explorer_read_only":True,
        "wallet_signing_or_btc_send_performed":False,
        "earned_btc_receipt_verified_by_static_test":False,
    }
    p=Path("btc-safety-evidence/BTC_RECEIVING_SAFETY.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(report,indent=2)+"\n")
    print("B1B2_OFFICIAL_BITCOIN_OPEN_SOURCE_RECEIVER_SAFETY_PASS "+json.dumps(report))


if __name__ == "__main__":
    main()
