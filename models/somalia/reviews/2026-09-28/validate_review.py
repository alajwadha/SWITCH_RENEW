"""Read-only package checks; writes one review verification record, not source data."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

HERE=Path(__file__).resolve().parent
SOMALIA=HERE.parents[1]
REPO=SOMALIA.parents[1]
LIT=SOMALIA/'literature/2026-09-28'
BASE='cf5da4ddf04082b6e1d6fb62ce269516d6a56a17'

def main():
    checks=[]
    def check(name,passed,details=None):
        checks.append({'check':name,'passed':bool(passed),'details':details})
    manifest=[]
    for line in (LIT/'checksums.sha256').read_text(encoding='utf-8').splitlines():
        digest,name=line.split('  ',1)
        p=LIT/name
        manifest.append({'path':name,'match':p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==digest})
    check('literature_manifest',all(r['match'] for r in manifest),{'files_checked':len(manifest),'mismatches':[r for r in manifest if not r['match']]})
    missing=[]
    for p in list(HERE.glob('*.md'))+list(LIT.rglob('*.md')):
        for target in re.findall(r'\]\(([^\s)]+)\)',p.read_text(encoding='utf-8-sig')):
            if re.match(r'^[A-Za-z][\w+.-]*:',target) or target.startswith('#'):continue
            q=(p.parent/unquote(target.split('#')[0])).resolve()
            if q==HERE/'POST_EDIT_VALIDATION.json':continue
            if not q.is_file():missing.append([str(p.relative_to(REPO)),target])
    check('review_and_literature_local_links',not missing,missing)
    diff=subprocess.check_output(['git','diff','--name-only',BASE,'--','models/somalia/data/2026-09-28'],cwd=REPO,text=True).strip()
    check('original_data_snapshot_unchanged',not diff,diff.splitlines())
    tracked=subprocess.check_output(['git','diff','--name-only',BASE],cwd=REPO,text=True).splitlines()
    untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=REPO,text=True).splitlines()
    allowed=lambda p:p in ('docs/DOCUMENTATION.md','models/somalia/README.md') or p.startswith(('models/somalia/literature/2026-09-28/','models/somalia/reviews/2026-09-28/'))
    outside=[p for p in tracked+untracked if not allowed(p)]
    check('changes_within_authorized_qc_and_contact_scope',not outside,outside)
    val=json.loads((LIT/'validation.json').read_text(encoding='utf-8'))
    check('corrected_literature_validation',val['checks_failed']==0,{'passed':val['checks_passed'],'failed':val['checks_failed']})
    requests=json.loads((LIT/'author_data_requests.json').read_text(encoding='utf-8'))['requests']
    check('request_register_not_outreach',all(r['outreach_status']=='Not contacted' for r in requests),{'requests':len(requests),'contact_entries':sum(len(r['contacts']) for r in requests)})
    check('both_independent_reports_present',all((HERE/p).is_file() for p in ['KAMMEN_PERSPECTIVE_REVIEW.md','EVIDENCE_QC_REVIEW.md']))
    report={'review_date':'2026-09-28','baseline_commit':BASE,'scope':'Post-edit integrity, links and change-scope checks; not source-data validation or inbox verification.','checks':checks,'passed':all(c['passed'] for c in checks)}
    (HERE/'POST_EDIT_VALIDATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report,ensure_ascii=False))
    if not report['passed']:raise SystemExit(1)

if __name__=='__main__':main()
