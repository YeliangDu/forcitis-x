"""Stage outcomes are mandatory; a successful local slice cannot silently advance a phase."""
import json, re, subprocess
from pathlib import Path
import cards
import assurance

class StageBlocked(RuntimeError):pass

def load(root):
 try:
  contracts=json.loads((root/'planning/stage-contracts.json').read_text())
  progress=json.loads((root/'planning/stage-progress.json').read_text())
  tasks=json.loads((root/'planning/tasks.json').read_text())
 except (OSError,ValueError) as e:raise StageBlocked('阶段目标/进度台账不可读：'+str(e))
 if contracts['version']!=progress['contract_version']:raise StageBlocked('阶段目标与进度版本不一致')
 if {s['id'] for s in contracts['stages']}!={t['id'] for t in tasks['tasks']}:raise StageBlocked('阶段合同与任务清单不一致')
 return contracts,progress,tasks

def evidence_exists(root,paths):
 if not paths:return False
 for raw in paths:
  rel=Path(raw)
  if rel.is_absolute() or '..' in rel.parts or not rel.parts or rel.parts[0]!='evidence':return False
  p=root/rel
  try:p.resolve().relative_to((root/'evidence').resolve())
  except ValueError:return False
  if p.is_symlink() or not p.is_file() or not p.stat().st_size:return False
 return True


def rollup(contract,state):
 for item in reversed(contract['work_items']):
  if not item.get('requires_decomposition'):continue
  children=[i for i in contract['work_items'] if i.get('parent_id')==item['id']]
  if children and all(state['items'][i['id']]['status']=='PASS' for i in children):
   state['items'][item['id']].update(status='PASS',reviewer='verified-child-rollup',evidence=list(dict.fromkeys(p for i in children for p in state['items'][i['id']]['evidence'])),reason='全部已定义子工作包独立通过；仍须本阶段最终验收。')


def register_breakdown(root,contract,state,assignment,proposal):
 if not proposal:return
 existing={i['id']:i for i in contract['work_items']};new_ids=[i.get('id') for i in proposal]
 if len(set(new_ids))!=len(new_ids) or any(i in existing for i in new_ids):raise ValueError('工作包ID重复或试图覆盖既有目标')
 parents={i.get('parent_id') for i in proposal}
 for parent_id in parents:
  parent=existing.get(parent_id)
  if not parent or not parent.get('requires_decomposition') or parent.get('planned_by')!=assignment['item']['id']:raise ValueError('当前工作包没有该容器的分解授权')
  if any(i.get('parent_id')==parent_id for i in contract['work_items']):raise ValueError('已冻结工作包不能静默重定义')
  source=parent['coverage_source'];rel=Path(source['path'])
  if rel.is_absolute() or '..' in rel.parts:raise ValueError('库存来源路径不安全')
  data=json.loads((root/rel).read_text());features=data.get(source['key'],[])
  required={f[source['id_field']] for f in features}
  if not data.get(source['closed_flag']) or not required:raise ValueError('不能从未关闭或空库存分解实施工作包')
  covered={fid for i in proposal if i['parent_id']==parent_id for fid in i.get('coverage_ids',[])}
  if covered!=required:raise ValueError('子工作包未完整覆盖实际库存或引入未批准功能')
 for item in proposal:
  if not re.fullmatch(re.escape(item['parent_id'])+r'-[A-Z0-9-]+',item['id'] or ''):raise ValueError('子包ID必须归属父工作包')
  if not all(item.get(k) for k in ('title','goal','inputs','outputs','done_when','coverage_ids')):raise ValueError('工作包缺少目标/输入/交付/验收或覆盖')
  if any(dep not in existing and dep not in new_ids for dep in item['depends_on']):raise ValueError('工作包依赖不存在')
  if item['id'] in item['depends_on']:raise ValueError('工作包不能依赖自己')
  if not all(str(raw).startswith('evidence/') and not Path(raw).is_absolute() and '..' not in Path(raw).parts for raw in item['outputs']):raise ValueError('工作包交付清单须为仓库内证据路径')
 # Detect dependency cycles in the proposed child graph.
 graph={i['id']:list(i.get('depends_on',[])) for i in contract['work_items']+proposal}
 for item in proposal:graph[item['parent_id']].append(item['id'])
 visiting=set();done=set()
 def visit(node):
  if node in visiting:raise ValueError('工作包依赖环')
  if node in done or node not in graph:return
  visiting.add(node)
  for dep in graph[node]:visit(dep)
  visiting.remove(node);done.add(node)
 for node in graph:visit(node)
 for item in proposal:
  item=dict(item,requires_decomposition=False,max_rounds_before_review=4,not_in_scope=contract['not_in_scope'],owner='执行/独立验收',acceptance_method='按冻结真实功能ID及案例逐项核对')
  contract['work_items'].append(item);state['items'][item['id']]={'status':'NOT_RUN','rounds':0,'evidence':[],'reviewer':None,'reason':'由实际库存分解并经独立审核登记。'}

