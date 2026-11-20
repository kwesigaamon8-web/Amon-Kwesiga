import {EXTRA_METHODS, calculateExtra, defaultsExtra} from "./global-1000-expansion.mjs";
/* B1/B2 original micro-app engine. One executable catalogue containing
 * 1,000 individually identified, user-operable specializations:
 * 100 distinct algorithms x 10 problem domains; original first 500 IDs unchanged. This is NOT 500 separate APIs
 * or 500 deployed services, and no country-specific sales are claimed.
 * MIT terms for this original file; formulas are educational estimates.
 */
export const DOMAINS = [
 "Farm and produce operations","Local shops and inventory",
 "Building and maintenance","Schools and learning",
 "Delivery and logistics","Community health administration",
 "Tourism and accommodation","Independent digital services",
 "Nonprofits and community projects","Digital infrastructure and Bitcoin"
];
export const ALGORITHMS = [
 ["Records total","Sum entered values","Total units"],                 // 00
 ["Average performance","Arithmetic average","Average units"],        // 01
 ["Median activity","Middle-ranked value","Median units"],            // 02
 ["Spread of readings","Maximum less minimum","Range"],              // 03
 ["Variation index","Population standard deviation","Spread units"],  // 04
 ["90th percentile","Nearest-rank percentile 90","90th percentile"], // 05
 ["Weighted reading","Later entries receive higher weight","Weighted average"],// 06
 ["Recent moving average","Last a entries average","Recent average"],// 07
 ["Linear trend","Best-fit slope per observation","Trend per step"],   // 08
 ["Change percent","a old, b new","Change %"],                         // 09
 ["Annualized growth","a initial, b final, c years","CAGR %"],       // 10
 ["Trend extrapolation","Linear regression forecast a steps ahead","Forecast"],//11
 ["Simple interest","a principal, b rate %, c years","Interest"],    //12
 ["Compound growth","a principal, b annual %, c years","Final value"],//13
 ["Installment estimate","a principal, b annual %, c months","Payment / month"],//14
 ["Break-even quantity","a fixed cost, b unit price, c unit expense","Units"],//15
 ["Gross margin","a sales, b related cost","Margin %"],              //16
 ["Selling markup","a unit cost, b selling price","Markup %"],        //17
 ["Discounted price","a original price, b discount %","Net price"],  //18
 ["Tax-inclusive amount","a amount, b entered tax %; not local tax advice","Gross amount"],//19
 ["Share of total","a subset, b total","Share %"],                   //20
 ["Cost per unit","a total cost, b units","Cost / unit"],             //21
 ["Stock shortfall","a target, b current stock","Shortfall"],         //22
 ["Reorder threshold","a demand/day, b supplier days, c buffer","Reorder units"],//23
 ["Safety stock estimate","a max daily, b max days, c avg daily, d avg days","Buffer units"],//24
 ["Stock cover days","a units on hand, b daily use","Cover days"],     //25
 ["Manual unit conversion","a quantity, b user-supplied conversion rate","Converted units"],//26
 ["Available working days","a period days, b excluded days","Working days"],//27
 ["Period duration","a start day index, b end day index","Days"],      //28
 ["Planned staff hours","a daily hours, b working days","Hours"],     //29
 ["Capacity utilization","a used, b available","Utilization %"],     //30
 ["Unused capacity","a capacity, b use","Units free"],                //31
 ["Defect percentage","a defective, b inspected","Defects %"],       //32
 ["Task completion","a completed, b planned","Completion %"],        //33
 ["Customer churn","a clients lost, b start clients","Churn %"],     //34
 ["Customer retention","a clients retained, b starting clients","Retention %"],//35
 ["Team attrition","a people left, b team size at start","Attrition %"],//36
 ["Value per sale","a revenue, b number of sales","Value per sale"],  //37
 ["Lead-to-sale rate","a converted, b genuine enquiries","Conversion %"],//38
 ["Acquisition expense","a marketing spent, b customers won","Cost / client"],//39
 ["Return on investment","a proceeds, b investment","ROI %"],        //40
 ["Investment payback","a initial cost, b monthly net benefit","Months"],//41
 ["Probability scenario","a success probability %, b gain, c loss","Expected value"],//42
 ["Effort priority score","a impact, b effort, c confidence fraction 0..1","Priority"],//43
 ["Satisfaction survey","List of real response scores (1 to 5)","Average / 5"],//44
 ["Goal achievement gap","a goal, b actual","Gap"],                 //45
 ["Electricity expense","a watts, b hours, c tariff per kWh","Electricity cost"],//46
 ["Mining BTC/day estimate","a hashes/sec, b network difficulty, c block subsidy BTC, d pool fee %","BTC / day"],//47
 ["Solo mining expectation","a hashes/sec, b network difficulty","Expected years / block"],//48
 ["Net cash flow","a inflows, b operating outflows, c other expense, d reserve","Cash left"]//49
];
export const TOTAL_TOOLS = DOMAINS.length * (ALGORITHMS.length + EXTRA_METHODS.length);
const ZERO=(x)=>Math.abs(x)<1e-12;
function div(a,b){if(!Number.isFinite(b)||ZERO(b))throw new Error("Denominator must be nonzero");return a/b;}
function list(value){
 const a=Array.isArray(value)?value:String(value??"").split(/[\s,;]+/).filter(Boolean).map(Number);
 if(a.length<1||a.length>400||a.some(x=>!Number.isFinite(x)))throw Error("Enter 1–400 valid finite values separated by commas");
 return a;
}
function quantile(a,p){const b=[...a].sort((x,y)=>x-y);return b[Math.min(b.length-1,Math.max(0,Math.ceil(p*b.length)-1))]}
function lr(series){const n=series.length;if(n<2)throw Error("At least two readings required");let sx=0,sy=0,sxx=0,sxy=0;for(let i=0;i<n;i++){sx+=i;sy+=series[i];sxx+=i*i;sxy+=i*series[i]}const slope=div(n*sxy-sx*sy,n*sxx-sx*sx);return {slope,intercept:(sy-slope*sx)/n}}
function finite(v){if(!Number.isFinite(v))throw Error("Result exceeds numeric range");return v}
function numeric(raw, key, fallback){const v=(raw?.[key]??fallback);if(v===""||v===null||!Number.isFinite(Number(v)))throw Error("Enter a valid number for "+key);return Number(v)}
export function calculate(algorithm,raw={}){
 if(!Number.isInteger(algorithm)||algorithm<0||algorithm>=ALGORITHMS.length+EXTRA_METHODS.length)throw Error("Unknown program");
 if(algorithm>=ALGORITHMS.length)return calculateExtra(algorithm-ALGORITHMS.length,raw);
 const a=numeric(raw,"a",100),b=numeric(raw,"b",12),c=numeric(raw,"c",3),d=numeric(raw,"d",0);
 const s=list(raw.series??"10,12,14,17,22"),n=s.length,sum=s.reduce((t,x)=>t+x,0);
 let value;
 switch(algorithm){
 case 0:value=sum;break;
 case 1:value=sum/n;break;
 case 2:{const sorted=[...s].sort((x,y)=>x-y),mid=Math.floor(n/2);value=n%2?sorted[mid]:(sorted[mid-1]+sorted[mid])/2;break}
 case 3:value=Math.max(...s)-Math.min(...s);break;
 case 4:value=Math.sqrt(s.reduce((x,y)=>x+(y-sum/n)**2,0)/n);break;
 case 5:value=quantile(s,.9);break;
 case 6:value=div(s.reduce((x,y,i)=>x+y*(i+1),0),n*(n+1)/2);break;
 case 7:{const window=Math.max(1,Math.min(n,Math.floor(a)));value=s.slice(-window).reduce((x,y)=>x+y,0)/window;break}
 case 8:value=lr(s).slope;break;
 case 9:value=div((b-a)*100,Math.abs(a));break;
 case 10:if(a<=0||b<0||c<=0)throw Error("Start and years must be positive, final nonnegative");value=((b/a)**(1/c)-1)*100;break;
 case 11:{const m=lr(s);value=m.intercept+m.slope*(n-1+a);break}
 case 12:value=a*b*c/100;break;
 case 13:if(c<0||b<=-100)throw Error("Years must be nonnegative and rate above -100%");value=a*(1+b/100)**c;break;
 case 14:{if(c<=0||b<0)throw Error("Months must be positive and APR nonnegative");const r=b/1200;value=ZERO(r)?a/c:div(a*r,1-(1+r)**(-c));break}
 case 15:if(b<=c)throw Error("Unit price must exceed unit cost");value=a/(b-c);break;
 case 16:value=div((a-b)*100,a);break;
 case 17:value=div((b-a)*100,a);break;
 case 18:value=a*(1-b/100);break;
 case 19:value=a*(1+b/100);break;
 case 20:value=div(a*100,b);break;
 case 21:value=div(a,b);break;
 case 22:value=Math.max(0,a-b);break;
 case 23:value=a*b+c;break;
 case 24:value=Math.max(0,a*b-c*d);break;
 case 25:value=div(a,b);break;
 case 26:value=a*b;break;
 case 27:value=Math.max(0,a-b);break;
 case 28:value=b-a;break;
 case 29:value=a*b;break;
 case 30:value=div(a*100,b);break;
 case 31:value=a-b;break;
 case 32:value=div(a*100,b);break;
 case 33:value=div(a*100,b);break;
 case 34:value=div(a*100,b);break;
 case 35:value=div(a*100,b);break;
 case 36:value=div(a*100,b);break;
 case 37:value=div(a,b);break;
 case 38:value=div(a*100,b);break;
 case 39:value=div(a,b);break;
 case 40:value=div((a-b)*100,b);break;
 case 41:value=div(a,b);break;
 case 42:if(a<0||a>100)throw Error("Probability must be 0–100");value=a*b/100-(1-a/100)*c;break;
 case 43:if(c<0||c>1)throw Error("Confidence must be between 0 and 1");value=div(a*c,b);break;
 case 44:if(s.some(x=>x<1||x>5))throw Error("Survey values must be 1 to 5");value=sum/n;break;
 case 45:value=a-b;break;
 case 46:value=a*b*c/1000;break;
 case 47:if(a<=0||b<=0||c<0||d<0||d>100)throw Error("Hash rate and difficulty must be positive; subsidy nonnegative; fee 0–100");value=a*86400*c/(b*4294967296)*(1-d/100);break;
 case 48:if(a<=0||b<=0)throw Error("Hash rate and difficulty must be positive");value=b*4294967296/a/(86400*365.25);break;
 case 49:value=a-b-c-d;break;
 }
 return {value:finite(value), label:ALGORITHMS[algorithm][2], algorithm:ALGORITHMS[algorithm][0], warning:algorithm===47||algorithm===48?"Estimate using YOUR supplied network difficulty, not live blockchain data. Pool share difficulty is NOT network difficulty. No profit or BTC payment is guaranteed.":null};
}
function defaults(algorithm,domain){
 const f=1+domain*.17, raw={a:100*f,b:12+domain,c:3,d:1,series:"10,12,14,17,22"};
 if(algorithm===7||algorithm===11)raw.a=3;
 if(algorithm===10)Object.assign(raw,{a:100,b:115,c:2});
 if(algorithm===14)Object.assign(raw,{a:1500*f,b:12,c:24});
 if(algorithm===15)Object.assign(raw,{a:400*f,b:30,c:12});
 if(algorithm===42)Object.assign(raw,{a:60,b:120,c:30});
 if(algorithm===43)Object.assign(raw,{a:8,b:2,c:0.75});
 if(algorithm===44)raw.series="4,5,4,3,5";
 if(algorithm===46)Object.assign(raw,{a:65,b:24,c:.15});
 if(algorithm===47)Object.assign(raw,{a:10000000,b:150000000000000,c:3.125,d:2.5});
 if(algorithm===48)Object.assign(raw,{a:10000000,b:150000000000000});
 return raw;
}
export function toolAt(index){
 if(!Number.isInteger(index)||index<0||index>=TOTAL_TOOLS)throw Error("Tool index outside 0–999");
 // Preserve old 500 links/meaning. New entries run the 50 genuinely new formulas.
 const newBlock=index>=500,domain=Math.floor((index-(newBlock?500:0))/50);
 const algorithm=(index%50)+(newBlock?50:0);
 const id="SW-"+String(index+1).padStart(3,"0");
 const [name,description,unit]=newBlock?EXTRA_METHODS[algorithm-50]:ALGORITHMS[algorithm];
 return {id,index,domain,algorithm,name:DOMAINS[domain]+": "+name,description,unit,sector:DOMAINS[domain],
         defaults:newBlock?defaultsExtra(algorithm-50,domain):defaults(algorithm,domain),url:"?tool="+id,
         evidence_status:"LIVE_BROWSER_CALCULATOR_NOT_COUNTRY_MARKET_RESEARCH",
         offline:true,payment_required:false};
}
export function toolById(id){
 if(!/^SW-(?:00[1-9]|0[1-9]\d|[1-9]\d{2}|1000)$/.test(id))throw Error("Invalid tool ID");
 const index=Number(id.slice(3))-1;return toolAt(index);
}
export const CODES = ("AW AF AO AI AX AL AD AE AR AM AS AQ TF AG AU AT AZ BI BE BJ BQ BF BD BG BH BS BA BL BY BZ BM BO BR BB BN BT BV BW CF CA CC CH CL CN CI CM CD CG CK CO KM CV CR CU CW CX KY CY CZ DE DJ DM DK DO DZ EC EG ER EH ES EE ET FI FJ FK FR FO FM GA GB GE GG GH GI GN GP GM GW GQ GR GD GL GT GF GU GY HK HM HN HR HT HU ID IM IN IO IE IR IQ IS IL IT JM JE JO JP KZ KE KG KH KI KN KR KW LA LB LR LY LC LI LK LS LT LU LV MO MF MA MC MD MG MV MX MH MK ML MT MM ME MN MP MZ MR MS MQ MU MW MY YT NA NC NE NF NG NI NU NL NO NP NR NZ OM PK PA PN PE PH PW PG PL PR KP PT PY PS PF QA RE RO RU RW SA SD SN SG GS SH SJ SB SL SV SM SO PM RS SS ST SR SK SI SE SZ SX SC SY TC TD TG TH TJ TK TM TL TO TT TN TR TV TW TZ UG UA UM UY US UZ VA VC VE VG VI VN VU WF WS YE ZA ZM ZW").split(" ");
export function countryAssignment(code){
 if(!CODES.includes(code))throw Error("Unknown ISO country/territory code");
 // Editorial suggestion only. NOT an audited claim about local market conditions.
 const hash=code.charCodeAt(0)*67+code.charCodeAt(1)*43;
 const tool=toolAt(hash%TOTAL_TOOLS);
 return {code,tool,region:"TO_RESEARCH",problem_hypothesis:tool.sector+" may benefit from "+tool.name.slice(tool.sector.length+2).toLowerCase(),
  verified_local_market_problem:false,verified_local_demand:false,verified_buyer:false,
  required_sources:["https://data.worldbank.org/country/"+code.toLowerCase(),
  "https://api.worldbank.org/v2/country/"+code+"/indicator/IT.NET.USER.ZS?format=json"],
  next_steps:["Verify country/territory coverage and suitable local industry","Find recent credible local evidence of the proposed problem","Check language, laws, payments, accessibility and software suitability","Only use permitted, connected channels and report actual publication URLs"]};
}
export const BTC_ROUTES={B1:"bc1qvprle87txnk7dgcgsau0nauxvvkwuyp0w9zc0z",B2:"bc1qtaunz7mx7k588p8v544tq7x7ezxxcfky0h2vn9"};
