#!/usr/bin/env python3
"""Reconcile existing version evidence; uses existing MSI reader and 7z, no PE parser."""
import hashlib, importlib.util, json, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/stages/B01/B01-01'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads((ROOT/p).read_text())
def versions(s):
 return [line.removeprefix('Comment = ') for line in s.splitlines() if line.startswith(('Comment = FileVersion:', 'FileVersion:', 'ProductVersion:'))]
def run():
 OUT.mkdir(parents=True,exist_ok=True)
 inputs=['evidence/baseline/installer-manifest.json','evidence/baseline/b01/file-inventory.json','evidence/baseline/b01/msi-decoded/summary.json','evidence/baseline/b01/msi-decoded/tables.json','evidence/baseline/b01/msi-decoded/file-map.json','evidence/scheduler/20261018T111131027072Z/stage-assignment.json','evidence/scheduler/20261018T111131027072Z/rea-preflight/version-check.json','scripts/audit-msi-streams.py','scripts/check-version-baseline.py']
 frozen={p:sha(ROOT/p) for p in inputs}
 manifest=load(inputs[0]); inv=load(inputs[1]); summary=load(inputs[2]); mapping={r['File']:r for r in load(inputs[4])}
 assets=[]
 base=ROOT/manifest['destination']
 assert {str(p.relative_to(base)) for p in base.rglob('*') if p.is_file()}=={r['path'] for r in manifest['files']}
 for f in manifest['files']:
  p=base/f['path']; assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes']; assets.append({'path':str(p.relative_to(ROOT)),**{k:f[k] for k in ('bytes','sha256')}})
 spec=importlib.util.spec_from_file_location('msiaudit',ROOT/'scripts/audit-msi-streams.py'); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 audit=m.audit(comparison=load(inputs[3])['tables'])
 props={r['values']['Property']:r['values']['Value'] for r in audit['tables']['Property']}
 assert props==summary['properties']
 pe=[];raw=OUT/'live-pe-listings';raw.mkdir(exist_ok=True)
 for f in inv['files']:
  p=ROOT/f['path'];assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes']
  if f.get('pe_metadata',{}).get('Type') != 'PE': continue
  listing=ROOT/f['listing'];frozen[f['listing']]=sha(listing)
  cp=subprocess.run(['7z','l',str(p)],capture_output=True,text=True);assert cp.returncode==0,cp.stderr
  target=raw/(p.name+'.txt');target.write_text(cp.stdout);assert versions(cp.stdout)==versions(listing.read_text()),f['path']
  row=mapping.get(p.name,{})
  pe.append({'path':f['path'],'sha256':f['sha256'],'original_name':row.get('FileName',f.get('pe_metadata',{}).get('Name')),'symbolic_target':row.get('symbolic_target'),'msi_file_version':row.get('Version'),'resource_versions':versions(cp.stdout),'recorded_metadata':f.get('pe_metadata',{}),'historical_listing':f['listing'],'live_listing':str(target.relative_to(ROOT)),'comparison':'MATCH','absence_meaning':'Empty resource_versions means 7z reported none; not proof no version resource exists.'})
 vendor_pe=[]
 for asset in assets:
  if not asset['path'].lower().endswith('.exe'): continue
  cp=subprocess.run(['7z','l',str(ROOT/asset['path'])],capture_output=True,text=True);assert cp.returncode==0,cp.stderr
  target=raw/(Path(asset['path']).name+'.vendor.txt');target.write_text(cp.stdout)
  vendor_pe.append({**asset,'resource_versions':versions(cp.stdout),'live_listing':str(target.relative_to(ROOT)),'source':'Current ordinary 7z static listing; no historical comparison claimed.'})
 main=next(r for r in pe if r['recorded_metadata'].get('Name')=='XWall.exe')
 assert main['msi_file_version']=='5.4.25.1209'
 after={r['path']:sha(ROOT/r['path']) for r in assets};assert all(after[r['path']]==r['sha256'] for r in assets)
 assert all(sha(ROOT/p)==h for p,h in frozen.items())
 result={'goal_id':'HWK-G001','stage_item_id':'B01-01','task_card':'HWK-000021','status':'PARTIAL','candidate_status':'READY_FOR_INDEPENDENT_REVIEW','evidence_type':'STATIC_PACKAGE_RECONCILIATION','goal':load(inputs[5])['item']['goal'],'inputs_sha256':frozen,'assets':assets,'baseline_selection':{'rule':'Exact complete installer manifest SHA-256 set is identity; labels do not override bytes.','manifest_sha256':frozen[inputs[0]],'directory_label':manifest['destination'],'directory_label_version':'5.4.25.1220','directory_label_source':inputs[0],'msi_properties':{k:props[k] for k in ['ProductName','ProductVersion','ProductCode','UpgradeCode']},'msi_source':'XWallClientX64.msi → extracted !Property → existing audit-msi-streams.py reader','main_payload':main},'pe_versions':pe,'vendor_pe_versions':vendor_pe,'msi_stream_inputs':audit['inputs'],'checks':{'asset_files':len(assets),'extracted_files_hashed':len(inv['files']),'pe_listings_replayed':len(pe),'msi_property_comparison':'MATCH','input_integrity':'MATCH'},'differences':[{'sources':['directory label','MSI Property.ProductVersion','XWall.exe MSI File.Version','XWall.exe PE version strings'],'values':['5.4.25.1220',props['ProductVersion'],main['msi_file_version'],main['resource_versions']],'interpretation':'Distinct literal declarations; no normalization or release-date ordering inferred.','cause':'UNKNOWN','runtime_display':'NOT_RUN'}],'historical_independent_review':['evidence/scheduler-reviews/20261018T091825Z/review.md','evidence/scheduler-reviews/20261018T095000Z/review.md','evidence/scheduler-reviews/20261018T105500Z/review.md'],'independent_review':{'status':'NOT_RUN','required':'External reviewer reruns this command and independently checks all done_when clauses; historical reviews do not certify this package.'},'rerun':'python3 scripts/check-version-baseline.py','rea':{'expected_package_version':'6.7.0','actual_mcp_status':'BLOCKED','message':'MCP tool call requires approval, but approval policy is never','scope':'No REA analysis performed this round; listings are ordinary 7z output. Old Evidence retains its original version.'},'not_verified':['Difference causes and runtime displayed version','Installation, actual loading/binding and all business behavior: B02 or later','Vendor globally latest release; only supplied asset baseline selected'],'architecture_solver':'NOT_RUN; no architecture/algorithm choices','outputs':['evidence/stages/B01/B01-01/work-package.json','evidence/stages/B01/B01-01/live-pe-listings/']}
 (OUT/'work-package.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result['checks'],ensure_ascii=False))
if __name__=='__main__':run()
