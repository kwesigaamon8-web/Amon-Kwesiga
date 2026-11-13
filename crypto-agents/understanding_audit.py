"""Audit each ACTUALLY ACTIVE agent's model-generated reply about owner and role.

We do not invent first-person replies for registered-but-never-executed agents.
All 375,188,632,680 software role identities are only mathematical definitions;
only real, saved role model calls get independent response evidence.
"""
import argparse,json
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument("--reports",default=None)
parser.add_argument("--output",default="understanding-audit")
args=parser.parse_args()
out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
brief=json.loads(Path("crypto-agents/professional_owner_context.json").read_text(encoding="utf-8"))
orders=json.loads(Path("crypto-agents/owner_orders.json").read_text(encoding="utf-8"))
errors=[]
seen={}
group=defaultdict(list)
level_stats=defaultdict(Counter)
expected={"director":10,"assistant":20,"manager":150,"worker":7500,
          "delegated_subagent":1125000,"microcompany_worker":562500000,
          "mega_branch_worker":374625000000}

def kind(ident):
    if "-H" in ident:return "mega_branch_worker"
    if "-G" in ident:return "microcompany_worker"
    if "-S" in ident:return "delegated_subagent"
    if "-W" in ident:return "worker"
    if "-M" in ident:return "manager"
    if ident.endswith(("-A","-B")):return "assistant"
    return "director"

def parent_expected(ident):
    if "-H" in ident:return ident.rsplit("-H",1)[0]
    if "-G" in ident:return ident.rsplit("-G",1)[0]
    if "-S" in ident:return ident.rsplit("-S",1)[0]
    if "-W" in ident:return ident.rsplit("-W",1)[0]
    if "-M" in ident:return ident.rsplit("-M",1)[0]
    if ident.endswith(("-A","-B")):return ident[:3]
    return "OWNER"

def accept_report(item):
    rep=item.get("understanding_response")
    if not isinstance(rep,dict):return
    ident=rep.get("agent_id")
    if not isinstance(ident,str) or not ident.startswith("D") or len(ident)<3:
        errors.append("Malformed actual agent ID");return
    if rep.get("reports_only_to")!=parent_expected(ident):
        errors.append("Wrong parent line for "+ident);return
    if rep.get("agent_name") in ("",None):
        errors.append("Missing role name "+ident);return
    seen[ident]=rep

if args.reports and Path(args.reports).is_dir():
    for path in Path(args.reports).rglob("*.json"):
        try:record=json.loads(path.read_text(encoding="utf-8"))
        except (ValueError,OSError):continue
        if isinstance(record,dict):accept_report(record)

by_director=defaultdict(list)
for ident,rep in seen.items():
    level=kind(ident)
    state=rep.get("understanding_check_status","missing")
    level_stats[level][state]+=1
    director=ident[:3]
    if director not in {f"D{i:02d}" for i in range(1,11)}:
        errors.append("Out-of-range director for "+ident)
        continue
    by_director[director].append(rep)

for i in range(1,11):
    director=f"D{i:02d}"
    responses=by_director[director]
    accepted=[x for x in responses if x.get("understanding_check_status")=="model_response_contains_key_goal_and_action"]
    weak=[x for x in responses if x.get("understanding_check_status")=="model_response_recorded_unverified_comprehension"]
    notrun=[x for x in responses if x.get("understanding_check_status")=="missing_or_failed_model_response"]
    details={
        "director":director,
        "professional_owner_brief_received_version":brief["version"],
        "company_configured_roles": 1+2+15+750+112500+56250000+37462500000,
        "distinct_role_reports_actually_provided":len(responses),
        "own_model_response_contains_goal_and_action":len(accepted),
        "weak_model_responses_to_recheck":len(weak),
        "failed_or_missing_inferences_in_supplied_role_reports":len(notrun),
        "important":"Distinct model evidence is not human comprehension and not a completed paid task.",
        "individual_responses":[
            {"agent_id":x["agent_id"],"parent":x["reports_only_to"],
             "model_status":x["actual_model_result_status"],
             "understanding_status":x["understanding_check_status"],
             "own_generated_reply":x.get("response_in_own_generated_words","")[:500]}
            for x in sorted(responses,key=lambda x:x["agent_id"])[:30]
        ],
        "uninspected_registered_roles":"These are registered definitions with no actual model reply in this report folder. No synthetic responses are created."
    }
    (out/(director+".json")).write_text(json.dumps(details,indent=2),encoding="utf-8")

good=sum(c.get("model_response_contains_key_goal_and_action",0) for c in level_stats.values())
weak=sum(c.get("model_response_recorded_unverified_comprehension",0) for c in level_stats.values())
missing=sum(c.get("missing_or_failed_model_response",0) for c in level_stats.values())
result={
    "at_utc":datetime.now(timezone.utc).isoformat(),
    "owner_professional_context_version":brief["version"],
    "defined_agent_role_ids":375188632680,
    "actual_distinct_agent_reply_reports_received":len(seen),
    "model_reply_check_passed_heuristic":good,
    "model_replies_present_but_not_confirmed_understanding":weak,
    "failed_or_unavailable_model_responses_recorded":missing,
    "levels":{k:{"roles_defined":n,"actual_reports":sum(level_stats[k].values()),
                  "check_states":dict(level_stats[k])} for k,n in expected.items()},
    "all_role_ids_had_their_own_response":len(seen)==375188632680,
    "owner_order_19_registered":any(x["id"]=="ORD-019" for x in orders["orders"]),
    "structural_reporting_errors":errors[:60],
    "scope":"Counts real model-generated replies from supplied GitHub Actions artifacts only. The 375bn mostly dormant IDs have no reply and are NEVER marked as responding.",
    "coin_receipts_verified_by_this_understanding_audit":[],
    "limitations":"A keyword-based model reply check is not proof of comprehension, independently hosted identity, paying contract or confirmed deposit."
}
(out/"audit.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
md=[
 "# Independent role-understanding response audit","",
 "Every **active** agent must produce a response in its own model-generated words. The owner's professional background is explained in an anonymous brief.",
 "",
 f"Configured role identifiers: **{result['defined_agent_role_ids']:,}**.",
 f"Unique role model replies actually received: **{len(seen)}**.",
 f"Model replies containing both coin-goal and actionable-work language: **{good}**.",
 f"Model replies not verified by the heuristic: **{weak}**.",
 f"Unavailable/failed model responses in submitted role files: **{missing}**.",
 "","| Level | Defined | Actual model report files |",
 "|---|---:|---:|"
]
for label,n in expected.items():
    md.append(f"| {label} | {n:,} | {sum(level_stats[label].values())} |")
md+=["","## Reporting-chain issues"]
md.extend("- "+x for x in errors[:20])
if not errors:md.append("No parent violations found among supplied understanding responses.")
md+=["","**No new cryptocurrency receipt can be established from these model-reply reports.**",
"**Do not describe the unactivated majority as having spoken or understood.**"]
(out/"AUDIT.md").write_text("\n".join(md)+"\n",encoding="utf-8")
print("UNDERSTANDING_AUDIT",json.dumps({"model_replies":len(seen),"model_checks_passed":good,"checks_weak":weak,
    "missing_or_failed":missing,"parent_errors":len(errors),"all_roles_replied":result["all_role_ids_had_their_own_response"]}))
if errors:raise SystemExit("Invalid parent reporting chains in role replies")
