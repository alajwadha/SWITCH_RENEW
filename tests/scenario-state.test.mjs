import test from 'node:test';
import assert from 'node:assert/strict';
import {scenarioBody,newDraft,hasDraftChanges,resolveDraft,effectiveCell,draftIssues} from '../components/scenario-state.ts';

const saved={id:'scenario-a',name:'Baseline',model:'tiny',revision:1,created_at:'2026-09-08',updated_at:'2026-09-08',edits:[],config:{demand_multiplier:1,fuel_multiplier:1,capital_multiplier:1,time_limit:120,mip_gap:.001,risk_weight:0,cvar_alpha:.95}};

test('the save request contains only API-editable fields',()=>{
 assert.deepEqual(Object.keys(scenarioBody(saved)).sort(),['config','edits','model','name','revision']);
 assert.equal(scenarioBody(saved).revision,1);
});
test('drafts survive navigation and a newer saved revision without silently rebasing',()=>{
 const draft=newDraft(saved);draft.value={...saved,name:'My experiment'};
 const latest={...saved,revision:2,name:'Changed elsewhere'};
 assert.equal(resolveDraft(saved,draft),draft);
 assert.equal(resolveDraft(latest,draft).base.revision,1);
 assert.equal(resolveDraft(latest,draft).value.name,'My experiment');
 assert.equal(resolveDraft(latest,newDraft(saved)).value.name,'Changed elsewhere');
 assert.equal(hasDraftChanges(newDraft(latest)),false);
});
test('preview uses the baseline once, and removing an override restores scaling',()=>{
 const scaled={...saved,config:{...saved.config,demand_multiplier:1.2}};
 const override={...scaled,edits:[{file:'loads.csv',row:0,column:'zone_demand_mw',value:9}]};
 assert.equal(effectiveCell(override,'loads.csv',0,'zone_demand_mw','4'),'9');
 assert.equal(effectiveCell(scaled,'loads.csv',0,'zone_demand_mw','4'),'4.8');
 assert.equal(effectiveCell(scaled,'loads.csv',0,'zone_demand_mw','.'),'.');
 assert.equal(effectiveCell(scaled,'gen_build_costs.csv',0,'gen_fixed_om','12'),'12');
});
test('invalid and incomplete edits remain a draft and cannot be saved',()=>{
 const draft=newDraft(saved);draft.cells={'loads.csv:0:zone_demand_mw':''};draft.errors={'loads.csv:0:zone_demand_mw':'Enter a demand value.'};
 draft.value={...saved,config:{...saved.config,time_limit:12.5,cvar_alpha:NaN}};
 assert.equal(hasDraftChanges(draft),true);
 assert.equal(draftIssues(draft).length,3);
 assert.equal(resolveDraft({...saved,revision:2},draft),draft);
});
