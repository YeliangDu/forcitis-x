#!/usr/bin/env python3
"""Source/hash and declared mapping checks; does not certify Windows execution."""
import argparse,hashlib,importlib.util,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify(out):
 inv=json.loads((out/'inventory.json').read_text());nodes={n['path']:n for n in inv['nodes']};assert len(nodes)==len(inv['nodes'])
 for path,n in nodes.items():
  p=ROOT/path;assert sha(p)==n['sha256'] and p.stat().st_size==n['bytes'],path
  if n['parent']:assert n['parent'] in nodes,path
 for r in inv['inputs']:assert sha(ROOT/r['source'])==sha(ROOT/r['copy'])==r['sha256']
 # Every physically extracted file has a node; table JSONs are derived evidence.
 missing=[]
 for i in range(4):
  for p in (out/f'package-{i}').rglob('*'):
   if p.is_file() and p.name!='.DS_Store' and not p.name.endswith('.tables.json') and str(p.relative_to(ROOT)) not in nodes:missing.append(str(p))
 assert not missing,missing[:10]
 assert len(inv['msi_packages'])==6, 'Two SQL plus four VC MSI packages must be mapped'
 for package in inv['msi_packages']:
  t=json.loads((ROOT/package['tables']).read_text())['tables'];maps=package['file_map']
  assert {m['file']['File'] for m in maps}=={f['File'] for f in t['File']}
  for m in maps:
   assert m['payload'] in nodes and sha(ROOT/m['payload'])==m['sha256'];assert m['file']['FileSize']==nodes[m['payload']]['bytes']
  assert len(package['binary'])==len(t.get('Binary',[]))
 # Reconstruct both overlay CAB ranges from parent bytes, independently of signature scan.
 for i in [2,3]:
  p=out/f'burn-{i}.json'
  if not p.exists():continue
  burn=json.loads(p.read_text());b=(out/f'package-{i}'/'[0]').read_bytes()
  for r in burn['overlay_ranges']:
   raw=b[r['offset']:r['offset']+r['bytes']];assert raw[:4]==b'MSCF' and len(raw)==struct.unpack_from('<I',raw,8)[0];assert hashlib.sha256(raw).hexdigest()==r['sha256']
  for d in burn['payloads']:
   raw=(ROOT/d['payload']).read_bytes();assert hashlib.sha1(raw).hexdigest().upper()==d['declaration']['Hash'].upper()
 # Existing independent fixed-schema reader compares SQL MSI declarations to decoder results.
 spec=importlib.util.spec_from_file_location('independent',ROOT/'scripts/audit-msi-streams.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 # SQL packages declare a 32-bit File.Sequence and CustomAction.ExtendedType.
 m.SCHEMAS={k:list(v) for k,v in m.SCHEMAS.items()}
 m.SCHEMAS['File'][-1]=('Sequence','i4')
 m.SCHEMAS['CustomAction'].append(('ExtendedType','i4'))
 for i in range(2):
  p=next(p for p in inv['msi_packages'] if p['source']==inv['inputs'][i]['copy']);tables=json.loads((ROOT/p['tables']).read_text())['tables'];m.audit(out/f'package-{i}',tables)
 print(json.dumps({'status':'PASS','verified_nodes':len(nodes),'msi_packages':len(inv['msi_packages']),'msi_files':sum(len(p['file_map']) for p in inv['msi_packages']),'scope':'Static members and declarations only; full work package remains pending/blocked on explicit gaps'}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);verify(p.parse_args().out.resolve())
