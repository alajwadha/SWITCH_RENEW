'use client';
import {useMemo} from 'react';
import {ArrowRight,ArrowUpRight,GitCompareArrows,LoaderCircle} from 'lucide-react';
import {CartesianGrid,Line,LineChart,ResponsiveContainer,Tooltip,XAxis,YAxis} from 'recharts';
import type {Atlas,Country,Histories,IndicatorMeta,Observation} from './types';
import {compact,number} from './types';
import {commonMix,comparisonObservation,periodOf} from './atlas-state';
import {chartObservations,numericObservation} from './map-state';

const generationKeys=['generation_coal','generation_gas','generation_other_fossil','generation_nuclear','generation_hydro','generation_wind','generation_solar','generation_bioenergy','generation_other_renewables'];
const technologyColors:Record<string,string>={generation_coal:'#697587',generation_gas:'#d68b54',generation_other_fossil:'#9b6069',generation_nuclear:'#9871c1',generation_hydro:'#318dc0',generation_wind:'#56b3a1',generation_solar:'#e0b638',generation_bioenergy:'#648941',generation_other_renewables:'#589585'};
const facts=[['generation_total','Generation'],['demand_total','Demand'],['share_renewables','Renewable share'],['power_intensity','Power carbon intensity']];
type Props={atlas:Atlas;country?:Country;histories:Histories;metric:string;meta:IndicatorMeta;current?:Observation;unit:string;period:string;normalization:string;values:Observation[];historyLoading:boolean;onMetric:(key:string)=>void;onOverview:()=>void;onCompare:()=>void;inComparison:boolean;comparisonFull:boolean;};

