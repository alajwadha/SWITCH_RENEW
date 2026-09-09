'use client';
import {useEffect,useMemo,useRef,useState} from 'react';
import maplibregl,{Map as MapLibreMap} from 'maplibre-gl';
import type {Country,IndicatorMeta,PowerAsset} from './types';
import {compact,number} from './types';
import {periodOf} from './atlas-state';
import {colorExpression,makeColorScale,NO_DATA_COLOR,numericObservation} from './map-state';
import type {MapView,ScaleMode} from './map-state';
import FlatMap from './flat-map';
import type {FlatMapControls} from './flat-map';
import {Maximize2,Minimize2,Globe2,Map as MapIcon,LocateFixed,RotateCcw,Plus,Minus} from 'lucide-react';

type Props={country:Country|undefined;countries:Country[];onSelect:(iso:string)=>void;layer?:string;modelCountry?:string;modelName?:string;assets?:PowerAsset[];legendNote?:string;indicatorMeta?:IndicatorMeta;unit?:string;period?:string;normalization?:string;loading?:boolean;assetAttribution?:string;};
const motionDuration=()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches?0:650;
const grid:GeoJSON.FeatureCollection={type:'FeatureCollection',features:[
 ...Array.from({length:11},(_,i)=>{const lon=(i-5)*30;return {type:'Feature' as const,properties:{},geometry:{type:'LineString' as const,coordinates:Array.from({length:35},(_,j)=>[lon,-85+j*5])}};}),
 ...[-60,-30,0,30,60].map(lat=>({type:'Feature' as const,properties:{},geometry:{type:'LineString' as const,coordinates:Array.from({length:73},(_,i)=>[-180+i*5,lat])}})),
]};

