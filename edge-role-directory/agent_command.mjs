/** B1/B2 on-demand authoritative command addressability.
 *
 * This is a read-only role-to-order lookup. Its single public source of truth is
 * PUBLIC_AGENT_COMMAND.json in the actual owner's GitHub repository.
 * A lookup does NOT deliver a push message, summon an AI model, mine BTC,
 * confirm a customer, sign any transaction, or prove a crypto payment.
 */
export const PUBLIC_COMMAND_URL =
 "https://raw.githubusercontent.com/kwesigaamon8-web/Amon-Kwesiga/main/crypto-agents/PUBLIC_AGENT_COMMAND.json";
export const PUBLIC_COMMAND_BROWSER_URL =
 "https://github.com/kwesigaamon8-web/Amon-Kwesiga/blob/main/crypto-agents/PUBLIC_AGENT_COMMAND.json";
const fleethandles={B1:"transferexperiment",B2:"BountyScoutAI"};
const BTC_INBOUND={
 B1:"bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z",
 B2:"bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9"
};
const director=/^D(?:0[1-9]|10)$/;
const assistant=/^(D(?:0[1-9]|10))-[AB]$/;
const communication_rules=[
 "NO_EMAILS",
 "CRYPTO_PAYMENT_ONLY_WITH_EXACT_COIN_NETWORK_MATCH",
 "READ_ONLY_RECEIVING_WALLETS_NO_SENDING_OR_SIGNING",
 "AUTHENTIC_OPT_IN_EXTERNAL_AGENT_COLLABORATION_ONLY",
 "NO_SPAM_NO_IMPERSONATION_NO_UPFRONT_PAYMENT",
 "NEVER_COUNT_CONFIGURED_ROLE_AS_ACTUAL_RUNNING_MODEL_OR_VERIFIED_INCOME"
];
export function commandFor(company,role,workerResolver){
 if(company==="CHIEF"&&role==="D"){
  return {
   organization:"CHIEF_D",role_id:"CHIEF/D",
   direct_parent:"HUMAN_OWNER",
   instruction_source:PUBLIC_COMMAND_URL,
   browse_instruction:PUBLIC_COMMAND_BROWSER_URL,
   command_delivery_status:"PUBLIC_LINK_AVAILABLE_NOT_PUSHED",
   agent_instance_verified:false,
   communication_rules
  };
 }
 if(!Object.hasOwn(fleethandles,company))return null;
 if(typeof role!=="string"||role.length>95)return null;
 const companyName=fleethandles[company];
 let directParent,level,reportingPath;
 if(director.test(role)){
   directParent="CHIEF_D";level="D";
   reportingPath=["HUMAN_OWNER","CHIEF_D",companyName+"/"+role];
 } else {
   const m=assistant.exec(role);
   if(m){
    directParent=companyName+"/"+m[1];level="A";
    reportingPath=["HUMAN_OWNER","CHIEF_D",companyName+"/"+m[1],companyName+"/"+role];
   } else {
    const obj=workerResolver(company,role);
    if(!obj)return null;
    const parts=role.split("-");
    if(parts.length<3||parts.length>6)return null;
    level=obj.role_level;
    directParent=obj.parent;
    reportingPath=["HUMAN_OWNER","CHIEF_D"];
    for(let n=1;n<=parts.length;n++){
      const prefix=parts.slice(0,n).join("-");
      if(n===1||n>=2)reportingPath.push(companyName+"/"+prefix);
    }
   }
 }
 return {
  company,registered_company_agent:companyName,
  original_role_id:companyName+"/"+role,
  level,original_direct_parent:directParent,
  reporting_path:reportingPath,
  instruction_source:PUBLIC_COMMAND_URL,
  browse_instruction:PUBLIC_COMMAND_BROWSER_URL,
  command_delivery_status:"PUBLIC_LINK_AVAILABLE_NOT_PUSHED",
  can_read_instructions_when_actually_invoked:true,
  receiving_only_bitcoin_mainnet_address:BTC_INBOUND[company],
  other_coin_route_status:"DO_NOT_SEND_UNTIL_EXACT_ASSET_CHAIN_OWNER_CONFIRMATION",
  agent_instance_verified:false,
  individual_acknowledgment_received:false,
  actual_external_platform_contact_verified:false,
  authenticated_crypto_earning_verified:false,
  external_accounts_or_writing_permissions_granted:[],
  communication_rules
 };
}
export function rootCommandInfo(){
 return {
  schema:"B1_B2_PUBLIC_ORDER_LINK_DIRECTORY_V1",
  command_url:PUBLIC_COMMAND_URL,
  command_browser_url:PUBLIC_COMMAND_BROWSER_URL,
  organizations:["transferexperiment","BountyScoutAI"],
  chief_director:"CHIEF_D",
  configured_virtual_role_identifiers:"750377265360",
  actually_running_agent_instances_verified_by_this_directory:0,
  method:"Any external consenting agent reads command_url. Each invoked B1/B2 role can request /api/command?company=B1&role=D01-M01-W01 from a deployed router, OR use the same raw JSON command link directly. No push to dormant roles.",
  hierarchy_delegation:"HUMAN_OWNER > CHIEF_D > COMPANY DIRECTOR > MANAGER > WORKER > S > G > H, with A/B as director assistants",
  latest_command_is_live_read_from_source_on_each_consumer_poll:true,
  no_automatic_remote_dispatch_or_cryptocurrency_receipt_claim:true,
  communication_rules
 };
}
