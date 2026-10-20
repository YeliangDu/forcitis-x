"""Audit frozen package bindings locally; never establishes remote availability."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def audit():
 rows=json.loads((ROOT/'evidence/baseline/b01/msi-decoded/file-map.json').read_text())
 old=json.loads((ROOT/'evidence/runtime/ecs-20261018/summary.json').read_text())
 env=json.loads((ROOT/'evidence/runtime/workflow-reset/environment/stdout').read_text(encoding='utf-8-sig'))
 selected=[]
 for name,expected in [('XWall.exe',old['client']['SHA256']),('门窗计算示例1.cwx',next(x['SHA256'] for x in env['Samples'] if x['FullName'].endswith('门窗计算示例1.cwx')))]:
  matches=[r for r in rows if r['symbolic_target'].endswith('/'+name)]
  assert len(matches)==1,(name,len(matches))
  r=matches[0];p=ROOT/'evidence/baseline/extracted/cab'/r['File']
  h=hashlib.sha256(p.read_bytes()).hexdigest()
  assert h==r['sha256']==expected.lower(),name
  selected.append({'name':name,'path':str(p.relative_to(ROOT)),'sha256':h,'prior_runtime_hash_matches':True})
 return {'status':'PASS','evidence_type':'LOCAL_FROZEN_INPUT_RECHECK','bindings':selected,'limitations':['Prior runtime records are historical; current SSH, desktop, isolation and dependencies are NOT verified.']}
if __name__=='__main__':
 print(json.dumps(audit(),ensure_ascii=False,indent=2))