def all_passed(root,contract,state):
 return bool(contract['work_items']) and all((i.get('requires_decomposition') or evidence_exists(root,i.get('outputs',[]))) and state['items'].get(i['id'],{}).get('status')=='PASS' and state['items'][i['id']].get('reviewer') and evidence_exists(root,state['items'][i['id']].get('evidence',[])) for i in contract['work_items'])


def ready_item(root,stage_id,item_id):
 contracts,progress,tasks=load(root)
 if not assurance.verified_plan(root,contracts,tasks):raise StageBlocked('WBS对整体Goal的独立审查尚未放行')
 if tasks['active_task']!=stage_id:raise StageBlocked('并行任务不属于当前阶段')
 check_entry_items(root,next(s for s in contracts['stages'] if s['id']==stage_id),progress)
 for dep in next(t for t in tasks['tasks'] if t['id']==stage_id).get('depends_on',[]):
  pc=next(s for s in contracts['stages'] if s['id']==dep)
  if not all_passed(root,pc,progress['stages'][dep]) or not assurance.verified_stage(root,contracts,progress,dep):raise StageBlocked('并行任务前置阶段未独立放行：'+dep)
 if tasks['active_task']!=stage_id:raise StageBlocked('并行任务不属于当前阶段')
 contract=next(s for s in contracts['stages'] if s['id']==stage_id);state=progress['stages'][stage_id];rollup(contract,state)
 item=next((i for i in contract['work_items'] if i['id']==item_id),None)
 if not item or item.get('requires_decomposition'):raise StageBlocked('并行卡没有可执行叶子工作包')
 if state['items'][item_id]['status'] in ('PASS','BLOCKED'):raise StageBlocked('并行目标工作包已关闭或阻塞')
 if not all(state['items'][x]['status']=='PASS' for x in item.get('depends_on',[])):raise StageBlocked('并行目标工作包前置未满足')
 return item

def check_entry_items(root,contract,progress):
 for ref in contract.get('entry_work_items',[]):
  entry=progress['stages'].get(ref['stage_id'],{}).get('items',{}).get(ref['item_id'],{})
  if entry.get('status')!='PASS' or not entry.get('reviewer') or not evidence_exists(root,entry.get('evidence',[])):
   raise StageBlocked('运行入口工作包未独立通过：'+ref['item_id'])
 for evidence in contract.get('entry_evidence',[]):
  if not evidence_exists(root,[evidence['path']]):raise StageBlocked('运行入口证据缺失')
  import hashlib
  if hashlib.sha256((root/evidence['path']).read_bytes()).hexdigest()!=evidence['sha256']:raise StageBlocked('运行入口证据变化，须重新审查')

def convergence_enabled(root):
 p=root/'planning/convergence-policy.json'
 return p.exists() and json.loads(p.read_text()).get('enabled') is True

