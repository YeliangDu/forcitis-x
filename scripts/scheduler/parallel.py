#!/usr/bin/env python3
"""One isolated evidence worker beside the serial main line; no shared editing."""
import argparse, fcntl, hashlib, json, os, re, shlex, shutil, signal, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import cards, check_rea, runner, stages
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/scheduler'
WORKSPACES=Path.home()/'Library/Application Support/HWKModern/workspaces'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def safe_relative(value):
 p=Path(value)
 if p.is_absolute() or not p.parts or '..' in p.parts:raise ValueError('Unsafe relative path: '+str(value))
 return p

def snapshot_inputs(root,workspace,job):
 manifest=[]
 for raw in job['inputs']:
  rel=safe_relative(raw);source=root/rel
  if source.is_symlink() or not source.is_file():raise ValueError('Input must be a regular explicit file: '+raw)
  source.resolve().relative_to(root.resolve())
  original=digest(source)
  dest=workspace/'inputs'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
  if digest(dest)!=original or digest(source)!=original:raise ValueError('Source changed during snapshot: '+raw)
  manifest.append({'path':str(rel),'sha256':digest(dest),'bytes':dest.stat().st_size})
 cards.save(workspace/'input-manifest.json',manifest)
 return manifest

def inventory(workspace):
 out={}
 for p in workspace.rglob('*'):
  if p.is_symlink():raise ValueError('Symlink rejected: '+str(p))
  if not p.is_file():continue
  rel=p.relative_to(workspace)
  if '__pycache__' in rel.parts or p.suffix=='.pyc':continue
  if p.stat().st_size>10000000:raise ValueError('Oversize parallel artifact: '+str(rel))
  out[str(rel)]=digest(p)
 return out

def validate(workspace,initial):
 current=inventory(workspace)
 for name,sha in initial.items():
  if current.get(name)!=sha:raise ValueError('Frozen input/control modified: '+name)
 for name in current:
  if name not in initial and Path(name).parts[0] not in ('scripts','evidence'):
   raise ValueError('Output outside scripts/evidence: '+name)
 if not any(x.startswith('evidence/') and x not in initial for x in current):raise ValueError('No evidence output')
 return current


from review_checks import verify_review_checks


def promote(root,workspace,card_id,submitted,review):
 # Recompute after read-only review; reject mutation, missing evidence, path escapes.
 if inventory(workspace)!=submitted:raise ValueError('Workspace changed during independent review')
 if review.get('verdict')!='PASS':raise ValueError('Only an independently accepted slice can be imported')
 checks=review.get('checks',[])
 if not checks or any(x.get('exit_code')!=0 for x in checks):raise ValueError('Independent successful checks required')
 for raw in review.get('evidence',[]):
  rel=safe_relative(raw)
  if rel.parts[0]!='evidence' or str(rel) not in submitted:raise ValueError('Review evidence missing or outside evidence: '+raw)
 if not review.get('evidence'):raise ValueError('Review must identify concrete evidence')
 parent=root/'evidence/parallel';parent.mkdir(parents=True,exist_ok=True);dest=parent/card_id
 if dest.exists():raise ValueError('Refusing to overwrite existing imported evidence: '+card_id)
 stage=Path(tempfile.mkdtemp(prefix='.import-',dir=parent))
 try:
  for raw in submitted:
   source=workspace/raw;target=stage/raw;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
   if digest(target)!=submitted[raw]:raise ValueError('Copy integrity failure: '+raw)
  cards.save(stage/'independent-review.json',review);cards.save(stage/'accepted-manifest.json',submitted)
  stage.rename(dest)
 except Exception:
  shutil.rmtree(stage);raise
 return str(dest.relative_to(root))

def merge_card(folder,**fields):
 # Shared index writes use the same inter-process lock as the serial runner.
 @cards.exclusive
 def change(root):
  path=folder/'task-card.json';card=json.loads(path.read_text());card.update(fields);cards.save(path,card)
  index=BASE/'cards.json';rows=json.loads(index.read_text());cards.save(index,[card if c['id']==card['id'] else c for c in rows])
 change(ROOT)


