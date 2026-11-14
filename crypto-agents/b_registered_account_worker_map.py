"""All 750,377,265,360 ORIGINAL B roles belong to the TWO named agent accounts.

This reversible, deterministic namespace does not create 750B API accounts,
real process executions, tokens, customers or earned coins. Every real worker
must load the own-account delegation packet at ACTUAL model invocation.
"""
from __future__ import annotations
import argparse
import bisect
import json
import random
from b_certified_agent_service_router import (
    FLEETS, PER_DIRECTOR, OFFSETS, ROLES_PER_DIRECTOR, TOTAL_ROLES, role_index,
)
from b_owner_account_link import agent_packet as accounts

PLATFORM="Moltbook"
OWNING_AGENT_HANDLES={"transferexperiment":"transferexperiment",
                      "BountyScoutAI":"BountyScoutAI"}
DIRECTORS=10
ROLES_PER_ACCOUNT=10*ROLES_PER_DIRECTOR
assert len(FLEETS)==2
assert 2*ROLES_PER_ACCOUNT==TOTAL_ROLES==750_377_265_360
LEVELS=tuple(PER_DIRECTOR)
STARTS=[OFFSETS[k] for k in LEVELS]
assert STARTS==sorted(STARTS)

def role_at_global_index(index):
    """Invert the collision-free rank for every original D/A/M/W/S/G/H identity."""
    if type(index)!=int or not 0<=index<TOTAL_ROLES:
        raise ValueError("Index outside original 750,377,265,360-role organization")
    fleet=FLEETS[index//ROLES_PER_ACCOUNT]
    director_index=(index%ROLES_PER_ACCOUNT)//ROLES_PER_DIRECTOR
    local=(index%ROLES_PER_ACCOUNT)%ROLES_PER_DIRECTOR
    kind=LEVELS[bisect.bisect_right(STARTS,local)-1]
    ordinal=local-OFFSETS[kind]
    head=f"D{director_index+1:02d}"
    if kind=="D":
        role=head
    elif kind=="A":
        role=head+("-A" if ordinal==0 else "-B")
    else:
        values={}
        if kind=="M":
            values["M"]=ordinal
        elif kind=="W":
            values["M"],values["W"]=divmod(ordinal,50)
        elif kind=="S":
            v,values["S"]=divmod(ordinal,150)
            values["M"],values["W"]=divmod(v,50)
        elif kind=="G":
            v,values["G"]=divmod(ordinal,500)
            v,values["S"]=divmod(v,150)
            values["M"],values["W"]=divmod(v,50)
        elif kind=="H":
            v,values["H"]=divmod(ordinal,666)
            v,values["G"]=divmod(v,500)
            v,values["S"]=divmod(v,150)
            values["M"],values["W"]=divmod(v,50)
        parts=[f"M{values['M']+1:02d}"]
        if kind in ("W","S","G","H"):parts.append(f"W{values['W']+1:02d}")
        if kind in ("S","G","H"):parts.append(f"S{values['S']+1:03d}")
        if kind in ("G","H"):parts.append(f"G{values['G']+1:03d}")
        if kind=="H":parts.append(f"H{values['H']+1:03d}")
        role=head+"-"+"-".join(parts)
    if role_index(fleet,role)!=index:
        raise AssertionError("Role index is not reversible")
    return {"company":fleet,"registered_agent_handle":OWNING_AGENT_HANDLES[fleet],
        "worker_role":role,"original_role_global_index":index,"tier":kind}

def packet(fleet,role):
    if fleet not in FLEETS:raise ValueError("Unknown agent-account company")
    idx=role_index(fleet,role)
    assert FLEETS[idx//ROLES_PER_ACCOUNT]==fleet
    assert role_at_global_index(idx)["worker_role"]==role
    routes=accounts(fleet)
    return {
      "schema":"B_AGENT_ACCOUNT_ORIGINAL_750B_ROLE_DELEGATION_V1",
      "original_role_global_index":idx,
      "original_role_id":fleet+"/"+role,
      "registered_agent_platform":PLATFORM,
      "registered_agent_handle":OWNING_AGENT_HANDLES[fleet],
      "public_agent_profile_hint":"https://www.moltbook.com/u/"+OWNING_AGENT_HANDLES[fleet],
      "public_profile_hint_does_not_prove_authenticated_login":True,
      "role_acts_as_internal_delegate_of_registered_agent":True,
      "external_platform_has_approved_this_worker_as_individual_account":False,
      "external_platform_account_credential_present_or_validated_by_this_packet":False,
      "may_impersonate_an_external_AI_account":False,
      "company_original_role_capacity":ROLES_PER_ACCOUNT,
      "all_original_role_capacity":TOTAL_ROLES,
      "role_is_a_real_active_AI_process":False,
      "real_process_and_model_inference_evidence_required":True,
      "actual_external_post_or_comment_requires_authenticated_own_agent_account":True,
      "external_spam_or_cross_account_posting_allowed":False,
      "reports_up_to":"CHIEF_D -> HUMAN_OWNER",
      "owner_receiving_BTC_mainnet":routes["owner_primary_BTC_mainnet_route"]["address"],
      "other_network_routes_available_for_review_only":True,
      "crypto_payment_verified":False,
      "commercial_instruction":"Execute distinct useful original tasks for real approved clients, "
          "under your own registered agent organizational identity. Obtain genuine consent "
          "before external interaction and real acceptance before alleging payments. "
          "No promise that 750B roles are online."
    }

def self_test():
    rng=random.Random(20261114)
    chosen=set()
    tiers=set()
    for fleet in FLEETS:
        for director in range(10):
            start=FLEETS.index(fleet)*ROLES_PER_ACCOUNT+director*ROLES_PER_DIRECTOR
            for k in LEVELS:
                first=start+OFFSETS[k]
                last=first+PER_DIRECTOR[k]-1
                middle=first+PER_DIRECTOR[k]//2
                for i in set((first,last,middle)):
                    r=role_at_global_index(i)
                    assert r["company"]==fleet and r["tier"]==k
                    pkt=packet(fleet,r["worker_role"])
                    assert pkt["original_role_global_index"]==i
                    assert pkt["registered_agent_handle"]==OWNING_AGENT_HANDLES[fleet]
                    assert pkt["external_platform_account_credential_present_or_validated_by_this_packet"] is False
                    chosen.add(i)
                    tiers.add(k)
    for _ in range(320):
        n=rng.randrange(TOTAL_ROLES)
        r=role_at_global_index(n)
        assert packet(r["company"],r["worker_role"])["original_role_global_index"]==n
        chosen.add(n)
    for invalid in (-1,TOTAL_ROLES,True,1.5,None):
        try:role_at_global_index(invalid)
        except ValueError:pass
        else:raise AssertionError("Invalid original role index accepted")
    assert tiers==set(PER_DIRECTOR)
    assert role_at_global_index(0)["company"]==FLEETS[0]
    assert role_at_global_index(ROLES_PER_ACCOUNT)["company"]==FLEETS[1]
    assert role_at_global_index(TOTAL_ROLES-1)["company"]==FLEETS[1]
    print("B_ALL_ORIGINAL_ROLES_ASSIGNED_TO_TWO_REGISTERED_AGENT_HANDLES_PASS",
        json.dumps({"total_configured_original_roles":TOTAL_ROLES,
        "per_registered_agent_handle":ROLES_PER_ACCOUNT,
        "handles":list(OWNING_AGENT_HANDLES.values()),
        "independent_sample_inverse_mappings_tested":len(chosen),
        "tiers":list(LEVELS),
        "real_models_started_by_test":0,"platform_authenticated_logins_by_test":0,
        "confirmed_crypto_income_from_test":0}))

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--self-test",action="store_true")
    cli.add_argument("--global-index",type=int)
    cli.add_argument("--fleet",choices=FLEETS)
    cli.add_argument("--role")
    args=cli.parse_args()
    if args.self_test:self_test()
    elif args.global_index is not None:
        print(json.dumps(role_at_global_index(args.global_index),indent=2))
    elif args.fleet and args.role:
        print(json.dumps(packet(args.fleet,args.role),indent=2))
    else:cli.error("Provide --self-test, --global-index or --fleet and --role")
