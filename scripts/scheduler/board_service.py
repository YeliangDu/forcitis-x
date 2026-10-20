#!/usr/bin/env python3
"""Manage the local read-only board independently of the development runner."""
import argparse, os, plistlib, socket, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LABEL='com.yeliang.hwk-modern-board'
TARGET='gui/'+str(os.getuid())+'/'+LABEL
PLIST=Path.home()/'Library/LaunchAgents'/(LABEL+'.plist')
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['install','status','stop','start']);a=p.parse_args()
 if a.action=='status': subprocess.run(['launchctl','print',TARGET],check=True);return
 if a.action=='stop':subprocess.run(['launchctl','bootout',TARGET],check=True);return
 if a.action=='start':subprocess.run(['launchctl','bootstrap','gui/'+str(os.getuid()),str(PLIST)],check=True);return
 logs=ROOT/'evidence/scheduler';logs.mkdir(parents=True,exist_ok=True)
 config={'Label':LABEL,'ProgramArguments':['/usr/bin/python3',str(ROOT/'scripts/scheduler/dashboard.py'),'--port','18743'],'WorkingDirectory':str(ROOT),'RunAtLoad':True,'KeepAlive':True,'ThrottleInterval':10,'StandardOutPath':str(logs/'board.stdout'),'StandardErrorPath':str(logs/'board.stderr')}
 if PLIST.exists() and plistlib.loads(PLIST.read_bytes())!=config:raise SystemExit('Existing different service; inspect before replacing '+str(PLIST))
 if subprocess.run(['launchctl','print',TARGET],capture_output=True).returncode:
  probe=socket.socket()
  try:probe.bind(('127.0.0.1',18743))
  finally:probe.close()
  PLIST.parent.mkdir(parents=True,exist_ok=True);PLIST.write_bytes(plistlib.dumps(config));subprocess.run(['launchctl','bootstrap','gui/'+str(os.getuid()),str(PLIST)],check=True)
 print('http://127.0.0.1:18743')
if __name__=='__main__':main()
