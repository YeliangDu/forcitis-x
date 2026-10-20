"""Independent validation of stage achievement and end-goal contribution."""
import hashlib,json,re,subprocess
from pathlib import Path
import cards
from review_checks import verify_review_checks

def read(path,default=None):
 try:return json.loads(path.read_text())
 except FileNotFoundError:
  if default is not None:return default
  raise

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def state(root):return read(root/'planning/goal-assurance.json',{'plan':None,'stages':{},'history':[]})
def policy(root):
 p=read(root/'planning/goal-assurance-policy.json')
 if not p.get('requirements'):raise ValueError('整体目标义务清单缺失，不能以工作包汇总代替判断')
 return p

def file_hashes(root,paths):
 result={}
 for raw in sorted(set(paths)):
  rel=Path(raw)
  if rel.is_absolute() or '..' in rel.parts or not rel.parts or rel.parts[0] not in ('planning','docs','evidence','replica','scripts') and str(rel) not in ('AGENTS.md','HANDOFF.md'):raise ValueError('不安全的审查证据路径：'+str(raw))
  p=root/rel;p.resolve().relative_to(root.resolve())
  if p.is_symlink() or not p.is_file():raise ValueError('审查证据不存在或为软链接：'+str(raw))
  result[str(rel)]=hashlib.sha256(p.read_bytes()).hexdigest()
 return result

def plan_subject(root,contracts,tasks):
 return {'execution_policy':read(root/'planning/convergence-policy.json',{'enabled':False}),'policy':policy(root),'contracts':contracts,'dependencies':{t['id']:t.get('depends_on',[]) for t in tasks['tasks']},'scope':read(root/'planning/scope.json',{})}

def stage_subject(root,contracts,progress,sid):
 contract=next(s for s in contracts['stages'] if s['id']==sid);items=progress['stages'][sid]['items'];paths=[]
 for item in contract['work_items']:
  paths+=items[item['id']].get('evidence',[])
  if not item.get('requires_decomposition'):paths+=item.get('outputs',[])
 return {'policy':policy(root),'goal':contracts.get('goal'),'stage':contract,'items':items,'proof_hashes':file_hashes(root,paths)}


def record_intact(root,record):
 if not record or not record.get('record_digest'):return False
 try:
  return digest(read(root/record['report']))==record['record_digest'] and file_hashes(root,record.get('support_hashes',{}))==record.get('support_hashes',{})
 except (OSError,ValueError,KeyError,TypeError):return False

def verified_plan(root,contracts,tasks):
 record=state(root).get('plan')
 return bool(record and record.get('approved') and record.get('subject_digest')==digest(plan_subject(root,contracts,tasks)) and record.get('reviewer') and record_intact(root,record))

def verified_stage(root,contracts,progress,sid):
 record=state(root)['stages'].get(sid)
 try:return bool(record and record.get('approved') and record.get('subject_digest')==digest(stage_subject(root,contracts,progress,sid)) and record.get('reviewer') and record_intact(root,record))
 except (OSError,ValueError,KeyError,TypeError):return False

def assignment(root,contracts,progress,tasks,kind,sid):
 p=policy(root)
 required=[x['id'] for x in p['requirements'] if kind=='plan_audit' or sid in x['stages']]
 subject=plan_subject(root,contracts,tasks) if kind=='plan_audit' else stage_subject(root,contracts,progress,sid)
 return {'kind':kind,'goal_id':p['goal_id'],'stage_id':sid,'subject_digest':digest(subject),'subject':subject,'required_requirement_ids':required,'stage_progress_snapshot':progress['stages'][sid],'instructions':'独立判断阶段是否实际达成与其对整体目标贡献，禁止以工作包全PASS直接替代。'}

def next_assignment(root,contracts,progress,tasks):
 import stages
 sid=tasks['active_task']
 if not verified_plan(root,contracts,tasks):return assignment(root,contracts,progress,tasks,'plan_audit',sid)
 current=next(t for t in tasks['tasks'] if t['id']==sid)
 for dep in current.get('depends_on',[])+[sid]:
  contract=next(s for s in contracts['stages'] if s['id']==dep)
  if stages.all_passed(root,contract,progress['stages'][dep]) and not verified_stage(root,contracts,progress,dep):return assignment(root,contracts,progress,tasks,'stage_audit',dep)
 return None

