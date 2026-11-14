"""Distinct, lawful second assignment: understand and improve available software.

Reference metadata was checked from each project's public GitHub repository
on 14 Nov 2026, but LICENSE must be rechecked at actual study and reuse time.
No repository is copied or cloned by this assignment module. Source code visible
on GitHub is NOT automatically free for unrestricted copying.
"""
from __future__ import annotations
import hashlib
import json
import re

ORDER="OWNER-20261114-090156"
PROJECTS=(
 ("BTCPay Server","https://github.com/btcpayserver/btcpayserver","MIT",
  "Bitcoin invoicing and merchant checkout",
  ("BTC invoice creation","payment status transitions","read-only receipt export",
   "payment link UX","merchant-facing payment guide")),
 ("Bitcoin Core","https://github.com/bitcoin/bitcoin","MIT",
  "Bitcoin mainnet node and transaction validation",
  ("confirmation depth evidence","output matching and network distinctions",
   "transaction decode documentation","testnet vs mainnet checks","read-only RPC example")),
 ("LNbits","https://github.com/lnbits/lnbits","MIT",
  "Lightning payments and wallet application",
  ("invoice expiry handling","Lightning receipt semantics","user-guide warnings",
   "fee disclosures","public QR display")),
 ("bitcoinjs-lib","https://github.com/bitcoinjs/bitcoinjs-lib","MIT",
  "Bitcoin JavaScript transaction construction utilities",
  ("network parameter separation","address format tests","PSBT signing caution",
   "UTXO data formatting","read-only address checks")),
 ("OpenZeppelin Contracts","https://github.com/OpenZeppelin/openzeppelin-contracts","MIT",
  "Ethereum-family contract library, not a native Bitcoin wallet",
  ("smart contract documentation","ERC20 token network warnings",
   "permission design tests","token decimal handling","base-chain deployment caution")),
)
ANGLES=(
 "Compare usability and identify one concrete confusion risk",
 "Write a beginner-friendly original explanation and test checklist",
 "Design an original example using fictitious data, no private keys",
 "Propose a legal interoperability interface with a documented test",
 "Find a feature gap and propose one scoped improvement",
 "Check install/security/privacy implications without accessing private systems",
 "Assess safe donation and payment handling and user consent",
 "Compare the reference's approach to a clean-room alternative",
 "Draft an independently original test case or documentation patch",
 "Trace how errors are surfaced and propose clearer remediation",
 "Check accessibility and international user onboarding",
 "Identify legal attribution and brand/confusion risks"
)
OUTPUTS=(
 "one-page technical comparison","licensed-reuse feasibility matrix",
 "original annotated pseudocode and two test cases",
 "user-guide correction with licence citation","clear one-feature backlog item",
 "short test plan with expected/actual evidence"
)
FLEETS=("transferexperiment","BountyScoutAI")

def study_task(fleet,role,parent,first_task_id):
    if fleet not in FLEETS or not re.fullmatch(
        r"D(?:0[1-9]|10)-M(?:0[1-9]|1[0-5])-W(?:0[1-9]|[1-4]\d|50)(?:-S\d{3}(?:-G\d{3}(?:-H\d{3})?)?)?",role):
        raise ValueError("Unknown fleet or worker role")
    if not parent or not str(first_task_id).startswith("FUND-"):
        raise ValueError("Must reference correct direct boss and first task")
    digest=hashlib.sha256((fleet+"/"+role+"/software2").encode()).digest()
    project=PROJECTS[digest[0]%len(PROJECTS)]
    features=project[4]
    feature=features[int.from_bytes(digest[1:3],"big")%len(features)]
    angle=ANGLES[int.from_bytes(digest[3:5],"big")%len(ANGLES)]
    artifact=OUTPUTS[int.from_bytes(digest[5:7],"big")%len(OUTPUTS)]
    task_id="SOFTWARE-"+hashlib.sha256((fleet+"/"+role+"/study").encode()).hexdigest()[:24]
    return {
      "task_id":task_id,"owner_order_id":ORDER,
      "first_task_id":first_task_id,
      "worker_id":fleet+"/"+role,"direct_supervisor":fleet+"/"+parent,
      "chief_director":"D","local_director":fleet+"/"+role.split("-")[0],
      "reference_software":project[0],"official_repository":project[1],
      "github_license_metadata_observed_2026_11_14":project[2],
      "current_license_verified_by_this_assignment":False,
      "public_software_description":project[3],
      "focus_feature":feature,"research_angle":angle,
      "required_artifact":artifact,
      "unique_work_scope":fleet+"/"+role+" / "+feature+" / "+angle+" / "+artifact,
      "task":"Study "+project[0]+" from its official repository and official docs. "+
         "Focus on '"+feature+"'. "+angle+". Deliver "+artifact+
         ". Explicitly recheck repository AND files' current licences, attribution, trademark and redistribution conditions. "+
         "Explain how ONE lawful, independently useful improvement to '"+feature+
         "' makes funding task "+first_task_id+" better. Do not copy proprietary code or secret material.",
      "legal_reuse_rule":"Copy or adapt source ONLY after verifying it is open source under terms that allow the specific use and satisfying any required notices, attribution, copyleft/source publication, patent/brand obligations. For unavailable/unclear licences, observe function and independently reimplement rather than copy.",
      "prohibited":["proprietary or unlicensed code copying","circumventing paywall/access controls",
       "private keys/passwords/client data","removing authorship/licence notices",
       "misrepresenting a cloned project as original","unapproved deployment or account access"],
      "minimum_evidence":["repo_url","licence file/source and date checked",
       "observed functionality","one limitation or risk",
       "original scoped implementation/test/documentation idea",
       "relationship to first unique funding task",
       "status if no code legally reusable"],
      "assignment_status":"ASSIGNED_NOT_INDEPENDENTLY_MODEL_EXECUTED",
      "actual_external_software_cloned":False,
      "actual_code_written":False,
      "confirmed_customer_payment":False,
    }

