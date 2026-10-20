"""Persistent task-card sequence and supported app-server session naming."""
import datetime, fcntl, functools, json, os, select, shutil, subprocess, time
from pathlib import Path

def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path,value):
 tmp=path.with_suffix('.tmp'); tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n'); tmp.replace(path)
def exclusive(fn):
 @functools.wraps(fn)
 def wrapped(root,*args,**kwargs):
  base=root/'evidence/scheduler';base.mkdir(parents=True,exist_ok=True)
  with (base/'cards.lock').open('a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX)
   return fn(root,*args,**kwargs)
 return wrapped

@exclusive
def create(root,folder,task_id=None,goal=None,track='main',stage_item_id=None,session_roles=None):
 base=root/'evidence/scheduler'; index=base/'cards.json'
 cards=json.loads(index.read_text()) if index.exists() else []
 old=next((x for x in cards if x['run']==str(folder)),None)
 if old: return old
 tasks=json.loads((root/'planning/tasks.json').read_text()); task_id=task_id or tasks['active_task']
 task=next(x for x in tasks['tasks'] if x['id']==task_id)
 seq=max((x['sequence'] for x in cards),default=0)+1
 card={'sequence':seq,'id':f'HWK-{seq:06d}','task_id':task_id,'goal':goal or task['goal'],'track':track,'goal_id':'HWK-G001','stage_item_id':stage_item_id,'previous':cards[-1]['id'] if cards else None,'run':str(folder),'created_at':stamp(),'session_home':str(root/'.codex-runtime'),'sessions':{}}
 for role,label in (session_roles or [('worker','执行'),('reviewer','验收')]):
  card['sessions'][role]={'title':f"{card['id']}-{task_id}-{label}｜{card['goal']}",'thread_id':None,'name_status':'pending'}
 if cards:
  cards[-1]['next']=card['id']; save(Path(cards[-1]['run'])/'task-card.json',cards[-1])
 cards.append(card); save(index,cards); save(folder/'task-card.json',card)
 return card

def rename(codex,thread_id,title,session_home=None):
 env=os.environ.copy()
 if session_home: env['CODEX_HOME']=str(session_home)
 env['PATH']=str(Path(codex).parent)+':/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin'
 p=subprocess.Popen([codex,'app-server','--stdio'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=env,text=True,bufsize=1)
 try:
  def request(msg):
   p.stdin.write(json.dumps(msg)+'\n'); p.stdin.flush()
   deadline=time.monotonic()+25
   while time.monotonic()<deadline:
    if not select.select([p.stdout],[],[],1)[0]: continue
    line=p.stdout.readline()
    if not line: raise RuntimeError('App-server closed before reply')
    data=json.loads(line)
    if data.get('id')==msg['id']:
     if 'error' in data: raise RuntimeError(str(data['error']))
     return data
   raise RuntimeError('App-server naming timeout')
  request({'id':1,'method':'initialize','params':{'clientInfo':{'name':'hwk_scheduler','version':'1.0'}}})
  p.stdin.write('{"method":"initialized"}\n'); p.stdin.flush()
  request({'id':2,'method':'thread/name/set','params':{'threadId':thread_id,'name':title}})
  readback=request({'id':3,'method':'thread/read','params':{'threadId':thread_id,'includeTurns':False}})
  actual=readback['result']['thread'].get('name')
  if actual!=title: raise RuntimeError('Session title readback mismatch: '+str(actual))
  return {'name':actual,'verified':True}
 finally:
  p.terminate()
  try: p.wait(timeout=5)
  except subprocess.TimeoutExpired: p.kill(); p.wait()

@exclusive
def sync(root,folder,codex):
 path=folder/'task-card.json'
 if not path.exists(): return
 card=json.loads(path.read_text())
 for role,entry in card['sessions'].items():
  log=folder/(role+'.jsonl')
  if not log.exists() or entry['name_status']=='set': continue
  for line in log.read_text().splitlines():
   try: event=json.loads(line)
   except json.JSONDecodeError: continue
   if event.get('type')=='thread.started':
    entry['thread_id']=event['thread_id']
    try:
     entry['name_response']=rename(codex,entry['thread_id'],entry['title'],card.get('session_home')); entry['name_status']='set'
    except Exception as e: entry['name_status']='error'; entry['name_error']=str(e)
    break
 save(path,card)
 index=root/'evidence/scheduler/cards.json'; cards=json.loads(index.read_text())
 cards=[card if x['id']==card['id'] else x for x in cards]; save(index,cards)


@exclusive
def archive(root,folder):
 """Mirror native JSONL for the initial globally-started cycle; no DB edits."""
 card=json.loads((folder/'task-card.json').read_text())
 home=Path(card.get('session_home',str(Path.home()/'.codex')))
 target=root/'.codex-runtime'
 for role,entry in card['sessions'].items():
  tid=entry.get('thread_id')
  if not tid: continue
  for source in (home/'sessions').rglob('*'+tid+'*.jsonl'):
   dest=target/'sessions'/source.relative_to(home/'sessions')
   if source.resolve()!=dest.resolve():
    dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,dest)
   entry['native_session']=str(dest.relative_to(root))
   entry['native_sha256']=__import__('hashlib').sha256(dest.read_bytes()).hexdigest()
 save(folder/'task-card.json',card)
 index=root/'evidence/scheduler/cards.json'; cards=json.loads(index.read_text())
 save(index,[card if x['id']==card['id'] else x for x in cards])


@exclusive
def finish(root,folder,state):
 path=folder/'task-card.json'; card=json.loads(path.read_text())
 card['finished_at']=stamp(); card['status']=state['status']; card['review_result']=state.get('result'); card['error']=state.get('reason')
 save(path,card)
 index=root/'evidence/scheduler/cards.json'; rows=json.loads(index.read_text())
 save(index,[card if x['id']==card['id'] else x for x in rows])