@cards.exclusive
def enqueue(root,job):
 """Reviewer can add bounded snapshot-only work without widening execution rights."""
 config_path=root/'planning/parallel-cards.json';config=json.loads(config_path.read_text())
 if not config.get('enabled'):raise ValueError('Parallel disabled; no new job enqueued')
 required=('id','parent_task','stage_item_id','goal','scope','inputs','parallel_reason')
 if not all(job.get(k) for k in required):raise ValueError('Missing reviewed job fields')
 stages.ready_item(root,job['parent_task'],job['stage_item_id'])
 if not re.fullmatch(r'[A-Z0-9-]{1,80}',job['id']):raise ValueError('Invalid job ID')
 if any(x['id']==job['id'] for x in config['jobs']):raise ValueError('Duplicate job ID')
 tasks=json.loads((root/'planning/tasks.json').read_text())['tasks'];parent=next((t for t in tasks if t['id']==job['parent_task']),None)
 if not parent or any(next((t.get('status') for t in tasks if t['id']==dep),None)!='PASS' for dep in parent.get('depends_on',[])):raise ValueError('Parent task prerequisites not satisfied')
 pending=[x for x in config['jobs'] if x.get('enabled',True) and not (root/'evidence/scheduler'/(x['id']+'.result.json')).exists()]
 if len(pending)>=2:raise ValueError('Parallel pending queue is full; wait for an accepted card')
 if not isinstance(job['inputs'],list) or len(job['inputs'])>20:raise ValueError('Bounded explicit input list required')
 fixed={'HANDOFF.md','AGENTS.md','docs/goal-driven-plan.md','planning/tasks.json','planning/naming-observations.json','planning/refactoring-preparation.json','planning/stage-contracts.json','planning/stage-progress.json'}
 for raw in job['inputs']:
  rel=safe_relative(raw);source=root/rel
  if str(rel) not in fixed and not str(rel).startswith('evidence/baseline/'):raise ValueError('Input outside approved source catalog')
  if source.is_symlink() or not source.is_file() or source.suffix not in ('.json','.md','.txt') or source.stat().st_size>10000000:raise ValueError('Input must be a bounded regular text evidence file')
  source.resolve().relative_to(root.resolve())
 if any(x.get('scope')==job['scope'] and sorted(x.get('inputs',[]))==sorted(job['inputs']) for x in config['jobs']):raise ValueError('Duplicate investigation scope')
 approved={k:job[k] for k in required};approved.update(depends_on=[],mode='evidence-only',approved_at=cards.stamp())
 config['jobs'].append(approved);cards.save(config_path,config)
 return approved

def worker_prompt(job,latest):
 return f'''你是HWK Modern隔离并行取证卡。用户授权可验证、可回收的并行。主线在另一个工作区运行。
先读本目录AGENTS.md、input-manifest.json及inputs/HANDOFF.md。任务：{job['goal']}。范围：{job['scope']}。
冻结输入只有input-manifest.json列出的inputs/文件。它们是主仓库只读快照，禁止从正在变化的主仓库补读输入。所有代码只写scripts/，所有证据只写evidence/；不得改inputs/、AGENTS、input-manifest或任何共享台账。不要创建产品实现，当前仅取证。不要提交/推送/安装依赖/启动代理或执行原版载荷。
每条结论标STATIC_PACKAGE及输入来源与哈希。声明依赖不是运行调用；名称不推断业务职责；求解器或架构候选保持候选，不决定正式术语/架构。采集代码须以本目录为基准相对定位inputs，禁止写死隔离工作目录的绝对路径。编写可重跑采集脚本与至少一个有拒绝/错配场景的实质回归，所有结果限本目录。
先做该切片，不重做整项B01。输出evidence/report.md、evidence/result.json和检查结果。完成后给出可重跑检查命令及仍未证明的内容，然后结束；不写主仓库HANDOFF或planning。
REA如需使用，仅限最新版{latest}。若MCP被客户端拒绝，不重试、不扩大审批；用已授权的rea CLI静态命令保存完整Evidence。若当前切片只需读取现有JSON，不必无关启动REA。'''

