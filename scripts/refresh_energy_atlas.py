"""Build all-country energy atlas v2, with separate observation periods and provenance.

Run with the project Python. --refresh downloads provider updates; the default reuses
exact cached provider files. --offline requires them all to exist. Publication is
versioned and the manifest is replaced last, so a failed refresh leaves the app usable.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import argparse
import csv
import hashlib
import gzip
import itertools
import json
import math
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile
import pycountry
from energy_sources import ROOT, RAW, URLS, WB, IRENA, GEM, acquire

CATEGORIES = [
 ('generation','Electricity generation','Generation by fuel, shares and annual changes.'),
 ('capacity','Capacity & projects','Installed renewable and conventional capacity, net additions and tracked project stages.'),
 ('demand','Electricity demand','Annual and monthly electricity use, growth and sector demand.'),
 ('energy','Whole energy system','Primary energy and direct end-use demand across sectors and fuels.'),
 ('fuels','Fuels & security','Fuel production, consumption, trade, reserves and import exposure.'),
 ('emissions','Emissions','Power lifecycle estimates and energy-related combustion CO₂, with distinct boundaries.'),
 ('grids','Trade & grids','Electricity trade, losses and interconnection data readiness.'),
 ('storage','Storage & flexibility','Pumped storage and the coverage of battery, flexibility and curtailment data.'),
 ('prices','Prices & costs','Comparable tariff bands and dated global technology cost benchmarks.'),
 ('access','Access & reliability','Urban/rural access, clean cooking and business-survey outages.'),
 ('resources','Renewable resources','National solar potential, spatial variation and long-term seasonal profiles.'),
 ('policy','Policies & targets','Dated emissions-target records and carbon-tax coverage.'),
 ('context','Country context','Population, economy, geography and energy rents.'),
]
RELEVANCE = {
 'generation':'Check the historical generation mix before calibrating a SWITCH baseline. Annual totals do not specify hourly dispatch.',
 'capacity':'Compare baseline plant capacity with the capacity-build inputs; planned inventory capacity is not an approved build decision.',
 'demand':'Check annual load totals. SWITCH also needs load-zone and timepoint demand profiles and representative-period weights.',
 'energy':'Explore demand drivers and potential sector coupling. End-use energy includes fuels that need a separate conversion model before becoming electricity demand.',
 'fuels':'Inform fuel supply scenarios, import constraints and price sensitivities; physical national totals are not plant fuel-cost assumptions.',
 'emissions':'Check emissions boundaries before selecting emission factors or caps. Lifecycle CO₂e is different from combustion CO₂.',
 'grids':'Inform trade and network assumptions. National trade does not identify individual line capacities, impedances or hourly limits.',
 'storage':'Inform storage scenarios. SWITCH needs both power and energy capacity, efficiencies, duration and operating constraints.',
 'prices':'Context for calibration. Retail tariffs include non-generation charges and are not a substitute for generator costs or wholesale prices.',
 'access':'Inform demand-development scenarios. Access percentages and business surveys do not define system reliability constraints.',
 'resources':'Screen renewable resources. Convert site-specific weather to timepoint capacity factors before using it in SWITCH.',
 'policy':'Translate a verified policy into the correct constraint, target year and sector boundary; a pledge is not an implemented constraint.',
 'context':'Provide scale and socioeconomic context. These indicators do not automatically modify a model.',
}
BASE_CATS={'population':'context','gdp':'context','gdp_per_capita':'context','urban_population':'context','land_area':'context','electricity_access':'access','clean_cooking':'access','electricity_per_capita':'demand','renewable_electricity':'generation','electricity_losses':'grids','energy_intensity':'energy'}


def numeric(v):
 try:
  value=float(v)
  return value if math.isfinite(value) else None
 except (ValueError,TypeError):return None


def jsonstat(data):
 """Decode sparse and dense JSON-stat in declared dimension order, retaining flags."""
 codes=[]
 for key in data['id']:
  index=data['dimension'][key]['category']['index']
  codes.append(index if isinstance(index,list) else sorted(index,key=index.get))
 values=data['value'];flags=data.get('status',{})
 for i,combo in enumerate(itertools.product(*codes)):
  value=values[i] if isinstance(values,list) else values.get(str(i))
  if value is None:continue
  flag=(flags[i] if i<len(flags) else None) if isinstance(flags,list) else flags.get(str(i))
  yield dict(zip(data['id'],combo)),value,flag


def xlsx_rows(path,sheet=1):
 """Read source spreadsheet values without adding a spreadsheet runtime dependency."""
 ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 with zipfile.ZipFile(path) as z:
  shared=[''.join(x.itertext()) for x in ET.fromstring(z.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in z.namelist() else []
  root=ET.fromstring(z.read(f'xl/worksheets/sheet{sheet}.xml'))
  for row in root.findall('.//m:sheetData/m:row',ns):
   out={}
   for c in row:
    v=c.find('m:v',ns)
    if v is None:continue
    text=v.text
    if c.get('t')=='s':text=shared[int(text)]
    out[re.sub(r'\d','',c.get('r'))]=text
   yield out


class Builder:
 def __init__(self,base=None):
  self.base=base or json.loads((ROOT/'public/atlas.json').read_text())
  if self.base.get('index_file'):self.base=json.loads(gzip.decompress((ROOT/'public'/self.base['index_file'].lstrip('/')).read_bytes()))
  self.countries={c['iso3']:{k:v for k,v in c.items() if k not in ('indicators','coverage')} for c in self.base['countries']}
  self.metadata={};self.hist=defaultdict(lambda:defaultdict(dict));self.sources={};self.issues=[];self.assets=defaultdict(list)
  self.stamp=datetime.now(timezone.utc).isoformat();self.completed=datetime.now().year-1
  self.names={}
  for iso,c in self.countries.items():
   self.names[c['name'].casefold()]=iso
   pc=pycountry.countries.get(alpha_3=iso)
   if pc:
    for key in ('name','official_name','common_name'):
     if getattr(pc,key,None):self.names[getattr(pc,key).casefold()]=iso
  self.names.update({k.casefold():v for k,v in {'Burkina-Faso':'BFA','Kosovo':'XKX','Taiwan':'TWN','Congo-Brazzaville':'COG','Congo-Kinshasa':'COD','DR Congo':'COD','Holy See':'VAT','Bonaire, Sint Eustatius, and Saba':'BES','Congo (Brazzaville)':'COG','Congo (Kinshasa)':'COD','Democratic Republic of the Congo':'COD','Republic of the Congo':'COG','South Korea':'KOR','Korea, South':'KOR','North Korea':'PRK','Korea, North':'PRK','Russia':'RUS','Iran':'IRN','Syria':'SYR','Vietnam':'VNM','Laos':'LAO','Burma':'MMR','Turkey':'TUR','Tanzania':'TZA','Venezuela':'VEN','Bolivia':'BOL','Moldova':'MDA','Brunei':'BRN','Czech Republic':'CZE','Palestine':'PSE','Palestinian Territories':'PSE','The Bahamas':'BHS','The Gambia':'GMB','Gambia, The':'GMB','Cote d’Ivoire':'CIV','Côte d’Ivoire':'CIV','Swaziland':'SWZ','Cape Verde':'CPV','Hong Kong':'HKG','Macau':'MAC','Macao':'MAC','Reunion':'REU','Micronesia':'FSM','U.S. Virgin Islands':'VIR','Saint Martin':'MAF','Turks and Caicos Islands':'TCA'}.items()})
 def iso(self,name):return self.names.get(name.strip().casefold())
 def source(self,key,file,label,url,license,**kwargs):
  path=RAW/file;raw=path.read_bytes();stamp=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat()
  provenance=path.with_suffix(path.suffix+'.provenance')
  if provenance.exists():stamp=json.loads(provenance.read_text())['retrieved_at']
  self.sources[key]={'name':label,'source_url':url,'retrieval_url':URLS.get(file,url),'retrieved_at':stamp,'sha256':hashlib.sha256(raw).hexdigest(),'license':license,**kwargs}
  return key
 def define(self,key,label,unit,cat,src,method='',**kw):
  s=self.sources[src]
  self.metadata[key]={'code':key,'label':label,'unit':unit,'category':cat,'source_id':src,'source':s['name'],'source_url':s['source_url'],'retrieved_at':s['retrieved_at'],'publication_date':s.get('publication_date'),'status':'source-reported; provider estimates may be included','value_type':'number','frequency':'annual','methodology':method,'switch_relevance':RELEVANCE[cat],**kw}
 def add(self,iso,key,period,value,**extra):
  if iso not in self.countries or value is None or (isinstance(value,str) and not value.strip()):return
  if self.metadata[key]['value_type']=='number':
   value=numeric(value)
   if value is None:return
   value=round(value,8)
  period=str(period);year=int(period[:4]) if re.match(r'^\d{4}',period) else None
  if self.metadata[key]['frequency']=='annual' and (year is None or not 2010<=year<=self.completed):return
  if year and year>datetime.now().year:return
  self.hist[iso][key][period]={'period':period,'year':year,'value':value,**{k:v for k,v in extra.items() if v is not None}}
 def base_data(self):
  histories={}
  for c in self.base['countries']:
   for key in BASE_CATS:
    entry=c['indicators'].get(key)
    if not entry:continue
    hist=entry.get('history',[])
    if self.base.get('history_files'):
     shard=self.base['history_files'][c['iso3'][0]]
     if shard not in histories:histories[shard]=json.loads(gzip.decompress((ROOT/'public'/shard.lstrip('/')).read_bytes()) if shard.endswith('.gz') else (ROOT/'public'/shard.lstrip('/')).read_bytes())
     hist=histories[shard].get(c['iso3'],{}).get(key,[])
    meta=self.base['metadata'][key]
    self.metadata[key]={**meta,'category':BASE_CATS[key],'value_type':'number','frequency':'annual','switch_relevance':RELEVANCE[BASE_CATS[key]],'source_id':'worldbank_context'}
    for obs in hist:self.add(c['iso3'],key,obs['year'],obs['value'])
  self.sources['worldbank_context']={'name':'World Bank · World Development Indicators','source_url':'https://data.worldbank.org/','license':'World Bank open-data terms; indicator-specific third-party conditions apply','retrieved_at':self.base['metadata']['population']['retrieved_at'],'note':'Per-indicator API URLs, retrieval times and hashes are retained in indicator metadata.'}
 def worldbank(self):
  for key,(code,label,unit) in WB.items():
   file=f'wb_{code}.json';d=json.loads((RAW/file).read_text());detail=json.loads((RAW/f'wb_meta_{code}.json').read_text())
   if not isinstance(d,list) or len(d)!=2 or not isinstance(d[1],list) or d[0].get('pages',1)>1:raise ValueError(f'Invalid/paginated WDI {code}')
   if not isinstance(detail,list) or len(detail)<2:raise ValueError(f'Invalid metadata {code}')
   detail=detail[1][0];cat='access' if key.startswith(('access','cooking','business')) else 'context' if key.endswith('_rents') else 'fuels' if key=='energy_import_dependence' else 'energy'
   s=self.source(key,file,'World Bank · World Development Indicators',f'https://data.worldbank.org/indicator/{code}','World Bank terms; see indicator for original provider',publication_date=d[0].get('lastupdated'))
   self.define(key,label,unit,cat,s,detail.get('sourceNote',''),code=code,source_organization=detail.get('sourceOrganization'),provider_label=detail.get('name'),survey=key.startswith('business'))
   for r in d[1]:self.add(r['countryiso3code'],key,r['date'],r['value'])
 def ember(self):
  s=self.source('ember','ember_yearly.csv','Ember · Yearly Electricity Data','https://ember-energy.org/data/yearly-electricity-data/','CC BY 4.0',methodology_url=URLS['ember_method.pdf'])
  fuel_names={'Solar':'solar','Wind':'wind','Hydro':'hydro','Bioenergy':'bioenergy','Other renewables':'other_renewables','Nuclear':'nuclear','Coal':'coal','Gas':'gas','Other fossil':'other_fossil','Renewables':'renewables','Clean':'low_carbon','Fossil':'fossil','Total generation':'total'}
  for label,key in fuel_names.items():
   aggregate=label in ['Renewables','Clean','Fossil','Total generation']
   self.define('generation_'+key,label+' electricity generation','TWh','generation',s,'Annual generation. Other fossil is not a pure oil category; other renewables can include geothermal.',aggregate=aggregate,per_capita={'scale':1e9,'unit':'kWh/person'})
   self.define('share_'+key,label+' generation share','% of generation','generation',s,'Generation from this category / total domestic generation × 100.',aggregate=aggregate)
   self.define('generation_growth_'+key,label+' generation growth','% year on year','generation',s,'Ember reported year-on-year change. Undefined when the prior total is zero.',aggregate=aggregate)
  self.define('demand_total','Electricity demand','TWh','demand',s,'Ember electricity demand: domestic generation plus net imports. May differ from final metered consumption.',per_capita={'scale':1e9,'unit':'kWh/person'})
  self.define('demand_growth','Electricity demand growth','% year on year','demand',s,'Source-reported annual demand change; undefined for a zero prior-year denominator.')
  self.define('net_imports','Net electricity imports','TWh','grids',s,'Imports minus exports: positive means net importer, negative means net exporter.',per_capita={'scale':1e9,'unit':'kWh/person'})
  self.define('power_emissions','Power generation lifecycle emissions (estimate)','Mt CO₂e','emissions',s,'Ember lifecycle estimates include upstream methane, manufacturing and supply chains. These are not combustion-only national inventory emissions.',status='estimated by provider',per_capita={'scale':1e6,'unit':'t CO₂e/person'})
  self.define('power_intensity','Power generation lifecycle emissions intensity','g CO₂e/kWh','emissions',s,'Ember estimated lifecycle emissions divided by domestic electricity generation.',status='estimated by provider')
  for r in csv.DictReader((RAW/'ember_yearly.csv').open()):
   iso=r['ISO 3 code'];year=r['Year'];fuel=r['Electricity source'];f=fuel_names.get(fuel)
   if f:
    for prefix,col in [('generation_','Generation (TWh)'),('share_','Share of generation (%)'),('generation_growth_','Generation YoY change (%)')]:self.add(iso,prefix+f,year,r[col])
   if fuel=='Demand':
    self.add(iso,'demand_total',year,r['Generation (TWh)']);self.add(iso,'demand_growth',year,r['Generation YoY change (%)'])
   if fuel=='Net imports':self.add(iso,'net_imports',year,r['Generation (TWh)'])
   if fuel=='Total generation':
    self.add(iso,'power_emissions',year,r['Emissions (MtCO2e)']);self.add(iso,'power_intensity',year,r['Emissions intensity (gCO2e/kWh)'])
  s=self.source('ember_monthly','ember_monthly.csv','Ember · Monthly Electricity Data','https://ember-energy.org/data/monthly-electricity-data/','CC BY 4.0')
  monthly={'Demand':('monthly_demand','Monthly electricity demand','demand'),'Total generation':('monthly_generation','Monthly electricity generation','generation'),'Net imports':('monthly_net_imports','Monthly net electricity imports','grids')}
  for label,key in fuel_names.items():
   if key in ['solar','wind','hydro','coal','gas','nuclear']:monthly[label]=('monthly_'+key,'Monthly '+label.lower()+' generation','generation')
  for key,label,cat in monthly.values():self.define(key,label,'TWh/month',cat,s,'Published monthly total; not a completed annual observation. Latest country months can differ.',frequency='monthly')
  for r in csv.DictReader((RAW/'ember_monthly.csv').open()):
   period=r['Date'][:7];item=monthly.get(r['Electricity source'])
   if item and '2020-01'<=period<self.stamp[:7]:self.add(r['ISO 3 code'],item[0],period,r['Generation (TWh)'])
  self.define('demand_ytd','Electricity demand, year to date','TWh YTD','demand',s,'Sum January through the latest contiguous available month. Compare only identical year/month ranges.',frequency='ytd',status='derived from monthly data')
  self.define('demand_ytd_growth','Electricity demand YTD growth, matched months','% vs same months a year earlier','demand',s,'(Current Jan–m total / prior Jan–m total − 1) × 100; requires every month in both windows.',frequency='ytd',status='derived from monthly data')
  for iso in list(self.hist):
   hist=self.hist[iso].get('monthly_demand',{})
   for year in range(2021,datetime.now().year+1):
    months=sorted(int(p[5:7]) for p in hist if p.startswith(str(year)))
    if not months:continue
    last=max(months)
    if months!=list(range(1,last+1)):continue
    vals=[hist[f'{year}-{m:02}']['value'] for m in months];period=f'{year}-YTD-{last:02}'
    self.add(iso,'demand_ytd',period,sum(vals),note=f'January–{last:02}; {last} complete months')
    prior=[hist.get(f'{year-1}-{m:02}',{}).get('value') for m in months]
    if all(v is not None for v in prior) and sum(prior)>0:self.add(iso,'demand_ytd_growth',period,(sum(vals)/sum(prior)-1)*100)
 def owid(self):
  s=self.source('owid','owid_energy.csv','Our World in Data · Energy (Energy Institute and other original providers)','https://github.com/owid/energy-data','OWID CC BY; original provider conditions apply')
  book={r['column']:r for r in csv.DictReader((RAW/'owid_codebook.csv').open())}
  keys=['primary_energy_consumption','energy_per_capita','energy_per_gdp','electricity_share_energy','energy_cons_change_pct']
  for fuel in ['coal','gas','oil','fossil','nuclear','hydro','solar','wind','renewables','low_carbon','biofuel']:
   keys += [fuel+'_consumption',fuel+'_share_energy',fuel+'_production',fuel+'_cons_change_pct']
  keys=[k for k in keys if k in book]
  for k in keys:
   b=book[k];unit=b['unit'];cat='fuels' if k.endswith('_production') else 'energy'
   extra={'per_capita':{'scale':1e9,'unit':'kWh/person'}} if unit=='terawatt-hours' else {}
   self.define('energy_'+k,b['title'],unit,cat,s,b['description'],source_organization=b['source'],**extra)
  for r in csv.DictReader((RAW/'owid_energy.csv').open()):
   for k in keys:self.add(r.get('iso_code'),'energy_'+k,r['year'],r.get(k))
 def irena(self):
  s=self.source('irena','irena_0.json','IRENA · Renewable Capacity Statistics 2026','https://www.irena.org/Publications/2026/Mar/Renewable-capacity-statistics-2026','IRENA terms; credited data reproduction',publication_date='2026-04-17',retrieval_url=IRENA)
  techs={'0':'renewables','1':'solar','2':'solar_pv','3':'csp','4':'wind','5':'wind_onshore','6':'wind_offshore','7':'hydro_renewable','8':'hydro_mixed','9':'marine','10':'bioenergy','11':'solid_biofuels','12':'liquid_biofuels','13':'biogas','14':'renewable_waste','15':'geothermal','16':'nonrenewable','17':'fossil','18':'coal','19':'oil','20':'gas','21':'nuclear','22':'nonrenewable_waste','23':'other_nonrenewable','24':'other_nonrenewable_nes','25':'pumped_hydro'}
  cells=defaultdict(dict)
  for batch in range(4):
   d=json.loads((RAW/f'irena_{batch}.json').read_text());labels=d['dimension']['Technology']['category']['label'];years=d['dimension']['Year']['category']['label']
   for code,label in labels.items():
    key='capacity_'+techs[code];cat='storage' if code=='25' else 'capacity'
    self.define(key,label+' installed capacity (on-grid)','GW',cat,s,'Year-end maximum net grid-connected generating capacity, reported MW / 1000. Off-grid installations are excluded. On-grid capacity is used consistently because some technologies have no off-grid observation.',status='derived unit conversion; provider estimates may be included',per_capita={'scale':1e9,'unit':'W/person'},aggregate=code in ['0','1','4','10','16','17','23'])
    self.define(key+'_net_additions',label+' net on-grid capacity additions','GW/year',cat,s,'Current year-end capacity minus the previous year-end capacity. Includes retirements/revisions; not gross new construction.',status='derived')
   for combo,value,flag in jsonstat(d):cells[(combo['Country/area'],techs[combo['Technology']],years[combo['Year']])][combo['Grid connection']]=(value,flag)
  for (iso,tech,year),parts in cells.items():
   if tech in ['renewables','solar_pv','hydro_renewable','bioenergy'] and '1' in parts:
    offkey='capacity_offgrid_'+tech
    if offkey not in self.metadata:self.define(offkey,tech.replace('_',' ').title()+' capacity (off-grid)','GW','capacity',s,'IRENA separately reported off-grid maximum net generating capacity; MW / 1000. Add to the corresponding on-grid category only for an identical year. Do not add overlapping parent and child technology categories.',status='derived unit conversion')
    self.add(iso,offkey,year,parts['1'][0]/1000,flag=parts['1'][1])
   if '0' not in parts:continue
   self.add(iso,'capacity_'+tech,year,parts['0'][0]/1000,flag=parts['0'][1])
  for iso in list(self.hist):
   for tech in techs.values():
    key='capacity_'+tech;h=self.hist[iso].get(key,{})
    for p,r in list(h.items()):
     prev=h.get(str(int(p)-1))
     if prev:self.add(iso,key+'_net_additions',p,r['value']-prev['value'])
 def eia(self):
  s=self.source('eia','eia_intl.zip','U.S. EIA · International Energy Statistics','https://www.eia.gov/international/data/world','U.S. government data; public domain')
  with zipfile.ZipFile(RAW/'eia_intl.zip') as archive:
   for ln in archive.open('INTL.txt'):
    r=json.loads(ln)
    if r.get('f')!='A' or r.get('geography') not in self.countries:continue
    gs=r['geoset_id'];match=re.match(r'INTL\.(\d+)-(\d+)-([A-Z]+)\.A',gs)
    if not match:continue
    fuel,measure,unit=match.groups();cat=None
    if fuel in ['7','26','5','53','54','57'] and measure in ['1','2','3','4'] and unit in ['MT','BCM','TBPD']:cat='fuels'
    if fuel=='7' and measure=='6' and unit=='MST':cat='fuels'
    if fuel=='2' and measure in ['3','4','9'] and unit=='BKWH':cat='grids'
    if fuel=='2' and measure=='2' and unit=='BKWH':cat='demand'
    if fuel in ['35','32'] and measure=='12' and unit=='BKWH':cat='generation'
    if fuel=='4008' and measure=='8' and unit=='MMTCD':cat='emissions'
    if not cat:continue
    k='eia_'+fuel+'_'+measure+'_'+unit.lower()
    if k not in self.metadata:
     label=r['name'].rsplit(', ',2)[0];displayunit={'BKWH':'TWh','MMTCD':'Mt CO₂','BCM':'billion m³','MT':'thousand metric tonnes','MST':'million short tons','TBPD':'thousand barrels/day'}[unit]
     method='EIA published annual series. Geographic and fuel definitions follow the source; missing values are not zero.'
     if cat=='emissions':method='Energy-related CO₂ from consumption of fossil fuels. Combustion boundary; excludes land-use change and is not Ember lifecycle CO₂e.'
     extra={'per_capita':{'scale':1e6,'unit':'t CO₂/person'}} if unit=='MMTCD' else {'per_capita':{'scale':1e9,'unit':'kWh/person'}} if unit=='BKWH' else {}
     self.define(k,label,displayunit,cat,s,method,code=gs,**extra)
    for period,value in r['data']:self.add(r['geography'],k,period,value,updated=r.get('last_updated'))
 def end_use(self):
  s=self.source('end_use','end_use.csv','U.S. EIA · International end-use energy','https://www.eia.gov/todayinenergy/detail.php?id=67384','U.S. government data; public domain',codebook_url=URLS['end_use_codes.xlsx'])
  sectors={'RESIDENTIAL':'residential','COMMERCIAL':'commercial','INDUSTRIAL':'industrial','TRANSPORTATION':'transport'}
  keys={};sums=defaultdict(float);counts=defaultdict(int);unmapped=set()
  for sector in list(sectors.values())+['agriculture','total']:
   for prefix,unit,cat in [('enduse_','PJ','energy'),('enduse_electricity_','TWh','demand')]:
    k=prefix+sector;keys[k]=True
    self.define(k,sector.title()+' direct '+('electricity' if cat=='demand' else 'end-use energy'),unit,cat,s,'Sum of EIA direct-use fuel rows in the selected end-use sectors. Excludes transformation, separately classified heat and non-energy feedstocks. Industry includes agriculture; agriculture is also shown separately and must not be added to industry. Regional residual aggregates are never allocated to countries. 1 trillion Btu = 1.05505585262 PJ; electricity: PJ / 3.6 = TWh.',status='derived from provider sector/fuel rows',per_capita={'scale':1e9 if unit=='TWh' else 1e6,'unit':'kWh/person' if unit=='TWh' else 'GJ/person'})
  for fuel in ['electricity','gas','petroleum','coal','other']:
   k='enduse_fuel_'+fuel;self.define(k,'Direct end-use '+fuel,'PJ','energy',s,'Direct-use rows across residential, commercial, industrial and transport sectors. Excludes transformation, separately classified heat and non-energy feedstocks.',status='derived')
  for r in csv.DictReader((RAW/'end_use.csv').open()):
   if r['Direct or Tranformed']!='Direct' or r['IEOSECTOR'] not in sectors:continue
   iso=self.iso(r['EIAGEOENTITY'])
   if not iso:unmapped.add(r['EIAGEOENTITY']);continue
   v=numeric(r['Trills'])
   if v is None:continue
   year=r['year'];sector=sectors[r['IEOSECTOR']];pj=v*1.05505585262
   targets=['enduse_'+sector,'enduse_total']
   if r['EIASUBSECTOR']=='AGRICULTURE':targets.append('enduse_agriculture')
   fuel='electricity' if r['Root']=='Electricity' else 'gas' if r['Root']=='Natural Gas' else 'petroleum' if r['Root']=='Petroleum' else 'coal' if r['Root'] in ['Steam Coal','Met coal and derivatives'] else 'other'
   targets.append('enduse_fuel_'+fuel)
   for k in targets:sums[(iso,k,year)]+=pj;counts[(iso,k,year)]+=1
   if fuel=='electricity':
    for x in [sector,'total']+(['agriculture'] if r['EIASUBSECTOR']=='AGRICULTURE' else []):sums[(iso,'enduse_electricity_'+x,year)]+=pj/3.6;counts[(iso,'enduse_electricity_'+x,year)]+=1
  for (iso,k,year),value in sums.items():self.add(iso,k,year,value)
  self.issues.append({'source':'end_use','note':'Regional aggregates or unmatched country names excluded, not assigned to constituent countries','excluded_names':sorted(unmapped)})
  self.define('enduse_electrification','Electricity share of direct end-use energy','% of selected direct end use','energy',s,'Direct-use electricity PJ / direct-use energy PJ × 100; same countries, sectors and observation year. This is not a whole-economy total-final-consumption balance.',status='derived')
  for iso in list(self.hist):
   for p,r in self.hist[iso].get('enduse_total',{}).items():
    e=self.hist[iso].get('enduse_fuel_electricity',{}).get(p)
    if e and r['value']>0:self.add(iso,'enduse_electrification',p,e['value']/r['value']*100)
 def prices(self):
  for key,file,code,label in [('household_tariff','price.json','nrg_pc_204','Household electricity price'),('industry_tariff','price_industry.json','nrg_pc_205','Non-household electricity price')]:
   d=json.loads((RAW/file).read_text());s=self.source(key,file,'Eurostat · Electricity prices',f'https://ec.europa.eu/eurostat/databrowser/view/{code}/default/table','European Commission reuse policy',publication_date=d.get('updated'))
   household=key=='household_tariff';method='EUR/kWh. '+('Households consuming 2,500–4,999 kWh/year; all taxes and levies included.' if household else 'Non-household band 500–1,999 MWh/year; excludes VAT and other recoverable taxes and levies.')+' Semester averages. These two bands are not directly interchangeable and are not global wholesale prices.'
   self.define(key,label,'EUR/kWh','prices',s,method,frequency='semiannual',band='2,500–4,999 kWh/year' if household else '500–1,999 MWh/year',tax='All taxes included' if household else 'Excluding recoverable taxes')
   for combo,value,flag in jsonstat(d):
    iso2={'EL':'GR','UK':'GB'}.get(combo['geo'],combo['geo']);country=pycountry.countries.get(alpha_2=iso2);iso=country.alpha_3 if country else 'XKX' if iso2=='XK' else None
    self.add(iso,key,combo['time'],value,flag=flag)
  s=self.source('irena_costs','costs.pdf','IRENA · Renewable Power Generation Costs in 2025','https://www.irena.org/Publications/2026/Jul/Renewable-Power-Generation-Costs-in-2025','IRENA terms; credited data reproduction',publication_date='2026-07-02')
  self.benchmarks={'source_id':s,'year':2025,'currency':'2025 USD','scope':'Global weighted averages for newly commissioned projects. Reference benchmarks, not country tariffs or country-specific SWITCH assumptions. Executive summary Figure S1.','technologies':[{'technology':t,'lcoe_usd_mwh':l,'capex_usd_kw':c,'capacity_factor_pct':f} for t,l,c,f in [('Onshore wind',33,976,36),('Solar PV',44,667,16),('Offshore wind',78,2931,41),('Concentrated solar power',115,2418,22),('Hydropower',62,2079,43),('Geothermal',89,5997,85),('Bioenergy',86,3606,78)]],'battery':{'installed_usd_kwh':140,'duration_hours':4,'scope':'Utility-scale four-hour battery installed-cost estimate; global reference, not a country observation.'}}
 def solar(self):
  s=self.source('solar','solar.xlsx','World Bank / ESMAP / Solargis · Global PV Potential Study 2020','https://energydata.info/dataset/global-photovoltaic-power-potential-by-country','CC BY 4.0 per World Bank/ESMAP dataset',publication_date='2020-05-05')
  desc='Long-term modeled national resource estimate from the 2020 study, not a 2020 or 2026 weather observation. Underlying climatology periods vary spatially; consult the source. PVOUT Level 1 excludes land with identified physical obstacles to utility-scale PV.'
  cols={'K':('solar_ghi','Average global horizontal irradiation','kWh/m²/day'),'L':('solar_pv_yield','Average practical PV yield (Level 1)','kWh/kWp/day'),'N':('solar_seasonality','PV seasonality ratio','highest / lowest monthly mean')}
  for k,label,unit in cols.values():self.define(k,label,unit,'resources',s,desc,frequency='climatology',status='modeled long-term resource')
  for r in list(xlsx_rows(RAW/'solar.xlsx'))[2:]:
   for col,(k,_,_) in cols.items():self.add(r.get('A'),k,'2020-study',r.get(col),note='Long-term average; study published 2020')
  for i in range(1,13):self.define('solar_month_'+str(i),'PV yield · '+datetime(2020,i,1).strftime('%B'),'kWh/kWp/day','resources',s,desc,frequency='climatology',status='modeled long-term resource')
  for r in list(xlsx_rows(RAW/'solar.xlsx',2))[2:]:
   for i in range(1,13):self.add(r.get('A'),'solar_month_'+str(i),'2020-study',r.get(chr(ord('E')+i)))
  for col,k,label,unit in [('F','solar_ghi_p10','GHI spatial 10th percentile','kWh/m²/day'),('K','solar_ghi_p90','GHI spatial 90th percentile','kWh/m²/day'),('N','solar_yield_p10','PV yield spatial 10th percentile','kWh/kWp/day'),('S','solar_yield_p90','PV yield spatial 90th percentile','kWh/kWp/day')]:
   self.define(k,label,unit,'resources',s,desc+' These are spatial percentiles, not forecast probabilities.',frequency='climatology',status='modeled long-term resource')
   for r in list(xlsx_rows(RAW/'solar.xlsx',3))[2:]:self.add(r.get('A'),k,'2020-study',r.get(col))
 def policy(self):
  s=self.source('targets','netzero_targets.csv','Net Zero Tracker · processed by Our World in Data','https://ourworldindata.org/grapher/net-zero-targets','OWID CC BY; Net Zero Tracker original terms',publication_date='2026-07-13')
  method='Tracker status and target date as displayed by OWID. The source includes other emissions-reduction targets, not strictly net-zero. Gas scope, target percentage, conditionality and sector coverage are not supplied in this extract; verify the underlying policy before modeling. Target year is not the observation year.'
  self.define('emissions_target_status','Emissions target status (tracker)','status','policy',s,method,value_type='text',frequency='snapshot')
  self.define('emissions_target_year','Emissions target year (tracker)','target year','policy',s,method,frequency='snapshot',map_eligible=False)
  for r in csv.DictReader((RAW/'netzero_targets.csv').open()):
   value=r[list(r)[-1]];target=re.search(r'\((\d{4})\)$',value)
   self.add(r['Code'],'emissions_target_status','2026-07-13',value)
   if target:self.add(r['Code'],'emissions_target_year','2026-07-13',int(target[1]))
  file='carbon-tax-instruments.csv';meta=json.loads((RAW/'carbon-tax-instruments.metadata.json').read_text());s=self.source('carbon_tax',file,'Resources for the Future · processed by Our World in Data','https://ourworldindata.org/grapher/carbon-tax-instruments','OWID CC BY; original RFF dataset terms',publication_date='2026-06-10')
  self.define('carbon_tax_status','Carbon tax jurisdiction coverage','status','policy',s,'Whether at least one sector/fuel has a national or only subnational carbon tax. Coverage of one sector does not mean the entire economy is taxed.',value_type='text')
  for r in csv.DictReader((RAW/file).open()):self.add(r['Code'],'carbon_tax_status',r['Year'],r[list(r)[-1]])
 def infrastructure(self):
  s=self.source('gem','gem_arcgis.json','Global Energy Monitor · public ArcGIS inventory','https://globalenergymonitor.org/projects/global-integrated-power-tracker/','CC BY 4.0; Global Energy Monitor, with Esri-hosted public distribution',publication_date='2026-02',inventory_vintage='February 2026',retrieval_url=GEM)
  fields=['operating','construction','announced','pre-construction','retired','mothballed','shelved','cancelled'];sums=defaultdict(float);unmatched=set();seen=set()
  count=json.loads((RAW/'gem_count.json').read_text())['count']
  for offset in range(0,count,2000):
   rows=json.loads((RAW/f'gem_page_{offset:06}.json').read_text())['features']
   for r in rows:
    a=r['attributes'];oid=a['OBJECTID']
    if oid in seen:raise ValueError('Duplicate GEM page object ID')
    seen.add(oid);country=self.iso(a['Country_area'] or '');allocations=[]
    c1=self.iso(a.get('Country_area_1__hydropower_only') or '');c2=self.iso(a.get('Country_area_2__hydropower_only') or '')
    if c1 and c2 and c1!=c2:allocations=[(c1,a.get('Country_area_1_Capacity__MW___h')),(c2,a.get('Country_area_2_Capacity__MW___h'))]
    elif country:allocations=[(country,a['Capacity__MW_'])]
    else:unmatched.add(a['Country_area']);continue
    for iso,mw in allocations:
     status=(a['Status'] or 'unknown').lower();asset={'id':str(oid),'unit_id':a['GEM_unit_phase_ID'],'name':a['Plant___Project_name'],'phase':a['Unit___Phase_name'],'type':a['Type'],'technology':a['Technology'],'fuel':a['Fuel'],'capacity_mw':numeric(mw),'status':status,'start_year':a['Start_year'],'retired_year':a['Retired_year'],'lat':numeric(a['Latitude']),'lon':numeric(a['Longitude']),'location_accuracy':a['Location_accuracy'],'url':a['GEM_Wiki_URL'],'shared':len(allocations)>1}
     self.assets[iso].append(asset)
     if mw is not None:sums[(iso,status)]+=float(mw)/1000
  assert len(seen)==count,'Incomplete global project inventory'
  for status in fields:
   k='tracked_'+status.replace('-','_');self.define(k,'Tracked '+status+' project capacity','GW','capacity',s,'Sum of capacity allocated to this country in GEM inventory records of this status. Partial inventory with technology-specific size thresholds and coverage rules; not a national installed-capacity total. Shared hydro uses country allocations when supplied. Does not include a complete battery inventory.',frequency='snapshot',status='derived inventory subtotal')
   for (iso,st),v in sums.items():
    if st==status:self.add(iso,k,'2026-02',v)
  self.issues.append({'source':'gem','note':'Inventory records with unmatched/ambiguous country labels are excluded; cross-border hydro uses published allocations','excluded_names':sorted(unmatched),'source_records':count,'country_allocated_records':sum(len(v) for v in self.assets.values())})
 def storage_inventory(self):
  s=self.source('doe_storage','storage.json','DOE / NTESS Sandia · Global Energy Storage Database','https://sandia.gov/ess-ssl/gesdb/public/projects.html','Underlying DOE data public domain; credit NTESS. Dataset is provided as-is and remains under validation.',publication_date='2022-01-12',inventory_vintage='January 2022; historical inventory, not a current national total')
  method='Historical January 2022 DOE/NTESS inventory. Operational electro-chemical battery and chemical storage projects only. Not a complete national total; project data are not necessarily validated. Positive reported ratings are aggregated; missing or nonpositive ratings do not establish zero installed storage. Power and energy have different reporting coverage.'
  self.define('tracked_battery_power','Tracked operational battery/chemical storage power (2022)','MW','storage',s,method,frequency='snapshot',status='derived historical inventory subtotal')
  self.define('tracked_battery_energy','Tracked operational battery/chemical storage energy (2022)','MWh','storage',s,method,frequency='snapshot',status='derived historical inventory subtotal')
  self.define('tracked_battery_duration','Duration of storage projects with both ratings (2022)','hours','storage',s,method+' Sum MWh / sum MW using only projects that report both positive ratings; equivalent power-weighted duration.',frequency='snapshot',status='derived historical inventory subset')
  sums=defaultdict(lambda:defaultdict(float));counts=defaultdict(lambda:defaultdict(int));unmatched=set();asset_count=0
  for r in json.loads((RAW/'storage.json').read_text()):
   iso=self.iso(r['Country'] or '')
   if not iso:unmatched.add(r['Country']);continue
   techs={sub.get('Storage Device',{}).get('Technology Broad Category') for sub in r.get('Subsystems',[])}
   if techs!={'Electro-chemical battery and chemical storage'}:continue
   power=numeric(r['Rated Power (kW)']);energy=numeric(r['Storage Capacity (kWh)'])
   mw=power/1000 if power and power>0 else None;mwh=energy/1000 if energy and energy>0 else None
   st={'Operational':'operating','Under Construction':'construction','De-Commissioned':'retired','Announced/Never Built':'cancelled'}.get(r['Status'],(r['Status'] or 'unknown').lower())
   mid=', '.join(sorted({sub.get('Storage Device',{}).get('Technology Mid-Type') or 'Unspecified' for sub in r.get('Subsystems',[])}))
   self.assets[iso].append({'id':'doe-'+str(r['ID']),'unit_id':str(r['ID']),'name':r['Project/Plant Name'],'phase':None,'type':'Battery / chemical storage','technology':mid,'fuel':None,'capacity_mw':mw,'energy_mwh':mwh,'duration_hours':mwh/mw if mw and mwh else None,'status':st,'start_year':None,'retired_year':None,'lat':numeric(r['Latitude']),'lon':numeric(r['Longitude']),'location_accuracy':'Source coordinates; validation '+str(r['Project Data Validated?']),'url':'https://sandia.gov/ess-ssl/gesdb/public/projects.html','shared':False,'source_id':'doe_storage','vintage':'2022-01-12'})
   asset_count+=1
   if st!='operating':continue
   for key,value in [('power',mw),('energy',mwh)]:
    if value is not None:sums[iso][key]+=value;counts[iso][key]+=1
   if mw and mwh:sums[iso]['paired_power']+=mw;sums[iso]['paired_energy']+=mwh
  for iso,totals in sums.items():
   for field in ['power','energy']:
    if counts[iso][field]:self.add(iso,'tracked_battery_'+field,'2022-01-12',totals[field],note=str(counts[iso][field])+' operational projects reporting a positive rating; historical inventory')
   if totals['paired_power']>0:self.add(iso,'tracked_battery_duration','2022-01-12',totals['paired_energy']/totals['paired_power'])
  self.issues.append({'source':'doe_storage','note':'Historical 2022 battery/chemical project subset. No personal contact details or project descriptions are redistributed. Zero/unreported ratings excluded from aggregates. Mixed technology projects excluded.','included_projects':asset_count,'excluded_names':sorted(str(x) for x in unmatched)})
 def derived(self):
  self.define('people_without_electricity','People without electricity access','people','access','worldbank_context','Population × (1 − electricity access / 100), requiring both observations in the same calendar year. Estimates inherit uncertainty from both World Bank series.',status='derived')
  for iso in list(self.hist):
   for period,a in self.hist[iso].get('electricity_access',{}).items():
    p=self.hist[iso].get('population',{}).get(period)
    if p:self.add(iso,'people_without_electricity',period,p['value']*(1-a['value']/100))
 def gaps(self):
  """Explicit requested fields whose comparable global observations aren't connected."""
  specs=[('business_outages','Power outages in firms in a typical month','outages/month','access','The legacy World Bank monthly outage-count series is archived; current survey exposure and losses are available separately.'),('peak_demand','Peak electricity demand','MW','demand','Hourly system-operator peaks require a harmonized national source and year.'),('battery_power','Battery storage power','MW','storage','No redistributable, harmonized global national battery-power series is connected.'),('battery_energy','Battery storage energy','MWh','storage','Energy capacity cannot be inferred from battery power without reported duration.'),('battery_duration','Battery duration','hours','storage','Requires power and energy capacities with identical scope and date.'),('curtailment','Renewable curtailment','% of available generation','storage','TSO definitions and technology coverage vary; no harmonized global source connected.'),('demand_response','Demand-response capacity','MW','storage','No harmonized global accredited demand-response dataset is connected.'),('interconnector_capacity','Cross-border interconnector capacity','MW','grids','Requires individual circuit ratings, direction, status and commissioning dates; national trade is not capacity.'),('trade_partners','Electricity trading partners','country list','grids','Bilateral trade requires a separate harmonized partner-by-partner dataset.'),('wholesale_price','Wholesale electricity price','currency/MWh','prices','Market hubs, settlement intervals, currencies and tax treatments need an explicit comparable source.'),('fuel_price','Delivered generator fuel price','currency/GJ','prices','Global commodity benchmarks are not country-delivered generator fuel prices.'),('subsidy','Energy subsidies','currency/year','prices','Budget transfers and price-gap estimates need distinct definitions and coverage.'),('saidi','Utility SAIDI','hours/customer/year','access','Business outage surveys are not utility SAIDI; no consistent global utility series connected.'),('saifi','Utility SAIFI','interruptions/customer/year','access','Business outage surveys are not utility SAIFI; no consistent global utility series connected.'),('generator_reliance','Backup generator reliance','% of electricity','access','A consistent global household/firm generation-share series is not connected.'),('wind_speed','Wind speed at 100 m','m/s','resources','Country area-weighted wind data at the specified height is not connected; use the linked Global Wind Atlas for site assessment.'),('wind_density','Wind power density at 100 m','W/m²','resources','Do not substitute a capital-city sample for a national spatial statistic.'),('oil_reserves','Proved oil reserves','billion barrels','fuels','No current comparable proved-reserve series in the connected EIA bulk extract.'),('gas_reserves','Proved gas reserves','billion m³','fuels','No current comparable proved-reserve series in the connected EIA bulk extract.'),('lng_capacity','LNG terminal capacity','million tonnes/year','fuels','An LNG facility inventory with terminal status is not connected.'),('renewable_target','Renewable energy target','% and target year','policy','Capacity, generation and final-energy targets must retain their exact policy basis; no harmonized extract connected.'),('coal_phaseout','Coal phase-out commitment','year and status','policy','Requires validated policy scope, exceptions and legal status.'),('carbon_price','Carbon price and emissions coverage','currency/t CO₂e and %','policy','Available extract has inconsistent currency-base metadata; withheld until units and coverage are verified.'),('ets_status','Emissions trading system coverage','status','policy','A verified harmonized national/subnational ETS source is not connected.')]
  self.sources['coverage_notes']={'name':'Coverage audit','source_url':'https://github.com/alajwadha/SWITCH_RENEW/blob/main/docs/ATLAS_DATA.md','retrieved_at':self.stamp,'license':'Project documentation'}
  for k,label,unit,cat,note in specs:self.define(k,label,unit,cat,'coverage_notes',note,status='unavailable',missing_reason=note,map_eligible=False)
 def publish(self):
  for key,meta in self.metadata.items():
   obs=[r for c in self.hist.values() for r in c.get(key,{}).values()]
   meta['coverage']=sum(bool(c.get(key)) for c in self.hist.values())
   meta['observation_count']=len(obs);meta['periods']=sorted({o['period'] for o in obs})
   meta.setdefault('map_eligible',meta['value_type']=='number')
   meta.setdefault('missing_reason','No published observation for this country and indicator in the connected source. Coverage and reporting periods vary; missing is not zero.')
  # Hash content, not wall-clock build time, for stable asset references and safe refreshes.
  digest=hashlib.sha256(json.dumps([self.hist,{k:v for k,v in self.sources.items() if k!='coverage_notes'}],sort_keys=True).encode()).hexdigest()[:12]
  public=ROOT/'public';folder=public/'atlas'/digest;folder.mkdir(parents=True,exist_ok=True)
  histories=defaultdict(dict);assets=defaultdict(dict);countryrows=[]
  for iso,c in self.countries.items():
   h={k:sorted(v.values(),key=lambda r:r['period']) for k,v in self.hist[iso].items() if v}
   histories[iso[0]][iso]=h;assets[iso[0]][iso]=self.assets[iso]
   indicators={}
   for key in self.metadata:
    series=h.get(key,[]);latest=series[-1] if series else {'value':None,'year':None,'period':None}
    indicators[key]={**latest,'history':[latest] if series else []}
   countryrows.append({**c,'indicators':indicators,'coverage':{cat:sum(indicators[k]['value'] is not None for k,m in self.metadata.items() if m['category']==cat) for cat,_,_ in CATEGORIES}})
  def write(path,obj):
   temp=path.with_suffix('.tmp');raw=json.dumps(obj,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode();temp.write_bytes(gzip.compress(raw,compresslevel=9,mtime=0) if path.suffix=='.gz' else raw);temp.replace(path)
  hf={};af={}
  provenance_files=[]
  for path in sorted(RAW.glob('*.provenance')):
   # Only source files declared by the reproducible downloader have sidecars.
   record=json.loads(path.read_text());provenance_files.append({'file':path.name.removesuffix('.provenance'),**record})
  write(folder/'provenance.json.gz',{'files':provenance_files,'note':'Hashes refer to exact provider responses, held in ignored workspace/atlas_raw/expanded. Downloads are not part of Git. The transformed dataset is reproducible from these dated sources.'})
  for letter in sorted(histories):
   write(folder/f'history-{letter}.json.gz',histories[letter]);hf[letter]=f'/atlas/{digest}/history-{letter}.json.gz'
   write(folder/f'assets-{letter}.json.gz',assets[letter]);af[letter]=f'/atlas/{digest}/assets-{letter}.json.gz'
  payload={**{k:v for k,v in self.base.items() if k not in ['countries','metadata','errors','history_files','asset_files','sources','categories','benchmarks','audit']},'schema_version':2,'retrieved_at':self.stamp,'latest_completed_year':self.completed,'history_start':2010,'metadata':self.metadata,'countries':countryrows,'sources':self.sources,'categories':[{'id':k,'label':l,'description':d} for k,l,d in CATEGORIES],'history_files':hf,'asset_files':af,'provenance_file':f'/atlas/{digest}/provenance.json.gz','benchmarks':self.benchmarks,'audit':self.issues,'errors':[]}
  write(folder/'index.json.gz',payload)
  write(public/'atlas.json',{'schema_version':2,'index_file':f'/atlas/{digest}/index.json.gz','countries':len(countryrows),'retrieved_at':self.stamp,'note':'Compressed all-country index; source data, metadata, histories and inventories are bundled locally.'})
  # Generated snapshot cleanup occurs only after complete publication. Refresh while the local app is stopped.
  for old in (public/'atlas').iterdir():
   if old.is_dir() and old.name!=digest:shutil.rmtree(old)
  stats={'countries':len(countryrows),'indicators':len(self.metadata),'populated_indicators':sum(m['coverage']>0 for m in self.metadata.values()),'latest_values':sum(sum(v['value'] is not None for v in c['indicators'].values()) for c in countryrows),'observations':sum(m['observation_count'] for m in self.metadata.values()),'assets':sum(len(v) for v in self.assets.values()),'sections':[{'id':cat,'indicators':sum(m['category']==cat for m in self.metadata.values()),'countries':sum(c['coverage'][cat]>0 for c in countryrows)} for cat,_,_ in CATEGORIES],'audit':self.issues}
  write(ROOT/'docs/atlas-coverage.json',stats);print(json.dumps(stats,indent=2),flush=True)
  return payload

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--refresh',action='store_true');parser.add_argument('--offline',action='store_true');args=parser.parse_args()
 if args.refresh and args.offline:parser.error('--refresh and --offline are mutually exclusive')
 if not args.offline:acquire(refresh=args.refresh)
 base=None
 if args.refresh:
  from country_context import main as refresh_context
  base=refresh_context(output_dir=RAW/'country_context')
 b=Builder(base=base)
 for method in ['base_data','worldbank','ember','owid','irena','eia','end_use','prices','solar','policy','infrastructure','storage_inventory','derived','gaps']:
  getattr(b,method)();print('Built',method,flush=True)
 b.publish()

if __name__=='__main__':main()
