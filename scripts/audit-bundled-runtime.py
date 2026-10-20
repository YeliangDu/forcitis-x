#!/usr/bin/env python3
"""Bounded offline inventory of four shipped prerequisite packages. Never executes them.
Reuses the existing MSI table decoder; 7z handles archive decompression.
"""
import shutil
import argparse, hashlib, importlib.util, json, struct, subprocess, traceback
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load_module(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
MSI=load_module('msi_tables','scripts/decode-msi-tables.py')
def run(out):
 out=out.resolve(); out.mkdir(parents=True,exist_ok=True)
 rows=json.loads((out/'inputs.json').read_text()); commands=[]; nodes=[]; packages=[]; gaps=[]
 def rel(p):return str(p.relative_to(ROOT))
 def save(name,obj): (out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 def command(c,label):
  p=subprocess.run(c,capture_output=True,text=True);idx=len(commands)
  (out/f'run-{idx}.stdout').write_text(p.stdout);(out/f'run-{idx}.stderr').write_text(p.stderr)
  commands.append({'command':c,'label':label,'exit_code':p.returncode,'stdout':rel(out/f'run-{idx}.stdout'),'stderr':rel(out/f'run-{idx}.stderr')})
  if p.returncode: raise ValueError(f'{label}: exit {p.returncode}')
  return p.stdout
 def node(p,parent,member):
  b=p.read_bytes();pe=False
  if b[:2]==b'MZ' and len(b)>64:
   n=struct.unpack_from('<I',b,60)[0];pe=b[n:n+4]==b'PE\0\0'
  n={'path':rel(p),'parent':rel(parent) if parent else None,'member':member,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'classification':'PE' if pe else 'NON_PE','classification_scope':'Signature only; compressed delta payload semantics unknown','runtime_binding':'NOT_RUN'}
  nodes.append(n);return n
 def extract(p,kind):
  dest=p.parent/(p.name+'.members')
  command(['7z','x','-y','-t'+kind,str(p),'-o'+str(dest)],'extract '+rel(p))
  return dest
 def msi(p,d,payloads):
  cp,cols,tables=MSI.decode(d)
  table_path=d.parent/(d.name+'.tables.json');table_path.write_text(json.dumps({'codepage':cp,'columns':cols,'tables':tables},ensure_ascii=False,indent=2)+'\n')
  dirs={r['Directory']:r for r in tables.get('Directory',[])};comps={r['Component']:r for r in tables.get('Component',[])}
  def target(key,seen=()):
   assert key not in seen
   r=dirs[key];v=r['DefaultDir'].split(':')[0].split('|')[-1]
   return (target(r['Directory_Parent'],seen+(key,)) if r['Directory_Parent'] else [f'[{key}]'])+([] if v=='.' or not r['Directory_Parent'] else [v])
  mapping=[]
  for f in tables.get('File',[]):
   c=comps[f['Component_']]; candidates=[x for x in payloads if x.name==f['File']]
   assert len(candidates)==1,(f['File'],len(candidates))
   x=candidates[0];assert x.stat().st_size==f['FileSize']
   mapping.append({'file':f,'component':c,'features':[r for r in tables.get('FeatureComponents',[]) if r['Component_']==f['Component_']],'symbolic_target':'/'.join(target(c['Directory_'])+[f['FileName'].split('|')[-1]]),'payload':rel(x),'sha256':digest(x),'source_tables':rel(table_path),'actual_installation':'NOT_RUN'})
  assert {f['File'] for f in tables.get('File',[])}=={x.name for x in payloads}
  package={'source':rel(p),'sha256':digest(p),'tables':rel(table_path),'table_counts':{k:len(v) for k,v in tables.items()},'properties':{r['Property']:r['Value'] for r in tables.get('Property',[])},'media':tables.get('Media',[]),'file_map':mapping,'binary':[],'non_file_components':[r for k,r in comps.items() if k not in {f['Component_'] for f in tables.get('File',[])}]}
  for r in tables.get('Binary',[]):
   x=d/('Binary.'+r['Name']);assert x.is_file()
   package['binary'].append({'row':r,'path':rel(x),'sha256':digest(x),'custom_actions':[a for a in tables.get('CustomAction',[]) if a.get('Source')==r['Name']]})
  packages.append(package)
 def recurse(p,depth=0):
  assert depth<6 and len(nodes)<12000,'bounded inventory exceeded'
  magic=p.read_bytes()[:8]
  if magic[:4]!=b'MSCF':return
  if p.name=='WSUSSCAN.cab':
   gaps.append({'source':rel(p),'error':'WSUS scan catalog retained as opaque CAB; recursive metadata inventory not closed','release_condition':'Review whether complete scan-catalog expansion is required by B01-02; preserve all obligations and independently inventory if required.'});return
  listing=command(['7z','l','-slt','-tCab',str(p)],'source member listing')
  records=listing.split('----------\n',1)[1].strip().split('\n\n')
  names=[dict(line.split(' = ',1) for line in r.splitlines() if ' = ' in line)['Path'] for r in records if r.startswith('Path = ')]
  assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in names)
  d=extract(p,'Cab');files=[d/n for n in names];assert all(x.is_file() for x in files)
  for x in files:node(x,p,str(x.relative_to(d)));recurse(x,depth+1)
  return files
 for i,r in enumerate(rows):
  src=ROOT/r['source'];p=ROOT/r['copy'];assert digest(src)==digest(p)==r['sha256'];node(p,None,r['path'])
  d=out/f'package-{i}'
  if d.exists(): shutil.rmtree(d)
  try:
   command(['7z','x','-y','-t'+('Compound' if i<2 else 'PE'),str(p),'-o'+str(d)],'root extraction')
   if i<2:
    payloads=recurse(d/'Redist.cab')
    for x in sorted(d.iterdir()):
     if x.is_file():node(x,p,x.name)
    msi(p,d,payloads)
   else:
    # Retain PE sections/resources as extraction artifacts, not installer file claims.
    for x in sorted(d.rglob('*')):
     if x.is_file() and '.members' not in str(x) and not any(part.startswith('cab-') for part in x.parts) and not x.name.startswith('overlay-'):node(x,p,str(x.relative_to(d)))
    overlay=d/'[0]';b=overlay.read_bytes();cabs=[];pos=0
    while True:
     pos=b.find(b'MSCF',pos)
     if pos<0:break
     size=struct.unpack_from('<I',b,pos+8)[0];assert size>=36 and pos+size<=len(b)
     x=d/f'overlay-{pos}.cab';x.write_bytes(b[pos:pos+size])
     n=node(x,overlay,f'offset:{pos}');n['offset']=pos;cabs.append((pos,size,x));pos+=size
    assert len(cabs)==2
    members=[recurse(x) for _,_,x in cabs]
    manifest=next(x for x in members[0] if x.name=='0');tree=ET.fromstring(manifest.read_bytes());decl=[]
    for e in tree.iter():
     if e.tag.split('}')[-1]!='Payload':continue
     a=dict(e.attrib);source=a.get('SourcePath');candidates=[x for group in members for x in group if x.name==source];assert len(candidates)==1,a
     x=candidates[0];assert x.stat().st_size==int(a['FileSize']);assert hashlib.sha1(x.read_bytes()).hexdigest().upper()==a['Hash'].upper()
     decl.append({'declaration':a,'payload':rel(x),'sha256':digest(x),'source_manifest':rel(manifest)})
    assert {x.name for group in members for x in group}=={'0'}|{a['declaration']['SourcePath'] for a in decl}
    save(f'burn-{i}.json',{'source':rel(p),'manifest':rel(manifest),'payloads':decl,'chain':[{'element':e.tag.split('}')[-1],'attributes':dict(e.attrib)} for e in tree.iter() if e.tag.split('}')[-1] in ['MsiPackage','MsuPackage','ExePackage','Container']],'overlay_ranges':[{'offset':o,'bytes':s,'sha256':digest(x)} for o,s,x in cabs],'uninterpreted_overlay_ranges':[{'offset':cabs[0][1],'bytes':cabs[1][0]-cabs[0][1]},{'offset':cabs[1][0]+cabs[1][1],'bytes':len(b)-cabs[1][0]-cabs[1][1]}]})
    for a in decl:
     if a['declaration']['FilePath'].lower().endswith('.msi'):
      x=ROOT/a['payload'];md=extract(x,'Compound')
      for f in sorted(md.iterdir()):
       if f.is_file():node(f,x,f.name)
      cabpath=a['declaration']['FilePath'].rsplit('\\',1)[0]+'\\cab1.cab'
      cab=next(ROOT/z['payload'] for z in decl if z['declaration']['FilePath']==cabpath)
      msi(x,md,sorted(f for f in (cab.parent/(cab.name+'.members')).rglob('*') if f.is_file() and f.name!='.DS_Store'))
  except Exception as e:gaps.append({'source':r['source'],'error':str(e),'traceback':traceback.format_exc(),'release_condition':'Complete unsupported extraction or mapping using a verified static decoder; independently rerun inventory.'})
 # Hash every materialized member; nested archive maps are represented by parent/member edges.
 save('raw-nodes.json',nodes);save('commands.json',commands);save('raw-packages.json',packages);save('raw-gaps.json',gaps)
 assert len({n['path'] for n in nodes})==len(nodes)
 save('hash-drift.json',[n for n in nodes if digest(ROOT/n['path'])!=n['sha256']])
 for n in nodes:assert digest(ROOT/n['path'])==n['sha256'],n['path']
 for r in rows:assert digest(ROOT/r['source'])==r['sha256']
 save('commands.json',commands);save('inventory.json',{'evidence_type':'STATIC_7Z_AND_EXISTING_MSI_DECODER','status':'PARTIAL','inputs':rows,'nodes':nodes,'msi_packages':packages,'gaps':gaps,'counts':{'nodes':len(nodes),'pe':sum(n['classification']=='PE' for n in nodes),'msi_mapped_files':sum(len(p['file_map']) for p in packages),'msi_packages':len(packages),'binary_rows':sum(len(p['binary']) for p in packages)},'limits':['Actual installation, binding and package selection NOT_RUN (B02).','MSU component destinations/delta reconstruction not decoded; retain servicing manifests as static source, mapping remains unverified.','PE signature classification does not interpret delta-compressed file contents.','7z extraction is ordinary tool output; only rea-*.json are REA Evidence.']})
 print(json.dumps({'counts':{'nodes':len(nodes),'msi_packages':len(packages),'mapped_files':sum(len(p['file_map']) for p in packages)},'gaps':gaps},ensure_ascii=False))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);run(a.parse_args().out)
