'use client';
import {useEffect,useRef,useState} from 'react';
import maplibregl,{Map} from 'maplibre-gl';
import {Country} from './types';
import {Maximize2,Globe2} from 'lucide-react';

export default function Globe({country,countries,onSelect,layer='model'}:{country:Country|undefined;countries:Country[];onSelect:(iso:string)=>void;layer?:string}){
 const element=useRef<HTMLDivElement>(null),map=useRef<Map|null>(null),select=useRef(onSelect),latest=useRef(country);
 const [ready,setReady]=useState(false),[error,setError]=useState('');
 select.current=onSelect;latest.current=country;
 useEffect(()=>{
  if(!element.current)return;
  let m:Map;
  try{
   m=new maplibregl.Map({container:element.current,attributionControl:{compact:true},style:{version:8,projection:{type:'globe'},sources:{countries:{type:'geojson',data:'/world.geojson',attribution:'Natural Earth · public domain'}},layers:[{id:'water',type:'background',paint:{'background-color':'#0b1929'}},{id:'land',type:'fill',source:'countries',paint:{'fill-color':'#273e4e','fill-opacity':1}},{id:'borders',type:'line',source:'countries',paint:{'line-color':'#536a78','line-width':0.55}},{id:'model-country',type:'fill',source:'countries',filter:['==',['get','iso3'],'KEN'],paint:{'fill-color':'#9edb65','fill-opacity':0.8}},{id:'selected',type:'fill',source:'countries',filter:['==',['get','iso3'],latest.current?.iso3||'KEN'],paint:{'fill-color':'#53d1c8','fill-opacity':0.85}},{id:'selected-outline',type:'line',source:'countries',filter:['==',['get','iso3'],latest.current?.iso3||'KEN'],paint:{'line-color':'#d0ffff','line-width':1.8}}]},center:[30,8],zoom:0.9,minZoom:0,maxZoom:6,renderWorldCopies:false});
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
  const m=map.current;if(!ready||!m||!country)return;
  for(const id of ['selected','selected-outline'])m.setFilter(id,['==',['get','iso3'],country.iso3]);
  if(country.lon!==null&&country.lat!==null){const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;m.flyTo({center:[country.lon,country.lat],zoom:Math.min(m.getZoom(),2),duration:reduce?0:1000,essential:false});}
 },[country,ready]);
 useEffect(()=>{
  const m=map.current;if(!ready||!m)return;
  if(layer==='model'){m.setPaintProperty('land','fill-color','#273e4e');m.setLayoutProperty('model-country','visibility','visible');return;}
  m.setLayoutProperty('model-country','visibility','none');
  const values:Record<string,number>={};for(const c of countries){const v=c.indicators[layer]?.value;if(v!=null)values[c.iso3]=v;}
  const max=Math.max(1,...Object.values(values));
  m.setPaintProperty('land','fill-color',['case',['has',['get','iso3'],['literal',values]],['interpolate',['linear'],['get',['get','iso3'],['literal',values]],0,'#263e50',max,'#57cab7'],'#182a39']);
 },[layer,countries,ready]);
 return <div className="globe-panel"><div ref={element} className="globe-canvas" aria-label="Interactive world globe; country selection is also available in the country picker"/>{error&&<div className="map-error"><Globe2/><p>Globe unavailable on this device. Use the country picker to explore the same data.</p><small>{error}</small></div>}<div className="globe-label"><span className="orbital-icon"><Globe2 size={15}/></span> WORLD VIEW</div><button className="globe-reset icon-button" title="Reset globe view" aria-label="Reset globe view" onClick={()=>map.current?.flyTo({center:[30,8],zoom:0.9,duration:window.matchMedia('(prefers-reduced-motion: reduce)').matches?0:900})}><Maximize2 size={17}/></button><div className="map-legend"><span><i className="legend-swatch mint"/> Selected area</span><span><i className="legend-swatch lime"/> SWITCH model: Kenya</span><small>{layer==='model'?'Drag to rotate · scroll to zoom':'Lighter = higher · dark = no data · latest available years differ'}</small></div></div>;
}
