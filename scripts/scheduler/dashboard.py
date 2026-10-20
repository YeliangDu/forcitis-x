#!/usr/bin/env python3
"""Read-only loopback dashboard. Source files stay authoritative."""
import argparse, datetime, json, mimetypes, os, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
ROOT=Path(__file__).resolve().parents[2]

def read_json(path,default,warnings):
 for _ in range(3):
  try: return json.loads(path.read_text())
  except FileNotFoundError: return default
  except (OSError,json.JSONDecodeError): time.sleep(.01)
 warnings.append('读取失败：'+path.name); return default

def log_tail(path):
 try:
  with path.open('rb') as f:
   f.seek(0,2); size=f.tell(); f.seek(max(0,size-180000)); data=f.read().decode('utf-8',errors='replace')
  events=[]; terminal=None
  for line in data.splitlines():
   try: event=json.loads(line)
   except json.JSONDecodeError: continue
   if event.get('type') in ('turn.completed','turn.failed'): terminal=event['type']
   if event.get('type')=='item.completed':
    item=event.get('item',{})
    if item.get('type')=='agent_message': events.append({'type':'message','text':item.get('text','')[:4000]})
    elif item.get('type')=='command_execution': events.append({'type':'command','text':item.get('command','')[:500],'exit_code':item.get('exit_code')})
  return {'events':events[-8:],'terminal':terminal,'updated_at':datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc).isoformat()}
 except OSError: return {'events':[],'terminal':None,'updated_at':None}

def safe_run(root,raw):
 try:
  path=Path(raw).resolve(); path.relative_to((root/'evidence/scheduler').resolve()); return path
 except (ValueError,TypeError): return None

