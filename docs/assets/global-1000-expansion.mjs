/* Enigma / B1 B2 original public-interest 500-tool expansion.
 * 50 NEW algorithms (indices 50-99) x ten existing domains.
 * Standard elementary formulas, authored for this project.
 * Not copied from third-party source. No live data or claims of local expertise.
 */
export const EXTRA_METHODS = [
["Learner attendance","a days attended, b days scheduled","Attendance %"],
["Absence count","a days scheduled, b days attended","Days absent"],
["Learners per instructor","a learners, b instructors","Learners / teacher"],
["Weekly reading time","a reading minutes per day, b days","Minutes / week"],
["Study completion time","a remaining pages, b pages per day","Study days"],
["Class supplies estimate","a learners, b cost per learner, c reserve %","Cost"],
["Nutrition batch ingredient quantity","a portions, b grams per portion","Grams"],
["Emergency water reserve","a people, b litres/person/day, c days","Litres"],
["Rain catchment potential","a roof area m², b rainfall mm, c collection efficiency %","Litres"],
["Household water requirement","a litres/day, b days","Litres"],
["Water expense estimate","a volume m³, b charge per m³, c fixed charge","Total expense"],
["Electricity carbon estimate","a energy kWh, b emission factor kg CO₂/kWh","kg CO₂ equivalent"],
["Appliance power use","a watts, b hours/day, c days","kWh"],
["Solar production estimate","a panels, b watts/panel, c sun-hours/day, d efficiency %","kWh/day"],
["Battery storage demand","a daily energy kWh, b days, c usable fraction %","Battery kWh"],
["Solar payback estimate","a equipment expense, b estimated monthly savings","Months"],
["Battery backup duration","a capacity Wh, b load W, c efficiency %","Hours"],
["Food spoilage rate","a spoiled weight, b weight received","Waste %"],
["Produce transport expense","a route distance km, b expense per km, c trips","Total expense"],
["Deliveries per driver-hour","a completed deliveries, b driver-hours","Deliveries/hour"],
["Delivery fuel budget","a distance km, b distance per litre, c unit fuel cost","Fuel cost"],
["Delivery ETA estimate","a travel km, b average km/hour, c minutes handling","Minutes"],
["Shared route expense","a transport expense, b delivery stops","Cost per stop"],
["Vehicle load utilization","a load kg, b rated payload kg","Payload utilization %"],
["Harvest yield","a produce kg, b land hectares","kg / hectare"],
["Harvest gross proceeds","a harvested kg, b price per kg","Gross proceeds"],
["Seed density","a seeds, b land area m²","Seeds / m²"],
["Irrigation volume estimate","a litres/m²/day, b area m², c days","Litres"],
["Farm labor expense","a staff, b hours per staff, c rate/hour","Expense"],
["Appointment throughput","a rooms, b service hours, c minutes/appointment","Appointments"],
["Waiting-time queue estimate","a arrivals/hour, b services/hour; simple M/M/1 assumptions","Minutes in system"],
["Medicine stock planning","a stock units, b used/day, c supply lead time days","Stock above lead-time need"],
["Visit-record workload","a visits/day, b working days","Records"],
["Meal cost per portion","a total ingredients cost, b number of portions","Cost / portion"],
["Community funds after reserve","a grant, b administration %, c reserve %","Funds for programs"],
["Volunteer contribution estimate","a hours, b user-supplied reference rate","Value estimate"],
["Project work remaining","a planned tasks, b completed tasks, c hours/task","Hours remaining"],
["Project throughput","a completed tasks, b elapsed weeks","Tasks per week"],
["Project expense overrun","a actual expense, b budget","Variance %"],
["Operating expense per day","a total expenses, b days","Expense / day"],
["Operating cash runway","a unrestricted cash, b monthly operating expense","Months"],
["Emergency reserve target","a essential monthly expense, b months","Target amount"],
["Monthly saving requirement","a savings target, b months available","Savings/month"],
["Loan remaining balance","a principal, b APR %, c months elapsed, d fixed monthly payment","Remaining principal"],
["Delay-weighted receivable","a outstanding amount, b days overdue","Amount-days"],
["Payment service net receipts","a gross receipt, b service fee %, c fixed fee","Net receipt"],
["Subscription total expense","a monthly charge, b months, c additional fee %","Total expense"],
["Accessible color contrast ratio","a relative foreground luminance 0–1, b background luminance 0–1","Contrast ratio"],
["Mobile data consumption","a MB/day, b days, c price per GB (decimal)","Data expense"],
["Community resource gap","a resources needed, b resources available","Resource gap"]
];
function number(raw,key,def){const v=raw?.[key]??def;if(v===""||v===null||!Number.isFinite(Number(v)))throw Error("Invalid "+key);return Number(v)}
function safeDiv(a,b){if(!Number.isFinite(b)||b===0)throw Error("Divisor must be nonzero");return a/b}
function nonNeg(...values){if(values.some(x=>x<0))throw Error("Inputs must be nonnegative")}
function percent(p){if(p<0||p>100)throw Error("Percent must be between 0 and 100")}
export function defaultsExtra(index,domain){
 const k=1+domain/10;
 const defaults={a:100*k,b:12,c:3,d:80,series:"10,12,14,17,22"};
 const patches={
 0:{a:18,b:20},1:{a:20,b:18},2:{a:180,b:9},3:{a:20,b:5},4:{a:120,b:20},
 5:{a:35,b:2000,c:10},6:{a:25,b:180},7:{a:6,b:3,c:7},
 8:{a:80,b:1100,c:75},9:{a:40,b:30},10:{a:15,b:2,c:10},
 11:{a:300,b:0.5},12:{a:100,b:8,c:30},13:{a:5,b:350,c:5,d:78},
 14:{a:3,b:2,c:80},15:{a:2200,b:150},16:{a:1200,b:200,c:90},
 17:{a:4,b:100},18:{a:75,b:1.8,c:2},19:{a:52,b:8},
 20:{a:100,b:12,c:4900},21:{a:42,b:35,c:15},22:{a:280,b:7},
 23:{a:450,b:1000},24:{a:3200,b:1.5},25:{a:1200,b:2.3},
 26:{a:4000,b:100},27:{a:7,b:120,c:5},28:{a:4,b:7,c:5000},
 29:{a:2,b:6,c:20},30:{a:3,b:5},31:{a:400,b:20,c:9},
 32:{a:15,b:24},33:{a:8500,b:35},34:{a:85000,b:12,c:10},
 35:{a:120,b:4500},36:{a:50,b:20,c:2},37:{a:32,b:4},
 38:{a:1200,b:1000},39:{a:90000,b:30},40:{a:200000,b:50000},
 41:{a:400000,b:3},42:{a:300000,b:12},
 43:{a:2000,b:12,c:3,d:150},44:{a:150000,b:30},
 45:{a:1000,b:2,c:0},46:{a:50,b:12,c:5},47:{a:0.12,b:0.8},
 48:{a:300,b:30,c:4},49:{a:400,b:250}
 };
 return Object.assign(defaults,patches[index]||{});
}
export function calculateExtra(index,raw={}){
 if(!Number.isInteger(index)||index<0||index>=EXTRA_METHODS.length)throw Error("Unknown public-interest tool");
 const a=number(raw,"a",100),b=number(raw,"b",12),c=number(raw,"c",3),d=number(raw,"d",80);
 let v;
 switch(index){
 case 0:nonNeg(a,b);v=safeDiv(a*100,b);break;
 case 1:nonNeg(a,b);v=Math.max(0,a-b);break;
 case 2:nonNeg(a,b);v=safeDiv(a,b);break;
 case 3:nonNeg(a,b);v=a*b;break;
 case 4:nonNeg(a,b);v=safeDiv(a,b);break;
 case 5:nonNeg(a,b);percent(c);v=a*b*(1+c/100);break;
 case 6:nonNeg(a,b);v=a*b;break;
 case 7:nonNeg(a,b,c);v=a*b*c;break;
 case 8:nonNeg(a,b);percent(c);v=a*b*c/100;break; // m²*mm = litres
 case 9:nonNeg(a,b);v=a*b;break;
 case 10:nonNeg(a,b,c);v=a*b+c;break;
 case 11:nonNeg(a,b);v=a*b;break;
 case 12:nonNeg(a,b,c);v=a*b*c/1000;break;
 case 13:nonNeg(a,b,c);percent(d);v=a*b*c*d/100000;break;
 case 14:nonNeg(a,b);percent(c);if(c===0)throw Error("Battery usable fraction must be > 0");v=a*b/(c/100);break;
 case 15:nonNeg(a,b);v=safeDiv(a,b);break;
 case 16:nonNeg(a,b);percent(c);v=safeDiv(a*c/100,b);break;
 case 17:nonNeg(a,b);v=safeDiv(a*100,b);break;
 case 18:nonNeg(a,b,c);v=a*b*c;break;
 case 19:nonNeg(a,b);v=safeDiv(a,b);break;
 case 20:nonNeg(a,b,c);v=safeDiv(a,b)*c;break;
 case 21:nonNeg(a,b,c);v=safeDiv(a,b)*60+c;break;
 case 22:nonNeg(a,b);v=safeDiv(a,b);break;
 case 23:nonNeg(a,b);v=safeDiv(a*100,b);break;
 case 24:nonNeg(a,b);v=safeDiv(a,b);break;
 case 25:nonNeg(a,b);v=a*b;break;
 case 26:nonNeg(a,b);v=safeDiv(a,b);break;
 case 27:nonNeg(a,b,c);v=a*b*c;break;
 case 28:nonNeg(a,b,c);v=a*b*c;break;
 case 29:nonNeg(a,b,c);v=safeDiv(a*b*60,c);break;
 case 30:nonNeg(a,b);if(b<=a)throw Error("Queue is unstable; service rate must exceed arrivals");v=60/(b-a);break;
 case 31:nonNeg(a,b,c);v=a-b*c;break;
 case 32:nonNeg(a,b);v=a*b;break;
 case 33:nonNeg(a,b);v=safeDiv(a,b);break;
 case 34:nonNeg(a);percent(b);percent(c);if(b+c>100)throw Error("Reserve and administration cannot exceed 100%");v=a*(1-(b+c)/100);break;
 case 35:nonNeg(a,b);v=a*b;break;
 case 36:nonNeg(a,b,c);v=Math.max(0,a-b)*c;break;
 case 37:nonNeg(a,b);v=safeDiv(a,b);break;
 case 38:nonNeg(a,b);v=safeDiv((a-b)*100,b);break;
 case 39:nonNeg(a,b);v=safeDiv(a,b);break;
 case 40:nonNeg(a,b);v=safeDiv(a,b);break;
 case 41:nonNeg(a,b);v=a*b;break;
 case 42:nonNeg(a,b);v=safeDiv(a,b);break;
 case 43:{nonNeg(a,b,c,d);const r=b/1200;if(c>600)throw Error("Maximum 600 elapsed months");v=r===0?a-d*c:a*(1+r)**c-d*((1+r)**c-1)/r;v=Math.max(0,v);break}
 case 44:nonNeg(a,b);v=a*b;break;
 case 45:nonNeg(a,c);percent(b);v=a*(1-b/100)-c;break;
 case 46:nonNeg(a,b);percent(c);v=a*b*(1+c/100);break;
 case 47:if(a<0||a>1||b<0||b>1)throw Error("Luminance values must be 0–1");v=(Math.max(a,b)+0.05)/(Math.min(a,b)+0.05);break;
 case 48:nonNeg(a,b,c);v=a*b/1000*c;break;
 case 49:nonNeg(a,b);v=Math.max(0,a-b);break;
 }
 if(!Number.isFinite(v))throw Error("Value overflows finite range");
 const caution=index===30?"Single-server M/M/1 assumption; not a medical wait-time prediction.":index===47?"Enter WCAG relative luminance, not RGB channel intensities.":index===43?"Illustrative amortization only; payments, compounding and legal terms vary.":null;
 return {value:v,label:EXTRA_METHODS[index][2],algorithm:EXTRA_METHODS[index][0],warning:caution};
}
