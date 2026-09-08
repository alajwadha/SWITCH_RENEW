export type Indicator = { value: number | null; year: number | null; history: {year:number; value:number}[] };
export type Country = {iso3:string;iso2:string;name:string;capital:string|null;region:string|null;income_group:string|null;lat:number|null;lon:number|null;indicators:Record<string,Indicator>};
export type Atlas = {retrieved_at:string;latest_completed_year:number;countries:Country[];errors:unknown[];metadata:Record<string,{code:string;label:string;unit:string;source:string;source_url:string;publication_date?:string;methodology?:string;source_organization?:string;status:string;retrieved_at:string}>};
export type Model = {id:string;name:string;description:string;country:string|null;kind:string;geography:string;available:boolean;modules:string[];zones:number;timepoints:number;periods:number;projects:number;license:string};
export type Config = {demand_multiplier:number;fuel_multiplier:number;capital_multiplier:number;time_limit:number;mip_gap:number;risk_weight:number;cvar_alpha:number};
export type Edit = {file:string;column:string;row:number;value:number};
export type Scenario = {id:string;name:string;model:string;config:Config;edits:Edit[];revision:number;created_at:string;updated_at:string};
export type Summary = {status:string;termination?:string;objective?:number;currency?:string;elapsed_seconds?:number;variables?:number;constraints?:number;has_integer_variables?:boolean;max_constraint_violation?:number;worst_constraint?:string;periods?:number[];tables?:Record<string,Record<string, string|number>[]>;expected_cost?:number;firm_build_mw?:number;solar_build_mw?:number;cvar?:number;vss?:number;evpi?:number;rp?:number;eev?:number;ws?:number;scenarios?:{name:string;probability:number;demand_mw:number;cost:number;firm_mw:number;solar_mw:number;unserved_mw:number}[];nonanticipativity_note?:string;assumptions?:Record<string,string|number>;risk_weight?:number;cvar_alpha?:number};
export type Run = {id:string;scenario_id:string;scenario_name:string;model:string;revision:number;status:string;created_at:string;started_at:string|null;finished_at:string|null;error:string|null;summary:Summary|null};
export const defaults:Config={demand_multiplier:1,fuel_multiplier:1,capital_multiplier:1,time_limit:120,mip_gap:0.001,risk_weight:0,cvar_alpha:0.95};
export async function api<T>(path:string, method='GET', body?:unknown):Promise<T>{
 const res=await fetch('/api'+path,{method,headers:body===undefined?{}:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});
 if(!res.ok){let msg=`Request failed (${res.status})`;try{const d=await res.json();msg=typeof d.detail==='string'?d.detail:JSON.stringify(d.detail);}catch{}throw new Error(msg);}
 return res.json();
}
export const number=(v:unknown,digits=1)=>typeof v==='number'&&Number.isFinite(v)?new Intl.NumberFormat('en',{maximumFractionDigits:digits}).format(v):'No data';
export const compact=(v:unknown)=>typeof v==='number'&&Number.isFinite(v)?new Intl.NumberFormat('en',{notation:'compact',maximumFractionDigits:2}).format(v):'No data';