def snapshot(root):
 warnings=[]; base=root/'evidence/scheduler'
 state=read_json(base/'state.json',{},warnings); active=read_json(base/'active.json',{},warnings)
 parallel_active=read_json(base/'parallel-active.json',{},warnings)
 actives=[a for a in (active,parallel_active) if a]
 def process_exists(a):
  try:os.kill(int(a.get('pid',0)),0);return bool(a.get('pid'))
  except (ProcessLookupError,ValueError,TypeError):return False
  except PermissionError:return True
 for a in actives:a['process_exists']=process_exists(a)
 task_data=read_json(root/'planning/tasks.json',{'tasks':[]},warnings)
 acceptance=read_json(root/'planning/acceptance.json',{'gates':{}},warnings)
 cards=read_json(base/'cards.json',[],warnings)
 by_id={c['id']:c for c in cards if isinstance(c,dict) and c.get('id')}
 # Per-run files recover a card even during index updates.
 for path in sorted(base.glob('*/task-card.json')):
  c=read_json(path,{},warnings)
  if c.get('id'): by_id[c['id']]=c
 display_active=active or parallel_active
 alive=process_exists(display_active) if display_active else False
 closures=read_json(base/'issue-closures.json',{'cards':{}},warnings).get('cards',{})
 parallel_state=read_json(base/'parallel-state.json',{},warnings)
 open_sources=set()
 for c in by_id.values():
  folder=safe_run(root,c.get('run'))
  if c.get('track')=='blocker' and folder:
   event=read_json(folder/'incident.json',{},warnings)
   if event.get('status') not in ('resolved','superseded','consolidated') and not closures.get(c['id']):open_sources.add(event.get('source_state',{}).get('run'))
 rows=[]
 for card in sorted(by_id.values(),key=lambda c:c.get('sequence',0),reverse=True):
  folder=safe_run(root,card.get('run')); sessions=card.get('sessions',{})
  details={role:log_tail(folder/(role+'.jsonl')) if folder else {'events':[],'terminal':None,'updated_at':None} for role in ('worker','reviewer','assessor','diagnostician','repairer','repair_review','planner')}
  result=card.get('review_result')
  if not result and folder: result=read_json(folder/'reviewer-final.txt',None,warnings)
  if card.get('track')=='blocker' and folder:
   incident=read_json(folder/'incident.json',{},warnings)
   result=dict(incident.get('resolution') or {},outcome=incident.get('status'),reason=incident.get('repair_error') or incident.get('error') or (incident.get('resolution') or {}).get('reason') or incident.get('reason'))
  if not result and folder and state.get('run')==str(folder): result=state.get('result')
  match=next((a for a in actives if a.get('card_id')==card['id'] or (folder and a.get('run')==str(folder))),None)
  is_active=bool(match)
  card_alive=match.get('process_exists',False) if match else False
  outcome=(result or {}).get('outcome') or card.get('status')
  closure=closures.get(card['id'])
  current_failure=(not state.get('run') or state.get('run')==str(folder)) and str(folder) not in open_sources
  current_parallel=parallel_state.get('run')==str(folder) and parallel_state.get('status') in ('blocked','error','cancelled')
  open_incident=card.get('track')=='blocker' and outcome in ('action_required','diagnosis_failed','repair_blocked','repair_exhausted','repairing')
  if is_active:
   lane=('review' if match.get('role') in ('reviewer','assessor','repair_review') else 'working') if card_alive else 'blocked'
  elif closure:lane='finished'
  elif open_incident or current_parallel:lane='blocked'
  elif outcome in ('blocked','error','repair_blocked','repair_exhausted') and current_failure:lane='blocked'
  elif result or card.get('finished_at') or details['reviewer']['terminal']=='turn.completed': lane='finished'
  elif any(v['terminal']=='turn.failed' for v in details.values()): lane='blocked'
  elif sessions.get('assessor',{}).get('thread_id') or sessions.get('reviewer',{}).get('thread_id'): lane='review'
  elif sessions.get('worker',{}).get('thread_id'): lane='working'
  else: lane='queued'
  evidence=list(dict.fromkeys((result or {}).get('evidence',[])+(closure or {}).get('evidence',[])))
  rows.append({'id':card['id'],'kind':'cycle','task_id':card.get('task_id'),'goal':card.get('goal'),'track':card.get('track','main'),'active_role':match.get('role') if match else None,'closure':closure,'lane':lane,'created_at':card.get('created_at'),'finished_at':card.get('finished_at'),'previous':card.get('previous'),'next':card.get('next'),'result':result,'error':card.get('error'),'sessions':sessions,'activity':details,'evidence':evidence,'is_active':bool(is_active),'process_exists':card_alive if is_active else None})
 parallel_config=read_json(root/'planning/parallel-cards.json',{},warnings)
 claimed={c.get('parallel_job_id') for c in by_id.values()}
 if parallel_config.get('enabled'):
  for job in parallel_config.get('jobs',[]):
   if not job.get('enabled',True) or job['id'] in claimed:continue
   rows.append({'id':'PARALLEL-'+job['id'],'kind':'task','track':'parallel','task_id':job['parent_task'],'goal':job['goal'],'lane':'queued','status':'NOT_RUN','depends_on':job.get('depends_on',[]),'evidence':[],'blockers':[]})
 tasks=task_data.get('tasks',[])
 represented={c['task_id'] for c in rows if c['lane'] in ('working','review','queued')}
 for task in tasks:
  if task['id'] in represented: continue
  # Current partial task is represented by its completed rounds; keep stage status below.
  if any(c['task_id']==task['id'] for c in rows): continue
  status=task.get('status','NOT_RUN')
  lane='finished' if status=='PASS' else 'blocked' if status in ('FAIL','BLOCKED') else 'queued'
  rows.append({'id':task['id'],'kind':'task','task_id':task['id'],'goal':task['goal'],'lane':lane,'status':status,'depends_on':task.get('depends_on',[]),'evidence':task.get('evidence',[]),'blockers':task.get('blockers',[])})
 pause=base/'PAUSED'
 try: pause_reason=pause.read_text() if pause.exists() else None
 except OSError: pause_reason='暂停原因暂不可读'
 contracts=read_json(root/'planning/stage-contracts.json',{},warnings)
 stage_progress=read_json(root/'planning/stage-progress.json',{},warnings)
 stage_views=[]
 for definition in contracts.get('stages',[]):
  view=dict(definition);entries=stage_progress.get('stages',{}).get(view['id'],{}).get('items',{})
  view['work_items']=[dict(i,progress=entries.get(i['id'],{'status':'NOT_RUN','rounds':0,'evidence':[]}),cards=[c['id'] for c in by_id.values() if c.get('stage_item_id')==i['id']],active_role=next((a['role'] for a in actives if by_id.get(a.get('card_id'),{}).get('stage_item_id')==i['id'] and a.get('process_exists')),None)) for i in view['work_items']]
  stage_views.append(view)
 assurance_data=read_json(root/'planning/goal-assurance.json',{'plan':None,'stages':{}},warnings)
 return {'goal_assurance':assurance_data,'stage_contracts':stage_views,'overall_goal':contracts.get('goal'),'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scheduler':{'status':state.get('status','unknown'),'paused':pause.exists(),'pause_reason':pause_reason,'active':display_active or None,'actives':actives,'parallel_enabled':read_json(root/'planning/parallel-cards.json',{},warnings).get('enabled',False),'parallel_paused':(base/'PARALLEL_PAUSED').exists(),'process_exists':alive,'last_cycle_at':state.get('at'),'reason':state.get('reason') or (state.get('result') or {}).get('reason')},'active_task':task_data.get('active_task'),'tasks':tasks,'cards':rows,'gates':acceptance.get('gates',{}),'warnings':warnings}

