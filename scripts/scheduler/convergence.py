"""Keep package acceptance separate from the agent's next executable increment."""
import copy,json,subprocess
from pathlib import Path
import cards,check_rea,stages,blockers
from review_checks import verify_review_checks

def enabled(root):
 p=root/'planning/convergence-policy.json'
 return p.exists() and json.loads(p.read_text()).get('enabled') is True

def assignment(root,reason='No immediately dispatchable package'):
 c,p,t=stages.load(root);sid=t['active_task']
 return {'kind':'continuation_plan','stage_id':sid,'reason':reason,'contract':next(s for s in c['stages'] if s['id']==sid),'progress':p['stages'][sid],'contract_version':c['version']}

def apply(root,a,report,folder):
 c,p,t=stages.load(root);sid=a['stage_id']
 contract=next(s for s in c['stages'] if s['id']==sid)
 if c['version']!=a['contract_version'] or contract!=a['contract'] or p['stages'][sid]!=a['progress'] or t['active_task']!=sid:raise ValueError('Continuation inputs changed during judgment')
 decision=report.get('decision')
 if decision not in ('CONTINUE','WAIT_EXTERNAL','STOP_SAFETY') or not report.get('reason'):raise ValueError('Invalid continuation judgment')
 verify_review_checks(report,folder/'planner.jsonl',require_success=decision=='CONTINUE')
 import assurance
 if not report.get('evidence'):raise ValueError('Continuation missing sources')
 assurance.file_hashes(root,report['evidence'])
 if decision=='CONTINUE':
  item=next((i for i in contract['work_items'] if i['id']==report.get('stage_item_id')),None)
  if not item or item.get('requires_decomposition') or not report.get('execution_focus'):raise ValueError('Continuation needs a concrete executable leaf and focus')
  entry=p['stages'][sid]['items'][item['id']]
  if entry['status']=='PASS' or not all(p['stages'][sid]['items'][dep]['status']=='PASS' for dep in item.get('depends_on',[])):raise ValueError('Continuation cannot bypass dependencies or reopen PASS')
  prior={k:copy.deepcopy(v) for k,v in entry.items() if k!='dispatch_history'}
  entry.setdefault('dispatch_history',[]).append({'at':cards.stamp(),'prior':prior,'judgment':str((folder/'planner-final.txt').relative_to(root))})
  # Keep the independent verdict, evidence and rounds. Only dispatch readiness changes.
  entry['dispatch_status']='ready';entry['execution_focus']=report['execution_focus']
  cards.save(root/'planning/stage-progress.json',p)
 return decision

def plan(root,run_agent,a=None,pause_reason=None):
 base=root/'evidence/scheduler';a=a or assignment(root)
 folder=base/(cards.stamp().replace(':','').replace('.','')+'-continuation');folder.mkdir()
 cards.save(folder/'continuation-assignment.json',a)
 cards.create(root,folder,task_id=a['stage_id'],goal='判断目标收敛与下一张可执行卡',track='continuation',session_roles=[('planner','续接主控')])
 try:
  check_rea.check(folder/'rea-preflight')
  asset=subprocess.run(['/usr/bin/python3','scripts/verify-installer.py'],cwd=root,capture_output=True,text=True)
  (folder/'asset-before.txt').write_text(asset.stdout+asset.stderr)
  if asset.returncode:raise ValueError('Original asset verification failed before continuation')
  prompt=(root/'scripts/scheduler/convergence-plan.txt').read_text()+'\n本卡：'+str((folder/'continuation-assignment.json').relative_to(root))
  run_agent('planner',folder,prompt=prompt,sandbox='read-only',schema=root/'scripts/scheduler/convergence-result.schema.json')
  asset=subprocess.run(['/usr/bin/python3','scripts/verify-installer.py'],cwd=root,capture_output=True,text=True)
  (folder/'asset-after.txt').write_text(asset.stdout+asset.stderr)
  if asset.returncode:raise ValueError('Original asset verification failed after continuation')
  report=json.loads((folder/'planner-final.txt').read_text());decision=apply(root,a,report,folder)
  state={'status':'ready' if decision=='CONTINUE' else 'waiting_external' if decision=='WAIT_EXTERNAL' else 'blocked','at':cards.stamp(),'reason':report['reason'],'run':str(folder),'no_progress':0,'continuation_decision':decision}
  pause=base/'PAUSED'
  if decision=='CONTINUE':
   if a.get('incident'):
    blockers.close_event(root,root/a['incident'],status='resolved',reason='已核实可续接，调度阻塞销项；原包完成情况仍由独立验收判断。'+report['reason'],evidence=report['evidence']+[str((folder/'planner-final.txt').relative_to(root))],by=json.loads((folder/'task-card.json').read_text())['id'])
   if pause.exists() and pause_reason is not None and pause.read_text()==pause_reason:pause.unlink()
  else:pause.write_text(report['reason']+'\n')
  cards.save(base/'state.json',state)
 except Exception as exc:
  state={'status':'error','reason':str(exc),'at':cards.stamp(),'run':str(folder)}
  cards.save(base/'state.json',state);(base/'PAUSED').write_text(str(exc)+'\n')
 finally:
  cards.finish(root,folder,state);(base/'active.json').unlink(missing_ok=True)

def recover_paused(root,run_agent):
 base=root/'evidence/scheduler';pause=base/'PAUSED'
 if not pause.exists() or pause.read_text().startswith('Paused by user'):return
 ref=base/'blocker-current.json'
 if not ref.exists():return
 incident_path=root/json.loads(ref.read_text())['incident'];incident=json.loads(incident_path.read_text())
 if incident.get('status')!='action_required' or incident.get('continuation_claimed'):return
 incident['continuation_claimed']=True;cards.save(incident_path,incident)
 a=assignment(root,incident.get('resolution',{}).get('reason',incident['reason']));a['incident']=str(incident_path.relative_to(root))
 plan(root,run_agent,a,pause.read_text())
