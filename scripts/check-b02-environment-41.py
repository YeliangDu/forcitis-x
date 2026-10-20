"""Verify live B02-01 collection; does not grant independent acceptance."""
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
REL=Path('evidence/stages/B02/B02-01/attempt-41')
def audit():
 p=BASE/REL
 x=json.loads((p/'environment-final/stdout').read_text(encoding='utf-8-sig'))
 pre=json.loads((p/'preflight/stdout').read_text(encoding='utf-8-sig'))
 assert json.loads((p/'environment-final/exit.json').read_text())['exit_code']==0
 assert pre['TargetExists'] is False and pre['SourceReparseCount']==0
 assert x['Root']==r'C:\hwk-modern\HWK-000041-B02-01'
 assert not x['ReparsePoints'] and not x['OutputFiles']
 for a in x['Ancestors']: assert 'ReparsePoint' not in a['Attributes']
 def manifest(rows):
  d={r['Path']:(r['Length'],r['SHA256']) for r in rows}
  assert len(d)==len(rows)>0
  return d
 assert manifest(x['Before'])==manifest(x['After'])==manifest(x['Client'])
 exe=next(r for r in x['Client'] if r['Path']==r'\XWall.exe')
 assert exe['SHA256']=='76838A839C5EF262499D6315570DA26FFD59DA7BB29ED616ADAA6B4BFE7221E5'
 assert x['SampleWorkingHash']==x['SampleSourceHash']=='2FFA32CB256324AE610C2215BFE554DDB42BA0CBB06108188C6727B2F060FBE3'
 assert any('administrator' in s.lower() and 'Active' in s for s in x['Sessions'])
 for key in ['OS','Culture','SystemLocale','Timezone','Fonts','Runtimes','DotNet','LocalDBInfo','Metadata','Cleanup']:assert x[key],key
 readback=json.loads((p/'readback/stdout').read_text(encoding='utf-8-sig'))
 assert len(readback['Directories'])==4
 assert all(not (d['Attributes'] & 1024) for d in readback['Directories'])
 assert readback['ClientHash']==readback['SourceHash']==exe['SHA256']
 db=json.loads((p/'localdb-encoding-probe/stdout').read_text(encoding='utf-8-sig'))
 assert db['ExitCode']==0 and db['BinaryVersion']['ProductVersion']=='11.0.7001.0'
 assert any('正在运行' in line for line in db['Info'])
 assert x['Cost']['Status']=='UNKNOWN'
 assert x['Cleanup']['AllowedDirectory']==x['Root'] and not x['Cleanup']['AllowedTasks']
 return {'status':'PASS','meaning':'collection consistency only; independent package acceptance pending','files':len(x['Client']),'fonts':len(x['Fonts']),'runtimes':len(x['Runtimes']),'metadata':x['Metadata'],'limitations':['Database SQL connectivity and application license not tested','No original calculation/report/save/reopen in B02-01']}
if __name__=='__main__':print(json.dumps(audit(),ensure_ascii=False,indent=2))
