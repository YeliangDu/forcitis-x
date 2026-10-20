"""Scoped SSH transport for the authorized HWK Windows test host. No credentials in logs."""
import base64,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HOST='Administrator@8.149.129.78'

def run_ps(script,out,timeout=60):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 prefix="[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false);$ProgressPreference='SilentlyContinue';$ErrorActionPreference='Stop';\n"
 encoded=base64.b64encode((prefix+script).encode('utf-16-le')).decode()
 cmd=['ssh','-i',str(Path.home()/'.ssh/hwk-win-test'),'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(ROOT/'evidence/runtime/ecs-20261018/known_hosts'),HOST,'powershell.exe -NoProfile -NonInteractive -EncodedCommand '+encoded]
 result=subprocess.run(cmd,capture_output=True,timeout=timeout)
 (out/'stdout').write_bytes(result.stdout);(out/'stderr').write_bytes(result.stderr)
 (out/'command.ps1').write_text(script)
 (out/'exit.json').write_text(json.dumps({'exit_code':result.returncode,'host':HOST,'transport':'SSH_PUBLICKEY','remote_command':'powershell.exe -NoProfile -NonInteractive -EncodedCommand <saved command.ps1>'},indent=2)+'\n')
 if result.returncode:raise RuntimeError(f'Remote PowerShell exit {result.returncode}; see {out}/stderr')
 return result.stdout.decode('utf-8-sig')

def upload(local,remote):
 # Raw stdin copy, without placing file contents or passwords in command arguments.
 encoded=base64.b64encode(("$p='"+remote.replace("'","''")+"';$s=[Console]::OpenStandardInput();$f=[IO.File]::Create($p);try{$s.CopyTo($f)}finally{$f.Dispose()}").encode('utf-16-le')).decode()
 cmd=['ssh','-i',str(Path.home()/'.ssh/hwk-win-test'),'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(ROOT/'evidence/runtime/ecs-20261018/known_hosts'),HOST,'powershell.exe -NoProfile -NonInteractive -EncodedCommand '+encoded]
 with Path(local).open('rb') as stream:r=subprocess.run(cmd,stdin=stream,capture_output=True,timeout=60)
 if r.returncode:raise RuntimeError('Upload failed')


def run_ps_stdin(script,out,timeout=60):
 """Send long scripts on stdin to avoid Windows command-line length limits."""
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 bootstrap="[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false);$ProgressPreference='SilentlyContinue';$ErrorActionPreference='Stop';$s=[Console]::OpenStandardInput();$b=New-Object byte[] "+str(len(script.encode('utf-8')))+";$n=0;while($n -lt $b.Length){$r=$s.Read($b,$n,$b.Length-$n);if($r -eq 0){throw 'Incomplete stdin'};$n+=$r};& ([scriptblock]::Create([Text.Encoding]::UTF8.GetString($b)))"
 encoded=base64.b64encode(bootstrap.encode('utf-16-le')).decode()
 cmd=['ssh','-i',str(Path.home()/'.ssh/hwk-win-test'),'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(ROOT/'evidence/runtime/ecs-20261018/known_hosts'),HOST,'powershell.exe -NoProfile -NonInteractive -EncodedCommand '+encoded]
 (out/'command.ps1').write_text(script)
 try:
  result=subprocess.run(cmd,input=script.encode('utf-8'),capture_output=True,timeout=timeout)
 except subprocess.TimeoutExpired as error:
  (out/'stdout').write_bytes(error.stdout or b'');(out/'stderr').write_bytes(error.stderr or b'')
  (out/'exit.json').write_text(json.dumps({'exit_code':None,'status':'TIMEOUT','timeout':timeout,'bootstrap':bootstrap})+'\n')
  raise
 (out/'stdout').write_bytes(result.stdout);(out/'stderr').write_bytes(result.stderr)
 (out/'exit.json').write_text(json.dumps({'exit_code':result.returncode,'host':HOST,'transport':'SSH_PUBLICKEY_STDIN_UTF8','bootstrap':bootstrap,'remote_command':'powershell.exe -NoProfile -NonInteractive -EncodedCommand <bootstrap>; stdin=command.ps1'},indent=2)+'\n')
 if result.returncode:raise RuntimeError(f'Remote PowerShell exit {result.returncode}; see {out}/stderr')
 return result.stdout.decode('utf-8-sig')