def reviewer_prompt(job,submitted):
 return f'''你是HWK Modern隔离卡的独立验收代理，使用只读sandbox。任务：{job['goal']}；范围：{job['scope']}。
读取AGENTS.md、input-manifest.json、inputs/及worker交付scripts/、evidence/。实际重跑回归：必要时复制当前目录到/tmp的独立目录再运行，避免修改已提交工作区；比对输入哈希、源字段、原始结果与边界。脚本成功不等于事实成立。拒绝从文件名推断职责、从声明推断运行、把局部映射当完整架构。
本次提交文件及哈希在主控持有，不允许更改提交文件。你只返回JSON，不改共享台账、原仓库或本工作区，不启动代理。只在本切片已独立核实、至少一个回归检查亲自运行成功、证据文件真实存在时verdict=PASS。缺失证据为PARTIAL/FAIL/BLOCKED。这里PASS只表示本隔离静态切片，不是B01或产品验收。evidence只列本工作区evidence/下实际文件，checks只列最终必需的验收检查，且每项exit_code必须为0；command必须逐字复制实际提交给exec_command的完整命令文本（或日志内完整command），不得用说明、占位符或省略号替代。初次环境/命令尝试失败后已修复的历史尝试保留在reason和日志，不冒充最终验收项；任何仍未通过的业务/采集回归必须verdict=FAIL，不得从检查中删去以求PASS。主控会把checks与真实reviewer.jsonl成功执行逐项比对。'''

def run_job(job):
 folder=BASE/(cards.stamp().replace('-','').replace(':','').replace('.','')+'-parallel');folder.mkdir()
 card=cards.create(ROOT,folder,task_id=job['parent_task'],goal=(job.get('stage_item_id','')+' · '+job['goal']).lstrip(' ·'),track='parallel',stage_item_id=job.get('stage_item_id'));card_id=card['id']
 work=WORKSPACES/card_id;work.mkdir(parents=True,exist_ok=False)
 merge_card(folder,parallel_job_id=job['id'],stage_item_id=job.get('stage_item_id'),workspace=str(work),parallel_phase='preflight')
 record={'status':'running','job_id':job['id'],'card_id':card_id,'run':str(folder),'workspace':str(work),'at':cards.stamp()};cards.save(BASE/'parallel-state.json',record)
 try:
  if not re.fullmatch(r'[A-Z0-9-]+',job['id']):raise ValueError('Unsafe job id')
  manifest=snapshot_inputs(ROOT,work,job)
  (work/'AGENTS.md').write_text('''# HWK Modern 隔离取证工作区
本目录仅接受当前job的取证交付。inputs/、input-manifest.json和本文件冻结；代码限scripts/，证据限evidence/。读取inputs/HANDOFF.md了解业务状态，写本地evidence/report.md交接，不修改主仓库或共享planning。原资产、原版执行、外部付费及选型边界沿原约定。并行卡无权通过父任务或最终验收。
''')
  initial=inventory(work);cards.save(folder/'workspace-before.json',initial);cards.save(folder/'inputs.json',manifest)
  latest=check_rea.check(folder/'rea-preflight')['latest']
  def cancelled():
   flag=BASE/'PARALLEL_CANCEL'
   return flag.exists() and flag.read_text().strip()==card_id
  if cancelled():raise RuntimeError('Card cancelled before execution')
  runner.run_agent('worker',folder,workspace=work,prompt=worker_prompt(job,latest),active_name='parallel-active.json')
  if cancelled():raise RuntimeError('Card cancelled after execution')
  submitted=validate(work,initial);cards.save(folder/'submitted.json',submitted);merge_card(folder,parallel_phase='review')
  runner.run_agent('reviewer',folder,workspace=work,prompt=reviewer_prompt(job,submitted),active_name='parallel-active.json',sandbox='read-only',schema=ROOT/'scripts/scheduler/parallel-result.schema.json')
  review=json.loads((folder/'reviewer-final.txt').read_text());dest=None
  if cancelled():raise RuntimeError('Card cancelled before import')
  if review.get('verdict')=='PASS':verify_review_checks(review,folder/'reviewer.jsonl');dest=promote(ROOT,work,card_id,submitted,review)
  outcome='continue' if dest else 'blocked'
  result={'outcome':outcome,'new_evidence':bool(dest),'reason':review.get('reason','Independent review incomplete'),'evidence':[dest+'/independent-review.json',dest+'/evidence/report.md'] if dest else []}
  record.update(status='accepted' if dest else 'blocked',verdict=review.get('verdict'),imported=dest,result=result,at=cards.stamp())
  cards.finish(ROOT,folder,{'status':outcome,'result':result});merge_card(folder,parallel_phase='accepted' if dest else 'blocked',imported=dest,independent_verdict=review.get('verdict'))
 except Exception as exc:
  record.update(status='cancelled' if (BASE/'PARALLEL_CANCEL').exists() and (BASE/'PARALLEL_CANCEL').read_text().strip()==card_id else 'error',reason=str(exc),at=cards.stamp());cards.finish(ROOT,folder,{'status':'error','reason':str(exc)});merge_card(folder,parallel_phase='error')
 finally:
  cards.save(BASE/'parallel-state.json',record)
  (BASE/'parallel-active.json').unlink(missing_ok=True)
  cards.save(BASE/(job['id']+'.result.json'),record)


