"""Two-company workforce census: distinct configured role IDs versus running AI.

All enormous S/G/H positions are lazy *definitions*. No new model process,
wallet account, social login, or contract is created by arithmetic.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path("crypto-agents")
OUT=Path("chief-D-reports")
OUT.mkdir(exist_ok=True)
cfg=json.loads((ROOT/"b_collection_assignments.json").read_text(encoding="utf-8"))
hierarchy=json.loads((ROOT/"company_hierarchy.json").read_text(encoding="utf-8"))
with (ROOT/"agent_registry.csv").open(encoding="utf-8",newline="") as fp:
    agents=list(csv.DictReader(fp))
registry=Counter(agent["level"] for agent in agents)
assert dict(registry)=={"director":10,"independent_assistant":20,"manager":150,"worker":7500}
assert len({r["id"] for r in agents})==7680
assert len(hierarchy["companies"])==10
assert hierarchy["independent_assistants_per_director"]==2
assert hierarchy["managers_per_company"]==15
assert hierarchy["workers_per_manager"]==50

d=registry["director"]
a=registry["independent_assistant"]
m=registry["manager"]
w=registry["worker"]
s=w*150
g=s*500
h=g*666
per_company={
    "directors":d,"assistants":a,"managers":m,
    "first_tier_workers":w,"S_subagent_definitions":s,
    "G_micro_worker_definitions":g,"H_branch_worker_definitions":h,
}
per_company_total=sum(per_company.values())
assert per_company_total==375188632680

companies={}
for fleet,board in cfg["hierarchy"]["companies"].items():
    director_ids=[fleet+"/"+f"D{i:02d}" for i in range(1,11)]
    assert board["local_director_ids"]==director_ids
    assert board["directors"]==10
    companies[fleet]={
       "account":board["account"],
       "company_name":board["company"],
       "local_directors":board["directors"],
       "local_payment_director":board["local_payment_director"],
       "per_level":dict(per_company),
       "mathematically_defined_total":per_company_total,
       "namespace_prefix":fleet+"/",
       "base_registry_rows_shared_as_template":len(agents),
       "real_running_models_claimed_by_census":0,
       "actual_model_completions": "not_assessed_by_this_census",
       "definition_status":"7,680 base template IDs, with lazily defined S/G/H descendants",
    }
assert set(companies)=={"transferexperiment","BountyScoutAI"}
combined={k:2*v for k,v in per_company.items()}
report={
 "as_of_utc":datetime.now(timezone.utc).isoformat(),
 "schema":"two-independent-companies-billion-scale-hierarchy-census",
 "companies":companies,
 "company_count":2,
 "global_chief_director":"D",
 "global_chief_director_count":1,
 "company_directors_total":20,
 "combined_by_level":combined,
 "company_1_total":per_company_total,
 "company_2_total":per_company_total,
 "combined_configured_company_role_positions":per_company_total*2,
 "combined_configured_roles_plus_chief_D":per_company_total*2+1,
 "company_director_base_registry_ids_reused_by_template":True,
 "distinct_company_director_namespace_verified":True,
 "no_billions_of_models_launched":True,
 "genuine_crypto_received": "not_assessed_by_census",
 "meaning":"A worker role definition is not an actual continuously executing AI agent, human, server process, independent account or payer.",
 "actual_capacity":"Each fleet schedules 30 research roles hourly and caps its daily worker model subprocess attempts at 20 x 10 = 200, subject to runner availability.",
}
(OUT/"TWO_COMPANY_WORKFORCE_CENSUS.json").write_text(
    json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
fmt=lambda n:f"{n:,}"
lines=[
 "# TWO COMPANY WORKFORCE CENSUS — OWNER / CHIEF D","",
 "UTC: "+report["as_of_utc"],"",
 "**Company 1: transferexperiment:** "+fmt(per_company_total)+" defined positions.",
 "**Company 2: BountyScoutAI:** "+fmt(per_company_total)+" defined positions.",
 "**Both companies:** "+fmt(per_company_total*2)+" defined positions.",
 "**Chief D:** 1 separate executive definition (not inside either company's count).",
 "**Grand total including Chief D:** "+fmt(per_company_total*2+1)+".","",
 "| Role level | Each separate company | Both companies |",
 "|---|---:|---:|",
]
labels=[("directors","Directors"),("assistants","Assistants"),("managers","Managers"),
        ("first_tier_workers","First-tier workers"),("S_subagent_definitions","S-level subagents"),
        ("G_micro_worker_definitions","G-level micro-workers"),
        ("H_branch_worker_definitions","H-level branch workers")]
for key,label in labels:
    lines.append(f"| {label} | {fmt(per_company[key])} | {fmt(2*per_company[key])} |")
lines += ["",
  "## Execution is not arithmetic",
  "These are software role definitions. **Most billions-scale descendants are lazily defined and have not individually run.**",
  "The two companies share the same template but use separate fleet prefixes and report to separate local D01-D10 boards. One Chief D receives both boards' evidence.",
  "Current scheduled potential (not a proof of actual completed inference): each fleet 200 model subprocess attempts per daily model workflow, plus 30 scheduled research roles each hour.",
  "To establish actual agent activity inspect the per-run GitHub Actions manifest and completed model output, not the defined role count.",
  "Money received is not assessed by this registry; use verified on-chain transaction and independent payer evidence."
]
(OUT/"TWO_COMPANY_WORKFORCE_CENSUS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("TWO_COMPANY_CENSUS",json.dumps({
    "company_1":per_company_total,"company_2":per_company_total,
    "both":per_company_total*2,"including_chief_D":per_company_total*2+1,
    "directors":20,"workforce_billion_roles_active":False
}))
