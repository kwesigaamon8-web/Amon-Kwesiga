#!/usr/bin/env python3
"""PC AI Miner: educational Bitcoin SHA256d + explicit opt-in configuration helper.

NOT a network miner. No unsolicited CPU use, network requests, wallet access,
account access, pool connection, startup tasks or cryptocurrency payments.
Authorized operators configure their own actual mining program separately.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from decimal import Decimal

B1="bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z"
B2="bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9"
GENESIS_MERKLE_LE=bytes.fromhex(
    "3ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a")
GENESIS_HASH="000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"
MODES={"solo":{"host":"public-pool.io","tls_port":4333},
       "pplns":{"host":"public-pool.io","tls_port":14333}}
SAFE_DIFFICULTY_BITS=12
MAX_DEMO_TRIES=250_000

def sha256d(blob:bytes)->bytes:
    return hashlib.sha256(hashlib.sha256(blob).digest()).digest()

def genesis_header(nonce=2083236893):
    if type(nonce) is not int or not 0 <= nonce <= 0xffffffff:
        raise ValueError("invalid nonce")
    return (struct.pack("<I",1)+bytes(32)+GENESIS_MERKLE_LE
            +struct.pack("<III",1231006505,0x1d00ffff,nonce))

def check_math():
    assert sha256d(genesis_header())[::-1].hex()==GENESIS_HASH
    assert len(genesis_header())==80
    return True

def demo(limit=15000,bits=SAFE_DIFFICULTY_BITS):
    if type(limit) is not int or not 1<=limit<=MAX_DEMO_TRIES:
        raise ValueError("demo must be finite and <= 250000 hashes")
    if type(bits) is not int or not 4<=bits<=20:
        raise ValueError("invalid educational target")
    prefix=genesis_header(0)[:76]
    target=(1<<(256-bits))-1
    first=None
    for nonce in range(limit):
        out=sha256d(prefix+struct.pack("<I",nonce))
        if int.from_bytes(out,"little")<=target:
            first={"nonce":nonce,"hash_hex":out[::-1].hex()}
            break
    return {"mode":"EDUCATIONAL_ONLY","tries":limit if first is None else first["nonce"]+1,
            "difficulty_bits":bits,"first_practice_proof":first,
            "actual_block_found":False,"coins_mined":0,
            "devices_or_networks_contacted":0}

def pool_configuration(fleet,mode,label,consent_hardware,consent_receiver):
    # Accept the donation only when both the device owner and fundraiser route
    # have knowingly opted in. No pool login is made by this program.
    if consent_hardware is not True or consent_receiver is not True:
        raise ValueError("explicit device-owner and receiver-donation consent required")
    if fleet not in ("B1","B2") or mode not in MODES:
        raise ValueError("invalid fleet or pool mode")
    if not isinstance(label,str) or not label.isalnum() or not 1<=len(label)<=20:
        raise ValueError("worker name must be 1-20 letters/digits")
    addr=B1 if fleet=="B1" else B2
    d=MODES[mode]
    return {"brand":"PC AI Miner","configuration_only":True,
            "does_not_start_a_miner":True,
            "manual_pool_url":f"stratum+tls://{d['host']}:{d['tls_port']}",
            "pool_mode":mode,"worker_username":addr+"."+label,
            "btc_network":"bitcoin-mainnet","donation_receiver":addr,
            "explicit_opt_in":True,
            "donation_disclosure":"Rewards from donated hashrate go to the selected B1/B2 address, not automatically to your own wallet.",
            "no_guaranteed_rewards":True}

def main():
    p=argparse.ArgumentParser(description="PC AI Miner: offline demos and voluntary manual pool configuration")
    sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("self-test")
    d=sub.add_parser("demo")
    d.add_argument("--tries",type=int,default=15000)
    d.add_argument("--bits",type=int,default=12)
    c=sub.add_parser("manual-config")
    c.add_argument("--fleet",choices=("B1","B2"),required=True)
    c.add_argument("--pool-mode",choices=("solo","pplns"),required=True)
    c.add_argument("--worker-label",default="Volunteer01")
    c.add_argument("--i-own-or-control-device",action="store_true")
    c.add_argument("--i-agree-to-donate-rewards",action="store_true")
    a=p.parse_args()
    check_math()
    if a.command=="self-test":
        print("PC_AI_MINER_GENESIS_SHA256D_PASS")
    elif a.command=="demo":
        print(json.dumps(demo(a.tries,a.bits),indent=2))
    else:
        x=pool_configuration(a.fleet,a.pool_mode,a.worker_label,
                             a.i_own_or_control_device,a.i_agree_to_donate_rewards)
        print(json.dumps(x,indent=2))

if __name__=="__main__":
    main()