def apply(root,a,report,reviewer,log):
 import stages
 contracts,progress,tasks=stages.load(root)
 if not re.fullmatch(r'HWK-[0-9]{6}',reviewer):raise ValueError('审查卡ID无效')
 if a['kind']=='stage_audit':
  contract=next(s for s in contracts['stages'] if s['id']==a['stage_id'])
  if not stages.all_passed(root,contract,progress['stages'][a['stage_id']]):raise ValueError('工作包基础证据未就绪，不能阶段放行')
  if reviewer in {x.get('reviewer') for x in progress['stages'][a['stage_id']]['items'].values()}:raise ValueError('阶段判断必须由不同于工作包验收的新审查会话完成')
 current=plan_subject(root,contracts,tasks) if a['kind']=='plan_audit' else stage_subject(root,contracts,progress,a['stage_id'])
 if digest(current)!=a['subject_digest']:raise ValueError('目标/合同/审查证据在审查期间变化，拒绝使用陈旧判断')
 if report.get('kind')!=a['kind'] or report.get('stage_id')!=a['stage_id']:raise ValueError('独立判断对象与本卡不符')
 if not report.get('reason') or not report.get('composition_argument') or not report.get('counterexamples'):raise ValueError('缺少独立论证与反证检查')
 ids=[x.get('requirement_id') for x in report.get('claims',[])]
 if len(set(ids))!=len(ids) or set(ids)!=set(a['required_requirement_ids']):raise ValueError('未逐项覆盖整体目标义务')
 for claim in report['claims']:
  if not claim.get('reason') or not claim.get('evidence'):raise ValueError('目标判断缺来源或论证')
  file_hashes(root,claim['evidence'])
 if not report.get('evidence'):raise ValueError('独立审查缺原始支持证据')
 file_hashes(root,report['evidence']);verify_review_checks(report,log,require_success=report.get('decision') in ('CONTINUE','COMPLETE'))
 stages_by_id={s['id'] for s in contracts['stages']}
 unresolved_gaps=any(gap.get('owner_stage') not in stages_by_id or not gap.get('verification') for gap in report.get('gaps',[]))
 stage_ok=report['stage_achievement']=='PASS'
 contribution_ok=report['goal_contribution']=='PASS'
 composition_ok=report['composition_status']=='PASS' or (report['composition_status']=='PARTIAL' and bool(report.get('gaps')) and all(not g['blocks_next_step'] for g in report['gaps']))
 approved=not unresolved_gaps and not any(c['status'] in ('FAIL','BLOCKED') for c in report['claims']) and report['decision'] in ('CONTINUE','COMPLETE') and report['next_step_justified'] and contribution_ok and composition_ok and not any(g['blocks_next_step'] for g in report.get('gaps',[]))
 if a['kind']=='stage_audit':approved=approved and stage_ok
 if a['stage_id']!='R01' and (report['overall_goal_achievement']=='PASS' or report['decision']=='COMPLETE'):raise ValueError('非最终阶段的判断不能宣称整体Goal达成')
 if a['kind']=='plan_audit' and (report['overall_goal_achievement']=='PASS' or report['decision']=='COMPLETE'):raise ValueError('计划合理不等于整体Goal已实现')
 if approved and a['kind']=='stage_audit' and a['stage_id']=='R01':
  if report['overall_goal_achievement']!='PASS' or report['decision']!='COMPLETE' or report['composition_status']!='PASS' or report.get('gaps') or any(c['status']!='PASS' or c['evidence_type']=='PLAN_ARGUMENT' for c in report['claims']):approved=False
  for t in tasks['tasks']:
   if t['id']!='R01' and not verified_stage(root,contracts,progress,t['id']):approved=False
  final=subprocess.run(['/usr/bin/python3','scripts/check-acceptance.py'],cwd=root,capture_output=True,text=True)
  if final.returncode:approved=False
 out=root/'evidence/goal-assurance';out.mkdir(parents=True,exist_ok=True);path=out/(reviewer+'.json')
 if path.exists():raise ValueError('独立审查报告ID不得覆盖')
 volatile={'planning/tasks.json','planning/stage-progress.json','planning/goal-assurance.json','HANDOFF.md','README.md'}
 supported=[str(log.relative_to(root))]+[p for p in report['evidence']+[p for c in report['claims'] for p in c['evidence']] if p not in volatile]
 record={'support_hashes':file_hashes(root,supported),'kind':a['kind'],'stage_id':a['stage_id'],'subject_digest':a['subject_digest'],'approved':bool(approved),'reviewer':reviewer,'report':str(path.relative_to(root)),'at':cards.stamp(),'result':report}
 cards.save(path,record);record=dict(record,record_digest=digest(record));ledger=state(root);ledger['history'].append({k:record[k] for k in ('kind','stage_id','subject_digest','approved','reviewer','report','at')})
 if a['kind']=='plan_audit':ledger['plan']=record
 else:ledger['stages'][a['stage_id']]=record
 cards.save(root/'planning/goal-assurance.json',ledger)
 if approved and a['kind']=='stage_audit':
  sid=a['stage_id'];contract=next(s for s in contracts['stages'] if s['id']==sid)
  if not stages.all_passed(root,contract,progress['stages'][sid]):raise ValueError('阶段独立放行前工作包基础证据已不完整')
  for t in tasks['tasks']:
   if t['id']==sid:t['status']='PASS'
  if tasks['active_task']==sid:
   following=[t for t in tasks['tasks'] if t['status']!='PASS' and all(next(p for p in tasks['tasks'] if p['id']==dep)['status']=='PASS' for dep in t.get('depends_on',[]))]
   if following:tasks['active_task']=min(following,key=lambda t:t.get('schedule_priority',0))['id']
  cards.save(root/'planning/tasks.json',tasks)
 outcome=('complete' if a['kind']=='stage_audit' and a['stage_id']=='R01' else 'continue') if approved else 'blocked'
 return {'outcome':outcome,'new_evidence':True,'reason':report['reason'],'evidence':[str(path.relative_to(root))],'assurance_kind':a['kind'],'stage_achievement':report['stage_achievement'],'goal_contribution':report['goal_contribution'],'composition_status':report['composition_status'],'overall_goal_achievement':report['overall_goal_achievement']}
