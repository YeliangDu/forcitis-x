#!/usr/bin/env python3
"""Verify npm latest, CLI and a fresh configured MCP server before each cycle."""
import argparse,json,os,select,shutil,subprocess,time
from pathlib import Path

def rpc_identity(command,env,out,expected):
 with (out/'mcp.stderr').open('wb') as err:
  p=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,env=env)
  buffer=b''
  try:
   def request(msg):
    nonlocal buffer
    p.stdin.write((json.dumps(msg)+'\n').encode());p.stdin.flush();deadline=time.monotonic()+45
    while time.monotonic()<deadline:
     while b'\n' in buffer:
      line,buffer=buffer.split(b'\n',1)
      if not line:continue
      value=json.loads(line)
      if value.get('id')==msg['id']:
       if 'error' in value:raise RuntimeError(str(value['error']))
       return value['result']
     if select.select([p.stdout],[],[],1)[0]:
      data=os.read(p.stdout.fileno(),1048576)
      if not data:raise RuntimeError('MCP closed before response')
      buffer+=data
    raise RuntimeError('MCP identity timeout')
   request({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'hwk-rea-preflight','version':'1.0'}}})
   p.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n');p.stdin.flush()
   result=request({'jsonrpc':'2.0','id':2,'method':'tools/call','params':{'name':'binary_session','arguments':{'expected_package_version':expected}}})
   (out/'mcp-session.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
   if result.get('isError'):raise RuntimeError('MCP identity call rejected')
   data=result.get('structuredContent')
   if not data:
    data=next(json.loads(x['text']) for x in result.get('content',[]) if x.get('type')=='text')
   return data.get('result',data)['server_identity']
  finally:
   p.terminate()
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:p.kill();p.wait()

def check(out):
 out.mkdir(parents=True,exist_ok=True)
 def run(args):return subprocess.check_output(args,text=True,timeout=45).strip()
 latest=json.loads(run(['npm','view','rea-agents','version','--json']))
 cli=run(['rea','--version'])
 if cli!=latest:raise RuntimeError(f'REA CLI {cli} differs from npm latest {latest}; update REA before resume')
 registration=json.loads(run(['codex','mcp','get','rea','--json']))
 t=registration['transport']
 if not registration['enabled'] or t['type']!='stdio':raise RuntimeError('REA stdio registration unavailable')
 env=os.environ.copy();env.update(t.get('env') or {})
 identity=rpc_identity([t['command']]+t.get('args',[]),env,out,latest)
 actual=identity['package']['version']
 if actual!=latest:raise RuntimeError(f'REA live MCP {actual} differs from latest {latest}')
 result={'status':'PASS','latest':latest,'cli':cli,'mcp':actual,'server_path':identity['server']['command_path'],'skill':identity['skill'],'catalog_counts':identity['catalog']['counts'],'checked_at':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()}
 (out/'version-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
 try:check(args.out)
 except Exception as e:print(str(e));raise SystemExit(1)