def tick():
 BASE.mkdir(parents=True,exist_ok=True)
 with (BASE/'parallel.lock').open('a') as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:return
  if (BASE/'PAUSED').exists() or (BASE/'PARALLEL_PAUSED').exists():return
  config=json.loads((ROOT/'planning/parallel-cards.json').read_text())
  if not config.get('enabled'):return
  if config.get('mode')!='evidence-only':raise ValueError('Only reviewed evidence-only sidecars are currently supported')
  if (BASE/'parallel-active.json').exists():
   (BASE/'PARALLEL_PAUSED').write_text('Unclean sidecar run; inspect PID, logs and workspace before resume.\n');return
  # Rejected cards stop this lane for investigation; never endlessly retry or broaden scope.
  for job in config['jobs']:
   if not job.get('enabled',True):continue
   result_path=BASE/(job['id']+'.result.json')
   if result_path.exists() and json.loads(result_path.read_text()).get('status') in ('blocked','error','cancelled'):
    (BASE/'PARALLEL_PAUSED').write_text('Review required: '+result_path.name+'\n');return
  for job in config['jobs']:
   if not job.get('enabled',True):continue
   if (BASE/(job['id']+'.result.json')).exists():continue
   try:stages.ready_item(ROOT,job['parent_task'],job.get('stage_item_id'))
   except stages.StageBlocked as exc:
    cards.save(BASE/(job['id']+'.result.json'),{'status':'superseded','job_id':job['id'],'reason':str(exc)});continue
   if all((BASE/(dep+'.result.json')).exists() and json.loads((BASE/(dep+'.result.json')).read_text())['status']=='accepted' for dep in job.get('depends_on',[])):
    run_job(job);return

def cancel():
 # Obtain the card/process identity, not an arbitrary user-supplied PID.
 path=BASE/'parallel-active.json'
 (BASE/'PARALLEL_PAUSED').write_text('Parallel execution paused/cancel requested.\n')
 if not path.exists():
  state=BASE/'parallel-state.json'
  if state.exists():
   current=json.loads(state.read_text())
   if current.get('status')=='running':(BASE/'PARALLEL_CANCEL').write_text(current['card_id'])
  return
 a=json.loads(path.read_text());(BASE/'PARALLEL_CANCEL').write_text(a['card_id']);pid=int(a['pid'])
 info=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True).stdout
 if 'codex' not in info or str(a['run']) not in info:raise RuntimeError('PID identity mismatch; no process signalled')
 os.killpg(pid,signal.SIGTERM)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['tick','cancel','pause','enqueue']);p.add_argument('job_file',nargs='?',type=Path);a=p.parse_args()
 if a.action=='tick':tick()
 elif a.action=='cancel':cancel()
 elif a.action=='enqueue':
  if not a.job_file:p.error('enqueue requires reviewed job JSON')
  print(json.dumps(enqueue(ROOT,json.loads(a.job_file.read_text())),ensure_ascii=False))
 else:(BASE/'PARALLEL_PAUSED').write_text('Parallel lane paused; current card may finish.\n')
