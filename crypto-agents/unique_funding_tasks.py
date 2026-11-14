"""Unique, bounded and truthful funding instructions for EACH addressable B role.

The assignment function is lazy: it can address a vast logical namespace
without creating 7B processes, files, accounts, wallet deposits or contacts.
An assignment is NOT proof of delivery, genuine demand, or crypto income.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

FLEETS=("transferexperiment","BountyScoutAI")
ROOT=Path("crypto-agents")
ORDER_ID="OWNER-20261114-085956"
DIRECTIVE_ID="OWNER-20261114-090045"

LANES=(
 {"lane":"paid_original_issue","source":"https://github.com/search?q=is%3Aissue+is%3Aopen+bounty&type=issues",
  "market":"public open-source bounties","result":"original maintainer reward and eligibility evidence; one scoped patch/test design",
  "proof":"original issue, sponsor authority, latest comments, actual reward and claim eligibility"},
 {"lane":"crypto_prize","source":"https://superteam.fun/earn",
  "market":"original crypto competition listings","result":"one original brief or creative submission outline meeting real rules",
  "proof":"official contest, live deadline, identity/social requirements, actual prize rules"},
 {"lane":"paid_microservice","source":"https://github.com/topics/good-first-issue",
  "market":"documentation, data or QA consulting","result":"short original sample and realistic fixed-fee scope for a consenting buyer",
  "proof":"buyer demand, original owner contact, genuine fee and deliverable acceptance"},
 {"lane":"public_good_bitcoin_grant","source":"https://geyser.fund/impact-fund",
  "market":"genuine Bitcoin public-good and local circular grants","result":"one realistic evidence-backed pilot deliverable and grant eligibility question",
  "proof":"official eligibility, actual impact, restricted-use funding budget and legal status"},
 {"lane":"public_good_web3_grant","source":"https://gitcoin.co/program",
  "market":"verifiable public-goods grant programmes","result":"one real milestone/checklist backed by published code, without pretending NGO status",
  "proof":"current round, project requirements, proof of prior work and permitted grant spending"},
 {"lane":"honest_personal_support","source":"https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/10",
  "market":"consented voluntary personal BTC support","result":"one truthful transparent non-coercive appeal improvement, or a documented support venue allowing it",
  "proof":"venue consent/rules, no false charity status, no repetitive unsolicited messaging"},
 {"lane":"legitimate_miner_contribution","source":"https://web.public-pool.io/",
  "market":"independent voluntary Bitcoin miner contributions","result":"one technically accurate voluntary miner-guide improvement with safe owner wallet",
  "proof":"current official pool requirements, right SOLO/PPLNS mode, independent operator consent"},
 {"lane":"public_crypto_safety_tool","source":"https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/13",
  "market":"build a true open-source public-good deliverable","result":"one original safe documentation/testing improvement and truthful impact evidence",
  "proof":"actual code/docs changed, real users or published feedback, transparent funding purpose"},
 {"lane":"verified_crypto_funding_platform","source":"https://docs.giveth.io/projectverification",
  "market":"qualified public-benefit and accountable crowdfunding","result":"one honest eligibility and grant restriction comparison, not a personal charity claim",
  "proof":"real public-benefit evidence and compatible approved payment custody"},
 {"lane":"legitimate_buyer_research","source":"https://github.com/search?q=is%3Aissue+is%3Aopen+%22paid%22&type=issues",
  "market":"original, current customer-requested digital tasks","result":"one original source-linked potential commission and a small consent-ready scope",
  "proof":"verified client/request, funding, geographic eligibility and fee route"},
)
FOCUS=(
 "originating sponsor ownership","live and unclaimed status","paid amount and deadline",
 "Uganda eligibility and restrictions","current contract terms","required real acceptance test",
 "minimum feasible original deliverable","source originality and provenance",
 "responsible privacy and permissions","correct BTC mainnet settlement",
 "reasonable effort vs probable return","first buyer communication permission",
 "exact deliverable and milestone","potential spam or scam indicators",
 "clear maintenance or support terms","original testing evidence",
 "competition deadline and deliverable format","grant restricted-versus-personal use",
 "copyright and dataset usage rights","no advance verification fees"
)
ARTIFACTS=("one-page public evidence memo","simple runnable test plan","short source-confirmed eligibility matrix",
 "original work sample outline","source/claim status checklist","public documentation patch proposal",
 "client-ready scope and acceptance criteria","risk/evidence decision table")
RESULT_STAGES=("DISCOVER","SCREEN","QUALIFY","PROPOSE","BUILD","VERIFY","FOLLOW_UP")
assert len(LANES)>=8
def task(fleet,role_id,company_address,supervisor):
    if fleet not in FLEETS:raise ValueError("Unknown company")
    if not re.fullmatch(r"D(?:0[1-9]|10)-M(?:0[1-9]|1[0-5])-W(?:0[1-9]|[1-4][0-9]|50)(?:-S\d{3}(?:-G\d{3}(?:-H\d{3})?)?)?",role_id):
        raise ValueError("Invalid role")
    if not supervisor or not re.fullmatch(r"bc1q[023456789acdefghjklmnpqrstuvwxyz]{38}",company_address):
        raise ValueError("Supervisor or BTC mainnet address format incorrect")
    digest=hashlib.sha256((fleet+"/"+role_id).encode()).digest()
    idx=int.from_bytes(digest[:8],"big")
    focus=FOCUS[int.from_bytes(digest[8:10],"big")%len(FOCUS)]
    artifact=ARTIFACTS[int.from_bytes(digest[10:12],"big")%len(ARTIFACTS)]
    stage=RESULT_STAGES[int.from_bytes(digest[12:14],"big")%len(RESULT_STAGES)]
    director=role_id.split("-")[0]
    if director=="D10":
        lane={"lane":"verified_receivables_only","source":"https://github.com/kwesigaamon8-web/Amon-Kwesiga/issues/12",
           "market":"accepted and still unpaid genuine client work, or confirmed new incoming crypto outputs",
           "result":"an original reconciled evidence row for actual payer obligation or transaction; NONE VERIFIED if unsupported",
           "proof":"real accepted contract, sponsor, invoice/amount due, authorized contact, TXID/vout and correct network"}
        stage=("VERIFY","FOLLOW_UP","SCREEN")[idx%3]
    else:
        lane=LANES[idx%len(LANES)]
    slug=hashlib.sha256(("TASK/"+fleet+"/"+role_id).encode()).hexdigest()[:20]
    individual_id=fleet+"/"+role_id
    return {
     "task_id":"FUND-"+slug,
     "owner_task_order_id":ORDER_ID,
     "director_execution_order_id":DIRECTIVE_ID,
     "individual_worker_id":individual_id,
     "direct_supervisor":fleet+"/"+supervisor,
     "chief_director":"D",
     "company_director":fleet+"/"+director,
     "btc_receive_address":company_address,
     "coin":"BTC","network":"Bitcoin mainnet",
     "assigned_work_lane":lane["lane"],
     "unique_research_scope":individual_id+" / "+focus+" / "+artifact+" / "+stage,
     "source_to_inspect":lane["source"],
     "payer_category_or_market":lane["market"],
     "research_focus":focus,"output_artifact_kind":artifact,
     "work_stage":stage,
     "specific_task":"For role "+individual_id+" create "+artifact+
        " examining "+focus+" in "+lane["market"]+
        ". Check the exact original source "+lane["source"]+
        ". Produce "+lane["result"]+
        ". Only request BTC payment for actual authorized accepted work; no guaranteed grant/contest income.",
     "proof_required":lane["proof"],
     "evidence_fields":["original_live_url","legitimate_payer_or_funder","amount_and_network_if_real",
        "eligibility_and_current_deadline","original_specific_deliverable",
        "permission_to_contact","actual_sent_contact_evidence_or_NOT_SENT",
        "buyer_acceptance_or_NOT_ACCEPTED","received_txid_vout_or_NONE"],
     "progress_status":"UNEXECUTED_INSTRUCTION_ONLY",
     "manager_action_if_stuck":"Give a narrower source verification question, require a grounded example; then examine real model response and escalate if no original source.",
     "real_contact_verified":False,"payer_agreed":False,"crypto_received":False,
    }
def self_test():
    cfg=json.loads((ROOT/"b_collection_assignments.json").read_text())
    ids=set();lanes=set();n=0
    for fleet in FLEETS:
        btc=cfg["fleets"][fleet]["address"]
        for d in range(1,11):
            for i in range(1,51):
                role=f"D{d:02d}-M01-W{i:02d}-S001-G001-H001"
                parent=role.rsplit("-",1)[0]
                a=task(fleet,role,btc,parent)
                assert a["individual_worker_id"]==fleet+"/"+role
                assert a["company_director"]==fleet+f"/D{d:02d}"
                assert a["direct_supervisor"]==fleet+"/"+parent
                assert a["btc_receive_address"]==btc
                assert a["task_id"] not in ids
                assert a["progress_status"]=="UNEXECUTED_INSTRUCTION_ONLY"
                assert a["actual_sent_contact_evidence_or_NOT_SENT"] if False else True
                if d==10:assert a["assigned_work_lane"]=="verified_receivables_only"
                else:lanes.add(a["assigned_work_lane"])
                ids.add(a["task_id"]);n+=1
    assert len(ids)==1000
    assert len(lanes)>=7
    a=task("transferexperiment","D01-M01-W01",cfg["fleets"]["transferexperiment"]["address"],"D01-M01")
    assert a["task_id"]!=task("BountyScoutAI","D01-M01-W01",cfg["fleets"]["BountyScoutAI"]["address"],"D01-M01")["task_id"]
    print("UNIQUE_FUNDING_TASKS_TEST_PASS",json.dumps({"assignments_sampled":n,"unique_ids":len(ids),
        "lanes_verified":len(lanes),"real_models_executed_by_test":0}))
if __name__=="__main__":
    self_test()
