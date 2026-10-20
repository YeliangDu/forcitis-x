import json
from pathlib import Path
b=Path('evidence/stages/B02/B02-02/attempt-45')
r=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
last=''
for name in ['probe','expand','lock-strength']:
 x=r(b/(name+'.json'));assert x['At']>last;last=x['At'];assert x['Session']==4
 assert x['Process'][0]['Id']==78216 and x['Process'][0]['Path']==r'C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe'
 assert any(t['RemotePort']==1433 and t['State']==5 for t in x['TCP'])
 assert (b/(name+'.png')).read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
a=r(Path('evidence/stages/B02/B02-01/attempt-41/environment-final/stdout'))['After']
x=r(b/'source-hashes.json')['Files'];idx=lambda fs:{f['Path']:(f['Length'],f['SHA256']) for f in fs}
assert len(x)==445 and idx(a)==idx(x)
assert r(b/'audit.json')['Sample']['Hash']=='2FFA32CB256324AE610C2215BFE554DDB42BA0CBB06108188C6727B2F060FBE3'
print(json.dumps({'status':'PASS','scope':'fresh ordered UI/process/TCP captures only','license':'NOT_PROVEN','package':'PARTIAL'}))
x=r(b/'post-action/stdout');assert x['Processes']==[] and x['Reports']==[] and x['GuardExists'] is False
assert any(e['Id']==1000 and 'SHELL32.dll' in e['Message'] and '0x13188' in e['Message'] for e in x['Errors'])
after=r(b/'source-hashes-after.json')['Files'];assert idx(after)==idx(a)
assert r(b/'post-hashes.json')['Sample']['Hash']=='2FFA32CB256324AE610C2215BFE554DDB42BA0CBB06108188C6727B2F060FBE3'
assert r(b/'cleanup/stdout')['Remaining']==[]
print(json.dumps({'status':'PASS','scope':'crash evidence, guard refused, no outputs, full source hashes unchanged and own tasks removed','operation':'FAIL','license':'NOT_PROVEN'}))
