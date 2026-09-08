'use client';

import {useEffect,useState} from 'react';
import {ChevronLeft,ChevronRight,Copy,LoaderCircle,Play,Save,ShieldCheck,X} from 'lucide-react';
import type {Config,Model,Run,Scenario} from './types';
import {api,number} from './types';
import {cellKey,configLabels,draftIssues,effectiveCell,hasDraftChanges,newDraft,scenarioBody} from './scenario-state';
import type {EditorDraft} from './scenario-state';

export type Act = <T>(fn:()=>Promise<T>,success?:string)=>Promise<T|undefined>;
type Table = {columns:string[];rows:Record<string,string>[];baseline_rows:Record<string,string>[];total:number;offset:number;editable:Record<string,[number,number|null,string,string]>;revision:number};
type Report = {valid:boolean;errors:string[];warnings:string[];revision:number};

export default function ScenarioEditor({scenario,editor,onEdit,model,busy,act,onRun,onDuplicate}:{
 scenario:Scenario;editor:EditorDraft;onEdit:(d:EditorDraft)=>void;model:Model|undefined;busy:boolean;act:Act;onRun:(r:Run)=>void;onDuplicate:(s:Scenario)=>void;
}) {
 const [report,setReport]=useState<Report|null>(null),[tableName,setTableName]=useState(''),[offset,setOffset]=useState(0);
 const [tables,setTables]=useState<{name:string}[]>([]),[table,setTable]=useState<Table|null>(null),[tableError,setTableError]=useState('');
 const draft=editor.value, dirty=hasDraftChanges(editor), conflict=editor.base.revision!==scenario.revision;
 const issues=draftIssues(editor), valid=issues.length===0;
 function edit(next:EditorDraft){onEdit(next);setReport(null);}
 function change(key:keyof Config,value:number){edit({...editor,value:{...draft,config:{...draft.config,[key]:value}}});}
 useEffect(()=>{
  if(scenario.model==='stochastic')return;
  let live=true;
  api<{name:string}[]>(`/scenarios/${scenario.id}/tables`).then(items=>{if(live){setTables(items);setTableName(items[0]?.name||'');}}).catch(e=>{if(live)setTableError(e.message);});
  return()=>{live=false;};
 },[scenario.id,scenario.model]);
 useEffect(()=>{
  if(!tableName)return;
  let live=true;setTable(null);setTableError('');
  api<Table>(`/scenarios/${scenario.id}/tables/${tableName}?offset=${offset}`).then(t=>{if(live)setTable(t);}).catch(e=>{if(live)setTableError(e.message);});
  return()=>{live=false;};
 },[scenario.id,tableName,offset]);
 async function save(){
  const saved=await act(()=>api<Scenario>(`/scenarios/${scenario.id}`,'PUT',scenarioBody(draft)),'Revision saved');
  if(saved)edit(newDraft(saved));
 }
 function discard(){if(window.confirm('Discard this unsaved draft and load the latest saved revision?'))edit(newDraft(scenario));}
 function updateCell(input:HTMLInputElement,row:number,column:string){
  const key=cellKey(tableName,row,column), cells={...editor.cells,[key]:input.value}, errors={...editor.errors};
  let value=draft;
  if(input.value==='' || !input.validity.valid || !Number.isFinite(Number(input.value))){errors[key]=`${column}, row ${row+1}: enter a number within the shown limits. Use Remove override to restore the baseline.`;}
  else {
   delete errors[key];
   value={...draft,edits:[...draft.edits.filter(e=>cellKey(e.file,e.row,e.column)!==key),{file:tableName,row,column,value:Number(input.value)}]};
  }
  edit({...editor,value,cells,errors});
 }
 function removeOverride(file:string,row:number,column:string){
  const key=cellKey(file,row,column), cells={...editor.cells}, errors={...editor.errors};delete cells[key];delete errors[key];
  edit({...editor,cells,errors,value:{...draft,edits:draft.edits.filter(e=>cellKey(e.file,e.row,e.column)!==key)}});
 }
 const controls:{key:keyof Config;label:string;min:number;max:number;help:string}[]=[
  {key:'demand_multiplier',label:'Demand multiplier',min:.05,max:5,help:scenario.model==='stochastic'?'Scales demand in all three possible outcomes.':'Scales baseline demand at every zone and sampled timepoint.'},
  {key:'fuel_multiplier',label:scenario.model==='stochastic'?'Firm operating-cost multiplier':'Fuel-price multiplier',min:0,max:10,help:scenario.model==='stochastic'?'Scales the illustrative firm generator’s 70 USD/MWh operating cost.':'Scales baseline fuel prices. Absolute cell overrides take precedence.'},
  {key:'capital_multiplier',label:'Capital-cost multiplier',min:.05,max:10,help:scenario.model==='stochastic'?'Scales annualized firm and solar build costs.':'Scales overnight generation cost; fixed O&M stays separate.'},
 ];
 const changed=(Object.keys(configLabels) as (keyof Config)[]).filter(key=>draft.config[key]!==editor.base.config[key]);
 const visibleReport=report && !dirty && !conflict && report.revision===scenario.revision ? report : null;
 return <>
  <section className="panel scenario-form">
   <div className="panel-heading"><div><h2>{model?.name||scenario.model}</h2><span className="muted">Revision {editor.base.revision} · {dirty?'Unsaved draft':'All scenario changes saved'}</span></div><div className="button-row">
    <button className="button secondary small" disabled={busy||!valid} onClick={()=>act(async()=>{
     const s=await api<Scenario>('/scenarios','POST',{...scenarioBody(draft),name:draft.name.slice(0,93)+' · copy'});edit(newDraft(scenario));onDuplicate(s);
    },'Copy saved as a new scenario')}><Copy size={15}/>{dirty?'Save draft as a copy':'Duplicate'}</button>
    {dirty&&<button className="text-button" disabled={busy} onClick={discard}>Discard draft</button>}
    <button className="button secondary small" disabled={!dirty||busy||!valid||conflict} onClick={save}><Save size={15}/>Save revision</button>
   </div></div>
   {conflict&&<div className="banner warning" role="alert"><div>Another window saved revision {scenario.revision}. Your draft based on revision {editor.base.revision} is still here. Save it as a copy, or discard it to load the latest revision.</div></div>}
   {dirty&&<p className="draft-note" role="status">Your draft stays here when you switch views or scenarios. Save revision to keep it on disk.</p>}
   <fieldset disabled={busy} className="editor-fields">
    <label className="scenario-name">Scenario name<input value={draft.name} required maxLength={100} onChange={e=>edit({...editor,value:{...draft,name:e.target.value}})}/></label>
    <div className="controls-grid">{controls.map(c=><div className="control" key={c.key}>
     <label htmlFor={c.key}><span>{c.label}</span><span className="exact-value"><input id={c.key} type="number" min={c.min} max={c.max} step="any" required value={draft.config[c.key]} onChange={e=>change(c.key,Number(e.target.value))}/>×</span></label>
     <input aria-label={`${c.label} slider`} type="range" min={c.min} max={c.max} step={.05} value={draft.config[c.key]} onChange={e=>change(c.key,Number(e.target.value))}/>
     <div className="range-ends"><small>{c.min}×</small><small>{c.max}×</small></div><small>{c.help}</small>
    </div>)}</div>
    <div className="solver-options"><label>Solver time limit (seconds)<input type="number" min={5} max={86400} step={1} required value={draft.config.time_limit} onChange={e=>change('time_limit',Number(e.target.value))}/></label>
     {scenario.model!=='stochastic'&&<label>MIP relative gap (fraction)<input type="number" min={0} max={.2} step={.001} required value={draft.config.mip_gap} onChange={e=>change('mip_gap',Number(e.target.value))}/><small className="muted">0.001 = 0.1%. Applies to mixed-integer solves.</small></label>}
     {scenario.model==='stochastic'&&<><label>Risk weight λ (0 to 1)<input type="number" min={0} max={1} step={.1} required value={draft.config.risk_weight} onChange={e=>change('risk_weight',Number(e.target.value))}/></label><label>CVaR confidence α<input type="number" min={.5} max={.99} step={.01} required value={draft.config.cvar_alpha} onChange={e=>change('cvar_alpha',Number(e.target.value))}/></label></>}
    </div>
   </fieldset>
   {issues.length>0&&<div className="validation invalid" role="alert"><strong>Check these inputs before saving</strong>{issues.slice(0,5).map((issue,i)=><p key={i}>{issue}</p>)}{issues.length>5&&<p>{issues.length-5} more input issues.</p>}</div>}
   {dirty&&<details className="draft-review"><summary>Review changes from saved revision {editor.base.revision}</summary><div className="table-scroll"><table><thead><tr><th>Assumption</th><th>Saved</th><th>Draft</th></tr></thead><tbody>
    {draft.name!==editor.base.name&&<tr><td>Scenario name</td><td>{editor.base.name}</td><td>{draft.name}</td></tr>}
    {changed.map(key=><tr key={key}><td>{configLabels[key]}</td><td>{number(editor.base.config[key],6)}</td><td>{number(draft.config[key],6)}</td></tr>)}
    <tr><td>Absolute cell overrides</td><td>{editor.base.edits.length}</td><td>{draft.edits.length}</td></tr>
   </tbody></table></div><p className="muted">The table below previews the draft: baseline × multiplier, then absolute cell overrides.</p></details>}
   <div className="run-actions"><span className="muted">{dirty?'Save this revision before validation or running.':`Run saved revision ${scenario.revision} with an immutable input snapshot.`}</span>
    <button className="button secondary" disabled={dirty||busy||conflict||!valid} onClick={()=>act(async()=>{const r=await api<Report>(`/scenarios/${scenario.id}/validate`,'POST',{revision:scenario.revision});setReport(r);})}><ShieldCheck size={17}/>Validate inputs</button>
    <button className="button primary" disabled={dirty||busy||conflict||!valid} onClick={()=>act(async()=>{const r=await api<Run>(`/scenarios/${scenario.id}/run`,'POST',{revision:scenario.revision});onRun(r);},'Run queued and input snapshot saved')}><Play size={16}/>Run model</button>
   </div>
   {visibleReport&&<div className={'validation '+(visibleReport.valid?'valid':'invalid')}><strong>{visibleReport.valid?'Preflight checks passed':'Input validation failed'} · revision {visibleReport.revision}</strong>{[...visibleReport.errors,...visibleReport.warnings].map((s,i)=><p key={i}>{s}</p>)}</div>}
  </section>
  {scenario.model!=='stochastic'&&<section className="panel input-editor">
   <div className="panel-heading"><div><h2>Input table editor</h2><span className="muted">Draft preview · cell overrides apply after multipliers</span></div><label>Input table<select value={tableName} disabled={busy} onChange={e=>{setTableName(e.target.value);setOffset(0);}}>{tables.map(t=><option key={t.name}>{t.name}</option>)}</select></label></div>
   {tableError&&<p className="error-text" role="alert">{tableError}</p>}
   {table?<>
    <details className="variable-help"><summary>Variables, units and allowed values in this table</summary><div className="table-scroll"><table><thead><tr><th>Input parameter</th><th>Meaning</th><th>Unit</th><th>Allowed range</th></tr></thead><tbody>{Object.entries(table.editable).filter(([key])=>table.columns.includes(key)).map(([key,[low,high,unit,meaning]])=><tr key={key}><td><code>{key}</code></td><td>{meaning}</td><td>{unit}</td><td>{low} to {high??'no upper limit'}</td></tr>)}</tbody></table></div><p className="muted">These are assumptions you choose. SWITCH determines investment and dispatch decision variables when it solves.</p></details>
    <div className="table-scroll input-scroll"><table><thead><tr><th>Row</th>{table.columns.map(col=><th key={col} title={table.editable[col]?.[3]}>{col}{table.editable[col]&&<small className="block">{table.editable[col][2]}</small>}</th>)}</tr></thead><tbody>
     {table.baseline_rows.map((row,i)=><tr key={table.offset+i}><td className="muted">{table.offset+i+1}</td>{table.columns.map(col=>{
      const index=table.offset+i, key=cellKey(tableName,index,col), meta=table.editable[col];
      const value=effectiveCell(draft,tableName,index,col,row[col]), hasOverride=draft.edits.some(e=>cellKey(e.file,e.row,e.column)===key);
      return <td key={col}>{meta?<div className="input-cell"><input aria-label={`${col}, row ${index+1}`} aria-invalid={Boolean(editor.errors[key])} disabled={busy} type="number" min={meta[0]} max={meta[1]??undefined} step="any" value={editor.cells[key]??(value==='.'?'':value)} placeholder={row[col]==='.'?'Not specified':undefined} title={`Baseline: ${row[col]} ${meta[2]}`} onChange={e=>updateCell(e.currentTarget,index,col)}/>{(hasOverride||key in editor.cells)&&<button className="icon-button" disabled={busy} aria-label={`Remove override for ${col}, row ${index+1}`} title="Restore baseline with multiplier" onClick={()=>removeOverride(tableName,index,col)}><X size={14}/></button>}<small>Baseline: {row[col]}{hasOverride?' · override':''}</small></div>:row[col]}</td>;
     })}</tr>)}
    </tbody></table></div>
    <div className="table-pagination"><span>{table.total?offset+1:0}–{Math.min(offset+100,table.total)} of {number(table.total,0)} rows · {draft.edits.length} overrides</span><button className="button secondary small" disabled={offset===0} onClick={()=>setOffset(Math.max(0,offset-100))}><ChevronLeft size={15}/>Previous</button><button className="button secondary small" disabled={offset+100>=table.total} onClick={()=>setOffset(offset+100)}>Next<ChevronRight size={15}/></button><button className="text-button" disabled={busy||(!draft.edits.length&&!Object.keys(editor.cells).length)} onClick={()=>edit({...editor,value:{...draft,edits:[]},cells:{},errors:{}})}>Clear all overrides</button></div>
   </>:!tableError&&<div className="loading-inline"><LoaderCircle className="spin"/>Loading inputs…</div>}
  </section>}
 </>;
}
