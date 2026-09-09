export type Equation = {tex:string; explain:string};
export type Section = {title:string; paragraphs:string[]; equations?:Equation[]; points?:string[]; code?:string; table?:{headers:string[]; rows:string[][]}};
export type Check = {level:'Foundation'|'Apply'|'Think deeper'; question:string; answer:string};
export type Lesson = {id:string; part:string; title:string; summary:string; goals:string[]; sections:Section[]; worked:{title:string; setup:string; steps:string[]; result:string}; pitfalls:string[]; checks:Check[]; sources:string[]; lab?:'dispatch'|'finance'|'weights'|'storage'|'uncertainty'};
export type Part = {id:string; title:string; description:string; level:string};
export type Variable = {symbol:string; object:string; kind:'Set / index'|'Input'|'Derived'|'Decision'|'Constraint'|'Objective'|'Registry'; meaning:string; units:string; domain:string; example:string; effect:string; source:string; lesson:string};
export const eq=(tex:string,explain:string):Equation=>({tex,explain});
export const sec=(title:string,paragraphs:string[],equations?:Equation[],points?:string[]):Section=>({title,paragraphs,equations,points});
export const checks=(a:[string,string],b:[string,string],c:[string,string]):Check[]=>[{level:'Foundation',question:a[0],answer:a[1]},{level:'Apply',question:b[0],answer:b[1]},{level:'Think deeper',question:c[0],answer:c[1]}];
