"""Build execution-only delivery manifest; never grants independent acceptance."""
import datetime,hashlib,json
from pathlib import Path
B=Path('evidence/stages/B02/B02-02/attempt-46')
A=Path('evidence/scheduler/20261018T181701861583Z/stage-assignment.json')
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=read(A)
x={
 'goal_id':'HWK-G001','stage_id':'B02','stage_item_id':'B02-02','card_id':'HWK-000046',
 'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'PARTIAL','candidate_status':'PARTIAL','independent_acceptance':'NOT_RUN',
 'goal':a['item']['goal'],'done_when':a['item']['done_when'],
 'inputs':[{'path':str(p),'sha256':sha(p)} for p in [*(Path(v) for v in a['item']['inputs']),A,A.parent/'rea-preflight/version-check.json']],
 'evidence_type':'LIVE_REMOTE_UI_TEXT_SCREENSHOT_PROCESS_TCP_EVENT_LOG_SHA256',
 'verified':[
  'Before recovery: no XWall; 445 source installation files equal B02-01 frozen inventory; isolated EXE and working real sample hashes match',
  'Restored SAME B02-01 isolated client and sample, PID113264/session4; no concurrent XWall launch',
  'Actual in-memory load calculation edit observed: initial20m -> accidental2021m -> corrected21m -> restored20m. Each final named capture has corresponding UI text and screenshot',
  '21m output height coefficient0.754007, gust coefficient1.976809 and pre-minimum negative horizontal load-0.768453kN/m2; restored20m outputs0.737993,1.98735,-0.756143kN/m2',
  'Minimum load branch leaves final panel combination1.672032kN/m2 at both20m and21m; changed intermediate result is evidence of recomputation rather than relying on unchanged final value',
  'Client responsive after operations; TCP165.154.20.222:1433 state5 observed. Endpoint identity, protocol semantics and relation to license remain unknown',
  'After actions445 source hashes still identical; isolated EXE and working sample unchanged; bounded Application IDs1000/1001/1026 query since18:17Z found no matching XWall event',
  'Own Probe task removed; PID113264 preserved responsive with20m restored; no save/export requested'
 ],
 'not_verified':[
  'The exercised load calculation is usable without observed license rejection, but whether this branch enforces a license is unknown. Global/full license availability not proven; no license bypass performed',
  'No report file, drawing export, save/reopen or complete calculation-system coverage; B02-03 remains separate',
  'Server identity/protocol/license validation semantics; this card did not refresh About expiry (prior display evidence remains historical)',
  'Installer control flow, reinstall and clean install/uninstall remain B01/R01; no claim of fresh installation',
  'Initial20m RichEdit text was not captured before edit; initial screenshot and restored20m full text are separate observations',
  'Independent package acceptance pending; B02 and overall Goal incomplete'
 ],
 'criterion_evidence':{
  'before':'preflight/stdout','before_comparison':'preflight-comparison.json',
  'launch':'launch.ps1','launch_observation':'launch-status/stdout',
  'accidental2021m':'height21-text.json','corrected21m':'height21-corrected.json',
  'restored20m':'height20-restored.json','after':'postflight/stdout','cleanup':'cleanup/stdout'
 },
 'checks':read(B/'checks.json'),'npm_checks':'NOT_RUN: no application established',
 'rea':{'expected_package_version':'6.7.0','status':'BLOCKED_BY_CLIENT_APPROVAL','raw':'MCP tool call requires approval, but approval policy is never','retry':False,'analysis':'NOT_RUN: OS/UI evidence only, no new binary analysis required'},
 'errors_retained':[
  'prepare query user returned exit1 despite valid session listing; directory creation succeeded. No duplicate prepare run',
  'Early capture reads raced output creation or mixed preceding ui.json and new desktop.png; retain early captures only as discovery, not synchronized proof',
  'Collector corrected to unique action-named remote files and bounded wait for JSON; read attempts use separate capture directories. Final height21-text/corrected/restored captures are unique',
  'Ctrl+A did not select all in native property editor: requested21 appended to20 producing2021. Actual result retained; corrected using HOME SHIFT+END with focused-process/class/value guards, then restored20',
  'focus-status serialized extended PowerShell Get-Content string properties, producing verbose raw output; not relied on for facts. No password file read',
  'Task LastRunTime/result can lag; action-named files and embedded observation times used instead'
 ],
 'remote_changes':['Own C:\\hwk-modern\\HWK-000046-B02-02 directory, probe script/evidence and own task only','Authorized recovery of existing isolated client; in-memory property edits and restoration; application may update its own isolated client files','No source installation/sample, license, binary or server edits; no historical C:\\hwk script execution or output requested'],
 'cleanup':read(B/'cleanup/stdout'),
 'resource':{'created':False,'cost':'UNKNOWN existing ECS'},
 'continuation':{'decision':'CONTINUE','execution_focus':'Independent review reruns check-b02-license-46.py and reads live PID113264/session4/path, source hashes, sample hash and TCP directly. Decide whether this actual load recomputation adequately demonstrates the required usable licensed operation; do not infer license enforcement. If more evidence needed, preserve this result and exercise another reversible calculation branch in SAME process or ordinary UI directory-tree navigation to this card authorized output directory; validate actual path before any report export, never C:\\hwk\\hook-out. No restart while process survives; no BFFM_SETSELECTIONW.'},
 'prior_delivery':str(B/'prior-work-package.json'),
 'output_hash_manifest':str(B/'delivery-hashes.json')
}
x['criterion_evidence']={k:str(B/v) for k,v in x['criterion_evidence'].items()}
out=Path('evidence/stages/B02/B02-02/work-package.json')
if not (B/'prior-work-package.json').exists():(B/'prior-work-package.json').write_bytes(out.read_bytes())
for p in [out,B/'work-package.json']:p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
paths=[p for p in B.rglob('*') if p.is_file() and p.name!='delivery-hashes.json']+[out,Path('scripts/check-b02-license-46.py'),Path('scripts/collect-b02-ui-46.py'),Path('scripts/make-b02-action-46.py'),Path(__file__),*Path('scripts').glob('ecs-b02-*-46.ps1')]
(B/'delivery-hashes.json').write_text(json.dumps({str(p):sha(p) for p in sorted(paths)},indent=2)+'\n')
