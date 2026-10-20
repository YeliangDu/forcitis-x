#!/usr/bin/env python3
"""Finite SCAN feasibility probe; ordinary 7z evidence, never executes payloads."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def run(out):
 out=out.resolve(); assert out.is_relative_to(ROOT/'evidence/scheduler/2026-10-18T134044124359+0000-recovery');out.mkdir(parents=True,exist_ok=False)
 source=ROOT/'evidence/stages/B01/B01-02/attempt-25/inventory.json';j=json.loads(source.read_text());roots=[n for n in j['nodes'] if n['path'].endswith('/WSUSSCAN.cab')];assert len(roots)==16
 frozen={n['path']:sha(ROOT/n['path']) for n in roots};assert all(frozen[n['path']]==n['sha256'] for n in roots)
 groups={}
 for n in roots:groups.setdefault(n['sha256'],[]).append(n['path'])
 commands=[];nodes=[];tails=[]
 def rel(p):return str(p.relative_to(ROOT))
 def command(args,stdout):
  err=stdout.with_suffix(stdout.suffix+'.stderr')
  with stdout.open('wb') as f,err.open('wb') as e:r=subprocess.run(args,stdout=f,stderr=e,timeout=60)
  commands.append({'argv':args,'exit_code':r.returncode,'stdout':rel(stdout),'stderr':rel(err)});assert r.returncode==0
 def walk(p,depth,parent=None,member=None):
  assert depth<6 and len(nodes)<256,'finite probe stop (global 12000 unchanged)'
  n={'path':rel(p),'sha256':sha(p),'bytes':p.stat().st_size,'parent':parent,'member':member};nodes.append(n)
  with p.open('rb') as f:magic=f.read(4)
  n['classification']='CAB' if magic==b'MSCF' else 'NON_CAB_UNINTERPRETED'
  if magic!=b'MSCF':return
  listing=p.with_suffix(p.suffix+'.listing.txt');command(['7z','l','-slt','-tCab',str(p)],listing);s=listing.read_text()
  records=s.split('----------\n',1)[1].strip().split('\n\n');rows=[dict(l.split(' = ',1) for l in r.splitlines() if ' = ' in l) for r in records if r.startswith('Path = ')]
  header=dict(l.split(' = ',1) for l in s.split('----------\n',1)[0].splitlines() if ' = ' in l)
  if int(header.get('Tail Size','0')):tails.append({'source':rel(p),'bytes':int(header['Tail Size']),'status':'UNRESOLVED_SIGNATURE_OR_OTHER_DATA'})
  assert len({r['Path'] for r in rows})==len(rows)
  for i,r in enumerate(rows):
   name=r['Path'];assert not Path(name).is_absolute() and '..' not in Path(name).parts and not name.startswith('-')
   child=p.parent/(p.name+f'.member-{i}');command(['7z','x','-so','-tCab',str(p),name],child);assert child.stat().st_size==int(r['Size']);walk(child,depth+1,rel(p),name)
 # One representative unique root, all aliases frozen. Never repeat whole runtime extraction.
 key=next(iter(groups));p=out/'root.cab';shutil.copyfile(ROOT/groups[key][0],p);assert sha(p)==key
 error=None
 try:walk(p,0)
 except Exception as e:error=str(e)
 after={n['path']:sha(ROOT/n['path']) for n in roots};assert after==frozen
 result={'evidence_type':'STATIC_7Z_STREAM_PROBE','status':'PASS' if error is None else 'BLOCKED','error':error,'inventory_source':str(source.relative_to(ROOT)),'inventory_sha256':sha(source),'root_aliases_by_sha256':groups,'source_integrity':{'before':frozen,'after':after,'status':'PASS'},'coverage':{'roots':16,'unique_roots':len(groups),'probed_unique_roots':1,'nodes':len(nodes)},'nodes':nodes,'tails':tails,'commands':commands,'limits':{'depth_exclusive':6,'probe_nodes':256,'global_nodes_unchanged':12000,'command_timeout_seconds':60},'remaining':['Other unique SCAN roots and all descendant semantics/classification beyond CAB signatures','MSU target/delta correspondence','Burn unknown intervals','CAB tails require independent attribution; no package PASS','Actual installation/runtime NOT_RUN']}
 (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':result['status'],'coverage':result['coverage'],'error':error}))
if __name__=='__main__':run(Path(sys.argv[1]))