export default function AtlasCountryPanel({atlas,country,histories,metric,meta,current,unit,period,normalization,values,historyLoading,onMetric,onOverview,onCompare,inComparison,comparisonFull}:Props){
 const history=useMemo(()=>chartObservations(values,meta.frequency).map(o=>({...o,label:periodOf(o),value:numericObservation(o)})),[values,meta.frequency]);
 const mix=useMemo(()=>country?commonMix(atlas,histories,country.iso3,generationKeys):{period:'',rows:[]},[atlas,histories,country]);
 const mixTotal=mix.rows.reduce((total,row)=>total+row.value,0);
 const numeric=meta.value_type!=='text',present=history.some(o=>o.value!==null);
 return <aside className="country-panel atlas-country-detail" aria-label="Selected country energy profile">
  <header className="country-detail-heading"><span className="country-code">{country?.iso3||'COUNTRY PROFILE'}</span><h2>{country?.name||'Choose a country'}</h2><p>{[country?.region,country?.capital].filter(Boolean).join(' · ')}</p></header>
  <section className="country-selected-metric" aria-label="Selected indicator">
   <span className="detail-section-label">SELECTED INDICATOR</span><h3>{meta.label}</h3>
   <div className="country-indicator-value" aria-live="polite"><strong title={numeric?number(current?.value,6):undefined}>{typeof current?.value==='string'?current.value:current?.value==null?'No data':compact(current.value)}</strong>{current?.value!=null&&<span>{unit}</span>}</div>
   <p className="country-observation-date">{current?.value!=null?`Observation: ${periodOf(current)}`:period==='latest'?'No reported observation':`No observation for ${period}`}</p>
   {current?.value==null&&<p className="country-missing">{normalization==='per_capita'?'A value and population from the same year are required.':meta.missing_reason}</p>}
   <div className="country-data-tags"><span>{meta.frequency}</span><span>{normalization!=='absolute'?'Derived display':meta.status.startsWith('estimated')?'Provider estimate':meta.status.startsWith('derived')?'Derived indicator':'Source data'}</span></div>
   {current?.note&&<p className="country-missing">{current.note}</p>}
   <a className="source-link" href={meta.source_url} target="_blank" rel="noreferrer">{meta.source}<ArrowUpRight size={14}/></a>
  </section>
  {numeric&&<section className="country-history" aria-label={`${meta.label} history`}>
   <div className="country-section-heading"><h3>Indicator history</h3><small>{unit}</small></div>
   {historyLoading?<p className="country-history-status" role="status"><LoaderCircle className="spin" size={15}/> Loading history…</p>:present?<><div className="country-history-chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={history} margin={{top:8,right:8,bottom:0,left:0}} accessibilityLayer><CartesianGrid vertical={false} stroke="#e1e8ef"/><XAxis dataKey="label" stroke="#5b7286" fontSize={12} minTickGap={45} tickLine={false} axisLine={false}/><YAxis stroke="#5b7286" fontSize={12} width={47} tickFormatter={v=>compact(v)} tickLine={false} axisLine={false}/><Tooltip contentStyle={{background:'#fff',border:'1px solid #d5e1ec',borderRadius:10,color:'#203e54',fontSize:13}} formatter={v=>[number(Number(v),3),unit]} labelFormatter={label=>`Observation: ${label}`}/><Line dataKey="value" stroke="#2877b7" strokeWidth={2.5} dot={history.filter(o=>o.value!==null).length<3} activeDot={{r:4}} connectNulls={false} isAnimationActive={false}/></LineChart></ResponsiveContainer></div><small className="country-chart-note">{history[0]?.label}–{history.at(-1)?.label} · missing years remain gaps</small></>:<p className="country-history-status">No numeric history for this indicator and display.</p>}
  </section>}
  <section className="country-system-facts" aria-label="Key energy statistics">
   <div className="country-section-heading"><h3>Energy at a glance</h3></div><p className="country-chart-note">As reported · {period==='latest'?'latest values; dates shown per indicator':`same period: ${period}`}</p>
   <div className="country-facts-grid">{facts.map(([key,label])=>{const m=atlas.metadata[key],o=country?comparisonObservation(atlas,histories,country,key,period,'absolute'):undefined;return <button key={key} className={metric===key?'active':''} onClick={()=>onMetric(key)} aria-label={`Explore ${label}`} title={`${m?.label} · ${m?.source}`}><span>{label}</span><strong title={number(o?.value,6)}>{compact(o?.value)}</strong><small>{m?.unit}</small><small>{o?.value!=null?periodOf(o):'No observation'}</small></button>;})}</div>
  </section>
  {mixTotal>0&&<section className="country-generation-mix" aria-label="Electricity generation mix">
   <div className="country-section-heading"><h3>Generation mix</h3><small>{mix.period}</small></div>
   <div className="country-mix-bar" role="img" aria-label={`Generation mix, ${mix.period}. ${mix.rows.filter(r=>r.value>0).map(r=>`${r.name}: ${number(r.value/mixTotal*100,1)} percent`).join('; ')}`}>{mix.rows.filter(r=>r.value>0).map(r=><span key={r.key} style={{width:`${r.value/mixTotal*100}%`,background:technologyColors[r.key]}} title={`${r.name}: ${number(r.value,3)} TWh`}/>)}</div>
   <div className="country-mix-labels">{mix.rows.filter(r=>r.value>0).sort((a,b)=>b.value-a.value).map(r=><button key={r.key} onClick={()=>onMetric(r.key)}><i style={{background:technologyColors[r.key]}}/><span>{r.name}</span><strong>{number(r.value/mixTotal*100,1)}%</strong></button>)}</div>
   <p className="country-chart-note">Ember · latest common year for all nine categories; independent of the selected indicator period.</p>
  </section>}
  <div className="country-detail-actions"><button className="button primary full" disabled={!country||inComparison||comparisonFull} onClick={onCompare}><GitCompareArrows size={16}/>{inComparison?'Added to comparison':comparisonFull?'Comparison full (6 countries)':'Add to comparison'}</button><button className="button secondary full" disabled={!country} onClick={onOverview}>Full country overview<ArrowRight size={16}/></button></div>
 </aside>;
}
