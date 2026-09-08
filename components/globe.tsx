'use client';
import {useEffect,useRef,useState} from 'react';
import maplibregl,{Map} from 'maplibre-gl';
import type {Country,PowerAsset} from './types';
import {colorDomain} from './atlas-state';
import {Maximize2,Minimize2,Globe2,LocateFixed,RotateCcw,Plus,Minus} from 'lucide-react';

export default function Globe({country,countries,onSelect,layer='model',modelCountry,modelName,assets,legendNote}:{country:Country|undefined;countries:Country[];onSelect:(iso:string)=>void;layer?:string;modelCountry?:string;modelName?:string;assets?:PowerAsset[];legendNote?:string}){
 const element=useRef<HTMLDivElement>(null),map=useRef<Map|null>(null),select=useRef(onSelect),latest=useRef(country);
 const [ready,setReady]=useState(false),[error,setError]=useState(''),[expanded,setExpanded]=useState(false),[hover,setHover]=useState('');
 const panel=useRef<HTMLDivElement>(null);
 const homeZoom=()=>{const el=element.current;return el?Math.max(.3,1.4+Math.log2(Math.max(150,Math.min(el.clientWidth-60,el.clientHeight-105))/326)):1.4;};
 const duration=()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches?0:900;
 useEffect(()=>{const changed=()=>setExpanded(document.fullscreenElement===panel.current);document.addEventListener('fullscreenchange',changed);return()=>document.removeEventListener('fullscreenchange',changed);},[]);
 select.current=onSelect;latest.current=country;
 useEffect(()=>{
  if(!element.current)return;
  let m:Map;let observer:ResizeObserver;
  try{
   m=new maplibregl.Map({container:element.current,attributionControl:{compact:true},style:{version:8,projection:{type:'globe'},sources:{countries:{type:'geojson',data:'/world.geojson',attribution:'Natural Earth · public domain'}},layers:[{id:'water',type:'background',paint:{'background-color':'#0b2b43'}},{id:'land',type:'fill',source:'countries',paint:{'fill-color':'#468b9d','fill-opacity':1}},{id:'borders',type:'line',source:'countries',paint:{'line-color':'#93c5d0','line-width':0.55}},{id:'model-country',type:'fill',source:'countries',filter:['==',['get','iso3'],modelCountry||''],paint:{'fill-color':'#9edb65','fill-opacity':0.8}},{id:'hover-country',type:'fill',source:'countries',filter:['==',['get','iso3'],''],paint:{'fill-color':'#dbf7ef','fill-opacity':0.25}},{id:'selected',type:'fill',source:'countries',filter:['==',['get','iso3'],latest.current?.iso3||''],paint:{'fill-color':'#62e0cc','fill-opacity':0.85}},{id:'selected-outline',type:'line',source:'countries',filter:['==',['get','iso3'],latest.current?.iso3||''],paint:{'line-color':'#ecfffa','line-width':1.8}}]},center:[30,8],zoom:homeZoom(),minZoom:0,maxZoom:6,renderWorldCopies:false});
   map.current=m;
   m.dragRotate.disable();m.touchZoomRotate.disableRotation();m.scrollZoom.disable();
   observer=new ResizeObserver(()=>m.resize());observer.observe(element.current);
   m.on('load',()=>{setReady(true);m.setSky({'sky-color':'#77bcee','horizon-color':'#d3f5ff','fog-color':'#102b46','sky-horizon-blend':0.5,'horizon-fog-blend':0.5,'fog-ground-blend':0.3,'atmosphere-blend':1});});
   m.on('click','land',e=>{const iso=e.features?.[0]?.properties?.iso3;if(iso)select.current(iso);});
   m.on('mousemove','land',e=>{const iso=e.features?.[0]?.properties?.iso3;m.getCanvas().style.cursor='pointer';m.setFilter('hover-country',['==',['get','iso3'],iso||'']);setHover(String(e.features?.[0]?.properties?.name||iso||''));});
   m.on('mouseleave','land',()=>{m.getCanvas().style.cursor='';m.setFilter('hover-country',['==',['get','iso3'],'']);setHover('');});
   m.on('error',e=>{if(!m.isStyleLoaded())setError(e.error.message);});
  }catch(e){setError(e instanceof Error?e.message:'Globe unavailable');}
  return()=>{observer?.disconnect();m?.remove();map.current=null;};
 },[]);
 useEffect(()=>{
  const m=map.current;if(!ready||!m)return;
  for(const id of ['selected','selected-outline'])m.setFilter(id,['==',['get','iso3'],country?.iso3||'']);
  if(country&&country.lon!==null&&country.lat!==null){const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;m.flyTo({center:[country.lon,country.lat],zoom:m.getZoom(),duration:reduce?0:1000,essential:false});}
 },[country?.iso3,country?.lon,country?.lat,ready]);
 useEffect(()=>{
  const m=map.current;if(!ready||!m)return;
  m.setFilter('model-country',['==',['get','iso3'],modelCountry||'']);
  m.setLayoutProperty('selected','visibility',layer==='model'?'visible':'none');
  if(layer==='model'){m.setPaintProperty('land','fill-color','#468b9d');m.setLayoutProperty('model-country','visibility',modelCountry?'visible':'none');return;}
  m.setLayoutProperty('model-country','visibility','none');
  const values:Record<string,number>={};for(const c of countries){const v=c.indicators[layer]?.value;if(typeof v==='number'&&Number.isFinite(v))values[c.iso3]=v;}
  const [min,max]=colorDomain(Object.values(values));
  m.setPaintProperty('land','fill-color',['case',['has',['get','iso3'],['literal',values]],['interpolate',['linear'],['get',['get','iso3'],['literal',values]],min,'#22435e',max,'#88eee0'],'#172c3d']);
 },[layer,countries,ready,modelCountry]);
 useEffect(()=>{
  const m=map.current;if(!ready||!m)return;
  if(!assets&&!m.getSource('power-projects'))return;
  const data:GeoJSON.FeatureCollection={type:'FeatureCollection',features:(assets||[]).filter(a=>a.lat!==null&&a.lon!==null&&Math.abs(a.lat)<=90&&Math.abs(a.lon)<=180).map(a=>({type:'Feature',geometry:{type:'Point',coordinates:[a.lon!,a.lat!]},properties:{name:a.name,type:a.type,mw:a.capacity_mw,status:a.status}}))};
  const existing=m.getSource('power-projects') as maplibregl.GeoJSONSource|undefined;
  if(existing){existing.setData(data);return;}
  m.addSource('power-projects',{type:'geojson',data,attribution:'Global Energy Monitor · CC BY 4.0 · February 2026'});
  m.addLayer({id:'power-projects',type:'circle',source:'power-projects',paint:{'circle-radius':['interpolate',['linear'],['zoom'],0,2,6,6],'circle-color':['match',['get','type'],'solar','#f1cc71','wind','#7dbdf1','coal','#d09294','hydropower','#71d1c6','#c4a6e8'],'circle-opacity':0.85,'circle-stroke-color':'#092031','circle-stroke-width':0.6}});
  m.on('click','power-projects',e=>{const p=e.features?.[0]?.properties;if(!p)return;const el=document.createElement('div');el.className='atlas-map-popup';const title=document.createElement('strong');title.textContent=String(p.name);const detail=document.createElement('p');detail.textContent=`${p.type} · ${p.status} · ${p.mw==null?'capacity unreported':p.mw+' MW'}`;el.append(title,detail);new maplibregl.Popup({closeButton:true,maxWidth:'280px'}).setLngLat(e.lngLat).setDOMContent(el).addTo(m);});
 },[assets,ready]);
 return <div ref={panel} className="globe-panel globe-observatory">
  <div ref={element} className="globe-canvas" aria-label="Interactive world globe. Drag or use arrow keys to rotate; pinch or use controls to zoom. Country selection is also available in the country picker."/>
  {!ready&&!error&&<div className="globe-loading" role="status">Preparing your world…</div>}
  {error&&<div className="map-error"><Globe2/><p>Use the country picker to explore the same data.</p><small>{error}</small></div>}
  <div className="globe-label"><Globe2 size={16}/><span>ENERGY ATLAS<small>Explore a connected world</small></span></div>
  <div className="globe-tools" role="group" aria-label="Globe controls">
   <button aria-label="Zoom in" title="Zoom in" disabled={!ready} onClick={()=>map.current?.zoomIn({duration:duration()/3})}><Plus size={17}/></button>
   <button aria-label="Zoom out" title="Zoom out" disabled={!ready} onClick={()=>map.current?.zoomOut({duration:duration()/3})}><Minus size={17}/></button>
   <button aria-label="Focus selected country" title="Focus selected country" disabled={!ready||country?.lat==null||country?.lon==null} onClick={()=>{if(country?.lon!=null&&country.lat!=null)map.current?.flyTo({center:[country.lon,country.lat],zoom:3.3,duration:duration()});}}><LocateFixed size={17}/></button>
   <button aria-label="Reset globe view" title="Reset globe view" disabled={!ready} onClick={()=>map.current?.flyTo({center:[30,8],zoom:homeZoom(),bearing:0,pitch:0,duration:duration()})}><RotateCcw size={16}/></button>
   <button aria-label={expanded?'Exit fullscreen':'Expand globe'} title={expanded?'Exit fullscreen':'Expand globe'} disabled={!ready} onClick={async()=>{try{if(document.fullscreenElement===panel.current)await document.exitFullscreen();else await panel.current?.requestFullscreen();}catch{setError('Fullscreen is not supported by this browser.');}}}>{expanded?<Minimize2 size={16}/>:<Maximize2 size={16}/>}</button>
  </div>
  <div className="globe-country-label"><i/>{hover||country?.name||'Select a country'}<small>{hover?'Click to explore':'Selected country'}</small></div>
  <div className="globe-bottom">
   <div className="map-legend"><span><i className="legend-swatch mint"/> {layer==='model'?'Selected country':'Selected outline'}</span>{layer==='model'&&modelCountry&&<span><i className="legend-swatch lime"/> Model area: {modelName||modelCountry}</span>}{layer!=='model'&&<><div className="globe-color-scale"/><small>Lower → Higher · dark = no data</small></>}{legendNote&&<small>{legendNote}</small>}</div>
   <span className="globe-gesture">Drag to rotate<span>Pinch or + / − to zoom</span></span>
  </div>
 </div>;
}
