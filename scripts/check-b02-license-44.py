"""Recompare live source inventory and validate completed UI capture provenance."""
import json,hashlib
from pathlib import Path
b=Path('evidence/stages/B02/B02-02/attempt-44')
r=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
a=r(Path('evidence/stages/B02/B02-01/attempt-41/environment-final/stdout'))['After']
c=r(b/'source-hashes.json')['Files']
index=lambda xs:{x['Path']:(x['Length'],x['SHA256']) for x in xs}
assert len(c)==445 and index(a)==index(c)
assert any(x['Path'].endswith('门窗计算示例1.cwx') for x in c)
for name in ['probe-retry','settings-final']:
 raw=r(b/(name+'-capture/stdout'));assert raw['Task']['LastTaskResult']==0
 ui=r(b/(name+'.json'));assert ui['Session']==4
 assert ui['Process'][0]['Id']==60096 and ui['Process'][0]['Path']==r'C:\hwk-modern\run-20261018\client\XWall.exe'
 assert (b/(name+'.png')).read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
 assert any(t['RemotePort']==1433 and t['State']==5 for t in ui['TCP'])
assert any('2028年5月17日' in n['Name'] for n in r(b/'probe-retry.json')['Nodes'])
assert index(r(b/'source-hashes-after.json')['Files'])==index(c)
assert r(b/'source-hashes-after.json')['At']>r(b/'launch-final.json')['At']
new=r(b/'launch-final.json');assert new['Process'][0]['Id']==78216
assert new['Process'][0]['Path']==r'C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe'
assert r(b/'launch-final-capture/stdout')['Task']['LastTaskResult']==0
assert new['At']>r(b/'normal-close-final.json')['At']
assert not r(b/'normal-close-final.json')['Windows']
assert any(t['RemotePort']==1433 and t['State']==5 for t in new['TCP'])
assert any(n['Name']=='sample-working.cwx' for n in new['Nodes'])
print(json.dumps({'status':'PASS','scope':'445 source file equality and completed runtime UI captures only','license':'NOT_RUN','new_launch':'OBSERVED','package':'PARTIAL'},indent=2))
