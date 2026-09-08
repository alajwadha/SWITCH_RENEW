"""Public, redistributable global atlas sources. No accounts or model input mutation."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'workspace' / 'atlas_raw' / 'expanded'
IRENA = 'https://pxweb.irena.org/api/v1/en/IRENASTAT/Power%20Capacity%20and%20Generation/' + urllib.parse.quote('Country_ELECCAP_2026_H1_v-PX 1.px')
GEM = 'https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/Global_Integrated_Power_v1/FeatureServer/0'
URLS = {
 'storage.json': 'https://sandia.gov/ess-ssl/gesdb/public/data/New_GESDB_1-12-2022.json',
 'owid_energy.csv': 'https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv',
 'owid_codebook.csv': 'https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-codebook.csv',
 'ember_yearly.csv': 'https://files.ember-energy.org/public-downloads/generation/outputs/release_generation_yearly_global.csv',
 'ember_monthly.csv': 'https://files.ember-energy.org/public-downloads/generation/outputs/release_generation_monthly_global.csv',
 'ember_method.pdf': 'https://files.ember-energy.org/public-downloads/ember_electricity_data_methodology.pdf',
 'irena_dims.json': IRENA,
 'eia_intl.zip': 'https://www.eia.gov/opendata/bulk/INTL.zip',
 'end_use.csv': 'https://www.eia.gov/international/content/end-use.csv',
 'end_use_codes.xlsx': 'https://www.eia.gov/international/content/End-useCodes.xlsx',
 'solar.xlsx': 'https://datacatalogfiles.worldbank.org/ddh-published/0038379/1/DR0046831/solargis_pvpotential_countryranking_2020_data.xlsx',
 'netzero_targets.csv': 'https://ourworldindata.org/grapher/net-zero-targets.csv',
 'netzero_targets_meta.json': 'https://ourworldindata.org/grapher/net-zero-targets.metadata.json',
 'carbon-tax-instruments.csv': 'https://ourworldindata.org/grapher/carbon-tax-instruments.csv',
 'carbon-tax-instruments.metadata.json': 'https://ourworldindata.org/grapher/carbon-tax-instruments.metadata.json',
 'price.json': 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_pc_204?lang=en&unit=KWH&currency=EUR&tax=I_TAX&nrg_cons=KWH2500-4999&sinceTimePeriod=2023-S1',
 'price_industry.json': 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_pc_205?lang=en&unit=KWH&currency=EUR&tax=X_VAT&nrg_cons=MWH500-1999&sinceTimePeriod=2023-S1',
 'costs.pdf': 'https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2026/Jul/IRENA_TEC_RPGC_2025_Executive_summary_2026.pdf',
 'gem_arcgis.json': 'https://www.arcgis.com/sharing/rest/content/items/d48c087b6d8141599d4923e70e610fca?f=json',
 'gem_layer.json': GEM + '?f=json',
}
WB = {
 'access_rural': ('EG.ELC.ACCS.RU.ZS', 'Rural electricity access', '% of rural population'),
 'access_urban': ('EG.ELC.ACCS.UR.ZS', 'Urban electricity access', '% of urban population'),
 'cooking_rural': ('EG.CFT.ACCS.RU.ZS', 'Rural clean cooking access', '% of rural population'),
 'cooking_urban': ('EG.CFT.ACCS.UR.ZS', 'Urban clean cooking access', '% of urban population'),
 'renewable_final_share': ('EG.FEC.RNEW.ZS', 'Renewables in total final energy consumption', '% of final energy'),
 'energy_use_oil_equivalent': ('EG.USE.PCAP.KG.OE', 'Energy use per person', 'kg oil equivalent/person'),
 'energy_import_dependence': ('EG.IMP.CONS.ZS', 'Net energy imports', '% of energy use'),
 'business_outage_exposure': ('IC.ELC.OUTG.ZS', 'Firms experiencing electrical outages', '% of firms'),
 'business_outage_loss': ('IC.FRM.OUTG.ZS', 'Sales lost to electrical outages (affected firms)', '% of sales for affected firms'),
 'oil_rents': ('NY.GDP.PETR.RT.ZS', 'Oil rents', '% of GDP'),
 'gas_rents': ('NY.GDP.NGAS.RT.ZS', 'Natural gas rents', '% of GDP'),
 'coal_rents': ('NY.GDP.COAL.RT.ZS', 'Coal rents', '% of GDP'),
}

def download(name, url, body=None, refresh=False):
 RAW.mkdir(parents=True, exist_ok=True)
 path = RAW / name
 if path.exists() and not refresh:
  provenance=path.with_suffix(path.suffix+'.provenance')
  if not provenance.exists():
   provenance.write_text(json.dumps({'url':url,'request':body,'retrieved_at':datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))
  return path
 request = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
  headers={'User-Agent': 'SWITCH-Workbench/0.2 research atlas', 'Content-Type': 'application/json'})
 with urllib.request.urlopen(request, timeout=120) as response:
  data = response.read()
 if name.endswith('.json'):
  parsed = json.loads(data)
  if isinstance(parsed, dict) and ('error' in parsed or parsed.get('success') is False):
   raise ValueError(f'{name}: source rejected request')
 temp = path.with_suffix(path.suffix + '.tmp'); temp.write_bytes(data); temp.replace(path)
 path.with_suffix(path.suffix + '.provenance').write_text(json.dumps({'url':url,'request':body,'retrieved_at':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(data).hexdigest()}))
 return path

def acquire(refresh=False):
 """Fail before publishing on a missing source; preserve previously built snapshot."""
 jobs = dict(URLS)
 year = datetime.now().year - 1
 for _,(code,_,_) in WB.items():
  jobs[f'wb_{code}.json'] = f'https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&date=2010:{year}&per_page=20000'
  jobs[f'wb_meta_{code}.json'] = f'https://api.worldbank.org/v2/indicator/{code}?format=json'
 with ThreadPoolExecutor(max_workers=5) as pool:
  futures = {pool.submit(download,k,u,refresh=refresh):k for k,u in jobs.items()}
  for f in as_completed(futures):
   f.result(); print('Source ready:',futures[f],flush=True)
 dims = json.loads((RAW/'irena_dims.json').read_text())
 for batch in range(4):
  query=[]
  for v in dims['variables']:
   values=v['values']
   if v['code']=='Technology':values=values[batch*7:(batch+1)*7]
   if v['code']=='Year':values=[code for code,label in zip(v['values'],v['valueTexts']) if 2010<=int(label)<=year]
   query.append({'code':v['code'],'selection':{'filter':'item','values':values}})
  download(f'irena_{batch}.json',IRENA,{'query':query,'response':{'format':'json-stat2'}},refresh)
 def gem_query(q):return GEM+'/query?'+urllib.parse.urlencode(q)
 count=json.loads(download('gem_count.json',gem_query({'where':'1=1','returnCountOnly':'true','f':'json'}),refresh=refresh).read_text())['count']
 fields='OBJECTID,Type,Country_area,Plant___Project_name,Unit___Phase_name,Capacity__MW_,Status,Start_year,Retired_year,Technology,Fuel,Latitude,Longitude,Location_accuracy,GEM_unit_phase_ID,GEM_Wiki_URL,Country_area_1__hydropower_only,Country_area_2__hydropower_only,Country_area_1_Capacity__MW___h,Country_area_2_Capacity__MW___h'
 def page(offset):
  q={'where':'1=1','outFields':fields,'returnGeometry':'false','orderByFields':'OBJECTID','resultOffset':offset,'resultRecordCount':2000,'f':'json'}
  p=download(f'gem_page_{offset:06}.json',gem_query(q),refresh=refresh)
  assert len(json.loads(p.read_text())['features'])==min(2000,count-offset),'Incomplete GEM page'
 with ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(page,range(0,count,2000)))
 return count
