#!/usr/bin/env python3
import json, os, plistlib, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LABEL='com.yeliang.hwk-modern'
TARGET='gui/'+str(os.getuid())+'/'+LABEL
PLIST=Path.home()/'Library/LaunchAgents'/ (LABEL+'.plist')
RUNNER=ROOT/'scripts/scheduler/runner.py'
LOGS=ROOT/'evidence/scheduler'

def retry_job(config,job_id):
 job=next(x for x in config['jobs'] if x['id']==job_id)
 original=job.get('retry_of',job['id'])
 if any(x.get('retry_of')==original for x in config['jobs']):raise ValueError('One recovery retry already used; inspect blocker instead of retrying again')
 retry=dict(job);n=2
 while any(x['id']==original+'-R'+str(n) for x in config['jobs']):n+=1
 job['enabled']=False;retry.update(id=original+'-R'+str(n),enabled=True,retry_of=original);config['jobs'].append(retry)
 return retry

def main():
 action=sys.argv[1] if len(sys.argv)>1 else 'status'
 if action=='install':
  LOGS.mkdir(parents=True,exist_ok=True); PLIST.parent.mkdir(parents=True,exist_ok=True)
  config={'Label':LABEL,'ProgramArguments':['/usr/bin/caffeinate','-i','-s','/usr/bin/python3',str(RUNNER),'tick'],'WorkingDirectory':str(ROOT),'RunAtLoad':True,'StartInterval':60,'ProcessType':'Background','StandardOutPath':str(LOGS/'launchd.stdout'),'StandardErrorPath':str(LOGS/'launchd.stderr'),'EnvironmentVariables':{'PATH':'/Users/yeliang/.nvm/versions/node/v24.18.0/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin'}}
  if PLIST.exists() and plistlib.loads(PLIST.read_bytes())!=config: raise SystemExit('Existing different plist: inspect before replacement: '+str(PLIST))
  PLIST.write_bytes(plistlib.dumps(config))
  existing=subprocess.run(['launchctl','print',TARGET],capture_output=True)
  if existing.returncode: subprocess.run(['launchctl','bootstrap','gui/'+str(os.getuid()),str(PLIST)],check=True)
 elif action in ('parallel-resume','parallel-retry'):
  import cards
  path=ROOT/'planning/parallel-cards.json';config=json.loads(path.read_text())
  if action=='parallel-retry':
   if (LOGS/'parallel-active.json').exists():raise SystemExit('Wait for current parallel process to finish before retry')
   if len(sys.argv)!=3:raise SystemExit('usage: control.py parallel-retry JOB-ID')
   result=LOGS/(sys.argv[2]+'.result.json')
   if not result.exists() or json.loads(result.read_text()).get('status') not in ('blocked','error','cancelled'):raise SystemExit('Only failed/cancelled jobs can be retried')
   retry_job(config,sys.argv[2])
  for job in config['jobs']:
   result=LOGS/(job['id']+'.result.json')
   if job.get('enabled',True) and result.exists() and json.loads(result.read_text()).get('status') in ('blocked','error','cancelled'):raise SystemExit('Inspect or retry failed job: '+job['id'])
  config['enabled']=True;cards.save(path,config);(LOGS/'PARALLEL_PAUSED').unlink(missing_ok=True)
  subprocess.run(['launchctl','kickstart',f'gui/{os.getuid()}/com.yeliang.hwk-modern-parallel'],check=True)
 elif action in ('serial','parallel-pause','parallel-cancel'):
  if action=='serial':
   import cards
   path=ROOT/'planning/parallel-cards.json';config=json.loads(path.read_text());config['enabled']=False;cards.save(path,config)
  else:subprocess.run(['/usr/bin/python3',str(ROOT/'scripts/scheduler/parallel.py'),'cancel' if action=='parallel-cancel' else 'pause'],check=True)
 elif action=='blockers':
  import blockers
  folder=blockers.capture(ROOT)
  if folder:print((folder/'incident.json').read_text())
  else:print('No automatic blocker (or user pause).')
 elif action in ('pause','resume','status'):
  subprocess.run(['/usr/bin/python3',str(RUNNER),action],check=True)
  if action=='resume': subprocess.run(['launchctl','kickstart',TARGET],check=True)
  if action=='status':
   subprocess.run(['launchctl','print',TARGET])
   for name in ('parallel-state.json','parallel-active.json','PARALLEL_PAUSED'):
    path=LOGS/name
    if path.exists():print(name+': '+path.read_text())
 else: raise SystemExit('usage: control.py install|status|pause|resume|serial|parallel-pause|parallel-cancel|parallel-resume|parallel-retry JOB-ID')
if __name__=='__main__': main()
