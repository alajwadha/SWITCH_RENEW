import type {Lesson,Part} from './types';
import {foundations} from './foundations';
import {system} from './system';
import {practice} from './practice';
import {kenyaUncertainty} from './kenya-uncertainty';
import {extensions} from './extensions';
export const parts:Part[]=[
 {id:'foundations',title:'Start from zero',description:'What is being optimized, what the units mean, and how to read the notation.',level:'Foundations'},
 {id:'optimization',title:'Think like the optimizer',description:'Hand-solvable dispatch, investment decisions, solver status and marginal values.',level:'Foundations'},
 {id:'time',title:'Understand time',description:'Years, representative blocks, statistical weights and physical chronology.',level:'Core'},
 {id:'money',title:'Follow the money',description:'Cost categories, capital recovery and the actual discounted objective.',level:'Core'},
 {id:'physical',title:'Build the power system',description:'Vintages, generation, storage, networks, reliability and operating detail.',level:'Core'},
 {id:'policy',title:'Ask better policy questions',description:'Carbon, renewable matching, flexible services and distributional outcomes.',level:'Applied'},
 {id:'practice',title:'Work with real SWITCH files',description:'Read modules and inputs, run the tutorial, interpret results and diagnose problems.',level:'Hands-on'},
 {id:'kenya',title:'Understand Xi Xi’s Kenya application',description:'Country data, source walkthrough, build limits, electrolysis and replication limits.',level:'Application'},
 {id:'uncertainty',title:'Plan before the future is known',description:'Scenarios, non-anticipativity, CVaR and the value of information.',level:'Advanced'},
 {id:'extensions',title:'Design your own extension',description:'Connect demand, write a small module, build a country case and complete a capstone.',level:'Research'}
];
export const lessons:Lesson[]=[...foundations,...system,...practice,...kenyaUncertainty,...extensions];
export function lessonText(l:Lesson){return [l.title,l.summary,...l.goals,...l.sections.flatMap(s=>[s.title,...s.paragraphs,...(s.points||[]),...(s.equations||[]).flatMap(e=>[e.tex,e.explain]),...(s.table?.rows.flat()||[])]),l.worked.title,l.worked.setup,...l.worked.steps,l.worked.result,...l.pitfalls,...l.checks.flatMap(q=>[q.question,q.answer])].join(' ');}
export function readingMinutes(l:Lesson){return Math.max(4,Math.ceil(lessonText(l).split(/\s+/).length/130));}
export function searchLessons(query:string){const terms=query.trim().toLowerCase().split(/\s+/).filter(Boolean);return lessons.filter(l=>terms.every(t=>lessonText(l).toLowerCase().includes(t)));}
export const equationIndex=lessons.flatMap(l=>l.sections.flatMap((s,sectionIndex)=>(s.equations||[]).map((e,index)=>({...e,lesson:l.id,title:l.title,section:s.title,sectionIndex,index}))));
export const LEARN_STORAGE_KEY='switch-learn-v1';
export type ReadingState={lesson:string;completed:string[]};
export function parseReadingState(raw:string|null):ReadingState{
 const fallback={lesson:lessons[0].id,completed:[]};
 if(!raw)return fallback;
 try{const value:unknown=JSON.parse(raw);if(!value||typeof value!=='object')return fallback;
  const obj=value as Record<string,unknown>;const valid=new Set(lessons.map(l=>l.id));
  return {lesson:typeof obj.lesson==='string'&&valid.has(obj.lesson)?obj.lesson:fallback.lesson,completed:Array.isArray(obj.completed)?[...new Set(obj.completed.filter((id):id is string=>typeof id==='string'&&valid.has(id)))]:[]};
 }catch{return fallback;}
}
