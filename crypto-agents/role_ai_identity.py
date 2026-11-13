"""Resolve first-tier and nested W/S/G/H worker identities on demand.

Identity generation is not an AI invocation. A process is real only when launched
and logged by ai_process_worker.py.
"""
import json
import re
from pathlib import Path
from subagent_factory import describe_child
from microcompany_factory import describe_micro_worker
from mega_branch_factory import describe_branch_worker

CONFIG=json.loads(Path("crypto-agents/company_hierarchy.json").read_text(encoding="utf-8"))
W=re.compile(r"^D(?:0[1-9]|10)-M(?:0[1-9]|1[0-5])-W(?:0[1-9]|[1-4][0-9]|50)$")
BOUNDS={"S":150,"G":500,"H":666}

def resolve_role(role_id):
    if not isinstance(role_id,str) or len(role_id)>95:raise ValueError("Invalid role length")
    parts=role_id.split("-")
    if not 3<=len(parts)<=6:raise ValueError("Invalid role depth")
    w="-".join(parts[:3])
    if not W.fullmatch(w):raise ValueError("Invalid W ancestor")
    director=parts[0];manager="-".join(parts[:2])
    company=next((x for x in CONFIG["companies"] if x["director_id"]==director),None)
    if company is None or not any(x["id"]==manager for x in company["managers"]):
        raise ValueError("Invalid manager")
    entry=CONFIG["worker_roles"][int(parts[2][1:])-1]
    current=w;parent=manager;level="W"
    specialty=entry["role_name"];query=entry["query"]
    task="Independently seek legitimate crypto-paid work in "+specialty+"; verify sources and payment."
    for i,suffix in enumerate(parts[3:]):
        tag="SGH"[i]
        matched=re.fullmatch(tag+r"(\d{3})",suffix)
        if not matched or not 1<=int(matched.group(1))<=BOUNDS[tag]:
            raise ValueError("Invalid nested slot or order")
        slot=int(matched.group(1));parent=current
        if tag=="S":
            child=describe_child(current,current,slot)
            specialty=child["assigned_role"];task=child["objective"]
        elif tag=="G":
            child=describe_micro_worker(current,current,slot)
            specialty=child["assigned_sector"]+" "+child["assigned_task"]
            task=child["independent_research_objective"]
        else:
            child=describe_branch_worker(current,current,slot)
            specialty=child["sector"]+" "+child["assigned_task"]
            task=child["mission"]
        current=child["id"];level=tag
        query=("remote "+specialty+" paid contract")[:140]
    if current!=role_id:raise ValueError("Factory role mismatch")
    return {"id":role_id,"level":level,"parent_id":parent,"manager_id":manager,
            "director_id":director,"specialty":str(specialty)[:180],
            "query":str(query)[:140],"task":str(task)[:650]}
