#!/usr/bin/env python3
"""Join existing inventories and verify bytes; no new binary analysis or execution."""
import argparse, hashlib, json, struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads((ROOT/p).read_text())
def run(out):
 out.mkdir(parents=True,exist_ok=True)
 base='evidence/baseline/b01/'
 inputs=['evidence/baseline/installer-manifest.json']+[base+p for p in ['file-inventory.json','msi-decoded/file-map.json','msi-decoded/tables.json','ole-bindings/audit.json','dependencies/inventory.json','clr/inventory.json']]+['evidence/scheduler/20261018T111719502460Z/stage-assignment.json','evidence/scheduler/20261018T111719502460Z/rea-preflight/version-check.json','scripts/check-component-baseline.py']
 frozen={p:sha(ROOT/p) for p in inputs}
 manifest,inv,mapping,tab,ole,dep,clr,assignment,pre=[load(p) for p in inputs[:-1]]
 files={r['path']:r for r in inv['files']}; maps={r['File']:r for r in mapping}; tables=tab['tables']; pes={r['source']:r for r in dep['pe']}; managed={r['source']:r for r in clr['records']}
 assert len(files)==len(inv['files']) and len(maps)==len(mapping)
 assets=[]
 for r in manifest['files']:
  p=ROOT/manifest['destination']/r['path'];assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes'];assets.append({**r,'path':str(p.relative_to(ROOT))})
 assert {str(p.relative_to(ROOT/manifest['destination'])) for p in (ROOT/manifest['destination']).rglob('*') if p.is_file()}=={r['path'] for r in manifest['files']}
 assert set(files)=={str(p.relative_to(ROOT)) for directory in ['cab','msi'] for p in (ROOT/'evidence/baseline/extracted'/directory).iterdir() if p.is_file()}
 assert set(maps)=={Path(p).name for p in files if '/cab/' in p}
 components={r['Component']:r for r in tables['Component']};directories={r['Directory']:r for r in tables['Directory']}
 rows=[]
 for path,r in files.items():
  p=ROOT/path;data=p.read_bytes();assert sha(p)==r['sha256'] and len(data)==r['bytes'];name=p.name
  pe=data[:2]==b'MZ'
  if pe:
   off=struct.unpack_from('<I',data,60)[0];assert data[off:off+4]==b'PE\0\0';assert path in pes and pes[path]['sha256']==r['sha256']
  else: assert path not in pes
  row={'path':path,'bytes':len(data),'sha256':r['sha256'],'container':'CAB' if '/cab/' in path else 'MSI_STREAM','classification':'PE' if pe else 'NON_PE','classification_scope':'MZ plus PE signature; NON_PE does not assert semantic file type','inventory_source':base+'file-inventory.json'}
  if '/cab/' in path:
   m=maps[name];assert m['sha256']==r['sha256'] and m['FileSize']==len(data) and m['cab_exists'] and m['size_matches'];c=components[m['Component_']];assert c['Directory_'] in directories
   features=[f for f in tables['FeatureComponents'] if f['Component_']==m['Component_']]
   assert features
   row['installation']={'file':m,'component':c,'directory':directories[c['Directory_']],'features':features,'source':base+'msi-decoded/tables.json','target_semantics':'symbolic declaration only; not installed path observation'}
  if path in pes:
   d=pes[path]; assert d['exit_code']==0
   row['declared_dependencies']={'imports':d['imports'],'clr_directory':d['clr_directory'],'raw':d['raw'],'raw_sha256':sha(ROOT/d['raw']),'source':base+'dependencies/inventory.json'}
   row['managed_metadata']=managed.get(path)
   row['actual_binding']={'status':'NOT_RUN','stage':'B02','unknown':'Resolved paths, versions, loader selection and executed calls'}
  rows.append(row)
 assert set(pes)=={r['path'] for r in rows if r['classification']=='PE'}
 assert set(managed)=={p for p,d in pes.items() if d['clr_directory']!=[0,0]}
 streams=[]
 for s in ole['streams']:
  p=ROOT/'evidence/baseline/extracted/msi'/s['name'];assert sha(p)==s['sha256'] and p.stat().st_size==s['size']; streams.append({'name':s['name'],'bytes':s['size'],'sha256':s['sha256'],'source_msi':ole['source'],'source_msi_sha256':ole['source_sha256'],'source_evidence':base+'ole-bindings/audit.json'})
 assert sha(ROOT/ole['source'])==ole['source_sha256']
 binary=[]
 for b in ole['binary_rows']:
  name=b['values']['Name'];s=next(s for s in streams if s['name']=='Binary.'+name);path='evidence/baseline/extracted/msi/'+s['name'];binary.append({**s,'binary_table_row':b,'classification':next(r['classification'] for r in rows if r['path']==path),'actions':[b for b in ole['bindings'] if b['binary_stream']==s['name']],'runtime_status':'NOT_RUN'})
 assert len(binary)==len(tables['Binary']) and {b['name'] for b in binary}=={s['name'] for s in streams if s['name'].startswith('Binary.')}
 # Preserve every root asset, including shipped runtime installers. Do not infer nested installation results.
 shipped=[{**r,'scope':'Supplied root asset; nested runtime install payloads not recursively inventoried or executed','runtime_binding':'NOT_RUN'} for r in assets if r['path'].lower().endswith(('.exe','.msi'))]
 refs={p:sha(ROOT/p) for p in ['evidence/scheduler-reviews/20261018T091825Z/review.md','evidence/scheduler-reviews/20261018T092331Z/review.md','evidence/scheduler-reviews/20261018T093700Z/review.md','evidence/scheduler-reviews/20261018T100100Z/review.md']}
 checks={'asset_files':len(assets),'extracted_files':len(rows),'cab_payloads':len(maps),'msi_streams':len(streams),'components':len(components),'directories':len(directories),'feature_component_mappings':len(tables['FeatureComponents']),'pe':len(pes),'non_pe':sum(r['classification']=='NON_PE' for r in rows),'cab_pe':sum(r['classification']=='PE' and r['container']=='CAB' for r in rows),'embedded_binary':len(binary),'managed_pe':len(managed),'all_inventory_hashes':'MATCH','cab_file_set':'MATCH','pe_dependency_set':'MATCH','managed_set':'MATCH'}
 assert all(sha(ROOT/p)==h for p,h in frozen.items())
 result={'goal_id':'HWK-G001','stage_item_id':'B01-02','task_card':'HWK-000022','status':'PARTIAL','candidate_status':'READY_FOR_INDEPENDENT_REVIEW','goal':assignment['item']['goal'],'done_when':assignment['item']['done_when'],'evidence_type':'STATIC_PACKAGE_RECONCILIATION','inputs_sha256':frozen,'historical_independent_sources_sha256':refs,'assets':assets,'files':rows,'streams':streams,'embedded_binary':binary,'components':tables['Component'],'directories':tables['Directory'],'feature_components':tables['FeatureComponents'],'media':tables['Media'],'shipped_installers':shipped,'checks':checks,'coverage':{'payloads':'Every CAB file is bijectively mapped to File, Component, Directory and feature declaration','streams':'Every extracted MSI stream is covered by historical source-byte OLE audit and current hash verification','non_file_components':[c for k,c in components.items() if k not in {m['Component_'] for m in mapping}],'declaration_vs_binding':'Imports, AssemblyRef, symbolic paths and sequence declarations are static; all actual bindings NOT_RUN'},'not_verified':[{'stage':'B02','scope':'Installation success, actual path/feature selection, prerequisites, runtime bindings and nested bundled runtime installer execution'},{'stage':'B03','scope':'Complete application functional inventory; package file inventory is not feature inventory'},{'stage':'P/E/R','scope':'Business calculation, solver behavior, reports, project round trips and final replacement'}],'scope_limits':['Root package assets, target MSI streams and external CAB are closed here; nested SQL/VC redistributable packages have root hashes only, not recursive file inventories. B02 must select and verify required installed runtime files.','Non-PE classification is a signature check only; content semantics not inferred.','Historical REA Evidence retains original acquisition version; this run uses ordinary file hashing and JSON reconciliation.'],'independent_review':{'status':'NOT_RUN','required':'Reviewer independently reruns reconciliation and source checks before deciding package PASS'},'rea':{'expected_package_version':pre['latest'],'actual_mcp_status':'BLOCKED','response':'MCP tool call requires approval, but approval policy is never','new_analysis':'NOT_RUN; no new binary analysis needed'},'rerun':'python3 scripts/check-component-baseline.py --out <fresh-directory>','check_results':'evidence/stages/B01/B01-02/checks.json','outputs':['evidence/stages/B01/B01-02/work-package.json','evidence/stages/B01/B01-02/checks.json']}
 (out/'work-package.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(checks,ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'evidence/stages/B01/B01-02');run(p.parse_args().out)
