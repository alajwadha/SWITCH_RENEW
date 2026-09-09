import test from 'node:test';
import assert from 'node:assert/strict';
import {createExpression} from '@maplibre/maplibre-gl-style-spec';
import {makeColorScale,colorExpression,chartObservations,NO_DATA_COLOR,colorAt} from '../components/map-state.ts';
const country=(iso,value)=>({iso3:iso,indicators:{metric:{value,year:2025}}});
function evaluator(countries,scale){const result=createExpression(colorExpression(countries,'metric',scale),{type:'color'});assert.equal(result.result,'success',JSON.stringify(result.value));return iso=>result.value.evaluate({zoom:1},{type:'Polygon',properties:{iso3:iso}});}
test('the actual MapLibre expression distinguishes a reported zero from a missing value',()=>{
 const countries=[country('ZERO',0),country('HIGH',100),country('NONE',null)];
 const scale=makeColorScale(countries.map(c=>c.indicators.metric.value),{percentage:true});
 const evaluate=evaluator(countries,scale);assert.equal(scale.count,2);
 assert.notDeepEqual(evaluate('ZERO'),evaluate('NONE'));assert.deepEqual(evaluate('NONE'),evaluate('UNKNOWN'));
 assert.notDeepEqual(evaluate('HIGH'),evaluate('ZERO'));
 assert.equal(NO_DATA_COLOR,'#344557');
});
test('percentage colors stay comparable across observation years',()=>{
 assert.deepEqual(makeColorScale([2,28,91],{percentage:true}).stops,makeColorScale([0,50],{percentage:true}).stops);
 assert.deepEqual(makeColorScale([0,50],{percentage:true}).stops.map(s=>s.value),[0,25,50,75,100]);
});
test('square-root labels and the shader use the same transformation',()=>{
 const scale=makeColorScale([0,100],{mode:'sqrt'});
 assert.deepEqual(scale.stops.map(s=>s.value),[0,6.25,25,56.25,100]);
 const countries=[country('LOW',0),country('MID',25),country('HIGH',100)];
 const evaluate=evaluator(countries,scale),mid=evaluate('MID');
 const expected=createExpression(scale.stops[2].color,{type:'color'}).value.evaluate({zoom:1});
 assert.deepEqual(mid,expected);
});
test('negative and growth values retain a symmetric zero-centered scale',()=>{
 const scale=makeColorScale([-40,0,12],{mode:'sqrt'});assert.equal(scale.mode,'linear');
 assert.deepEqual(scale.stops.map(s=>s.value),[-40,-20,0,20,40]);
 const evaluate=evaluator([country('NEG',-40),country('ZERO',0),country('POS',40)],scale);
 assert.notDeepEqual(evaluate('NEG'),evaluate('POS'));assert.notDeepEqual(evaluate('ZERO'),evaluate('NONE'));
 assert.equal(makeColorScale([4,7],{diverging:true}).stops[2].value,0);
});
test('small fractional values, empty domains and constant zeros have valid scales',()=>{
 assert.equal(makeColorScale([.001,.003]).stops.at(-1).value,.003);
 for(const values of [[],[0,0],[null,NaN,Infinity]]){
  const scale=makeColorScale(values);assert.ok(scale.stops.every((s,i)=>!i||s.value>scale.stops[i-1].value));
  evaluator([],scale)('NONE');
 }
});
test('annual history charts insert gaps instead of joining over missing years',()=>{
 const result=chartObservations([{year:2024,value:10},{year:2022,value:5}],'annual');
 assert.deepEqual(result.map(o=>[o.year,o.value]),[[2022,5],[2023,null],[2024,10]]);
 assert.equal(chartObservations([{year:2022,value:5},{year:2024,value:10}],'snapshot').length,2);
});

test('SVG country colors match the WebGL palette at every scale stop',()=>{
 for(const options of [{mode:'linear'},{mode:'sqrt'},{diverging:true}]){
  const scale=makeColorScale([0,100],options);
  const countries=scale.stops.map((s,i)=>country(String(i),s.value));
  const evaluate=evaluator(countries,scale);
  for(const [i,stop] of scale.stops.entries()){
   assert.equal(colorAt(stop.value,scale),stop.color);
   const expected=createExpression(colorAt(stop.value,scale),{type:'color'}).value.evaluate({zoom:1});
   assert.deepEqual(evaluate(String(i)),expected);
  }
 }
 assert.equal(colorAt(null,makeColorScale([])),NO_DATA_COLOR);
});
