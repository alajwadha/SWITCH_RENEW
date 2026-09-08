import test from 'node:test';
import assert from 'node:assert/strict';
import {colorDomain,transformObservation,transformedSeries,comparisonObservation,makeCSV,commonMix,fetchAtlasJSON} from '../components/atlas-state.ts';
import {gzipSync} from 'node:zlib';
const meta={label:'Demand',unit:'TWh',frequency:'annual',per_capita:{scale:1e9,unit:'kWh/person'}};
test('per-person values require the exact observation-year population',()=>{
 const o={year:2024,period:'2024',value:10};
 assert.equal(transformObservation(o,meta,[{year:2025,value:1e6}],'per_capita'),undefined);
 assert.equal(transformObservation(o,meta,[{year:2024,value:1e6}],'per_capita').value,10000);
 assert.equal(transformObservation(o,meta,[{year:2024,value:0}],'per_capita'),undefined);
});
test('growth requires an adjacent year and positive denominator',()=>{
 const values=[{year:2021,period:'2021',value:0},{year:2022,period:'2022',value:10},{year:2024,period:'2024',value:20},{year:2025,period:'2025',value:25}];
 assert.deepEqual(transformedSeries(values,meta,[],'growth').map(o=>o.value),[null,null,null,25]);
});
test('same-period comparisons never silently fall back to the latest year',()=>{
 const c={iso3:'KEN',indicators:{demand:{year:2025,period:'2025',value:15,history:[]}}};
 const atlas={countries:[c],metadata:{demand:meta}};
 assert.equal(comparisonObservation(atlas,{},c,'demand','2024','absolute'),undefined);
 assert.equal(comparisonObservation(atlas,{},c,'demand','latest','absolute').value,15);
});
test('map scale includes negative net imports and handles constant zero series',()=>{
 assert.deepEqual(colorDomain([-40,5,12]),[-40,12]);assert.deepEqual(colorDomain([0,0]),[0,1]);assert.deepEqual(colorDomain([]),[0,1]);
});
test('exports preserve numeric negatives, quotes, missing cells and neutralize formulas',()=>{
 const csv=makeCSV([['=HYPERLINK("bad")',-5,null,'a,b','x\ny']]);
 assert.match(csv,/'=HYPERLINK/);assert.match(csv,/"-5","","a,b"/);assert.match(csv,/x\ny/);
});
test('generation mix uses one common year and retains source-reported zeros',()=>{
 const atlas={countries:[],metadata:{a:{label:'Coal electricity generation'},b:{label:'Solar electricity generation'}}};
 const h={KEN:{a:[{year:2024,period:'2024',value:0},{year:2025,period:'2025',value:1}],b:[{year:2024,period:'2024',value:5}]}};
 const mix=commonMix(atlas,h,'KEN',['a','b']);assert.equal(mix.period,'2024');assert.equal(mix.rows[0].value,0);assert.equal(mix.rows[1].value,5);
});
test('static compressed shards decode in the browser-compatible path',async()=>{
 const original=globalThis.fetch;
 try{globalThis.fetch=async()=>new Response(gzipSync(JSON.stringify({KEN:{demand:[{value:1,year:2025}]}})));
 assert.deepEqual(await fetchAtlasJSON('/atlas/history-K.json.gz'),{KEN:{demand:[{value:1,year:2025}]}});
 }finally{globalThis.fetch=original;}
});

test('decoding handles both an HTTP-decoded file and an extra HTTP gzip layer',async()=>{
 const original=globalThis.fetch;const data={ok:true};
 try{for(const body of [JSON.stringify(data),gzipSync(JSON.stringify(data))]){
  globalThis.fetch=async()=>new Response(body,{headers:{'Content-Encoding':'gzip'}});
  assert.deepEqual(await fetchAtlasJSON('/atlas/index.json.gz'),data);
 }}finally{globalThis.fetch=original;}
});
