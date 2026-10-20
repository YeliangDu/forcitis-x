"""Bounded repair -> independent review -> controller registration -> fresh goal audit."""
import copy, hashlib, json, subprocess
from pathlib import Path
import cards, check_rea, stages, blockers
from review_checks import verify_review_checks


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path,default):return json.loads(path.read_text()) if path.exists() else default

def snapshot(root,folder):
 # Only fresh evidence and top-level analysis scripts are writable by a repair session.
 saved={}
 for name in ('planning','scripts','vendor','replica','docs'):
  for p in (root/name).rglob('*'):
   if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and not any(x in p.parts for x in ('node_modules','.git','dist')):
    rel=str(p.relative_to(root));saved[rel]=digest(p)
 for name in ('AGENTS.md','HANDOFF.md','README.md'):
  if (root/name).exists():saved[name]=digest(root/name)
 return saved

def allowed(rel):return Path(rel).parent==Path('scripts') and Path(rel).suffix in ('.py','.mjs','.sh')

def changes(root,before,after):
 changed=[p for p in set(before)|set(after) if before.get(p)!=after.get(p)]
 forbidden=[p for p in changed if not allowed(p)]
 if forbidden:raise ValueError('Repair changed protected files: '+', '.join(sorted(forbidden)))
 return {p:{'before':before.get(p),'after':after.get(p)} for p in sorted(changed)}

def target(root,incident,policy):
 contracts,progress,tasks=stages.load(root)
 contract=next(s for s in contracts['stages'] if s['id']==tasks['active_task'])
 history=read(root/'planning/recovery-history.json',{'entries':[]})['entries']
 if sum(e['stage_id']==contract['id'] for e in history)>=policy['max_incidents_per_stage']:raise ValueError('Stage automatic recovery budget exhausted')
 for item in contract['work_items']:
  state=progress['stages'][contract['id']]['items'][item['id']]
  if incident.get('repair_item_attempts',{}).get(item['id'],0)>=policy.get('max_repairs_per_item',2):continue
  if state['status']=='BLOCKED' and state['rounds']>=item['max_rounds_before_review'] and len(state.get('recoveries',[]))<policy['max_reopens_per_item']:
   return contract['id'],copy.deepcopy(item),copy.deepcopy(state)
 if incident['resolution']['route']=='LOCAL_FIX':return contract['id'],None,None
 raise ValueError('No eligible work package for bounded automatic review')


def register(root,assignment,report,folder):
 """Controller is sole ledger writer. Keep old attempts and immutable goal intact."""
 policy=read(root/'planning/auto-recovery-policy.json',{})
 for rel,sha in assignment['frozen'].items():
  if digest(root/rel)!=sha:raise ValueError('Frozen input changed: '+rel)
 if not report.get('approved'):raise ValueError('Independent recovery review rejected: '+report.get('reason',''))
 verify_review_checks(report,folder/'repair_review.jsonl')
 blockers.validate_report(root,{'route':'LOCAL_FIX','reason':report['reason'],'next_actions':['reviewed'],'release_conditions':['verified'],'evidence':report['evidence']})
 contracts,progress,tasks=stages.load(root)
 item=assignment['item'];sid=assignment['stage_id']
 if report.get('reopen_item_id')!=(item['id'] if item else ''):raise ValueError('Recovery target mismatch')
 if item:
  contract=next(s for s in contracts['stages'] if s['id']==sid)
  current=next(i for i in contract['work_items'] if i['id']==item['id'])
  state=progress['stages'][sid]['items'][item['id']]
  if current!=item or state!=assignment['prior_state']:raise ValueError('Work package changed during review')
  if state['status']!='BLOCKED' or len(state.get('recoveries',[]))>=policy['max_reopens_per_item']:raise ValueError('Work package recovery not eligible')
  state.setdefault('recoveries',[]).append({'prior_state':copy.deepcopy(assignment['prior_state']),'prior_limit':current['max_rounds_before_review'],'report':str((folder/'repair_review-final.txt').relative_to(root)),'reviewer':read(folder/'task-card.json',{})['id'],'reason':report['reason']})
  # Explicit reviewed amendment under user's automatic-repair authorization; never reset rounds.
  current['max_rounds_before_review']=state['rounds']+policy['extra_rounds_per_item']
  current.setdefault('reviewed_recovery',[]).append(str((folder/'recovery-assignment.json').relative_to(root)))
  state['status']='PARTIAL';state['reason']='有限复盘经独立验证登记；原有失败/轮次保留，尚未通过。'+report['reason']
  contracts['version']+=1;progress['contract_version']=contracts['version']
 # A crash during paired writes leaves this marker: next runner must stay paused.
 marker=root/'evidence/scheduler/recovery-transaction.json'
 cards.save(folder/'before-contracts.json',stages.load(root)[0]);cards.save(folder/'before-progress.json',stages.load(root)[1])
 cards.save(marker,{'status':'writing','folder':str(folder),'at':cards.stamp()})
 cards.save(root/'planning/stage-contracts.json',contracts);cards.save(root/'planning/stage-progress.json',progress)
 next_assignment=stages.select(root)
 if not next_assignment:raise ValueError('Recovery produced no legal next assignment')
 history=read(root/'planning/recovery-history.json',{'entries':[]})
 history['entries'].append({'stage_id':sid,'item_id':item['id'] if item else None,'report':str((folder/'repair_review-final.txt').relative_to(root)),'at':cards.stamp()})
 cards.save(root/'planning/recovery-history.json',history)
 marker.unlink()
 return next_assignment


