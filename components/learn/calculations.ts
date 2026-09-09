// Browser-only teaching calculations. These never submit or represent a SWITCH run.
function nonnegative(...values:number[]){if(values.some(v=>!Number.isFinite(v)||v<0))throw new Error('Use finite, nonnegative inputs.');}
export function crf(rate:number,years:number){nonnegative(rate,years);if(years===0)throw new Error('Lifetime must be positive.');return rate===0?1/years:rate/-Math.expm1(-years*Math.log1p(rate));}
export function finance(principal:number,rate:number,years:number,fom:number){nonnegative(principal,fom);const factor=crf(rate,years);return {factor,capital:principal*factor,total:principal*factor+fom};}
export function dispatch(load:number,capA:number,capB:number,costA=40,costB=100,penalty=1000){
 nonnegative(load,capA,capB,costA,costB,penalty);if(penalty<Math.max(costA,costB))throw new Error('Teaching shortage penalty must be at least the generator costs.');
 const ordered=[{id:'a',cap:capA,cost:costA},{id:'b',cap:capB,cost:costB}].sort((a,b)=>a.cost-b.cost);
 const out={a:0,b:0,shortage:0,cost:0};let remaining=load;
 for(const plant of ordered){const power=Math.min(plant.cap,remaining);out[plant.id as 'a'|'b']=power;remaining-=power;out.cost+=power*plant.cost;}
 out.shortage=remaining;out.cost+=remaining*penalty;return out;
}
export function weights(duration:number,repetitions:number,years:number,power:number,price:number){nonnegative(duration,repetitions,years,power,price);if(duration===0||years===0)throw new Error('Duration and period length must be positive.');const period=duration*repetitions,annual=period/years;return {duration,period,annual,energy:power*annual,cost:power*annual*price};}
export function storage(initial:number,energyCapacity:number,charge:number,chargeHours:number,discharge:number,dischargeHours:number,efficiency:number){
 nonnegative(initial,energyCapacity,charge,chargeHours,discharge,dischargeHours,efficiency);if(efficiency>1)throw new Error('Efficiency cannot exceed one.');
 const input=charge*chargeHours,output=discharge*dischargeHours,afterCharge=initial+input*efficiency,final=afterCharge-output;
 return {input,output,loss:input*(1-efficiency),afterCharge,final,feasible:initial<=energyCapacity&&afterCharge<=energyCapacity+1e-9&&final>=-1e-9,rows:[{step:'Start',stored:initial},{step:'After charging',stored:afterCharge},{step:'After discharging',stored:final}]};
}
export function cvar(costs:number[],probabilities:number[],alpha:number){
 if(!costs.length||costs.length!==probabilities.length||costs.some(c=>!Number.isFinite(c)))throw new Error('Provide matching finite costs and probabilities.');nonnegative(...probabilities,alpha);
 const total=probabilities.reduce((a,b)=>a+b,0);if(Math.abs(total-1)>1e-8||alpha>=1)throw new Error('Probabilities must sum to one and alpha must be below one.');
 let tail=1-alpha,weighted=0;const rows=costs.map((cost,i)=>({cost,p:probabilities[i]})).sort((a,b)=>b.cost-a.cost);
 for(const row of rows){const take=Math.min(tail,row.p);weighted+=take*row.cost;tail-=take;if(tail<1e-12)break;}
 return weighted/(1-alpha);
}
export function uncertainty(highProbability:number,capitalCost:number,shortageCost:number,alpha:number,risk:number){
 nonnegative(highProbability,capitalCost,shortageCost,alpha,risk);if(highProbability>1||alpha>=1||risk>1)throw new Error('Use valid probabilities and risk settings.');
 const demand=[50,100],probabilities=[1-highProbability,highProbability];
 // One physical hour, zero running cost, no existing capacity. Units: CU for the complete illustrative interval.
 function evaluate(capacity:number){const costs=demand.map(d=>capitalCost*capacity+shortageCost*Math.max(d-capacity,0));const expected=costs.reduce((v,c,i)=>v+c*probabilities[i],0);const tail=cvar(costs,probabilities,alpha);return {capacity,costs,expected,cvar:tail,objective:(1-risk)*expected+risk*tail};}
 const candidates=[0,50,100];
 // Piecewise-linear objective has breakpoints at demands, with fixed scenario cost ordering in this toy.
 const selected=candidates.map(evaluate).reduce((best,x)=>x.objective<best.objective-1e-9?x:best);
 const neutral=candidates.map(evaluate).reduce((best,x)=>x.expected<best.expected-1e-9?x:best);
 const mean=demand.reduce((v,d,i)=>v+d*probabilities[i],0);
 const evCapacity=capitalCost<=shortageCost?mean:0;
 const eev=evaluate(evCapacity).expected;
 const ws=demand.reduce((v,d,i)=>v+probabilities[i]*Math.min(capitalCost*d,shortageCost*d),0);
 return {selected,rp:neutral.expected,neutralCapacity:neutral.capacity,eev,ws,vss:eev-neutral.expected,evpi:neutral.expected-ws,evCapacity,probabilities,demand,curve:Array.from({length:41},(_,i)=>{const r=evaluate(i*2.5);return {capacity:r.capacity,expected:r.expected,riskObjective:r.objective};})};
}
