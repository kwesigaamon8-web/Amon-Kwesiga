/** Superworker planner. It does not start a model, create miners or grant access. */
export function profile(role){
 if(!role || typeof role.id!=="string" || !role.parent)return null;
 const i=role.id.indexOf("/");
 const fleet=role.id.slice(0,i),parts=role.id.slice(i+1).split("-");
 if(parts.length<3||parts.length>6)return null;
 const reporting=[];
 for(let n=parts.length-1;n>=1;n--)reporting.push(fleet+"/"+parts.slice(0,n).join("-"));
 reporting.push("CHIEF_D","HUMAN_OWNER");
 if(reporting[0]!==role.parent)throw new Error("Direct parent changed");
 return {
  id:role.id,original_parent:role.parent,upward_reporting_chain:reporting,
  status:"CONFIGURED_SUPERWORKER_NOT_EXECUTING",
  money_making_capability:role.task_lane,primary_action:role.feasible_task,
  stages:["VERIFY_SOURCE","PLAN_FEASIBLE_WORK","BUILD_ORIGINAL","SELF_TEST",
    "DELIVER_ONLY_WITH_APPROVAL","VERIFY_ACCEPTANCE_AND_CORRECT_CHAIN_PAYMENT","REPORT_THROUGH_PARENT"],
  account_access_granted:[],actual_models_started:0,actual_ASIC_miners_started:0,
  earned_BTC_verified:false,
  proof:"original source, actual artifact/test, authorized submission, acceptance and verified TXID or explicit blocker"
 };
}