def select(root):
 contracts,progress,tasks=load(root);stage_id=tasks['active_task'];converging=convergence_enabled(root)
 contract=next(s for s in contracts['stages'] if s['id']==stage_id)
 task=next(t for t in tasks['tasks'] if t['id']==stage_id);state=progress['stages'][stage_id]
 rollup(contract,state)
 try:audit=assurance.next_assignment(root,contracts,progress,tasks)
 except (OSError,ValueError) as exc:raise StageBlocked('独立目标审查不可用：'+str(exc))
 if audit:return audit
 check_entry_items(root,contract,progress)
 for dep in task.get('depends_on',[]):
  parent=next(t for t in tasks['tasks'] if t['id']==dep);pc=next(s for s in contracts['stages'] if s['id']==dep)
  if parent['status']!='PASS' or not all_passed(root,pc,progress['stages'][dep]) or not assurance.verified_stage(root,contracts,progress,dep):raise StageBlocked(stage_id+'前置阶段未通过：'+dep)
 if task.get('status')=='PASS' and not all_passed(root,contract,state):raise StageBlocked('拒绝仅凭任务标记推进：'+stage_id+'工作包未独立通过')
 for item in contract['work_items']:
  entry=state['items'][item['id']]
  if item.get('requires_decomposition'):continue
  if entry['status']=='PASS':continue
  if entry['status']=='BLOCKED' and (not converging or entry.get('dispatch_status')!='ready'):continue
  if converging and entry.get('dispatch_status')=='needs_plan':continue
  if not all(state['items'][x]['status']=='PASS' for x in item.get('depends_on',[])):continue
  if not converging and entry['rounds']>=item['max_rounds_before_review']:continue
  return {'goal_id':contracts.get('goal',{}).get('id','HWK-G001'),'overall_goal':contracts.get('goal',{}).get('outcome'),'stage_id':stage_id,'stage_outcome':contract['outcome'],'item':item,'not_in_scope':contract['not_in_scope'],'block_when':contract['block_when'],'contract_version':contracts['version'],'execution_focus':entry.get('execution_focus','按完整包目标选择能缩小缺口的下一步增量')}
 if converging:
  import convergence
  return convergence.assignment(root)
 reasons=[i['id']+': '+state['items'][i['id']].get('reason','未关闭') for i in contract['work_items'] if state['items'][i['id']]['status']!='PASS']
 raise StageBlocked('阶段需复盘，停止新增探索卡：'+'；'.join(reasons))

def apply(root,assignment,result,reviewer):
 contracts,progress,tasks=load(root);sid=assignment['stage_id'];item_id=assignment['item']['id']
 if result.get('stage_item_id')!=item_id:raise ValueError('验收结果未绑定派发的工作包')
 verdict=result.get('stage_item_status')
 if verdict not in ('PASS','PARTIAL','BLOCKED','FAIL'):raise ValueError('无明确工作包验收状态')
 if result.get('outcome')=='complete':raise ValueError('局部阶段不能声明全产品complete')
 entry=progress['stages'][sid]['items'][item_id]
 proof=result.get('stage_item_evidence',[])
 if verdict=='PASS' and not evidence_exists(root,proof):raise ValueError('工作包PASS缺失独立证据或路径不安全')
 if verdict=='PASS' and not evidence_exists(root,assignment['item'].get('outputs',[])):raise ValueError('工作包PASS缺失约定交付物')
 contract=next(s for s in contracts['stages'] if s['id']==sid)
 if result.get('breakdown'):
  if verdict!='PASS':raise ValueError('未经独立通过的规划不能注册实施工作包')
  register_breakdown(root,contract,progress['stages'][sid],assignment,result['breakdown'])
 rounds=entry['rounds']+1
 if verdict=='FAIL':verdict='BLOCKED'
 if not convergence_enabled(root) and verdict=='PARTIAL' and rounds>=assignment['item']['max_rounds_before_review']:verdict='BLOCKED'
 entry.setdefault('review_history',[]).append({k:entry.get(k) for k in ('status','rounds','evidence','reviewer','reason')})
 entry.update(status=verdict,rounds=rounds,evidence=proof,reviewer=reviewer,reason=result['reason'])
 if convergence_enabled(root):
  advice=result.get('continuation',{})
  ready=advice.get('decision') in ('CONTINUE','CHANGE_METHOD') and bool(advice.get('execution_focus')) and bool(advice.get('reason'))
  entry['dispatch_status']='ready' if ready else 'needs_plan'
  entry['execution_focus']=advice.get('execution_focus','')
  entry['continuation']=advice
 task=next(t for t in tasks['tasks'] if t['id']==sid);contract=next(s for s in contracts['stages'] if s['id']==sid)
 rollup(contract,progress['stages'][sid])
 complete=all_passed(root,contract,progress['stages'][sid])
 # Packages only nominate a stage candidate. A separate goal-assessor decides release.
 progress['stages'][sid]['candidate_ready']=bool(complete)
 task['status']='PARTIAL'
 task['stage_contract']='planning/stage-contracts.json#'+sid
 if complete:result['outcome']='continue'
 elif result.get('outcome')=='blocked':result['outcome']='continue'
 progress['updated_at']=cards.stamp()
 cards.save(root/'planning/stage-contracts.json',contracts);cards.save(root/'planning/stage-progress.json',progress);cards.save(root/'planning/tasks.json',tasks)
 if not complete:
  try:select(root)
  except StageBlocked as exc:
   result['outcome']='blocked';result['reason']+='\n'+str(exc)
 return complete
