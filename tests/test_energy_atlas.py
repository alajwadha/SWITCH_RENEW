"""Cross-source invariants for the published snapshot; tests do not need the network."""
import gzip
import importlib.util
import json
from pathlib import Path
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from refresh_energy_atlas import jsonstat, numeric

@pytest.fixture(scope='module')
def atlas():
 manifest=json.loads((ROOT/'public/atlas.json').read_text())
 return read_shard(manifest['index_file']) if manifest.get('index_file') else manifest

def read_shard(path):
 raw=(ROOT/'public'/path.lstrip('/')).read_bytes()
 return json.loads(gzip.decompress(raw) if path.endswith('.gz') else raw)

def test_all_profiles_and_periods_have_complete_provenance(atlas):
 assert len(atlas['countries'])==251
 assert len(atlas['categories'])==13 # twelve energy sections plus retained context
 assert len(atlas['metadata'])>=250
 seen=0
 for letter,path in atlas['history_files'].items():
  hist=read_shard(path)
  for c in (c for c in atlas['countries'] if c['iso3'][0]==letter):
   assert set(c['indicators'])==set(atlas['metadata'])
   for key,obs in c['indicators'].items():
    m=atlas['metadata'][key];assert m['unit'] and m['source_url'].startswith('https://') and m['retrieved_at']
    if obs['value'] is None:
     assert obs['period'] is None and obs['year'] is None
     assert not hist[c['iso3']].get(key)
     continue
    values=hist[c['iso3']][key];seen+=len(values)
    assert obs['period']==values[-1]['period']
    assert obs['value']==values[-1]['value']
    assert len({r['period'] for r in values})==len(values)
    for r in values:
     if m['frequency']=='annual':assert 2010<=r['year']<=atlas['latest_completed_year']
     if m['value_type']=='number':assert numeric(r['value']) is not None
 assert seen>450000

def test_generation_balance_and_missing_are_not_zero(atlas):
 for c in atlas['countries']:
  h=read_shard(atlas['history_files'][c['iso3'][0]])[c['iso3']]
  total={r['period']:r['value'] for r in h.get('generation_total',[])}
  imports={r['period']:r['value'] for r in h.get('net_imports',[])}
  for o in h.get('demand_total',[]):
   if o['period'] in total and o['period'] in imports:
    assert o['value']==pytest.approx(total[o['period']]+imports[o['period']],abs=.025)
 # A missing country-specific tariff is never filled with a European average.
 kenya=next(c for c in atlas['countries'] if c['iso3']=='KEN')
 assert kenya['indicators']['household_tariff']['value'] is None

def test_survey_tariffs_resources_and_emissions_keep_distinct_boundaries(atlas):
 m=atlas['metadata']
 assert m['business_outage_exposure']['code']=='IC.ELC.OUTG.ZS'
 assert m['business_outage_loss']['code']=='IC.FRM.OUTG.ZS'
 assert 'affected firms' in m['business_outage_loss']['unit']
 assert m['household_tariff']['frequency']=='semiannual'
 assert '2,500' in m['household_tariff']['methodology']
 assert 'recoverable' in m['industry_tariff']['methodology']
 assert m['solar_ghi']['frequency']=='climatology'
 assert 'lifecycle' in m['power_emissions']['methodology']
 assert 'Combustion' in m['eia_4008_8_mmtcd']['methodology']
 assert 'not strictly net-zero' in m['emissions_target_status']['methodology']


def test_irena_grid_scope_and_physical_scale(atlas):
 china=next(c for c in atlas['countries'] if c['iso3']=='CHN')
 assert 'grid-connected' in atlas['metadata']['capacity_pumped_hydro']['methodology']
 assert china['indicators']['capacity_pumped_hydro']['value']>40
 assert china['indicators']['capacity_solar_pv']['value']>1000
 assert atlas['metadata']['capacity_pumped_hydro']['coverage']>=35


def test_same_year_population_derivation(atlas):
 h=read_shard(atlas['history_files']['K'])['KEN'];p={o['period']:o['value'] for o in h['population']};a={o['period']:o['value'] for o in h['electricity_access']}
 for r in h['people_without_electricity']:assert r['value']==pytest.approx(p[r['period']]*(1-a[r['period']]/100),abs=.01)


def test_ytd_uses_contiguous_and_matching_months(atlas):
 for path in atlas['history_files'].values():
  for h in read_shard(path).values():
   months={r['period']:r['value'] for r in h.get('monthly_demand',[])}
   for o in h.get('demand_ytd_growth',[]):
    year=int(o['period'][:4]);last=int(o['period'][-2:]);current=sum(months[f'{year}-{m:02}'] for m in range(1,last+1));prior=sum(months[f'{year-1}-{m:02}'] for m in range(1,last+1))
    assert o['value']==pytest.approx((current/prior-1)*100,abs=1e-7)


def test_inventory_is_paginated_complete_and_cross_border_allocated(atlas):
 count=0;shared=0
 for path in atlas['asset_files'].values():
  for iso,assets in read_shard(path).items():
   assets=[a for a in assets if a.get('source_id','gem')=='gem']
   assert len({a['id'] for a in assets})==len(assets)
   count+=len(assets);shared+=sum(a['shared'] for a in assets)
   for a in assets:
    assert a['status'] and a['type']
    assert a['capacity_mw'] is None or a['capacity_mw']>=0
 audit=next(a for a in atlas['audit'] if a['source']=='gem')
 assert count==audit['country_allocated_records']
 assert count>=audit['source_records']-10
 assert shared>0 and not audit['excluded_names']


def test_sparse_jsonstat_keeps_dimension_order_flags_and_zero():
 d={'id':['geo','year'],'size':[2,2],'dimension':{'geo':{'category':{'index':{'B':1,'A':0}}},'year':{'category':{'index':{'2024':0,'2025':1}}}},'value':{'0':0,'3':7},'status':{'3':'e'}}
 assert list(jsonstat(d))==[({'geo':'A','year':'2024'},0,None),({'geo':'B','year':'2025'},7,'e')]
