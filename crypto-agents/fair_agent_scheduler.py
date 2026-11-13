"""Fair, bounded activation of B's W/S/G/H identities without making fake processes.

Each selected role is eligible for one separately launched local LLM task.
The mathematical address-space supports all 375.2B identities, but actual work
is counted ONLY if launched and proven by individual model-process evidence.

Algorithm guarantees distinct IDs across all four tiers until the smallest
tier under each director has been completely cycled. It enumerates a new
sequence from a workflow-run counter; no materialization of billions of IDs.
"""
from __future__ import annotations
import math
import re
from collections import Counter

DIRECTORS=10
MANAGERS_PER_DIRECTOR=15
W_PER_MANAGER=50
S_PER_W=150
G_PER_S=500
H_PER_G=666
W_PER_DIRECTOR=MANAGERS_PER_DIRECTOR*W_PER_MANAGER
TOTAL_BY_DIRECTOR={
    "W":W_PER_DIRECTOR,
    "S":W_PER_DIRECTOR*S_PER_W,
    "G":W_PER_DIRECTOR*S_PER_W*G_PER_S,
    "H":W_PER_DIRECTOR*S_PER_W*G_PER_S*H_PER_G,
}
TOTAL_HIERARCHY = sum(TOTAL_BY_DIRECTOR.values())*DIRECTORS + 10 + 20 + 150
assert TOTAL_HIERARCHY == 375188632680
# Affine multipliers are invertible mod the corresponding tier radix.
assert all(math.gcd(a,n)==1 for a,n in ((479,750),(31,150),(37,500),(5,666)))

def role_for_ordinal(director:str,tier:str,ordinal:int)->str:
    """One unique W/S/G/H path per ordinal (mod that tier's full size).

    Variable mixing spreads operations across managers, workers and branches.
    For each tier, applying the transform is a reversible bijection.
    """
    if not re.fullmatch(r"D(?:0[1-9]|10)",director):
        raise ValueError("Invalid director")
    if tier not in TOTAL_BY_DIRECTOR or not isinstance(ordinal,int) or ordinal<0:
        raise ValueError("Invalid tier or ordinal")
    d=int(director[1:])
    x=ordinal%TOTAL_BY_DIRECTOR[tier]
    w0=x%750
    x//=750
    s0=x%150 if tier in ("S","G","H") else 0
    if tier in ("S","G","H"):x//=150
    g0=x%500 if tier in ("G","H") else 0
    if tier in ("G","H"):x//=500
    h0=x%666 if tier=="H" else 0
    h=(5*h0+17*d)%666
    g=(37*g0+11*h0+7*d)%500
    s=(31*s0+13*g0+5*h0+11*d)%150
    w=(479*w0+17*s0+7*g0+3*h0+29*d)%750
    role=f"{director}-M{w//50+1:02d}-W{w%50+1:02d}"
    if tier in ("S","G","H"):role+=f"-S{s+1:03d}"
    if tier in ("G","H"):role+=f"-G{g+1:03d}"
    if tier=="H":role+=f"-H{h+1:03d}"
    return role

def select_roles(director:str,cycle:int,slots:int=50)->list[str]:
    """Activate a quarter of the real subprocess budget from each level.

    No more than 50 per director per cycle. A mathematical role is never
    represented as currently running until its separate model process runs.
    """
    if not isinstance(cycle,int) or cycle<0:
        raise ValueError("cycle must be a nonnegative integer")
    if not isinstance(slots,int) or not 1<=slots<=50:
        raise ValueError("slots must be between 1 and 50")
    result=[]
    for slot in range(slots):
        global_position=cycle*slots+slot
        tier="WSGH"[global_position%4]
        ordinal=global_position//4
        result.append(role_for_ordinal(director,tier,ordinal))
    if len(result)!=len(set(result)):raise AssertionError("Duplicate selected roles")
    return result

def activation_summary(director:str,cycle:int,slots:int=50)->dict:
    selection=select_roles(director,cycle,slots)
    tiers=Counter("H" if "-H" in wid else "G" if "-G" in wid else
                  "S" if "-S" in wid else "W" for wid in selection)
    managers=len({wid.split("-")[1] for wid in selection})
    return {
        "director":director,"cycle":cycle,"subprocess_budget":slots,
        "configured_identity_count_across_B":TOTAL_HIERARCHY,
        "configured_identity_count_under_director":sum(TOTAL_BY_DIRECTOR.values()),
        "activation_counts_by_tier":{t:tiers.get(t,0) for t in "WSGH"},
        "distinct_managers_selected":managers,
        "selection_guarantee":"Mathematically distinct identities in each tier until full tier rotation; a selected role is not an active model until independently run",
        "all_billions_concurrently_running":False,
        "selected_ids":selection
    }

if __name__=="__main__":
    for i in range(1,11):
        x=activation_summary(f"D{i:02d}",0)
        print(x["director"],x["activation_counts_by_tier"],x["distinct_managers_selected"])
