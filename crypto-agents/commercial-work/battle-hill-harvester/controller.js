// Original B1/B2 Chief D "Hill-Harvester" controller, 2026-11-19.
// battle.training Armor s2.0.0, not based on copied starter source.
// Scoring first: APC holds highest-value point; scout captures a second;
// MBT screens contacts; engineer supports the APC with smoke near threats.
const Q = 65536, TURN = 4096, RAD = Math.PI * 2;
let battlefield, rules, mySide, middle;
const distance=(a,b,c,d)=>Math.hypot(c-a,d-b);
const aim=(x,y,tx,ty)=>(Math.round(Math.atan2(ty-y,tx-x)*TURN/RAD)+TURN)&4095;
const diff=(a,b)=>((b-a+6144)&4095)-2048;
function traversable(x,y) {
  let ix=(x/Q)|0, iy=(y/Q)|0;
  if (ix<0||iy<0||ix>=battlefield.width||iy>=battlefield.height) return false;
  const id=battlefield.terrain[iy*battlefield.width+ix];
  return rules.terrainSpeed ? rules.terrainSpeed[id]>0 : (id!==2&&id!==4&&id!==6&&id!==8);
}
function guide(u,goal,spec) {
  const want=aim(u.x,u.y,goal.x,goal.y);
  const offsets=[0,245,-245,490,-490,768,-768,1024,-1024,1536,-1536,2048];
  let heading=want;
  for(const n of offsets) {
    const tryAngle=(want+n+TURN)&4095, rad=tryAngle*RAD/TURN;
    if(traversable(u.x+Math.cos(rad)*Q*2,u.y+Math.sin(rad)*Q*2)){
      heading=tryAngle;break;
    }
  }
  const d=diff(u.heading,heading);
  if(u.blocked) return {steer:Q,throttle:-Math.floor(Q*0.75)};
  return {steer:Math.max(-Q,Math.min(Q,Math.round(d*Q/Math.max(1,spec.turnRate||24)))),
    throttle:Math.abs(d)>800?Math.floor(Q*0.22):Math.abs(d)>400?Math.floor(Q*0.55):Q};
}
function selectPoint(points,x,y,role,tick) {
  let best=null,bestScore=-1e30;
  for(let i=0;i<points.length;i++){
    const p=points[i];
    const held=p.owner===mySide&&p.state==='held';
    const dist=distance(x,y,p.x,p.y)/Q;
    const s=(p.weight||1)*(role==='apc'?5:3)
      -(held?25:0)-Math.min(70,dist)*(role==='scout'?0.35:0.65)
      +(role==='apc'?0:(i%2===0?-1:1))*((role==='scout')?8:0)
      +(p.owner!==null&&p.owner!==mySide?7:0);
    if(s>bestScore){best=p;bestScore=s;}
  }
  return best||{x:middle[0],y:middle[1]};
}
function enemyFor(u,contacts) {
  let best=null,score=-Infinity;
  for(const c of contacts){
    if(c.alive===false||typeof c.x!=='number'||typeof c.y!=='number')continue;
    const r=distance(u.x,u.y,c.x,c.y)/Q;
    const hot=c.kind==='mbt'?8:c.kind==='artillery'?11:c.kind==='apc'?9:0;
    const s=hot-0.95*r;
    if(s>score){score=s;best={c,range:r};}
  }
  return best;
}
globalThis.controller = {
  draft(h) {
    const pick=['apc','mbt','engineer','scout'];
    const d=h.draft;
    if(!d||!Array.isArray(d.roster))return undefined;
    if(pick.reduce((n,k)=>n+(d.costs[k]||999),0)<=d.budget&&pick.every(k=>d.roster.includes(k))) return pick;
    return undefined;
  },
  hello(h) {
    battlefield=h.map;rules=h.rules;mySide=h.side;
    middle=[battlefield.width*Q/2,battlefield.height*Q/2];
  },
  tick(o) {
    const orders=[], contacts=Array.isArray(o.contacts)?o.contacts:[];
    const points=Array.isArray(o.objectives)?o.objectives:[];
    for(const u of o.units||[]){
      if(!u.alive)continue;
      const spec=rules.units[u.kind],enemy=enemyFor(u,contacts);
      if(!spec)continue;
      const bestPoint=selectPoint(points,u.x,u.y,u.kind,o.tick);
      let goal=bestPoint;
      if(u.kind==='mbt') {
        // Screen the APC: confront nearby threats while retaining hill priority.
        if(enemy&&enemy.range<13) goal={x:enemy.c.x,y:enemy.c.y};
      }
      if(u.kind==='engineer'&&enemy&&enemy.range<10){
        // Smoke approach only when threatened, not permanently.
        goal={x:bestPoint.x,y:bestPoint.y};
      }
      if(u.kind==='scout'&&points.length>1){
        // Fan out from highest-value APC point, avoiding a pile-up on one hill.
        const sorted=points.slice().sort((a,b)=>(b.weight||1)-(a.weight||1));
        goal=sorted.find(p=>p!==bestPoint&&p.owner!==mySide)||sorted[sorted.length-1]||bestPoint;
      }
      let order={id:u.id};
      const distGoal=distance(u.x,u.y,goal.x,goal.y)/Q;
      if(o.canMove && distGoal>1.8)Object.assign(order,guide(u,goal,spec));
      else if(o.canMove)order.throttle=0;
      if(enemy){
        const range=enemy.range;
        const weapon=spec.gun;
        if(weapon&&weapon.mode==='direct'){
          order.aimAt=[enemy.c.x,enemy.c.y];
          const tolerance=weapon.aimTolerance||120;
          const aimed=Math.abs(diff(u.turret||u.heading,aim(u.x,u.y,enemy.c.x,enemy.c.y)))<=tolerance;
          if(u.reload===0&&range<=(weapon.maxRange||0)&&aimed)order.fire=true;
        } else if(weapon&&weapon.mode==='indirect'){
          if(u.reload===0&&range>=weapon.minRange&&range<=weapon.maxRange)order.fire=[enemy.c.x,enemy.c.y];
        } else if(spec.secondary&&u.reload2===0&&range<=spec.secondary.maxRange){
          order.fire=true;
        }
      }
      if(u.kind==='engineer'&&enemy&&enemy.range<12&&u.smoke===0)order.ability='smoke';
      orders.push(order);
    }
    return {units:orders};
  }
};