export default function Globe({country,countries,onSelect,layer='share_renewables',modelCountry,modelName,assets,legendNote,indicatorMeta,unit:displayUnit,period='latest',normalization='absolute',loading=false,assetAttribution='Global Energy Monitor · CC BY 4.0 · February 2026'}:Props){
 const element=useRef<HTMLDivElement>(null),panel=useRef<HTMLDivElement>(null),map=useRef<MapLibreMap|null>(null);
 const flat=useRef<FlatMapControls>(null);
 const selection=useRef(onSelect),latest=useRef(country),profiles=useRef(countries);
 selection.current=onSelect;latest.current=country;profiles.current=countries;
 const [ready,setReady]=useState(false),[error,setError]=useState(''),[attempt,setAttempt]=useState(0),[expanded,setExpanded]=useState(false),[hover,setHover]=useState<{iso:string;name:string}|null>(null);
 const [view,setView]=useState<MapView>('globe'),[scaleMode,setScaleMode]=useState<ScaleMode>('linear');
 const numeric=layer!=='model',unit=displayUnit||indicatorMeta?.unit||'',title=indicatorMeta?.label||(numeric?'Renewables generation share':'Country geography');
 const scale=useMemo(()=>makeColorScale(countries.map(c=>c.indicators[layer]?.value),{mode:scaleMode,percentage:normalization==='absolute'&&unit.startsWith('%'),diverging:normalization==='growth'}),[countries,layer,scaleMode,unit,normalization]);
 const interactive=view==='flat'||ready;
 const outOfRange=unit==='% of generation'&&normalization==='absolute'?countries.filter(c=>{const v=numericObservation(c.indicators[layer]);return v!=null&&(v<0||v>100);}).length:0;
 const hoveredCountry=hover?countries.find(c=>c.iso3===hover.iso):undefined;
 const hoveredObservation=hoveredCountry?.indicators[layer];
 const homeZoom=()=>{const el=element.current;return el?Math.max(.2,1.4+Math.log2(Math.max(150,Math.min(el.clientWidth-100,el.clientHeight-65))/326)):1.4;};
 function resetView(projection:MapView=view,duration=motionDuration()){
  if(projection==='flat'){flat.current?.reset();return;}
  const m=map.current;if(!m)return;
  m.flyTo({center:[30,8],zoom:homeZoom(),bearing:0,pitch:0,duration});
 }
 useEffect(()=>{const changed=()=>setExpanded(document.fullscreenElement===panel.current);document.addEventListener('fullscreenchange',changed);return()=>document.removeEventListener('fullscreenchange',changed);},[]);
 useEffect(()=>{
  if(!element.current)return;
  let m:MapLibreMap|undefined,observer:ResizeObserver|undefined;
  setReady(false);setError('');
  try{
   m=new maplibregl.Map({container:element.current,attributionControl:{compact:true},style:{version:8,projection:{type:'globe'},sources:{countries:{type:'geojson',data:'/world.geojson',attribution:'Natural Earth · public domain'},graticule:{type:'geojson',data:grid}},layers:[
    {id:'water',type:'background',paint:{'background-color':'#10263b'}},
    {id:'graticule',type:'line',source:'graticule',paint:{'line-color':'#94b1c3','line-opacity':.12,'line-width':.6}},
    {id:'land',type:'fill',source:'countries',paint:{'fill-color':NO_DATA_COLOR,'fill-opacity':1}},
    {id:'borders',type:'line',source:'countries',paint:{'line-color':'#d4e4ee','line-opacity':.55,'line-width':['interpolate',['linear'],['zoom'],0,.45,6,1]}},
    {id:'model-country',type:'line',source:'countries',filter:['==',['get','iso3'],''],paint:{'line-color':'#9edb65','line-width':2,'line-dasharray':[2,2]}},
    {id:'hover-country',type:'line',source:'countries',filter:['==',['get','iso3'],''],paint:{'line-color':'#fff','line-width':1.5}},
    {id:'selected-casing',type:'line',source:'countries',filter:['==',['get','iso3'],''],paint:{'line-color':'#091c2d','line-width':4}},
    {id:'selected-outline',type:'line',source:'countries',filter:['==',['get','iso3'],''],paint:{'line-color':'#fff','line-width':2}},
   ]},center:[30,8],zoom:homeZoom(),minZoom:0,maxZoom:8,renderWorldCopies:false});
   const current=m;map.current=current;
   current.dragRotate.disable();current.touchZoomRotate.disableRotation();current.scrollZoom.disable();
   observer=new ResizeObserver(()=>current.resize());observer.observe(element.current);
   current.on('load',()=>{setReady(true);current.setSky({'sky-color':'#183b58','horizon-color':'#8fcde4','fog-color':'#10263b','sky-horizon-blend':.7,'horizon-fog-blend':.7,'fog-ground-blend':.3,'atmosphere-blend':1});});
   current.on('click','land',e=>{
    if(current.getLayer('power-projects')&&current.queryRenderedFeatures(e.point,{layers:['power-projects']}).length)return;
    const iso=e.features?.[0]?.properties?.iso3;
    if(iso&&profiles.current.some(c=>c.iso3===iso))selection.current(iso);
   });
   current.on('mousemove','land',e=>{const p=e.features?.[0]?.properties;if(!p)return;const iso=String(p.iso3);current.getCanvas().style.cursor=profiles.current.some(c=>c.iso3===iso)?'pointer':'';current.setFilter('hover-country',['==',['get','iso3'],iso]);setHover(previous=>previous?.iso===iso?previous:{iso,name:String(p.name||iso)});});
   current.on('mouseleave','land',()=>{current.getCanvas().style.cursor='';current.setFilter('hover-country',['==',['get','iso3'],'']);setHover(null);});
   current.on('dragstart',()=>setHover(null));
   current.on('error',e=>{setError(e.error?.message||'The map could not load.');setView('flat');});
  }catch(e){setError(e instanceof Error?e.message:'Map unavailable');setView('flat');}
  return()=>{observer?.disconnect();m?.remove();map.current=null;};
 },[attempt]);
 useEffect(()=>{
  const m=map.current;if(!ready||!m)return;
  if(view==='flat')return;
  m.setProjection({type:'globe'});m.resize();
  // Projection changes keep both the selected country and the indicator unchanged.
  resetView(view,0);
 },[ready,view]);
 useEffect(()=>{
  const m=map.current;if(!ready||!m)return;
  for(const id of ['selected-casing','selected-outline'])m.setFilter(id,['==',['get','iso3'],country?.iso3||'']);
  if(country?.lon!=null&&country.lat!=null)m.flyTo({center:[country.lon,country.lat],zoom:m.getZoom(),duration:motionDuration()});
 },[country?.iso3,country?.lon,country?.lat,ready]);
 useEffect(()=>{
  const m=map.current;if(!ready||!m)return;
  m.setFilter('model-country',['==',['get','iso3'],modelCountry||'']);
  m.setPaintProperty('land','fill-color',numeric?colorExpression(countries,layer,scale) as maplibregl.ExpressionSpecification:'#466a7e');
 },[layer,countries,scale,ready,modelCountry,numeric]);
 useEffect(()=>{
  const m=map.current;if(!ready||!m)return;
  if(!assets&&!m.getSource('power-projects'))return;
  const data:GeoJSON.FeatureCollection={type:'FeatureCollection',features:(assets||[]).filter(a=>a.lat!==null&&a.lon!==null&&Number.isFinite(a.lat)&&Number.isFinite(a.lon)&&Math.abs(a.lat)<=90&&Math.abs(a.lon)<=180).map(a=>({type:'Feature',geometry:{type:'Point',coordinates:[a.lon!,a.lat!]},properties:{name:a.name,type:a.type,mw:a.capacity_mw,status:a.status}}))};
  const existing=m.getSource('power-projects') as maplibregl.GeoJSONSource|undefined;
  if(existing){existing.setData(data);return;}
  m.addSource('power-projects',{type:'geojson',data,attribution:assetAttribution});
  m.addLayer({id:'power-projects',type:'circle',source:'power-projects',paint:{'circle-radius':['interpolate',['linear'],['zoom'],0,2.5,6,6],'circle-color':['match',['get','type'],'solar','#f1cc71','wind','#7dbdf1','coal','#d09294','hydropower','#71d1c6','#c4a6e8'],'circle-opacity':.9,'circle-stroke-color':'#092031','circle-stroke-width':1}});
  m.on('click','power-projects',e=>{const p=e.features?.[0]?.properties;if(!p)return;const el=document.createElement('div');el.className='atlas-map-popup';const title=document.createElement('strong');title.textContent=String(p.name);const detail=document.createElement('p');detail.textContent=`${p.type} · ${p.status} · ${p.mw==null?'capacity unreported':number(Number(p.mw))+' MW'}`;el.append(title,detail);new maplibregl.Popup({closeButton:true,maxWidth:'280px'}).setLngLat(e.lngLat).setDOMContent(el).addTo(m);});
 },[assets,ready,assetAttribution]);
 return <div ref={panel} className="globe-panel globe-observatory" data-map-view={view}>
  <div className="atlas-map-header"><span className="atlas-map-caption"><Globe2 size={17}/> WORLD ENERGY</span><div className="map-projection-switch" role="group" aria-label="Map projection">
   <button aria-pressed={view==='globe'} disabled={!!error} title={error?'3D graphics are unavailable in this browser':'Switch to 3D globe'} onClick={()=>setView('globe')}><Globe2 size={16}/> 3D globe</button>
   <button aria-pressed={view==='flat'} onClick={()=>setView('flat')}><MapIcon size={16}/> Flat map</button>
  </div></div>
  <div className="atlas-map-stage">
   <div ref={element} style={{visibility:view==='flat'?'hidden':'visible'}} className="globe-canvas" aria-label={`${view==='globe'?'World globe':'World map'}. Country colors show ${title}. Drag or use arrow keys to move, and use plus or minus to zoom. Use the country picker for keyboard selection.`}/>
   {view==='flat'&&<FlatMap ref={flat} countries={countries} selected={country?.iso3} layer={layer} scale={scale} modelCountry={modelCountry} assets={assets} onSelect={onSelect} onHover={setHover}/>}
   {view==='globe'&&!ready&&!error&&<div className="globe-loading" role="status">Preparing the world map…</div>}
   {view==='globe'&&error&&<div className="map-error" role="alert"><Globe2/><p>The map could not load. Country search and charts remain available.</p><button onClick={()=>setAttempt(v=>v+1)}>Reload map</button><details><summary>Error details</summary><small>{error}</small></details></div>}
   {hover&&(view==='flat'||!error)&&<div className="map-hover-card" role="status"><strong>{hoveredCountry?.name||hover.name}</strong>{numeric&&<><span>{hoveredObservation?.value==null?'No observation':`${typeof hoveredObservation.value==='number'?number(hoveredObservation.value,3):hoveredObservation.value} ${unit}`}</span><small>{hoveredObservation?.value!=null?periodOf(hoveredObservation):'Missing data is not zero'}</small></>}<small>{hoveredCountry?'Click for country details':'No statistical profile in this atlas'}</small></div>}
   <div className="globe-tools" role="group" aria-label="Map controls">
    <button aria-label="Zoom in" title="Zoom in" disabled={!interactive} onClick={()=>view==='flat'?flat.current?.zoom(1):map.current?.zoomIn({duration:motionDuration()/3})}><Plus size={18}/></button>
    <button aria-label="Zoom out" title="Zoom out" disabled={!interactive} onClick={()=>view==='flat'?flat.current?.zoom(-1):map.current?.zoomOut({duration:motionDuration()/3})}><Minus size={18}/></button>
    <button aria-label="Focus selected country" title="Focus selected country" disabled={!interactive||country?.lat==null||country?.lon==null} onClick={()=>{if(view==='flat'&&country){flat.current?.focus(country);return;}if(country?.lon!=null&&country.lat!=null)map.current?.flyTo({center:[country.lon,country.lat],zoom:4,duration:motionDuration()});}}><LocateFixed size={18}/></button>
    <button aria-label="Reset world view" title="Reset world view" disabled={!interactive} onClick={()=>resetView()}><RotateCcw size={18}/></button>
    <button aria-label={expanded?'Exit fullscreen':'Expand map'} title={expanded?'Exit fullscreen':'Expand map'} disabled={!interactive} onClick={async()=>{try{if(document.fullscreenElement===panel.current)await document.exitFullscreen();else await panel.current?.requestFullscreen();}catch{ /* The map remains usable when fullscreen is unavailable. */ }}}>{expanded?<Minimize2 size={18}/>:<Maximize2 size={18}/>}</button>
   </div>
   <span className="map-gesture">{view==='globe'?'Drag to rotate · pinch or + / − to zoom':'Drag to pan · + / − to zoom'}</span>
  </div>
  <div className="atlas-map-legend" aria-label="Country color legend">
   <div className="map-legend-heading"><strong>{title}</strong>{numeric&&!scale.diverging&&<label>Scale<select aria-label="Country color scale" value={scaleMode} onChange={e=>setScaleMode(e.target.value as ScaleMode)}><option value="linear">Linear</option><option value="sqrt">Square root</option></select></label>}</div>
   {numeric&&scale.count>0&&<><div className="globe-color-scale" style={{background:`linear-gradient(90deg,${scale.stops.map(s=>s.color).join(',')})`}}/><div className="map-scale-ticks">{scale.stops.map((s,i)=><span key={i} title={number(s.value,6)}>{compact(s.value)}</span>)}</div></>}
   <div className="map-legend-meta"><span>{unit}{numeric&&scale.mode==='sqrt'?' · square-root scale':''}{numeric&&scale.diverging?' · centered on zero':''}</span><span className="map-legend-key"><i style={{background:NO_DATA_COLOR}}/> No data</span><span className="map-legend-key"><i className="outline"/> Selected</span>{modelCountry&&<span className="map-legend-key model-outline">Model: {modelName||modelCountry}</span>}</div>
   {numeric&&<p className="map-period-note">{loading?'Loading observations…':scale.count?`${scale.count} of ${countries.length} profiles have values`:'No numeric observations for this selection'} · {period==='latest'?'latest available; country dates differ':period}{scale.count>0&&numericObservation(country?.indicators[layer])===null?' · selected country has no value':''}</p>}
   {outOfRange>0&&<p className="map-period-note">{outOfRange} source observation{outOfRange===1?' is':'s are'} outside 0–100%; values are retained.</p>}
   {view==='flat'&&<p className="map-period-note">Natural Earth · public domain · Natural Earth projection{assets?.length?` · ${assetAttribution}`:''}</p>}
   {error&&view==='flat'&&<p className="map-fallback-note">3D graphics unavailable in this browser. The flat map remains interactive.</p>}
   {legendNote&&<p className="map-period-note">{legendNote}</p>}
   {!numeric&&<p className="map-period-note">Geographic view · this indicator has no numeric country color scale.</p>}
  </div>
 </div>;
}
