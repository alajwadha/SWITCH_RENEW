"""Validate review structure and selected transparent arithmetic, not all source truth."""
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse, unquote
from difflib import SequenceMatcher

ROOT=Path(__file__).resolve().parents[1]
def main():
    rs=json.loads((ROOT/'publications.json').read_text(encoding='utf-8'))
    schema=json.loads((ROOT/'record_schema.json').read_text(encoding='utf-8'))
    errors=[]; checks=[]
    def check(name,ok,details=None):
        checks.append({'check':name,'passed':bool(ok),'details':details})
        if not ok: errors.append(name)
    check('unique_record_ids',len({r['id'] for r in rs})==len(rs))
    dois=[r['doi'].lower() for r in rs if r['doi']]
    check('unique_primary_dois',len(set(dois))==len(dois))
    substantive=['method','data_sources','key_findings','limitations','project_relevance','quality_appraisal','data_code_availability']
    wordcounts={}
    for r in rs:
        rid=r['id']
        check(rid+':required_fields',all(k in r for k in schema['required_fields']))
        check(rid+':theme',r['primary_theme'] in schema['primary_theme_values'])
        check(rid+':inspection_depth',r['inspection_depth'] in schema['inspection_depth_values'])
        check(rid+':authors_and_tags',isinstance(r['authors'],list) and bool(r['authors']) and isinstance(r['themes'],list))
        check(rid+':publication_year',r['year'] is None or 1800<=r['year']<=2026)
        check(rid+':retrieval_date',r['retrieved_date']=='2026-09-28')
        check(rid+':primary_url',urlparse(r['primary_url']).scheme in ('http','https') and bool(urlparse(r['primary_url']).netloc))
        check(rid+':locator_and_queries',bool(r['verification_locator']) and bool(r['discovery_queries']))
        check(rid+':doi_format',not r['doi'] or bool(re.match(r'^10\.\d{4,9}/\S+$',r['doi'])))
        wordcounts[rid]=len(' '.join(str(r[k]) for k in substantive).split())
        check(rid+':compact_original_summary',wordcounts[rid]<=200,wordcounts[rid])
    with (ROOT/'publications.csv').open(encoding='utf-8',newline='') as f: csvrows=list(csv.DictReader(f))
    check('csv_roundtrip_ids', [r['id'] for r in csvrows]==[r['id'] for r in rs])
    b=(ROOT/'references.bib').read_text(encoding='utf-8')
    check('bibtex_one_entry_per_record',len(re.findall(r'^@\w+\{',b,re.M))==len(rs))
    check('bibtex_balanced_braces',b.count('{')==b.count('}'))
    request_package=json.loads((ROOT/'author_data_requests.json').read_text(encoding='utf-8'))
    requests=request_package['requests']
    request_ids={r['id'] for r in requests}
    paper_ids={r['id'] for r in rs}
    check('unique_data_request_ids',len(request_ids)==len(requests))
    check('data_requests_reference_catalogued_publications',all(r['publication_ids'] and set(r['publication_ids'])<=paper_ids for r in requests))
    check('publication_request_cross_references',all(r.get('data_request_ids',[])==[q['id'] for q in requests if r['id'] in q['publication_ids']] for r in rs))
    contacts=[c for r in requests for c in r['contacts']]
    check('contacts_have_public_source_and_locator',all(c.get('name') and c.get('role') and c.get('locator') and urlparse(c.get('source_url','')).scheme=='https' for c in contacts))
    check('contact_email_syntax_only',all(re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',c['email']) for c in contacts))
    statuses={'not_obtained','author_request','confidential','partial_public','not_located','public_base_missing_replication','restricted_author_request'}
    check('request_access_status_and_limits',all(r['availability_status'] in statuses and r['availability_detail'] and r['reuse_limit'] and r['availability_locator'] for r in requests))
    with (ROOT/'author_data_requests.csv').open(encoding='utf-8',newline='') as f: request_csv=list(csv.DictReader(f))
    check('request_csv_roundtrip',len(request_csv)==len(requests) and all(c['request_id']==r['id'] and c['data_to_request']==r['data_to_request'] and c['contact_emails']=='; '.join(x['email'] for x in r['contacts']) for c,r in zip(request_csv,requests)))
    request_md=(ROOT/'AUTHOR_DATA_REQUESTS.md').read_text(encoding='utf-8')
    check('request_link_anchors',all('id="'+r['id'].lower()+'"' in request_md for r in requests))
    missing_links=[]
    for p in ROOT.rglob('*.md'):
        body=p.read_text(encoding='utf-8-sig')
        for target in re.findall(r'\]\(([^\s)]+)\)',body):
            if re.match(r'^[A-Za-z][\w+.-]*:',target) or target.startswith('#'): continue
            path=unquote(target.split('#')[0])
            if p.parent==ROOT and path in ('validation.json','checksums.sha256'): continue
            # Explicit sibling snapshot link is checked in the publication checkout.
            if path.startswith('../../data/'): continue
            if not (p.parent/path).exists(): missing_links.append([str(p.relative_to(ROOT)),target])
    check('internal_markdown_file_links',not missing_links,missing_links)
    files=[p for p in ROOT.rglob('*') if p.is_file()]
    forbidden=[str(p.relative_to(ROOT)) for p in files if p.suffix.lower() in ('.pdf','.png','.jpg','.xml','.xlsm','.xlsx') or '__pycache__' in p.parts]
    check('no_full_documents_or_private_caches',not forbidden,forbidden)
    corrupt=[str(p.relative_to(ROOT)) for p in files if p.suffix in ('.json','.md','.csv','.bib','.py') and '\ufffd' in p.read_text(encoding='utf-8-sig')]
    check('no_unicode_replacement_characters',not corrupt,corrupt)
    metadata={}
    for p in (ROOT/'raw_metadata/crossref').glob('*.json'):
        m=json.loads(p.read_text(encoding='utf-8'));metadata[m['requested_doi'].lower()]=m
    titlechecks=[]; metadata_errors=[]
    for r in rs:
        if not r['doi']:continue
        m=metadata.get(r['doi'].lower())
        if not m or m['status']!='retrieved':metadata_errors.append({'id':r['id'],'doi':r['doi'],'status':m.get('error') if m else 'not retrieved'});continue
        mt=m['metadata'].get('title',[''])[0]
        similarity=SequenceMatcher(None,re.sub(r'\W','',r['title'].casefold()),re.sub(r'\W','',mt.casefold())).ratio()
        titlechecks.append({'id':r['id'],'similarity':round(similarity,4)})
    check('retrieved_doi_titles_match',all(x['similarity']>=0.95 for x in titlechecks),titlechecks)
    # Derived checks reproduce the stated published numbers, without correcting source inputs.
    arithmetic={
        'E11_CAGR_percent':{'formula':'100*((1814.2/133.2)**(1/30)-1)','derived':100*((1814.2/133.2)**(1/30)-1),'source_reported':1.88},
        'E11_diesel_sum_MW':{'terms':['124.9','84','52.75','17.8','9.6','8.4','48.8'],'derived':str(sum(Decimal(v) for v in ['124.9','84','52.75','17.8','9.6','8.4','48.8'])),'source_total':'302.35'},
        'COOK12_forest_area_ratio':{'formula':'8729400/87294','derived':8729400/87294},
        'E06_WT7_Xumbo_AEP_GWh':{'formula':'1500*8760*0.29/1e6','derived':1500*8760*0.29/1e6,'source_reported_GWh':6.04,'source_locator':'Tables2/11 and Eq33; source CF rounded to2 decimals','rounding_max_GWh':1500*8760*0.295/1e6}}
    check('independent_arithmetic_checks',abs(arithmetic['E11_CAGR_percent']['derived']-9.095297580578832)<1e-10 and arithmetic['E11_diesel_sum_MW']['derived']=='346.25' and arithmetic['COOK12_forest_area_ratio']['derived']==100)
    check('E06_turbine_arithmetic_and_rounding_conflict',abs(arithmetic['E06_WT7_Xumbo_AEP_GWh']['derived']-3.8106)<1e-10 and arithmetic['E06_WT7_Xumbo_AEP_GWh']['rounding_max_GWh']<6.035)
    result={'review_date':'2026-09-28','scope':'Structural, bibliography and selected arithmetic checks. Passing is not validation of every source finding.','records':len(rs),'checks_passed':sum(x['passed'] for x in checks),'checks_failed':len(errors),'doi_metadata_retrieved':len(titlechecks),'doi_metadata_exceptions':metadata_errors,'arithmetic_checks':arithmetic,'maximum_substantive_words_per_record':max(wordcounts.values()),'checks':checks}
    (ROOT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    manifest=[]
    for p in sorted(ROOT.rglob('*')):
        if p.is_file() and p.name!='checksums.sha256': manifest.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix())
    (ROOT/'checksums.sha256').write_text('\n'.join(manifest)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
    if errors:raise SystemExit('FAILED: '+', '.join(errors))

if __name__=='__main__':main()
