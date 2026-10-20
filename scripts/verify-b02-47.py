"""Independent re-read of the ECS for the B02-02 attempt-47 slice.

Does not reuse the attempt's own captures: it recomputes the source manifest, the
frozen hashes, the process/connection state, the produced document hash and a text
excerpt, then compares them with the recorded baseline and the delivered claims.
"""
import json
from pathlib import Path

from hwk_ecs import run_ps

OUT = Path('evidence/stages/B02/B02-02/attempt-47/acceptance')
OUT.mkdir(parents=True, exist_ok=True)

CMD = r'''$ErrorActionPreference='Stop'
$source='C:\Program Files\HWKSoft\XWallClient'
$client='C:\hwk-modern\HWK-000041-B02-01\client'
$sample='C:\hwk-modern\HWK-000041-B02-01\projects\sample-working.cwx'
$card='C:\hwk-modern\HWK-000048-B02-02'
$files=@(Get-ChildItem -LiteralPath $source -File -Recurse -Force|Sort-Object FullName|ForEach-Object{[ordered]@{Path=$_.FullName.Substring($source.Length);Length=$_.Length;SHA256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}})
$px=@(Get-Process XWall -ErrorAction SilentlyContinue)
$rep=@(Get-ChildItem -LiteralPath "$card\reports" -File -Force)
$doc=$null;$docHash='';$excerpt='';$fragments=@();$numbers=@()
if($rep.Count -eq 1){
 $doc=[ordered]@{Name=$rep[0].Name;Length=$rep[0].Length;LastWriteTimeUtc=$rep[0].LastWriteTime.ToUniversalTime().ToString('o')}
 $docHash=(Get-FileHash -LiteralPath $rep[0].FullName -Algorithm SHA256).Hash
 $text=[IO.File]::ReadAllText($rep[0].FullName)
 $excerpt=$text.Substring(0,[Math]::Min(1500,$text.Length))
 $numbers=@([regex]::Matches($text,'\d+\.\d{4,6}')|ForEach-Object{$_.Value}|Select-Object -Unique -First 25)
 $fragments=@([regex]::Matches($text,'[\u4e00-\u9fa5]{4,14}')|ForEach-Object{$_.Value}|Select-Object -Unique -First 60)
}
[ordered]@{
 At=[DateTime]::UtcNow.ToString('o')
 Files=$files
 FileCount=$files.Count
 Client=(Get-FileHash -LiteralPath "$client\XWall.exe" -Algorithm SHA256).Hash
 SampleHash=(Get-FileHash -LiteralPath $sample -Algorithm SHA256).Hash
 ClientFiles=@(Get-ChildItem -LiteralPath $client -File -Recurse -Force).Count
 Processes=@($px|Select-Object Id,Path,SessionId,Responding,MainWindowHandle)
 TCP=@(foreach($p in $px){Get-NetTCPConnection -OwningProcess $p.Id -ErrorAction SilentlyContinue|Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,State})
 Report=$doc
 ReportHash=$docHash
 Excerpt=$excerpt
 Fragments=$fragments
 Numbers=$numbers
 ReportsCount=$rep.Count
 HookOutRecent=@(Get-ChildItem -LiteralPath 'C:\hwk\hook-out' -Recurse -File -ErrorAction SilentlyContinue|Where-Object {$_.LastWriteTime.ToUniversalTime() -gt [datetime]'2026-10-19T19:45:00Z'}|Select-Object FullName,Length)
 Task=@(Get-ScheduledTask -TaskName 'HWKModern-000048-Probe' -ErrorAction SilentlyContinue|Select-Object TaskName,State)
 CardWrites=@(Get-ChildItem -LiteralPath $card -Recurse -File -Force|Where-Object {$_.LastWriteTime.ToUniversalTime() -gt [datetime]'2026-10-19T19:45:00Z'}|Select-Object FullName,Length)
 Errors=@(Get-WinEvent -FilterHashtable @{LogName='Application';Id=1000,1001,1026;StartTime=[datetime]'2026-10-19T19:45:00Z'} -ErrorAction SilentlyContinue|Where-Object {$_.Message -match 'XWall'}|ForEach-Object{[ordered]@{Time=$_.TimeCreated.ToUniversalTime().ToString('o');Id=$_.Id}})
}|ConvertTo-Json -Depth 6|Set-Content "$card\independent.json" -Encoding UTF8
'''

read_back = r'''$p=Get-Content 'C:\hwk-modern\HWK-000048-B02-02\independent.json' -Raw -Encoding UTF8|ConvertFrom-Json
[ordered]@{At=$p.At;Files=$p.Files;FileCount=$p.FileCount;Client=$p.Client;SampleHash=$p.SampleHash;ClientFiles=$p.ClientFiles;Processes=$p.Processes;TCP=$p.TCP;Report=$p.Report;ReportHash=$p.ReportHash;Excerpt=$p.Excerpt;Fragments=$p.Fragments;Numbers=$p.Numbers;ReportsCount=$p.ReportsCount;HookOutRecent=$p.HookOutRecent;Task=$p.Task;CardWrites=$p.CardWrites;Errors=$p.Errors}|ConvertTo-Json -Depth 6
'''


def load(path):
    try:
        return json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f'cannot read {path}: {error}') from error


print(run_ps(CMD, OUT / 'independent-capture', timeout=600))
raw = run_ps(read_back, OUT / 'independent-read', timeout=300)
try:
    data = json.loads(raw)
except json.JSONDecodeError as error:
    raise SystemExit(f'independent capture is not JSON: {error}') from error
(OUT / 'independent.json').write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')

baseline = load('evidence/stages/B02/B02-01/attempt-41/environment-final/stdout')['After']
claimed = load('evidence/stages/B02/B02-02/attempt-47/final.json')
index = lambda rows: {r['Path']: (r['Length'], r['SHA256']) for r in rows}  # noqa: E731

now = index(data['Files'])
result = {
    'at': data['At'],
    'file_count': data['FileCount'],
    'source_equals_frozen_baseline': now == index(baseline),
    'source_equals_delivered': now == index(claimed['Files']),
    'client_hash': data['Client'],
    'client_hash_claimed': data['Client'] == '76838A839C5EF262499D6315570DA26FFD59DA7BB29ED616ADAA6B4BFE7221E5',
    'sample_hash': data['SampleHash'],
    'sample_hash_claimed': data['SampleHash'] == '2FFA32CB256324AE610C2215BFE554DDB42BA0CBB06108188C6727B2F060FBE3',
    'processes': data['Processes'],
    'tcp': data['TCP'],
    'reports_count': data['ReportsCount'],
    'report': data['Report'],
    'report_hash': data['ReportHash'],
    'report_hash_matches_claim': data['ReportHash'] == '577D61F43EB26BFD603BDB1A654D31F1E2B396F078934BFC8544CDE33A52A7B0',
    'numbers_sample': data['Numbers'][:8],
    'fragment_sample': data['Fragments'][:12],
    'writes_to_default_dir': data['HookOutRecent'],
    'task': data['Task'],
    'card_writes_outside_reports': [
        row for row in data['CardWrites'] if '\\reports\\' not in row['FullName']
    ][:40],
    'errors': data['Errors'],
}
(OUT / 'verify.json').write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding='utf-8')
print(json.dumps({k: v for k, v in result.items() if k not in ('card_writes_outside_reports',)},
                 ensure_ascii=False, indent=1)[:3000])
