#!/usr/bin/env python3
"""Bootstrap ledger gate only. Does not validate engineering equivalence."""
from pathlib import Path
import json, sys, tempfile
ROOT=Path(__file__).resolve().parents[1]
def check(root, scope, acceptance):
 errors=[]
 if scope.get('inventory_complete') is not True: errors.append('Scope inventory not independently closed')
 if not scope.get('reviewer') or not scope.get('inventory_evidence'): errors.append('Missing inventory review/evidence')
 features=scope.get('features',[])
 if not features: errors.append('Empty feature inventory')
 ids=[f.get('id') for f in features]
 if any(not isinstance(i,str) or not i for i in ids) or len(set(ids))!=len(ids): errors.append('Invalid/duplicate feature IDs')
 records=acceptance.get('features',[])
 recids=[x.get('id') for x in records]
 if len(set(recids))!=len(recids) or set(recids)!=set(ids): errors.append('Acceptance IDs must exactly match scope')
 paths=list(scope.get('inventory_evidence',[]))
 for item in records:
  if item.get('status')!='PASS' or not item.get('reviewer'): errors.append('Not independently passed: '+str(item.get('id')))
  if not item.get('cases') or not item.get('evidence'): errors.append('Missing cases/evidence: '+str(item.get('id')))
  paths.extend(item.get('evidence',[]))
 for p in paths:
  q=(root/p).resolve()
  if not q.is_relative_to(root.resolve()) or not q.is_file() or q.stat().st_size==0: errors.append('Invalid evidence file: '+str(p))
 for key in ['automated_regression','build','lint','original_differential','ui_workflows','file_roundtrip','user_acceptance']:
  gate=acceptance.get('gates',{}).get(key,{})
  if gate.get('status')!='PASS' or not gate.get('reviewer') or not gate.get('evidence'): errors.append('Gate not passed: '+key)
  for p in gate.get('evidence',[]):
   q=(root/p).resolve()
   if not q.is_relative_to(root.resolve()) or not q.is_file() or q.stat().st_size==0: errors.append('Invalid gate evidence: '+str(p))
 return errors
if '--self-test' in sys.argv:
 with tempfile.TemporaryDirectory() as tmp:
  r=Path(tmp); (r/'proof').write_text('test-only ledger fixture')
  s={'inventory_complete':True,'reviewer':'test','inventory_evidence':['proof'],'features':[{'id':'F1'}]}
  gates={k:{'status':'PASS','reviewer':'test','evidence':['proof']} for k in ['automated_regression','build','lint','original_differential','ui_workflows','file_roundtrip','user_acceptance']}
  a={'features':[{'id':'F1','status':'PASS','reviewer':'test','cases':['C1'],'evidence':['proof']}],'gates':gates}
  assert not check(r,s,a)
  assert check(r,{},a)
  a['features'][0]['evidence']=[]; assert check(r,s,a)
  a['features'][0]['evidence']=['missing']; assert check(r,s,a)
  a['features'][0]['evidence']=['proof']; a['features'][0]['status']='NOT_RUN'; assert check(r,s,a)
  a['features'][0]['status']='PASS'; a['features'].append(dict(a['features'][0])); assert check(r,s,a)
 print('PASS: bootstrap gate rejects empty scope, missing evidence, missing files, unrun and duplicate entries')
else:
 errors=check(ROOT,json.loads((ROOT/'planning/scope.json').read_text()),json.loads((ROOT/'planning/acceptance.json').read_text()))
 print(json.dumps({'status':'FAIL' if errors else 'PASS','errors':errors,'boundary':'Ledger check only; independent evidence review and differential runners required'},ensure_ascii=False,indent=2))
 sys.exit(bool(errors))
