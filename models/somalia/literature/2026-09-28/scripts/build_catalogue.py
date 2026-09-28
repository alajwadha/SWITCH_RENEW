"""Build deterministic review exports from manually appraised contribution records."""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
THEMES={'electricity':'Electricity and resources','cooking_biomass':'Cooking and biomass','transport_fuels_governance':'Transport fuels and governance','productive_uses':'Productive uses'}
DEPTH={'selected_full_text_sections':'Selected full-text sections','full_text':'Full short document','publisher_abstract':'Abstract only','official_summary':'Official summary'}

def write(name,text):
    (ROOT/name).write_text(text.rstrip()+'\n',encoding='utf-8',newline='\n')

def records():
    return [r for p in sorted((ROOT/'contributions').glob('*_records.json')) for r in json.loads(p.read_text(encoding='utf-8-sig'))]

def main():
    rows=records()
    rows.sort(key=lambda r:(list(THEMES).index(r['primary_theme']),r['year'] is None,-(r['year'] or 0),r['id']))
    write('publications.json',json.dumps(rows,ensure_ascii=False,indent=2))
    keys=list(json.loads((ROOT/'record_schema.json').read_text(encoding='utf-8'))['required_fields'])
    keys+=sorted({k for r in rows for k in r}-set(keys))
    with (ROOT/'publications.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=keys,lineterminator='\n')
        writer.writeheader()
        writer.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in rows)
    table=['# Somalia energy publication catalogue','',f'Review date: 28 September 2026. **{len(rows)} publication/source records.** Counts describe records, not independent studies. One identity-only lead and regional context are explicitly marked.','',
           'Every finding below is bounded by the recorded inspection depth. Full provenance, data years, author lists, methods and appraisal are in [JSON](publications.json) / [CSV](publications.csv); citations are in [BibTeX](references.bib). See [synthesis](REVIEW.md), [source issues](SOURCE_ISSUES.md) and [protocol](PROTOCOL.md).','']
    def cell(value): return str(value).replace('|',' / ').replace('\n',' ').replace('<','&lt;')
    for theme,label in THEMES.items():
        group=[r for r in rows if r['primary_theme']==theme]
        table += ['## '+label,'',f'{len(group)} records.','', '| ID / year | Publication | Geography and method | Finding or contribution | Limitation and inspection |','|---|---|---|---|---|']
        for r in group:
            author=r['authors'][0]+(' et al.' if len(r['authors'])>1 else '')
            status=' **Identity only; findings unreviewed.**' if r.get('review_status')=='identity_only' else ''
            if r.get('scope_role')=='regional_context': status+=' **Regional context.**'
            table.append(f'| <a id="{r["id"].lower()}"></a> {r["id"]} / {r["year"] or "undated"} | [{cell(r["title"])}]({r["primary_url"]})<br>{cell(author)}; {cell(r["publication_type"])} | {cell(r["geographic_scope"])}. {cell(r["method"])} | {cell(r["key_findings"])}{status} | {cell(r["limitations"])} **{DEPTH[r["inspection_depth"]]}.** |')
        table.append('')
    write('PUBLICATIONS.md','\n'.join(table))
    registry={}
    for p in sorted((ROOT/'raw_metadata/crossref').glob('*.json')):
        entry=json.loads(p.read_text(encoding='utf-8'))
        m=entry.get('metadata',{})
        author_names={}
        for a in m.get('author',[]):
            if a.get('given') and a.get('family'): author_names[a['given']+' '+a['family']]=a['family']+', '+a['given']
        registry[entry['requested_doi'].lower()]=author_names
    bib=['% Somalia energy literature review, 2026-09-28. Original metadata and access labels; no abstracts.','']
    for r in rows:
        typ=r['publication_type']
        kind='article' if ('journal' in typ or typ=='review_article') else 'incollection' if 'chapter' in typ else 'techreport' if 'report' in typ else 'misc'
        corporate=kind in ('techreport','misc') and not r['doi']
        names=['{'+a+'}' if corporate else registry.get(r['doi'].lower(),{}).get(a,a) for a in r['authors']]
        values={'title':r['title'],'author':' and '.join(names),'year':r['year'],'journal' if kind=='article' else 'publisher':r['venue_or_publisher'],'doi':r['doi'],'url':r['primary_url'],'urldate':r['retrieved_date'],'note':'Catalogue '+r['id']+'; inspection: '+r['inspection_depth']+(' (identity only)' if r.get('review_status')=='identity_only' else '')}
        bib.append('@'+kind+'{'+r['id']+',')
        for k,v in values.items():
            if v is not None and v!='': bib.append('  '+k+' = {'+str(v).replace('&',r'\&').replace('%',r'\%')+'},')
        bib += ['}','']
    write('references.bib','\n'.join(bib))
    counts=Counter(r['primary_theme'] for r in rows)
    depths=Counter(r['inspection_depth'] for r in rows)
    summary={'review_date':'2026-09-28','records':len(rows),'content_appraised_records':sum(r.get('review_status')!='identity_only' for r in rows),'identity_only_records':sum(r.get('review_status')=='identity_only' for r in rows),'by_primary_theme':dict(counts),'inspection_depth':dict(depths),'doi_records':sum(bool(r['doi']) for r in rows),'publication_type':dict(Counter(r['publication_type'] for r in rows))}
    write('catalogue_summary.json',json.dumps(summary,ensure_ascii=False,indent=2))
    readme=['# Somalia energy literature review','',f'**{len(rows)} organized publication/source records**, reviewed 28 September 2026. Academic and institutional evidence receive critical appraisal across all energy topics. One record verifies publication identity only; regional-context material is labeled.','',
    '**Main judgment:** the opportunity is better evidence, validation and energy-service research. Existing OnSSET, OSeMOSYS, LEAP, hybrid-system, cooking and productive-use studies make a broad first-study claim unsuitable. See the [critical synthesis](REVIEW.md).','',
    '| Topic | Records | What the review covers |','|---|---:|---|']
    descriptions={'electricity':'Access, planning, resources, grids, storage, hybrid systems and adoption','cooking_biomass':'Cooking fuels, household surveys, charcoal, biomass, exposure and continued use','transport_fuels_governance':'Transport, petroleum, mobility, climate reporting and institutions','productive_uses':'Water, irrigation, cold chains, firms, health, schools and ports'}
    for t,label in THEMES.items(): readme.append(f'| {label} | {counts[t]} | {descriptions[t]} |')
    readme += ['', '## Open the outputs','',
    '- [Full publication table](PUBLICATIONS.md) — source links, methods, findings, limitations and access depth.',
    '- [Review](REVIEW.md) and [balanced reading route](READING_GUIDE.md).',
    '- [Data/reproducibility leads](DATA_LEADS.md), [evidence gaps](EVIDENCE_GAPS.md), [source issues](SOURCE_ISSUES.md).',
    '- [CSV](publications.csv), [JSON](publications.json), [BibTeX](references.bib) for reuse.',
    '- [Advisor brief](ADVISOR_BRIEF.md), [protocol](PROTOCOL.md), [numbered work log](WORK_LOG.md).',
    '- [Reproduction and verification](REPRODUCE.md), [validation results](validation.json), [file hashes](checksums.sha256).',
    '', '## What was verified','',f'{depths["full_text"]} short documents were read in full; {depths["selected_full_text_sections"]} records were inspected through selected full-text sections; {depths["publisher_abstract"]} through abstracts; {depths["official_summary"]} through official summaries, including the identity-only lead. These are inspection categories, not quality scores. DOI metadata, selected arithmetic/definition checks and linked-repository file listings supplement the content review.','',
    'This is a structured scoping review, not exhaustive systematic coverage. Underlying datasets, source calculations and models have not all been reproduced. Full article/report PDFs and extracted text are not redistributed here. Numerical conflicts and inaccessible corrections are retained explicitly.','',
    'The earlier [Somalia data snapshot](../../data/2026-09-28/README.md) remains separate and unchanged. This review does not make Somalia runnable or introduce additional modeled sectors.']
    write('README.md','\n'.join(readme))
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__': main()
