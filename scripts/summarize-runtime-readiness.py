#!/usr/bin/env python3
"""Join retained static evidence; no target execution or runtime resolution."""
import hashlib,json,shutil,platform
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('evidence/baseline/b01')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def collect(root=ROOT):
    inputs=['msi-decoded/tables.json','msi-decoded/file-map.json','dependencies/inventory.json','clr-independent/audit.json','datainfo/decoded.json']
    docs={f:json.loads((root/BASE/f).read_text()) for f in inputs}
    deps=docs['dependencies/inventory.json']['pe']; files=docs['msi-decoded/file-map.json']
    mapped={r['File']:r for r in files}
    for r in deps:
        assert digest(root/r['source'])==r['sha256'],r['source']
    def basename(r): return r['target_label'].rsplit('/',1)[-1].casefold()
    joins=[]
    for r in deps:
        for name in r['imports']:
            candidates=[p for p in deps if basename(p)==name.casefold()]
            joins.append({'importer':r['source'],'importer_label':r['target_label'],'importer_format':r['format'],'import_name':name,'package_candidates':[{'source':p['source'],'target_label':p['target_label'],'format':p['format'],'same_format':p['format']==r['format'],'sha256':p['sha256']} for p in candidates], 'classification':'PACKAGE_BASENAME_CANDIDATE' if candidates else 'NO_PE_BASENAME_CANDIDATE','runtime_binding':'NOT_RUN'})
    managed=[]
    for r in docs['clr-independent/audit.json']['records']:
        assert digest(root/r['source'])==r['source_sha256']
        managed.append({'source':r['source'],'symbolic_target':mapped[Path(r['source']).name]['symbolic_target'],'framework_declarations':[a['framework'] for a in r['attributes']],'runtime_binding':'NOT_RUN'})
    properties={r['Property']:r['Value'] for r in docs['msi-decoded/tables.json']['tables']['Property']}
    xwall=next(r for r in files if r['symbolic_target'].endswith('/XWall.exe'))
    return {'status':'PARTIAL','evidence_type':'RETAINED_STATIC_EVIDENCE_JOIN','inputs':[{'path':str(BASE/f),'sha256':digest(root/BASE/f)} for f in inputs],'versions':{'package_product_version':properties['ProductVersion'],'xwall_file_version':xwall['Version'],'installed_version':None},'pe_count':len(deps),'import_edge_count':len(joins),'import_edges':joins,'managed_declarations':managed,'framework_properties':docs['dependencies/inventory.json']['framework_properties'],'database_selectors':[{'source':r['source'],'selectors':r['selectors']} for r in docs['datainfo/decoded.json']['sources']],'unknowns':['Basename candidates are not Windows loader resolution; paths, architecture, exports and transitive binding need runtime verification.','No candidate does not mean a DLL is missing from Windows or an installation requirement.','Plugin framework declarations do not set the main product minimum framework.','Database engine/provider/version, CheckFX/HWKInstallDo effects, OS support, fonts and license remain unverified.'],'runtime_status':'NOT_RUN'}
if __name__=='__main__':
    out=ROOT/BASE/'runtime-readiness'; out.mkdir(exist_ok=True)
    result=collect(); (out/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    probes={n:shutil.which(n) for n in ['aliyun','acs','virsh','VBoxManage','prlctl','qemu-system-x86_64','wine','pwsh','ssh','rea']}
    (out/'local-tools.json').write_text(json.dumps({'evidence_type':'LOCAL_PATH_DISCOVERY','system':platform.system(),'machine':platform.machine(),'tools':probes,'cloud_resource_query':'NOT_RUN','limitations':'PATH-only bounded discovery; no credentials read, no remote query, no proof that Windows or cloud resources do not exist.'},indent=2)+'\n')
    print(json.dumps({'pe_count':result['pe_count'],'imports':result['import_edge_count'],'candidate_edges':sum(bool(r['package_candidates']) for r in result['import_edges']),'managed':len(result['managed_declarations'])}))
