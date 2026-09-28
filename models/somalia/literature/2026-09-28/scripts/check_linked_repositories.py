"""Inspect public repository metadata without downloading or running model inputs."""
import json
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
def get(url):
    with urlopen(Request(url,headers={'User-Agent':'SomaliaEnergyLiteratureReview/1.0'}),timeout=35) as response:
        return json.loads(response.read()),response.url

out=[]
for name,url in [
 ('OnSSET Somalia-1.0','https://api.github.com/repos/OnSSET/onsset/git/trees/Somalia-1.0?recursive=1'),
 ('Somalia energy starter kit','https://zenodo.org/api/records/4725474'),
 ('Somalia transport starter kit','https://zenodo.org/api/records/7998431')]:
    item=dict(name=name,requested_url=url,retrieved_at_utc=datetime.now(timezone.utc).isoformat(),inspection='Repository metadata/file listing only; inputs not validated or executed')
    try:
        data,resolved=get(url)
        item.update(status='retrieved',resolved_url=resolved)
        if 'github.com' in url:
            tree=data
            item['tree_sha']=tree['sha']
            item['files']=[{k:x[k] for k in ['path','sha','size'] if k in x} for x in tree['tree'] if x['type']=='blob']
            item['tree_truncated']=tree.get('truncated')
        else:
            item['doi']=data.get('doi')
            item['title']=data.get('metadata',{}).get('title')
            item['publication_date']=data.get('metadata',{}).get('publication_date')
            item['license']=data.get('metadata',{}).get('license')
            item['files']=[{k:x[k] for k in ['key','size','checksum','links'] if k in x} for x in data.get('files',[])]
    except Exception as exc: item.update(status='error',error=str(exc))
    out.append(item)
    print(name,item['status'],len(item.get('files',[])))
target=ROOT/'provenance/linked_repositories.json'
target.parent.mkdir(parents=True,exist_ok=True)
if target.exists():
    previous=json.loads(target.read_text(encoding='utf-8'))
    for item in out:
        item['previous_attempts']=[p for p in previous if p['name']==item['name']]
target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
