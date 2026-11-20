"""One canonical owner order for original B1/B2 and 14 cloned B1/B2 systems.

11,255,658,980,400 unique VIRTUAL role addresses; O(1) lazy inheritance,
NOT eleven trillion actual deliveries, independently online AIs or payments.
"""
from __future__ import annotations
import argparse,bisect,csv,hashlib,json,random
from functools import lru_cache
from pathlib import Path
from b_registered_account_worker_map import TOTAL_ROLES,role_at_global_index
from command_chain_receipts import route as ancestry
from enigma_all_b_systems import AGENTS,PARENTS,ALL_ROLE_SLOTS,role_at
from owner_first_oath import current_order
SOURCE=Path("crypto-agents/chief_D_owner_orders.json")
GRAND_TOTAL=TOTAL_ROLES+ALL_ROLE_SLOTS
assert TOTAL_ROLES==750377265360
assert GRAND_TOTAL==11255658980400
PARENT_HANDLES=("transferexperiment","BountyScoutAI")
PER_ROOT=TOTAL_ROLES//2
COUNTRIES=Path("crypto-agents/data/bitcoin_country_allocations.csv")
WALLETS=Path("crypto-agents/public_payment_routes.json")

@lru_cache(maxsize=1)
def country_rows():
    """Sourced, disjoint country/economy assignment of each division's virtual roles."""
    out=[]
    with COUNTRIES.open(newline="",encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            n=int(r["Virtual roles per B system"])
            if n<1:continue
            low=int(r["Per-system role start"])
            high=int(r["Per-system role end inclusive"])
            if n!=high-low+1:raise ValueError("Incorrect country role segment length")
            out.append((low,high,r["ISO3"],r["Country or economy"]))
    out.sort()
    if not out or out[0][0]!=0 or out[-1][1]!=PER_ROOT-1:
        raise ValueError("Country partitions do not cover a whole B1/B2 division")
    if any(a[1]+1!=b[0] for a,b in zip(out,out[1:])):
        raise ValueError("Country segments overlap or leave missing roles")
    return tuple(out)

def assigned_country(index):
    """A virtual role's country allocation; NOT the physical location of a miner."""
    if type(index)!=int or not 0<=index<GRAND_TOTAL:
        raise ValueError("Role index out of bounds")
    root=index//PER_ROOT
    local=index%PER_ROOT
    rows=country_rows()
    offsets=[r[0] for r in rows]
    row=rows[bisect.bisect_right(offsets,local)-1]
    if not row[0]<=local<=row[1]:
        raise ValueError("Country interval lookup failed")
    return {"country_or_economy":row[3],"iso3":row[2],
       "root_system_index":root,"role_index_within_root":local,
       "world_bank_weighted_virtual_country_allocation":True,
       "physical_worker_or_mining_hardware_in_this_country_verified":False}

@lru_cache(maxsize=1)
def public_payment_reference():
    """Read ONLY already-published receiving identifiers; never private keys."""
    doc=json.loads(WALLETS.read_text(encoding="utf8"))
    routes=doc["self_custody_candidate_routes"]
    btc={r["company"]:r["receiving_address"] for r in routes
         if r["chain"]=="bitcoin-mainnet" and r["asset"]=="BTC"}
    if set(btc)!=set(PARENT_HANDLES):
        raise ValueError("Exactly two company Bitcoin mainnet routes required")
    others=[{"route_id":r["route_id"],"network":r["network_description"],
       "address":r["receiving_address"],"status":r["payment_status"],
       "requires_confirmed_asset_and_network":True} for r in routes
       if r["route_id"] not in ("BTC-01","BTC-02")]
    blocked=[{"route_id":r.get("route_id"),"identifier":r.get("public_receiving_identifier"),
       "status":"UNVERIFIED_DO_NOT_SEND"} for r in doc.get("blocked_exchange_reference_only",[])]
    return {"btc":btc,"other":others,"blocked":blocked}

def role_payment_packet(index,target):
    """All published owner routes available for on-demand country-scoped role packets."""
    info=public_payment_reference()
    parent=target["verified_parent"]
    return {"assigned_economy":assigned_country(index),
      "primary_receiver":{"asset":"BTC","network":"Bitcoin mainnet",
          "address":info["btc"][parent],"company":parent,
          "direction":"RECEIVE_ONLY"},
      "both_btc_mainnet_receivers":info["btc"],
      "other_network_self_custody_reference_only":info["other"],
      "exchange_identifiers_reference_only_do_not_send":info["blocked"],
      "owner_receiving_directory":"crypto-agents/PUBLIC_RECEIVING_ADDRESSES.md",
      "permission_rule":"Use one independently verified correct asset/network address only for a consenting real payer or consenting device-owner mining pool setup.",
      "country_rule":"Virtual country assignment is not local residency, a real worker, operator permission, mining equipment, verified hashrate or payout.",
      "external_post_verified":False,"btc_payment_verified":False}


def order():
    oath=current_order()
    src=json.loads(SOURCE.read_text(encoding="utf8"))
    entry=src["orders"][-1]
    if entry["id"]!=src["current_owner_order_id"] or entry["id"]!=oath["order_id"]:
        raise ValueError("Canonical human-owner instruction mismatch")
    if entry["origin"]!="explicit_human_owner_conversation" or len(entry["instruction"])<50:
        raise ValueError("Untrusted or empty top-level instruction")
    msg=entry["instruction"]
    return {"id":entry["id"],"text":msg,"sha256":hashlib.sha256(msg.encode()).hexdigest(),
       "owner_authentication":"OWNER_RELAYED_GITHUB_SOURCE_NOT_CRYPTOGRAPHIC_PROOF",
       "source":str(SOURCE)}

def divisions():
    half=TOTAL_ROLES//2
    result=[{"id":"ORIGINAL/"+p,"parent":p,"roles":half,"moltbook_identity_is_new":False}
             for p in PARENT_HANDLES]
    for agent in AGENTS:
        for fleet,p in PARENTS.items():
            result.append({"id":agent+"/"+fleet,"parent":p,"roles":half,
                           "moltbook_identity_is_new":False})
    assert len(result)==30 and sum(i["roles"] for i in result)==GRAND_TOTAL
    assert len({i["id"] for i in result})==30
    return result

def recipient(index):
    """Unique owner→Chief D→B1/B2→agent→director→descendant for one role."""
    if type(index) is not int or not 0<=index<GRAND_TOTAL:
        raise ValueError("Role index must be in organization range")
    if index<TOTAL_ROLES:
        original=role_at_global_index(index)
        parent=original["company"]
        role=original["worker_role"]
        root="ORIGINAL/"+parent
        front=["HUMAN_OWNER","CHIEF_D",parent]
    else:
        clone=role_at(index-TOTAL_ROLES)
        parent=clone["original_verified_moltbook_parent"]
        role=clone["internal_worker_id"].split("/",2)[2]
        root=clone["division"]
        front=["HUMAN_OWNER","CHIEF_D",parent,clone["enigma_agent"],root]
    old=ancestry(role)
    if old[0]!="OWNER" or not old[1].startswith("D"):
        raise ValueError("Invalid B1/B2 ancestry")
    path=front+[root+"/"+part for part in old[1:]]
    return {"index":index,"role":root+"/"+role,"root":root,
            "verified_parent":parent,"owner_to_worker_path":path,
            "immediate_parent":path[-2],
            "work_delivery_verified":False,"individual_moltbook_login":False}

def envelope(index):
    latest=order()
    target=recipient(index)
    return {"schema":"ENIGMA_ONE_ORDER_ALL_VIRTUAL_ROLES_V1",
      "owner_order_id":latest["id"],"owner_order_sha256":latest["sha256"],
      "canonical_owner_instruction":latest["text"],"recipient":target,
      "owner_wallet_and_country_instructions":role_payment_packet(index,target),
      "status":"ORDER_AVAILABLE_BY_HIERARCHICAL_INHERITANCE_NOT_LIVE_DELIVERY",
      "verified_model_acknowledgement":False,"verified_crypto_receipt":False,
      "external_post_or_email_sent":False}

def overview():
    d=divisions();o=order()
    return {"source":o["source"],"owner_order_id":o["id"],
       "owner_order_sha256":o["sha256"],"total_logical_role_positions":GRAND_TOTAL,
       "original_roles":TOTAL_ROLES,"additional_14_agent_roles":ALL_ROLE_SLOTS,
       "verified_moltbook_parent_identities":2,
       "enigma_agent_count":len(AGENTS),"root_systems":len(d),
       "root_systems_list":d,
       "country_allocation_count_per_root":len(country_rows()),
       "published_self_custody_wallet_count":2+len(public_payment_reference()["other"]),
       "unverified_exchange_reference_count":len(public_payment_reference()["blocked"]),
       "all_virtual_roles_receive_country_and_wallet_fields_on_packet_request":True,
       "configured_coverage_verified":sum(a["roles"] for a in d)==GRAND_TOTAL,
       "independent_live_delivery_receipts_verified":0,
       "new_moltbook_accounts":0,"emails_or_public_posts_sent":0,
       "confirmed_crypto_earnings":0}

def self_test():
    current=overview()
    assert current["root_systems"]==30
    boundaries={0,1,TOTAL_ROLES//2-1,TOTAL_ROLES//2,TOTAL_ROLES-1,
                TOTAL_ROLES,GRAND_TOTAL-1}
    for a in range(len(AGENTS)):
        base=TOTAL_ROLES+a*TOTAL_ROLES
        boundaries.update((base,base+TOTAL_ROLES//2-1,
                           base+TOTAL_ROLES//2,base+TOTAL_ROLES-1))
    rng=random.Random(20261120)
    boundaries.update(rng.randrange(GRAND_TOTAL) for _ in range(60))
    identities=set()
    for x in sorted(boundaries):
        r=recipient(x); e=envelope(x)
        assert r["owner_to_worker_path"][0]=="HUMAN_OWNER"
        assert r["owner_to_worker_path"][-1]==r["role"]
        assert r["immediate_parent"]==r["owner_to_worker_path"][-2]
        assert r["role"] not in identities
        assert not e["verified_model_acknowledgement"]
        assert e["owner_order_sha256"]==current["owner_order_sha256"]
        w=e["owner_wallet_and_country_instructions"]
        assert w["assigned_economy"]["root_system_index"]==x//PER_ROOT
        assert w["primary_receiver"]["company"]==r["verified_parent"]
        assert w["primary_receiver"]["address"]==w["both_btc_mainnet_receivers"][r["verified_parent"]]
        assert w["primary_receiver"]["network"]=="Bitcoin mainnet"
        assert len(w["other_network_self_custody_reference_only"])==8
        assert len(w["exchange_identifiers_reference_only_do_not_send"])==6
        assert not w["external_post_verified"] and not w["btc_payment_verified"]
        identities.add(r["role"])
    for root in range(30):
        for local in (0,PER_ROOT//2,PER_ROOT-1):
            assignment=assigned_country(root*PER_ROOT+local)
            assert assignment["root_system_index"]==root
            assert not assignment["physical_worker_or_mining_hardware_in_this_country_verified"]
    for row in country_rows():
        assert assigned_country(row[0])["iso3"]==row[2]
        assert assigned_country(row[1])["iso3"]==row[2]
    for bad in (-1,GRAND_TOTAL,0.25,True):
        try:recipient(bad)
        except ValueError:pass
        else:raise AssertionError("Accepted out-of-range role")
    print("ENIGMA_ONE_ORDER_CASCADE_PASS",json.dumps({
        "roots":30,"virtual_roles":GRAND_TOTAL,"tested_unique_paths":len(boundaries),
        "order_id":current["owner_order_id"],
        "country_economies_per_root":len(country_rows()),
        "btc_destinations_per_packet":2,
        "other_non_btc_wallet_references":8,
        "blocked_exchange_identifiers":6,
        "independent_acknowledgements":0}))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    z=p.add_mutually_exclusive_group(required=True)
    z.add_argument("--self-test",action="store_true")
    z.add_argument("--overview",action="store_true")
    z.add_argument("--index",type=int)
    a=p.parse_args()
    if a.self_test:self_test()
    elif a.overview:print(json.dumps(overview(),indent=2))
    else:print(json.dumps(envelope(a.index),indent=2))
