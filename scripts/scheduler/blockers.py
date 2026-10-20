"""Durable, bounded blocker diagnosis. Never clears PAUSED or changes acceptance."""
import hashlib, json
from pathlib import Path
import cards
import check_rea


def capture(root):
 base=root/'evidence/scheduler'; pause=base/'PAUSED'
 if not pause.exists():return None
 reason=pause.read_text()
 if reason.startswith('Paused by user'):return None
 state=json.loads((base/'state.json').read_text()) if (base/'state.json').exists() else {}
 if state.get('status')=='complete':return None
 # Bind to the incident, not volatile clock/diagnostic files.
 identity={'reason':reason,'run':state.get('run')}
 key=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()[:24]
 folder=base/'blockers'/key;folder.mkdir(parents=True,exist_ok=True)
 path=folder/'incident.json'
 if not path.exists():
  cards.save(path,{'id':key,'status':'pending','reason':reason,'source_state':state,
   'owner':'local-controller','attempts':0,'resolution':None})
 cards.save(base/'blocker-current.json',{'id':key,'incident':str(path.relative_to(root))})
 return folder


def diagnose(root,run_agent):
 base=root/'evidence/scheduler'
 if (base/'active.json').exists():return
 folder=capture(root)
 if folder is None:return
 path=folder/'incident.json';incident=json.loads(path.read_text())
 if incident['attempts']>=1:return
 # Claim before spawning: a crash cannot create unlimited automatic retries.
 incident.update(status='diagnosing',attempts=1);cards.save(path,incident)
 try:
  cards.create(root,folder,goal='阻塞独立诊断与有限恢复方案',track='blocker',session_roles=[('diagnostician','阻塞诊断')])
  check_rea.check(folder/'rea-preflight')
  prompt=(root/'scripts/scheduler/blocker.txt').read_text()+'\n阻塞记录：'+str(path.relative_to(root))
  run_agent('diagnostician',folder,prompt=prompt,sandbox='read-only',schema=root/'scripts/scheduler/blocker-result.schema.json')
  report=json.loads((folder/'diagnostician-final.txt').read_text())
  report=validate_report(root,report)
  incident.update(status='action_required',resolution=report)
 except Exception as exc:incident.update(status='diagnosis_failed',error=str(exc))
 finally:
  cards.save(path,incident)
  if (folder/'task-card.json').exists():cards.finish(root,folder,{'status':incident['status'],'reason':incident.get('error',incident['reason'])})
  (base/'active.json').unlink(missing_ok=True)


def validate_report(root,report):
 if report.get('route') not in ('LOCAL_FIX','REPLAN','EXTERNAL_INPUT') or not all(report.get(k) for k in ('reason','next_actions','release_conditions','evidence')):raise ValueError('Incomplete blocker diagnosis')
 report=dict(report);paths=[]
 for raw in report['evidence']:
  p=Path(raw)
  if '..' in p.parts:raise ValueError('Unsafe evidence')
  if p.is_absolute():p=p.relative_to(root)
  target=root/p
  target.resolve().relative_to(root.resolve())
  if any(part.is_symlink() for part in [target,*target.parents] if part!=root and root in part.parents):raise ValueError('Symlink evidence')
  if not target.is_file():raise ValueError('Missing evidence: '+raw)
  paths.append(str(p))
 report['evidence']=paths
 return report


def close_event(root,incident_path,*,status,reason,evidence,by,related_packages=None):
 """Close a scheduling incident, keeping original failures and package verdicts."""
 if status not in ('resolved','superseded','consolidated'):raise ValueError('Invalid incident closure')
 validated=validate_report(root,{'route':'LOCAL_FIX','reason':reason,'next_actions':['closed with evidence'],'release_conditions':['checked'],'evidence':evidence})
 incident=json.loads(incident_path.read_text());base=root/'evidence/scheduler'
 record={'status':status,'reason':reason,'evidence':validated['evidence'],'by':by,'at':cards.stamp(),'scope':'dispatch incident only; package acceptance unchanged','related_packages':related_packages or []}
 incident.setdefault('closure_history',[]).append(record);incident['closure']=record;incident['status']=status;cards.save(incident_path,incident)
 ledger_path=base/'issue-closures.json';ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else {'cards':{},'events':[]}
 index=json.loads((base/'cards.json').read_text()) if (base/'cards.json').exists() else []
 source=incident.get('source_state',{}).get('run');diagnostic=str(incident_path.parent)
 for card in index:
  run=card.get('run');related=run in (source,diagnostic)
  if run and not related:
   p=Path(run)/'recovery-assignment.json'
   if p.exists():related=json.loads(p.read_text()).get('incident')==str(incident_path.relative_to(root))
  if related:ledger['cards'][card['id']]=record
 ledger['events'].append(dict(record,incident=str(incident_path.relative_to(root))));cards.save(ledger_path,ledger)
 return record