class Handler(BaseHTTPRequestHandler):
 def log_message(self,format,*args): pass
 def respond(self,status,content,kind):
  self.send_response(status); self.send_header('Content-Type',kind); self.send_header('Content-Length',str(len(content))); self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'"); self.end_headers(); self.wfile.write(content)
 def do_GET(self):
  # Reject browser DNS rebinding/foreign origins; the service only binds loopback.
  port=self.server.server_port
  if self.headers.get('Host') not in (f'127.0.0.1:{port}',f'localhost:{port}'):
   self.respond(403,b'Forbidden host','text/plain'); return
  root=self.server.workspace; route=urlsplit(self.path)
  if route.path=='/api/snapshot':
   self.respond(200,json.dumps(snapshot(root),ensure_ascii=False).encode(),'application/json; charset=utf-8'); return
  if route.path=='/api/file':
   raw=parse_qs(route.query).get('path',[''])[0]
   path=(root/raw).resolve()
   try: path.relative_to((root/'evidence').resolve())
   except ValueError: self.respond(403,b'Only evidence files are readable','text/plain'); return
   if path.suffix not in ('.json','.md','.txt','.log') or not path.is_file():
    self.respond(404,b'Not available','text/plain'); return
   if path.stat().st_size>1500000: self.respond(413,b'File too large','text/plain'); return
   self.respond(200,path.read_bytes(),'text/plain; charset=utf-8'); return
  dist=root/'replica/dev-board/dist'; path=(dist/('index.html' if route.path=='/' else route.path.lstrip('/'))).resolve()
  try: path.relative_to(dist.resolve())
  except ValueError: self.respond(403,b'Forbidden','text/plain'); return
  if not path.is_file(): self.respond(404,b'Not found','text/plain'); return
  self.respond(200,path.read_bytes(),mimetypes.guess_type(path.name)[0] or 'application/octet-stream')

def serve(root,port):
 server=ThreadingHTTPServer(('127.0.0.1',port),Handler); server.workspace=root; return server
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('--port',type=int,default=18743); args=p.parse_args()
 print(f'HWK development board http://127.0.0.1:{args.port}',flush=True); serve(ROOT,args.port).serve_forever()
