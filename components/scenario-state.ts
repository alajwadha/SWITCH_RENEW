import type {Config, Scenario} from './types';

export type EditorDraft = {base: Scenario; value: Scenario; cells: Record<string, string>; errors: Record<string, string>};
export const configLabels: Record<keyof Config, string> = {
 demand_multiplier: 'Demand multiplier', fuel_multiplier: 'Fuel-price multiplier',
 capital_multiplier: 'Capital-cost multiplier', time_limit: 'Solver time limit (s)',
 mip_gap: 'MIP relative gap', risk_weight: 'Risk weight λ', cvar_alpha: 'CVaR confidence α',
};

// The API accepts editable fields only, never database IDs or timestamps.
export function scenarioBody(s: Scenario) {
 return {name: s.name, model: s.model, config: s.config, edits: s.edits, revision: s.revision};
}
export function newDraft(s: Scenario): EditorDraft {return {base: s, value: s, cells: {}, errors: {}};}
export function hasDraftChanges(d: EditorDraft) {
 const values = (s: Scenario) => JSON.stringify({name: s.name, config: s.config, edits: [...s.edits].sort((a,b)=>cellKey(a.file,a.row,a.column).localeCompare(cellKey(b.file,b.row,b.column)))});
 return values(d.base) !== values(d.value) || Object.keys(d.cells).length > 0;
}
export function resolveDraft(saved: Scenario, cached?: EditorDraft): EditorDraft {
 return cached && hasDraftChanges(cached) ? cached : newDraft(saved);
}
export function cellKey(file: string, row: number, column: string) {return `${file}:${row}:${column}`;}
export function effectiveCell(s: Scenario, file: string, row: number, column: string, raw: string): string {
 const edit = s.edits.find(e=>e.file===file && e.row===row && e.column===column);
 if(edit) return String(edit.value);
 if(raw==='.' || raw==='' || !Number.isFinite(Number(raw))) return raw;
 const scales: Record<string, [string, number]> = {
  'loads.csv': ['zone_demand_mw', s.config.demand_multiplier],
  'fuel_cost.csv': ['fuel_cost', s.config.fuel_multiplier],
  'gen_build_costs.csv': ['gen_overnight_cost', s.config.capital_multiplier],
 };
 const scale = scales[file];
 return scale?.[0]===column ? String(Number(raw)*scale[1]) : raw;
}
export function draftIssues(d: EditorDraft): string[] {
 const issues = Object.values(d.errors);
 if(!d.value.name.trim()) issues.push('Enter a scenario name.');
 const limits: Record<keyof Config, [number,number]> = {demand_multiplier:[.05,5],fuel_multiplier:[0,10],capital_multiplier:[.05,10],time_limit:[5,86400],mip_gap:[0,.2],risk_weight:[0,1],cvar_alpha:[.5,.99]};
 for(const key of Object.keys(limits) as (keyof Config)[]) {
  const value = d.value.config[key], [low,high] = limits[key];
  if(!Number.isFinite(value) || value<low || value>high || (key==='time_limit' && !Number.isInteger(value))) issues.push(`${configLabels[key]} must be ${key==='time_limit'?'a whole number ':''}between ${low} and ${high}.`);
 }
 return issues;
}
