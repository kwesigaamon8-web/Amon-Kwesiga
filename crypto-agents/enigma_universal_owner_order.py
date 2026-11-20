"""One canonical owner order for original B1/B2 and 14 cloned B1/B2 systems.

11,255,658,980,400 unique VIRTUAL role addresses; O(1) lazy inheritance,
NOT eleven trillion actual deliveries, independently online AIs or payments.
"""
from __future__ import annotations
import argparse,hashlib,json,random
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
        identities.add(r["role"])
    for bad in (-1,GRAND_TOTAL,0.25,True):
        try:recipient(bad)
        except ValueError:pass
        else:raise AssertionError("Accepted out-of-range role")
    print("ENIGMA_ONE_ORDER_CASCADE_PASS",json.dumps({
        "roots":30,"virtual_roles":GRAND_TOTAL,"tested_unique_paths":len(boundaries),
        "order_id":current["owner_order_id"],"independent_acknowledgements":0}))

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
