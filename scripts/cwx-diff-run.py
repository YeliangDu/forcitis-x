"""Run one bounded probe script in the authorized Windows session-4 desktop and pull artifacts back.

Usage:
  python3 scripts/cwx-diff-run.py run <name>   # upload scripts/cwx-probes/<name>.ps1 and start scheduled task
  python3 scripts/cwx-diff-run.py read <name>  # wait for <name>.json/.png, copy back into evidence dir
  python3 scripts/cwx-diff-run.py clean        # delete the scheduled task
"""
import base64
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hwk_ecs import run_ps  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REMOTE = r'C:\hwk-modern\run-20261019-cwx'
TASK = 'HWKModern-20261019-CWX'
LOCAL = ROOT / 'migration_workspace/raw/cwx-diff-20261019'
PROBES = ROOT / 'scripts/cwx-probes'


def probe_dir(name):
    d = LOCAL / name
    d.mkdir(parents=True, exist_ok=True)
    return d


def upload_chunked(local, remote, chunk=768):
    """Write a file through several short ssh calls; one-shot stdin copies stall intermittently.

    Scripts get a UTF-8 BOM so Windows PowerShell 5.1 does not decode CJK literals as ANSI.
    """
    data = Path(local).read_bytes()
    if Path(local).suffix.lower() == '.ps1' and not data.startswith(b'\xef\xbb\xbf'):
        data = b'\xef\xbb\xbf' + data
    for index, start in enumerate(range(0, len(data), chunk)):
        part = base64.b64encode(data[start:start + chunk]).decode()
        op = 'WriteAllText' if index == 0 else 'AppendAllText'
        out = LOCAL / 'uploads' / f'{Path(local).stem}-{index}'
        run_ps(
            f"$p='{remote}';$b='{part}';"
            f"[IO.File]::{op}($p,[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($b)))",
            out, timeout=90)
    written = run_ps(f"(Get-Item '{remote}').Length", LOCAL / 'uploads' / f'{Path(local).stem}-size', timeout=90).strip()
    try:
        remote_size = int(written)
    except ValueError as error:
        raise SystemExit(f'unreadable remote size {written!r} for {remote}') from error
    if remote_size != len(data):
        raise SystemExit(f'remote size {remote_size} != local {len(data)} for {remote}')


def upload_probe(name):
    src = PROBES / (name + '.ps1')
    if not src.exists():
        raise SystemExit(f'missing probe {src}')
    upload_chunked(src, REMOTE + '\\' + name + '.ps1')
    probe_dir(name).joinpath('probe.ps1').write_text(src.read_text())


def schedule(name, probe_args=()):
    out = probe_dir(name)
    probe = REMOTE + '\\' + name + '.ps1'
    log = REMOTE + '\\' + name + '.error.txt'
    wrapper = REMOTE + '\\' + name + '.wrap.ps1'
    driver = out / 'wrapper.ps1'
    arg_list = ''.join(" '" + str(a).replace("'", "''") + "'" for a in probe_args)
    driver.write_text(
        "$ErrorActionPreference='Stop'\n"
        "try {\n"
        f"  & '{probe}'{arg_list}\n"
        "} catch {\n"
        f"  ('ERROR: ' + ($_ | Out-String) + ' @ ' + $_.ScriptStackTrace) | Set-Content '{log}'\n"
        "}\n"
    )
    upload_chunked(driver, wrapper)
    cmd = (
        "$a=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "
        "'-NoProfile -WindowStyle Hidden -File " + wrapper + "';"
        f"$p=New-ScheduledTaskPrincipal -UserId '{os.environ.get('CWX_TASK_USER', 'Administrator')}' -LogonType Interactive -RunLevel Highest;"
        f"Register-ScheduledTask -Force -TaskName '{TASK}' -Action $a -Principal $p|Out-Null;"
        f"Start-ScheduledTask -TaskName '{TASK}'"
    )
    print(run_ps(cmd, out / 'schedule', timeout=120))


