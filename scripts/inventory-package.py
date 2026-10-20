#!/usr/bin/env python3
"""Static extracted-file inventory. Does not execute package binaries."""
from pathlib import Path
import hashlib, json, subprocess
root=Path(__file__).resolve().parents[1]
base=root/'evidence/baseline/extracted'
out=root/'evidence/baseline/b01'
(out/'pe-listings').mkdir(parents=True,exist_ok=True)
rows=[]
for p in sorted(base.rglob('*')):
 if not p.is_file(): continue
 data=p.read_bytes()
 row={'path':str(p.relative_to(root)), 'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
 if data[:2]==b'MZ':
  r=subprocess.run(['7z','l',str(p)],capture_output=True,text=True)
  log=out/'pe-listings'/ (p.name+'.txt')
  log.write_text(r.stdout+r.stderr)
  fields={}
  for line in r.stdout.splitlines():
   if ' = ' in line:
    k,v=line.split(' = ',1)
    if k in ('Type','CPU','Name','Subsystem','Characteristics'): fields[k]=v
   elif ': ' in line:
    k,v=line.split(': ',1)
    if k in ('FileVersion','ProductVersion','OriginalFilename','ProductName','FileDescription','CompanyName'):
     fields.setdefault(k,[]).append(v)
  row.update(pe_metadata=fields,listing=str(log.relative_to(root)),tool_exit=r.returncode)
 rows.append(row)
(out/'file-inventory.json').write_text(json.dumps({'evidence_type':'STATIC_PACKAGE','tool':'7z 17.05','files':rows},ensure_ascii=False,indent=2)+'\n')
print('files',len(rows),'MZ',sum('pe_metadata' in r for r in rows))
for r in rows:
 m=r.get('pe_metadata',{})
 if any('xwall' in str(v).lower() or '5.4.' in str(v) for v in m.values()): print(r['path'],m)
