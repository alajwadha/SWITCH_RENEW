'use client';
import {useEffect,useRef,useState} from 'react';
import maplibregl,{Map} from 'maplibre-gl';
import type {Country,PowerAsset} from './types';
import {colorDomain} from './atlas-state';
import {Maximize2,Globe2} from 'lucide-react';

export default function Globe({country,countries,onSelect,layer='model',modelCountry,modelName,assets,legendNote}:{country:Country|undefined;countries:Country[];onSelect:(iso:string)=>void;layer?:string;modelCountry?:string;modelName?:string;assets?:PowerAsset[];legendNote?:string}){
 const element=useRef<HTMLDivElement>(null),map=useRef<Map|null>(null),select=useRef(onSelect),latest=useRef(country);
 const [ready,setReady]=useState(false),[error,setError]=useState('');
 select.current=onSelect;latest.current=country;
 useEffect(()=>{
  if(!element.current)return;
  let m:Map;
  try{
   m=new maplibregl.Map({container:element.current,attributionControl:{compact:true},style:{version:8,projection:{type:'globe'},sources:{countries:{type:'geojson',data:'/world.geojson',attribution:'Natural Earth · public domain'}},layers:[{id:'water',type:'background',paint:{'background-color':'#0b1929'}},{id:'land',type:'fill',source:'countries',paint:{'fill-color':'#273e4e','fill-opacity':1}},{id:'borders',type:'line',source:'countries',paint:{'line-color':'#536a78','line-width':0.55}},{id:'model-country',type:'fill',source:'countries',filter:['==',['get','iso3'],modelCountry||''],paint:{'fill-color':'#9edb65','fill-opacity':0.8}},{id:'selected',type:'fill',source:'countries',filter:['==',['get','iso3'],latest.current?.iso3||''],paint:{'fill-color':'#53d1c8','fill-opacity':0.85}},{id:'selected-outline',type:'line',source:'countries',filter:['==',['get','iso3'],latest.current?.iso3||''],paint:{'line-color':'#d0ffff','line-width':1.8}}]},center:[30,8],zoom:0.9,minZoom:0,maxZoom:6,renderWorldCopies:false});
   map.current=m;
   m.addControl(new maplibregl.NavigationControl({showCompass:false}),'bottom-right');
   m.on('load',()=>{setReady(true);m.setSky({'sky-color':'#071321','horizon-color':'#263f53','fog-color':'#071321','sky-horizon-blend':0.5,'horizon-fog-blend':0.5,'fog-ground-blend':0.3});});
   m.on('click','land',e=>{const iso=e.features?.[0]?.properties?.iso3;if(iso)select.current(iso);});
   m.on('mouseenter','land',()=>{m.getCanvas().style.cursor='pointer';});
   m.on('mouseleave','land',()=>{m.getCanvas().style.cursor='';});
   m.on('error',e=>{if(!m.isStyleLoaded())setError(e.error.message);});
  }catch(e){setError(e instanceof Error?e.message:'Globe unavailable');}
  return()=>{m?.remove();map.current=null;};
 },[]);
 useEffect(()=>{
  const m=map.current;if(!ready||!m)return;
  for(const id of ['selected','selected-outline'])m.setFilter(id,['==',['get','iso3'],country?.iso3||'']);
  if(country&&country.lon!==null&&country.lat!==null){const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;m.flyTo({center:[country.lon,country.lat],zoom:Math.min(m.getZoom(),2),duration:reduce?0:1000,essential:false});}
 },[country,ready]);
 useEffect(()=>{
  const m=map.current;if(!ready||!m)return;
  m.setFilter('model-country',['==',['get','iso3'],modelCountry||'']);
  m.setLayoutProperty('selected','visibility',layer==='model'?'visible':'none');
  if(layer==='model'){m.setPaintProperty('land','fill-color','#273e4e');m.setLayoutProperty('model-country','visibility',modelCountry?'visible':'none');return;}
  m.setLayoutProperty('model-country','visibility','none');
  const values:Record<string,number>={};for(const c of countries){const v=c.indicators[layer]?.value;if(typeof v==='number'&&Number.isFinite(v))values[c.iso3]=v;}
  const [min,max]=colorDomain(Object.values(values));
  m.setPaintProperty('land','fill-color',['case',['has',['get','iso3'],['literal',values]],['interpolate',['linear'],['get',['get','iso3'],['literal',values]],min,'#263e50',max,'#57cab7'],'#182a39']);
 },[layer,countries,ready,modelCountry]);
 useEffect(()=>{
  const m=map.current;if(!ready||!m)return;
  const data:GeoJSON.FeatureCollection={type:'FeatureCollection',features:(assets||[]).filter(a=>a.lat!==null&&a.lon!==null&&Math.abs(a.lat)<=90&&Math.abs(a.lon)<=180).map(a=>({type:'Feature',geometry:{type:'Point',coordinates:[a.lon!,a.lat!]},properties:{name:a.name,type:a.type,mw:a.capacity_mw,status:a.status}}))};
  const existing=m.getSource('power-projects') as maplibregl.GeoJSONSource|undefined;
  if(existing){existing.setData(data);return;}
  m.addSource('power-projects',{type:'geojson',data,attribution:'Global Energy Monitor · CC BY 4.0 · February 2026'});
  m.addLayer({id:'power-projects',type:'circle',source:'power-projects',paint:{'circle-radius':['interpolate',['linear'],['zoom'],0,2,6,6],'circle-color':['match',['get','type'],'Solar','#f1cc71','Wind','#7dbdf1','Coal','#d09294','Hydro','#71d1c6','#c4a6e8'],'circle-opacity':0.85,'circle-stroke-color':'#092031','circle-stroke-width':0.6}});
  m.on('click','power-projects',e=>{const p=e.features?.[0]?.properties;if(!p)return;const el=document.createElement('div');el.className='atlas-map-popup';const title=document.createElement('strong');title.textContent=String(p.name);const detail=document.createElement('p');detail.textContent=`${p.type} · ${p.status} · ${p.mw==null?'capacity unreported':p.mw+' MW'}`;el.append(title,detail);new maplibregl.Popup({closeButton:true,maxWidth:'280px'}).setLngLat(e.lngLat).setDOMContent(el).addTo(m);});
 },[assets,ready]);
 return <div className="globe-panel"><div ref={element} className="globe-canvas" aria-label="Interactive world globe; country selection is also available in the country picker"/>{error&&<div className="map-error"><Globe2/><p>Globe unavailable on this device. Use the country picker to explore the same data.</p><small>{error}</small></div>}<div className="globe-label"><span className="orbital-icon"><Globe2 size={15}/></span> WORLD VIEW</div><button className="globe-reset icon-button" title="Reset globe view" aria-label="Reset globe view" onClick={()=>map.current?.flyTo({center:[30,8],zoom:0.9,duration:window.matchMedia('(prefers-reduced-motion: reduce)').matches?0:900})}><Maximize2 size={17}/></button><div className="map-legend"><span><i className="legend-swatch mint"/> {layer==='model'?'Selected area':'Selected outline'}</span>{layer==='model'&&modelCountry&&<span><i className="legend-swatch lime"/> Model area: {modelName||modelCountry}</span>}<small>{legendNote|| (layer==='model'?'Drag to rotate · scroll to zoom':'Lighter = higher · dark = no data · latest available years differ')}</small>{layer!=='model'&&<small>Lighter = higher · dark = no data</small>}</div></div>;
}