def grade_worker_study(reply,study,real_model_completed):
    text=str(reply or "").strip()
    low=text.lower()
    repo=study["official_repository"]
    project=study["reference_software"]
    c={
      "real_model_inference_reported":bool(real_model_completed),
      "correct_software_named":project.lower() in low,
      "correct_repository_link_present":repo.lower() in low,
      "license_discussed":("mit" in low or "license" in low or "licence" in low),
      "feature_discussed":any(w in low for w in study["focus_feature"].lower().split() if len(w)>4),
      "real_original_improvement_proposed":any(x in low for x in ("propose","improve","draft","test","compare","create","build","document","check","design")),
      "not_claiming_unverified_payment":not bool(re.search(r"(?i)\b(?:already got paid|funds received|money deposited)\b",text))
    }
    passed=len(text)>=115 and all(c.values())
    return {"status":"MODEL_STUDY_REPLY_REQUIRES_CODE_AND_LICENSE_REVIEW" if passed else
        "STUDY_FAILED_OR_NOT_EVIDENCED",
        "checks":c,"model_output_excerpt":text[:1350],
        "verified_repository_license_at_runtime":False,
        "code_copied_or_original_deliverable_committed":False,
        "customer_accepted_result":False,
        "receipt_verified":False,
        "note":"Text quality check only, not proof of source inspection, licence compliance or software development."}

def self_test():
    from collections import Counter
    seen=set();projects=Counter();first="FUND-demo"
    for fleet in FLEETS:
        for d in range(1,11):
            for w in range(1,51):
                role=f"D{d:02d}-M01-W{w:02d}-S001-G001-H001"
                x=study_task(fleet,role,role.rsplit("-",1)[0],first)
                assert x["task_id"] not in seen
                assert x["first_task_id"]==first
                assert x["worker_id"]==fleet+"/"+role
                assert x["actual_external_software_cloned"] is False
                seen.add(x["task_id"]);projects[x["reference_software"]]+=1
    assert len(seen)==1000
    assert len(projects)==len(PROJECTS)
    demo=study_task(FLEETS[0],"D01-M01-W01","D01-M01","FUND-123")
    assert grade_worker_study("",demo,False)["status"]=="STUDY_FAILED_OR_NOT_EVIDENCED"
    answer="Review "+demo["reference_software"]+" at "+demo["official_repository"]+\
      " MIT license. Focus feature: "+demo["focus_feature"]+". Propose a test and original improvement; check licence and attribution before any copying."
    assert grade_worker_study(answer,demo,True)["status"]=="MODEL_STUDY_REPLY_REQUIRES_CODE_AND_LICENSE_REVIEW"
    print("SECOND_SOFTWARE_STUDY_TEST_PASS",json.dumps({
      "unique_sample_assignments":len(seen),"referenced_real_public_repositories":len(projects),
      "actual_AI_models_run_by_assignment":0,"actual_software_copied_by_test":0
    }))

if __name__=="__main__":
    self_test()