def read(name, timeout=120):
    out = probe_dir(name)
    shared = (
        "function Read-Shared([string]$path){"
        "$fs=[IO.File]::Open($path,'Open','Read','ReadWrite');"
        "try{$sr=New-Object IO.StreamReader($fs,[Text.Encoding]::UTF8);return $sr.ReadToEnd()}finally{$sr.Dispose();$fs.Dispose()}};"
        "function Bytes-Shared([string]$path){"
        "$fs=[IO.File]::Open($path,'Open','Read','ReadWrite');"
        "try{$ms=New-Object IO.MemoryStream;$fs.CopyTo($ms);return [Convert]::ToBase64String($ms.ToArray())}finally{$ms.Dispose();$fs.Dispose()}};"
    )
    script = (
        f"$b='{REMOTE}';"
        f"for($i=0;$i -lt {timeout} -and !(Test-Path (\"$b\\{name}.json\"));$i++){{Start-Sleep -Seconds 1}};"
        + shared +
        "[ordered]@{"
        f"Task=(Get-ScheduledTaskInfo -TaskName '{TASK}'|Select-Object LastTaskResult,LastRunTime);"
        f"Json=$(if(Test-Path \"$b\\{name}.json\"){{Read-Shared \"$b\\{name}.json\"}}else{{$null}});"
        f"Png=$(if(Test-Path \"$b\\{name}.png\"){{Bytes-Shared \"$b\\{name}.png\"}}else{{$null}});"
        f"Text=$(if(Test-Path \"$b\\{name}.txt\"){{Read-Shared \"$b\\{name}.txt\"}}else{{$null}})"
        "}|ConvertTo-Json -Depth 5"
    )
    stamp = len(list(out.glob('read-*')))
    raw = run_ps(script, out / f'read-{stamp}', timeout=timeout + 120)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        out.joinpath('read-error.txt').write_text(raw)
        raise SystemExit(f'unparseable read result ({error}); raw saved in {out}') from error
    if data.get('Png'):
        out.joinpath(name + '.png').write_bytes(base64.b64decode(data['Png']))
    if data.get('Json'):
        out.joinpath(name + '.json').write_text(data['Json'])
    if data.get('Text'):
        out.joinpath(name + '.txt').write_text(data['Text'])
    print(json.dumps(data.get('Task'), indent=2))
    if data.get('Json'):
        print(data['Json'][:3000])
    if data.get('Text'):
        print(data['Text'][:3000])
    if not data.get('Json'):
        print('--- probe left no json; error text follows ---')
        print(run_ps(
            f"if(Test-Path '{REMOTE}\\{name}.error.txt'){{Get-Content '{REMOTE}\\{name}.error.txt' -Raw}}",
            out / 'error-fetch', timeout=90))


def clean():
    out = LOCAL / 'cleanup'
    print(run_ps(
        f"if(Get-ScheduledTask -TaskName '{TASK}' -ErrorAction SilentlyContinue)"
        f"{{Unregister-ScheduledTask -TaskName '{TASK}' -Confirm:$false}};"
        f"Write-Output ('remaining=' + (@(Get-ScheduledTask -TaskName '{TASK}' -ErrorAction SilentlyContinue).Count));"
        "Get-Process XWall -ErrorAction SilentlyContinue|ForEach-Object{Write-Output ('pid=' + $_.Id + ' session=' + $_.SessionId + ' title=' + $_.MainWindowTitle)}",
        out / 'cleanup', timeout=120))


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in ('run', 'read', 'clean'):
        raise SystemExit(__doc__)
    mode = sys.argv[1]
    if mode == 'run':
        if len(sys.argv) < 3:
            raise SystemExit(__doc__)
        name = sys.argv[2]
        upload_probe(name)
        schedule(name, sys.argv[3:])
    elif mode == 'read':
        if len(sys.argv) < 3:
            raise SystemExit(__doc__)
        try:
            wait = int(sys.argv[3]) if len(sys.argv) > 3 else 120
        except ValueError:
            raise SystemExit('timeout must be an integer number of seconds') from None
        read(sys.argv[2], wait)
    else:
        clean()
