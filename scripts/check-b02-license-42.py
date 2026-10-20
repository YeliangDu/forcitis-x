"""Validate runtime slice provenance; never declares license/package acceptance."""
import json,hashlib
from pathlib import Path
p=Path('evidence/stages/B02/B02-02/attempt-42')
def read(f):return json.loads(f.read_text(encoding='utf-8-sig'))
x=read(p/'capture/stdout');u=x['UI'];u=json.loads(u['value'] if isinstance(u,dict) else u)
a=read(p/'source-audit/stdout')
b=read(Path('evidence/stages/B02/B02-01/attempt-41/environment-final/stdout'))
assert a['Source']==b['Before']==b['After'], 'Source installation/sample changed'
assert a['NewClient']==b['Client'], 'Frozen isolation changed'
assert a['Sample']=='2FFA32CB256324AE610C2215BFE554DDB42BA0CBB06108188C6727B2F060FBE3'
assert u['Session']==4 and u['Process'][0]['Id']==60096
assert u['Process'][0]['Path']==r'C:\hwk-modern\run-20261018\client\XWall.exe'
assert any(c['RemoteAddress']=='165.154.20.222' and c['RemotePort']==1433 and c['State']=='Established' for c in a['Connections'])
assert x['Task']['LastTaskResult']==0
assert (p/'desktop.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
print(json.dumps({'status':'PASS','scope':'retained process UI and single-time connection, unchanged source/frozen copy only','license':'NOT_RUN','new_client_launch':'NOT_RUN','package_acceptance':'PARTIAL','source_files':len(a['Source']),'screenshots':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in p.glob('*.png')}},indent=2))