def handle(root,run_agent):
 base=root/'evidence/scheduler';policy=read(root/'planning/auto-recovery-policy.json',{})
 if not policy.get('enabled') or (base/'active.json').exists() or (base/'recovery-transaction.json').exists():return
 incident_folder=blockers.capture(root)
 if not incident_folder:return
 path=incident_folder/'incident.json';incident=read(path,{})
 if incident.get('status') not in ('action_required','repair_blocked'):return
 if incident['resolution']['route'] not in policy['allowed_routes']:return
 incident['repair_attempted']=True;incident['status']='repairing';cards.save(path,incident)
 folder=base/(cards.stamp().replace(':','').replace('.','')+'-recovery');folder.mkdir()
 try:
  sid,item,prior=target(root,incident,policy)
  key=item['id'] if item else 'LOCAL_FIX'
  counts=incident.setdefault('repair_item_attempts',{})
  if counts.get(key,0)>=policy.get('max_repairs_per_item',2):raise ValueError('No eligible work package for bounded automatic review')
  counts[key]=counts.get(key,0)+1
  cards.save(path,incident)
  frozen={str(p.relative_to(root)):digest(p) for p in [root/'planning/stage-contracts.json',root/'planning/stage-progress.json',root/'planning/tasks.json',root/'planning/auto-recovery-policy.json']}
  assignment={'incident':str(path.relative_to(root)),'stage_id':sid,'item':item,'prior_state':prior,'frozen':frozen,'authorization':policy['authorization'],'previous_recovery_run':incident.get('recovery_run'),'repair_attempt':counts[key]}
  cards.save(folder/'recovery-assignment.json',assignment)
  cards.create(root,folder,task_id=sid,goal='自动修复与有限复盘 · '+(item['id'] if item else 'LOCAL_FIX'),track='recovery',stage_item_id=item['id'] if item else None,session_roles=[('repairer','阻塞修复'),('repair_review','修复独立复核')])
  check_rea.check(folder/'rea-preflight')
  asset=subprocess.run(['/usr/bin/python3','scripts/verify-installer.py'],cwd=root,capture_output=True,text=True)
  (folder/'asset-before.txt').write_text(asset.stdout+asset.stderr)
  if asset.returncode:raise ValueError('Asset verification failed')
  before=snapshot(root,folder);cards.save(folder/'protected-before.json',before)
  prompt=(root/'scripts/scheduler/recovery-worker.txt').read_text()+'\n本卡合同：'+str((folder/'recovery-assignment.json').relative_to(root))
  run_agent('repairer',folder,prompt=prompt,schema=root/'scripts/scheduler/recovery-worker.schema.json')
  after=snapshot(root,folder);diff=changes(root,before,after);cards.save(folder/'diff.json',diff)
  worker=read(folder/'repairer-final.txt',{})
  if worker.get('status')!='ready':raise ValueError('Repair blocked: '+worker.get('reason','No report'))
  prompt=(root/'scripts/scheduler/recovery-reviewer.txt').read_text()+'\n本卡合同：'+str((folder/'recovery-assignment.json').relative_to(root))
  run_agent('repair_review',folder,prompt=prompt,sandbox='read-only',schema=root/'scripts/scheduler/recovery-reviewer.schema.json')
  if snapshot(root,folder)!=after:raise ValueError('Files changed during independent review')
  asset=subprocess.run(['/usr/bin/python3','scripts/verify-installer.py'],cwd=root,capture_output=True,text=True)
  (folder/'asset-after.txt').write_text(asset.stdout+asset.stderr)
  if asset.returncode:raise ValueError('Asset verification failed after repair')
  report=read(folder/'repair_review-final.txt',{})
  next_assignment=register(root,assignment,report,folder)
  incident.update(status='resolved_for_retry',recovery_run=str(folder.relative_to(root)),next_assignment_kind=next_assignment.get('kind','work_package'))
  cards.save(path,incident)
  # Never override a user pause that arrived during repair.
  if (base/'PAUSED').exists() and (base/'PAUSED').read_text()==incident['reason']:
   cards.save(base/'state.json',{'status':'ready','at':cards.stamp(),'reason':'自动修复已独立验证；重新选择合法任务/目标审查','recovery':str(folder.relative_to(root)),'no_progress':0})
   (base/'PAUSED').unlink()
 except Exception as exc:
  incident.update(status='repair_exhausted' if 'No eligible' in str(exc) or 'budget exhausted' in str(exc) else 'repair_blocked',repair_error=str(exc),recovery_run=str(folder.relative_to(root)));cards.save(path,incident)
 finally:
  if (folder/'task-card.json').exists():cards.finish(root,folder,{'status':incident['status'],'reason':incident.get('repair_error','reviewed recovery registered')})
  (base/'active.json').unlink(missing_ok=True)
