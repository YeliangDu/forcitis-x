#!/usr/bin/env python3
"""launchd tick: one serialized execution/review cycle, fresh CLI sessions."""
import argparse, datetime, fcntl, hashlib, json, os, signal, subprocess, sys, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/scheduler'
CONFIG=ROOT/'scripts/scheduler'
sys.path.insert(0,str(CONFIG))
import cards
import check_rea
import stages
import assurance
import blockers
import recovery
import convergence
CODEX='/Users/yeliang/.nvm/versions/node/v24.18.0/bin/codex'

def write(path,data):
 tmp=path.with_suffix('.tmp'); tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n'); tmp.replace(path)

def hashes():
 return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
         for p in (ROOT/'evidence').rglob('*') if p.is_file() and BASE not in p.parents}

def agent_permissions(role,sandbox,workspace):
 # Isolated parallel workspaces keep their original permission boundary.
 if workspace!=ROOT:return ['-s',sandbox]
 name='hwk_read_network' if sandbox=='read-only' else 'hwk_work_network'
 parent=':read-only' if sandbox=='read-only' else ':workspace'
 return ['-c','default_permissions="'+name+'"','-c','permissions.'+name+'.extends="'+parent+'"','-c','permissions.'+name+'.network.enabled=true']

def run_agent(role,folder,*,workspace=None,prompt=None,active_name="active.json",sandbox="workspace-write",schema=None):
 workspace=workspace or ROOT
 options=agent_permissions(role,sandbox,workspace)
 cmd=[CODEX,'-c','approval_policy="never"']+options+['exec','-C',str(workspace),'--skip-git-repo-check','--json','--color','never','-o',str(folder/(role+'-final.txt'))]
 if role=='reviewer' or schema is not None: cmd+=['--output-schema',str(schema or CONFIG/('stage-result.schema.json' if (folder/'stage-assignment.json').exists() else 'result.schema.json'))]
 cmd+=['-']
 env=os.environ.copy(); env['CODEX_HOME']=str(ROOT/'.codex-runtime'); env['PATH']=str(Path(CODEX).parent)+':/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin'
 with (folder/(role+'.jsonl')).open('w') as out,(folder/(role+'.stderr')).open('w') as err:
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=out,stderr=err,cwd=workspace,env=env,start_new_session=True)
  card=json.loads((folder/'task-card.json').read_text())
  write(BASE/active_name,{'role':role,'title':card['sessions'][role]['title'],'card_id':card['id'],'pid':p.pid,'run':str(folder),'started_at':now()})
  try:
   header='任务卡：'+card['sessions'][role]['title']+'\n流水卡路径：'+str(folder/'task-card.json')+'\n'
   if (folder/'assurance-assignment.json').exists():header+='独立目标审查对象：\n'+(folder/'assurance-assignment.json').read_text()+'\n'
   if (folder/'stage-assignment.json').exists():header+='本轮唯一工作包（先读此合同，完成done_when才可通过）：\n'+(folder/'stage-assignment.json').read_text()+'\n'
   p.stdin.write(header.encode()+(prompt.encode() if prompt is not None else (CONFIG/(role+'.txt')).read_bytes())); p.stdin.close()
   deadline=time.monotonic()+5400
   named=False
   while p.poll() is None:
    if not named:
     cards.sync(ROOT,folder,CODEX)
     c=json.loads((folder/'task-card.json').read_text()); named=c['sessions'][role]['name_status']=='set'
    if time.monotonic()>deadline: raise subprocess.TimeoutExpired(cmd,5400)
    time.sleep(1)
   cards.sync(ROOT,folder,CODEX); cards.archive(ROOT,folder)
  except subprocess.TimeoutExpired:
   os.killpg(p.pid,signal.SIGTERM)
   try: p.wait(timeout=20)
   except subprocess.TimeoutExpired: os.killpg(p.pid,signal.SIGKILL); p.wait()
   raise RuntimeError(role+' exceeded 90 minute watchdog; inspect logs before resume')
  if p.returncode: raise RuntimeError(role+' exit '+str(p.returncode)+'; inspect stderr/JSONL')

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()


def run_assurance(assignment):
 folder=BASE/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'-assurance');folder.mkdir()
 label='WBS对整体Goal的覆盖与可组合审查' if assignment['kind']=='plan_audit' else assignment['stage_id']+'阶段达成与总目标贡献独立审查'
 card=cards.create(ROOT,folder,task_id=assignment['stage_id'],goal=label,track='assurance',session_roles=[('assessor','独立目标审查')])
 write(folder/'assurance-assignment.json',assignment)
 try:
  check_rea.check(folder/'rea-preflight')
  check=subprocess.run(['/usr/bin/python3','scripts/verify-installer.py'],cwd=ROOT,capture_output=True,text=True)
  (folder/'asset-before.txt').write_text(check.stdout+check.stderr)
  if check.returncode:raise RuntimeError('Asset check failed before goal audit')
  write(BASE/'state.json',{'status':'running','run':str(folder),'at':now(),'review_kind':assignment['kind']})
  run_agent('assessor',folder,prompt=(CONFIG/'assessor.txt').read_text(),sandbox='read-only',schema=CONFIG/'assurance-result.schema.json')
  report=json.loads((folder/'assessor-final.txt').read_text())
  check=subprocess.run(['/usr/bin/python3','scripts/verify-installer.py'],cwd=ROOT,capture_output=True,text=True)
  (folder/'asset-after.txt').write_text(check.stdout+check.stderr)
  if check.returncode:raise RuntimeError('Asset check failed after goal audit')
  result=assurance.apply(ROOT,assignment,report,card['id'],folder/'assessor.jsonl')
  if result['outcome']!='continue':(BASE/'PAUSED').write_text(result['reason']+'\n')
  write(BASE/'state.json',{'status':result['outcome'],'result':result,'run':str(folder),'at':now(),'no_progress':0})
 except Exception as exc:
  (BASE/'PAUSED').write_text(str(exc)+'\n');write(BASE/'state.json',{'status':'error','reason':str(exc),'run':str(folder),'at':now()})
 finally:
  cards.finish(ROOT,folder,json.loads((BASE/'state.json').read_text()));(BASE/'active.json').unlink(missing_ok=True)

