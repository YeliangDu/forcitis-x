"""Check retained UI observation provenance, not license or package acceptance."""
import json,hashlib
from pathlib import Path
b=Path('evidence/stages/B02/B02-02/attempt-43')
r=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
p=r(b/'preflight/stdout' ) if False else None
pre=(b/'preflight/stdout').read_text(encoding='utf-8-sig')
assert '60096' in pre and 'run-20261018' in pre
for n in ['help-menu','about','about-open']:
 assert (b/(n+'.png')).read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
assert r(b/'about-open-capture-retry/stdout')['Image']
x=r(b/'observations.json')
assert x['license_operation']=='NOT_RUN' and x['new_client_launch']=='NOT_RUN'
assert x['candidate_status']=='PARTIAL'
assert x['screenshot_ui_timestamp_mismatch_retained'] is True
print(json.dumps({'status':'PASS','scope':'observation provenance and honest incomplete boundaries only','license':'NOT_RUN','package':'PARTIAL','screenshots':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in b.glob('*.png')}},indent=2))
