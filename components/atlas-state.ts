import type {Atlas,Country,Histories,IndicatorMeta,Observation} from './types.ts';

export function periodOf(o:Observation):string {return o.period||String(o.year??'');}
export function seriesFor(atlas:Atlas,histories:Histories,iso:string,key:string):Observation[]{
 return histories[iso]?.[key]||atlas.countries.find(c=>c.iso3===iso)?.indicators[key]?.history||[];
}
export function observation(atlas:Atlas,histories:Histories,c:Country,key:string,period='latest'):Observation|undefined{
 if(period==='latest')return c.indicators[key];
 return seriesFor(atlas,histories,c.iso3,key).find(o=>periodOf(o)===period);
}
export function transformObservation(o:Observation|undefined,meta:IndicatorMeta,population:Observation[],mode:string):Observation|undefined{
 if(!o||o.value===null)return undefined;
 if(mode!=='per_capita')return o;
 if(!meta.per_capita||meta.frequency!=='annual'||typeof o.value!=='number')return undefined;
 const pop=population.find(p=>p.year===o.year&&typeof p.value==='number'&&p.value>0);
 if(!pop||typeof pop.value!=='number')return undefined;
 return {...o,value:o.value*meta.per_capita.scale/pop.value,note:`Divided by population from ${o.year}; source: World Bank`};
}
export function transformedSeries(values:Observation[],meta:IndicatorMeta,pop:Observation[],mode:string):Observation[]{
 if(mode==='growth')return values.map(o=>{
  const prior=values.find(p=>p.year===(o.year??0)-1&&periodOf(p)===String((o.year??0)-1));
  return {...o,note:'Derived: 100 × (value / preceding calendar-year value − 1), with a positive prior value.',value:typeof o.value==='number'&&typeof prior?.value==='number'&&prior.value>0?(o.value/prior.value-1)*100:null};
 });
 return values.map(o=>transformObservation(o,meta,pop,mode)||{...o,value:null});
}
export function comparisonObservation(atlas:Atlas,hist:Histories,c:Country,key:string,period:string,mode:string):Observation|undefined{
 const meta=atlas.metadata[key];const values=transformedSeries(seriesFor(atlas,hist,c.iso3,key),meta,seriesFor(atlas,hist,c.iso3,'population'),mode);
 if(mode==='absolute')return observation(atlas,hist,c,key,period);
 const wanted=period==='latest'?periodOf(c.indicators[key]):period;
 return values.find(o=>periodOf(o)===wanted);
}
export function displayUnit(meta:IndicatorMeta,mode:string):string{return mode==='per_capita'?meta.per_capita?.unit||meta.unit:mode==='growth'?'% year on year':meta.unit;}
export function colorDomain(values:number[]):[number,number]{
 const valid=values.filter(Number.isFinite);if(!valid.length)return [0,1];
 const min=Math.min(0,...valid),max=Math.max(0,...valid);
 return min===max?[min,min+1]:[min,max];
}
export function csvCell(value:unknown):string{
 let text=value==null?'':String(value);
 // Protect text opened in spreadsheet software; real numeric negatives remain numeric.
 if(typeof value!=='number'&&/^[\s]*[=+\-@]/.test(text))text="'"+text;
 return '"'+text.replaceAll('"','""')+'"';
}
export function makeCSV(rows:unknown[][]):string{return '\ufeff'+rows.map(r=>r.map(csvCell).join(',')).join('\r\n');}
export function observationCSV(atlas:Atlas,rows:{country:Country;key:string;obs:Observation|undefined;unit?:string}[]):string{
 return makeCSV([['country','iso3','indicator','value','unit','observation_period','frequency','status','source','source_url','source_retrieved_at','note'],...rows.map(({country,key,obs,unit})=>{
  const m=atlas.metadata[key];return [country.name,country.iso3,m.label,obs?.value,unit||m.unit,obs?periodOf(obs):null,m.frequency,unit&&unit!==m.unit?'derived display transformation; '+m.status:m.status,m.source,m.source_url,m.retrieved_at,obs?.note|| (obs?.value==null?m.missing_reason:'')];
 })]);
}
export function commonMix(atlas:Atlas,hist:Histories,iso:string,keys:string[],requireAll=true):{period:string;rows:{name:string;value:number;key:string}[];missing?:number}{
 const periods=keys.map(k=>seriesFor(atlas,hist,iso,k).filter(o=>typeof o.value==='number').map(periodOf));
 const common=(requireAll?(periods[0]||[]).filter(p=>periods.every(x=>x.includes(p))):periods.flat()).sort().at(-1);
 if(!common)return {period:'',rows:[]};
 const present=keys.filter(key=>seriesFor(atlas,hist,iso,key).some(o=>periodOf(o)===common&&typeof o.value==='number'));
 return {period:common,missing:keys.length-present.length,rows:present.map(key=>({key,name:atlas.metadata[key]?.label.replace(/ electricity generation| installed capacity \(on-grid\)/g,'')||key,value:Number(seriesFor(atlas,hist,iso,key).find(o=>periodOf(o)===common)?.value)}))};
}

export async function fetchAtlasJSON<T>(url:string):Promise<T>{
 const response=await fetch(url);
 if(!response.ok)throw new Error(`Atlas data could not load (${response.status}).`);
 if(!url.endsWith('.gz'))return response.json();
 // Fetch may already have decoded an HTTP Content-Encoding layer. Inspect bytes,
 // because the file itself is gzip and servers can additionally compress it.
 const buffer=await response.arrayBuffer(),bytes=new Uint8Array(buffer);
 if(bytes[0]!==0x1f||bytes[1]!==0x8b)return JSON.parse(new TextDecoder().decode(bytes));
 if(typeof DecompressionStream==='undefined')throw new Error('This browser cannot unpack the atlas. Update to a current browser.');
 const stream=new Blob([buffer]).stream().pipeThrough(new DecompressionStream('gzip'));
 return new Response(stream).json();
}
