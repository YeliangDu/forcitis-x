#!/usr/bin/env python3
import argparse,os,plistlib,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LABEL='com.yeliang.hwk-modern-parallel';TARGET=f'gui/{os.getuid()}/{LABEL}'
PLIST=Path.home()/'Library/LaunchAgents'/(LABEL+'.plist')
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['install','status','stop','start']);a=p.parse_args()
 if a.action=='status':subprocess.run(['launchctl','print',TARGET],check=True);return
 if a.action=='stop':subprocess.run(['launchctl','bootout',TARGET],check=True);return
 if a.action=='start':subprocess.run(['launchctl','bootstrap',f'gui/{os.getuid()}',str(PLIST)],check=True);return
 base=ROOT/'evidence/scheduler';base.mkdir(parents=True,exist_ok=True)
 config={'Label':LABEL,'ProgramArguments':['/usr/bin/caffeinate','-i','-s','/usr/bin/python3',str(ROOT/'scripts/scheduler/parallel.py'),'tick'],'WorkingDirectory':str(ROOT),'RunAtLoad':True,'StartInterval':60,'ProcessType':'Background','StandardOutPath':str(base/'parallel.stdout'),'StandardErrorPath':str(base/'parallel.stderr'),'EnvironmentVariables':{'PATH':'/Users/yeliang/.nvm/versions/node/v24.18.0/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin'}}
 if PLIST.exists() and plistlib.loads(PLIST.read_bytes())!=config:raise SystemExit('Existing different service: inspect '+str(PLIST))
 PLIST.write_bytes(plistlib.dumps(config))
 if subprocess.run(['launchctl','print',TARGET],capture_output=True).returncode:subprocess.run(['launchctl','bootstrap',f'gui/{os.getuid()}',str(PLIST)],check=True)
if __name__=='__main__':main()