def main():
 parser=argparse.ArgumentParser(); parser.add_argument('action',choices=['tick','status','pause','resume']); args=parser.parse_args()
 BASE.mkdir(parents=True,exist_ok=True)
 pause=BASE/'PAUSED'
 if args.action=='pause': pause.write_text('Paused by user at '+now()+'; current cycle may finish.\n'); return
 if args.action=='resume':
  pause.unlink(missing_ok=True); write(BASE/'state.json',{'status':'ready','no_progress':0,'at':now()}); return
 if args.action=='status':
  for name in ('PAUSED','state.json','active.json'):
   p=BASE/name
   if p.exists(): print(name+': '+p.read_text())
  return
 with (BASE/'runner.lock').open('a') as lock:
  try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError: return
  for old in sorted(BASE.glob('*/task-card.json')):
   cards.sync(ROOT,old.parent,CODEX); cards.archive(ROOT,old.parent)
  if pause.exists():
   paused_state=json.loads((BASE/'state.json').read_text()) if (BASE/'state.json').exists() else {}
   if convergence.enabled(ROOT) and paused_state.get('continuation_decision') in ('WAIT_EXTERNAL','STOP_SAFETY'):return
   blockers.diagnose(ROOT,run_agent)
   if convergence.enabled(ROOT):convergence.recover_paused(ROOT,run_agent)
   else:recovery.handle(ROOT,run_agent)
   return
  state=json.loads((BASE/'state.json').read_text()) if (BASE/'state.json').exists() else {}
  # A prior supervisor crash may have left a live CLI in its own process group.
  active=BASE/'active.json'
  if active.exists():
   pause.write_text('Unclean previous run; inspect active.json and processes before resume.\n'); return
  try:assignment=convergence.assignment(ROOT,'连续未见可核实增量，需要agent换方法') if convergence.enabled(ROOT) and state.get('no_progress',0)>=2 else stages.select(ROOT)
  except stages.StageBlocked as exc:
   pause.write_text(str(exc)+'\n');write(BASE/'state.json',{'status':'blocked','reason':str(exc),'at':now()});return
  if assignment and assignment.get('kind')=='continuation_plan':
   convergence.plan(ROOT,run_agent,assignment);return
  if assignment and assignment.get('kind') in ('plan_audit','stage_audit'):
   run_assurance(assignment);return
  folder=BASE/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'); folder.mkdir()
  cards.create(ROOT,folder,goal=(assignment['item']['id']+' · '+assignment['item']['title']) if assignment else None,stage_item_id=assignment['item']['id'] if assignment else None)
  if assignment:write(folder/'stage-assignment.json',assignment)
  before=hashes()
  try:
   check=subprocess.run(['/usr/bin/python3','scripts/verify-installer.py'],cwd=ROOT,capture_output=True,text=True)
   (folder/'asset-before.txt').write_text(check.stdout+check.stderr)
   if check.returncode: raise RuntimeError('Asset check failed before cycle')
   check_rea.check(folder/'rea-preflight')
   write(BASE/'state.json',{'status':'running','run':str(folder),'at':now()})
   run_agent('worker',folder)
   run_agent('reviewer',folder)
   result=json.loads((folder/'reviewer-final.txt').read_text())
   if result.get('outcome') not in ('continue','blocked','complete') or not isinstance(result.get('evidence'),list): raise RuntimeError('Invalid reviewer result')
   after=hashes(); changed=[x for x in result['evidence'] if x in after and before.get(x)!=after[x]]
   check=subprocess.run(['/usr/bin/python3','scripts/verify-installer.py'],cwd=ROOT,capture_output=True,text=True)
   (folder/'asset-after.txt').write_text(check.stdout+check.stderr)
   if check.returncode: raise RuntimeError('Asset check failed after cycle')
   if assignment:stages.apply(ROOT,assignment,result,json.loads((folder/'task-card.json').read_text())['id'])
   count=0 if result.get('new_evidence') is True and changed else state.get('no_progress',0)+1
   outcome=result['outcome']
   if outcome=='complete':
    check=subprocess.run(['/usr/bin/python3','scripts/check-acceptance.py'],cwd=ROOT,capture_output=True,text=True)
    (folder/'completion-gate.txt').write_text(check.stdout+check.stderr)
    if check.returncode: raise RuntimeError('Reviewer completion rejected by acceptance gate')
   if outcome!='continue' or (count>=2 and not convergence.enabled(ROOT)): pause.write_text(result['reason']+'\n'+('Two cycles without changed evidence.\n' if count>=2 else ''))
   write(BASE/'state.json',{'status':outcome,'no_progress':count,'changed_evidence':changed,'result':result,'run':str(folder),'at':now()})
  except Exception as exc:
   pause.write_text(str(exc)+'\n'); write(BASE/'state.json',{'status':'error','reason':str(exc),'run':str(folder),'at':now()})
  finally:
   cards.finish(ROOT,folder,json.loads((BASE/'state.json').read_text()))
   active.unlink(missing_ok=True)

if __name__=='__main__': main()
