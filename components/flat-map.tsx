'use client';
import {forwardRef,useEffect,useImperativeHandle,useMemo,useRef,useState} from 'react';
import {geoGraticule10,geoNaturalEarth1,geoPath} from 'd3-geo';
import {X} from 'lucide-react';
import type {ColorScale} from './map-state';
import {colorAt} from './map-state';
import type {Country,PowerAsset} from './types';
import {number} from './types';

type World=GeoJSON.FeatureCollection<GeoJSON.Geometry,{iso3:string;name:string}>;
let worldRequest:Promise<World>|undefined;
function loadWorld(){return worldRequest??=(fetch('/world.geojson').then(r=>{if(!r.ok)throw Error('Country boundaries could not load.');return r.json() as Promise<World>;}).catch(e=>{worldRequest=undefined;throw e;}));}
export type FlatMapControls={zoom:(direction:number)=>void;reset:()=>void;focus:(country:Country)=>void;};
type Props={countries:Country[];selected?:string;layer:string;scale:ColorScale;modelCountry?:string;assets?:PowerAsset[];onSelect:(iso:string)=>void;onHover:(value:{iso:string;name:string}|null)=>void;};
const width=1000,height=570;

const FlatMap=forwardRef<FlatMapControls,Props>(function FlatMap({countries,selected,layer,scale,modelCountry,assets,onSelect,onHover},ref){
 const [world,setWorld]=useState<World|null>(null),[error,setError]=useState(''),[retry,setRetry]=useState(0),[camera,setCamera]=useState({zoom:1,x:0,y:0}),[asset,setAsset]=useState<PowerAsset|null>(null);
 const drag=useRef<{x:number;y:number;panX:number;panY:number}|null>(null),moved=useRef(false);
 const index=useMemo(()=>new Map(countries.map(c=>[c.iso3,c])),[countries]);
 useEffect(()=>{let active=true;setError('');loadWorld().then(data=>{if(active)setWorld(data);}).catch(e=>{if(active)setError(e.message);});return()=>{active=false;};},[retry]);
 const geography=useMemo(()=>{
  if(!world)return null;
  const projection=geoNaturalEarth1().fitExtent([[20,18],[width-20,height-18]],world),path=geoPath(projection);
  return {projection,features:world.features.map(f=>({iso:f.properties.iso3,name:f.properties.name,path:path(f)||''})),grid:path(geoGraticule10())||'',sphere:path({type:'Sphere'})||''};
 },[world]);
 const reset=()=>setCamera({zoom:1,x:0,y:0});
 const zoom=(direction:number)=>setCamera(v=>{const z=Math.min(8,Math.max(1,v.zoom*(direction>0?1.5:1/1.5)));return {zoom:z,x:z===1?0:v.x*z/v.zoom,y:z===1?0:v.y*z/v.zoom};});
 function focus(country:Country){
  if(!geography||country.lon==null||country.lat==null)return;
  const point=geography.projection([country.lon,country.lat]);if(!point)return;
  const z=3;setCamera({zoom:z,x:(width/2-point[0])*z,y:(height/2-point[1])*z});
 }
 useImperativeHandle(ref,()=>({zoom,reset,focus}),[geography]);
 useEffect(()=>{setAsset(null);},[assets,selected]);
 if(error)return <div className="map-error" role="alert"><p>{error} Country search remains available.</p><button onClick={()=>setRetry(v=>v+1)}>Reload boundaries</button></div>;
 if(!geography)return <div className="globe-loading" role="status">Loading country boundaries…</div>;
 return <div className="flat-map-surface">
  <svg viewBox={`0 0 ${width} ${height}`} role="group" aria-label="Interactive flat world map. Use the country picker to select any country. Arrow keys pan; plus and minus zoom." tabIndex={0}
   onKeyDown={e=>{const delta=40;if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-','Home'].includes(e.key))e.preventDefault();if(e.key==='+'||e.key==='=')zoom(1);else if(e.key==='-')zoom(-1);else if(e.key==='Home')reset();else if(e.key.startsWith('Arrow'))setCamera(v=>({...v,x:v.x+(e.key==='ArrowLeft'?delta:e.key==='ArrowRight'?-delta:0),y:v.y+(e.key==='ArrowUp'?delta:e.key==='ArrowDown'?-delta:0)}));}}
   onPointerDown={e=>{if(e.button!==0)return;drag.current={x:e.clientX,y:e.clientY,panX:camera.x,panY:camera.y};moved.current=false;}}
   onPointerMove={e=>{if(!drag.current)return;const dx=e.clientX-drag.current.x,dy=e.clientY-drag.current.y;if(Math.abs(dx)+Math.abs(dy)<4&&!moved.current)return;moved.current=true;e.currentTarget.setPointerCapture(e.pointerId);onHover(null);const rect=e.currentTarget.getBoundingClientRect(),factor=Math.min(rect.width/width,rect.height/height);setCamera(v=>({...v,x:drag.current!.panX+dx/factor,y:drag.current!.panY+dy/factor}));}}
   onPointerUp={e=>{drag.current=null;if(e.currentTarget.hasPointerCapture(e.pointerId))e.currentTarget.releasePointerCapture(e.pointerId);}}
   onPointerCancel={()=>{drag.current=null;}}
   onPointerLeave={()=>{if(!moved.current)drag.current=null;onHover(null);}}>
   <g transform={`translate(${width/2+camera.x} ${height/2+camera.y}) scale(${camera.zoom}) translate(${-width/2} ${-height/2})`}>
    <path d={geography.sphere} fill="#142e45" stroke="#779ab44d" strokeWidth={1} vectorEffect="non-scaling-stroke"/>
    <path d={geography.grid} fill="none" stroke="#a1bfd825" strokeWidth={.7} vectorEffect="non-scaling-stroke"/>
    {geography.features.map(f=><path key={f.iso} d={f.path} fill={layer==='model'?'#466a7e':colorAt(index.get(f.iso)?.indicators[layer]?.value,scale)} stroke="#cee1ed90" strokeWidth={.65} vectorEffect="non-scaling-stroke" data-country={f.iso} aria-label={index.get(f.iso)?.name||f.name} role="button" style={{cursor:index.has(f.iso)?'pointer':'default'}}
     onPointerEnter={()=>{if(!moved.current)onHover({iso:f.iso,name:f.name});}}
     onPointerLeave={()=>onHover(null)}
     onClick={e=>{e.stopPropagation();if(!moved.current&&index.has(f.iso)){setAsset(null);onSelect(f.iso);}}}/>) }
    {geography.features.filter(f=>f.iso===modelCountry).map(f=><path key={'model-'+f.iso} d={f.path} fill="none" stroke="#b6df77" strokeWidth={2} strokeDasharray="4 3" vectorEffect="non-scaling-stroke" pointerEvents="none"/>)}
    {geography.features.filter(f=>f.iso===selected).map(f=><g key={'selected-'+f.iso} pointerEvents="none"><path d={f.path} fill="none" stroke="#0a2137" strokeWidth={4.5} vectorEffect="non-scaling-stroke"/><path d={f.path} fill="none" stroke="#fff" strokeWidth={2.5} vectorEffect="non-scaling-stroke"/></g>)}
    {(assets||[]).map(a=>{if(a.lon==null||a.lat==null||!Number.isFinite(a.lon)||!Number.isFinite(a.lat)||Math.abs(a.lon)>180||Math.abs(a.lat)>90)return null;const p=geography.projection([a.lon,a.lat]);if(!p)return null;const color=({solar:'#f1cc71',wind:'#7dbdf1',coal:'#d09294',hydropower:'#71d1c6'} as Record<string,string>)[a.type]||'#c4a6e8';return <circle key={a.id} cx={p[0]} cy={p[1]} r={3/camera.zoom} fill={color} stroke="#0b2135" strokeWidth={.8} vectorEffect="non-scaling-stroke" role="button" aria-label={a.name} style={{cursor:'pointer'}} onClick={e=>{e.stopPropagation();if(!moved.current){setAsset(a);onHover(null);}}}><title>{a.name} · {a.type} · {a.status}</title></circle>;})}
   </g>
  </svg>
  {asset&&<div className="flat-map-asset"><button aria-label="Close project details" onClick={()=>setAsset(null)}><X size={15}/></button><strong>{asset.name}</strong><p>{asset.type} · {asset.status} · {number(asset.capacity_mw)} MW</p><small>{asset.vintage||'See selected inventory vintage'}</small></div>}
 </div>;
});
export default FlatMap;
