import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import recovery

class RecoveryTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.base=self.root/'evidence/scheduler';self.base.mkdir(parents=True);(self.root/'planning').mkdir()
  self.folder=self.base/'recovery';self.folder.mkdir()
  item={'id':'B01-02','goal':'full inventory','done_when':'all payload hashes','depends_on':[],'max_rounds_before_review':2}
  prior={'status':'BLOCKED','rounds':2,'reason':'missing payloads','evidence':['evidence/fail.json'],'reviewer':'old'}
  data={'stage-contracts':{'version':1,'goal':{'id':'HWK-G001','outcome':'full replacement'},'stages':[{'id':'B01','work_items':[item]}]},'stage-progress':{'contract_version':1,'stages':{'B01':{'items':{'B01-02':prior}}}},'tasks':{'active_task':'B01','tasks':[{'id':'B01'}]},'auto-recovery-policy':{'enabled':True,'max_incidents_per_stage':4,'max_reopens_per_item':1,'extra_rounds_per_item':2}}
  for name,d in data.items():self.save(self.root/'planning'/ (name+'.json'),d)
  self.a={'stage_id':'B01','item':copy.deepcopy(item),'prior_state':copy.deepcopy(prior),'frozen':{str(p.relative_to(self.root)):recovery.digest(p) for p in (self.root/'planning').glob('*.json')}}
  self.save(self.folder/'task-card.json',{'id':'HWK-000032'})
  self.save(self.folder/'repair_review.jsonl',{'type':'item.completed','item':{'type':'command_execution','command':'real verification','exit_code':0}})
  (self.root/'evidence/proof').write_text('verified real fixture')
  self.r={'approved':True,'reason':'new finite extraction verified','reopen_item_id':'B01-02','evidence':['evidence/proof'],'checks':[{'command':'real verification','exit_code':0}]}
 def save(self,p,v):p.write_text(json.dumps(v))
 def register(self):
  with patch.object(recovery.stages,'select',return_value={'kind':'plan_audit'}):return recovery.register(self.root,self.a,self.r,self.folder)
 def test_reviewed_reopen_keeps_goal_done_when_failure_and_rounds(self):
  self.register();c,p,t=recovery.stages.load(self.root)
  item=c['stages'][0]['work_items'][0];state=p['stages']['B01']['items']['B01-02']
  self.assertEqual(item['done_when'],'all payload hashes');self.assertEqual(c['goal']['outcome'],'full replacement')
  self.assertEqual(state['rounds'],2);self.assertEqual(state['recoveries'][0]['prior_state'],self.a['prior_state'])
  self.assertEqual(state['status'],'PARTIAL');self.assertEqual(item['max_rounds_before_review'],4)
  self.assertEqual(c['version'],p['contract_version']);self.assertFalse((self.base/'recovery-transaction.json').exists())
 def test_rejection_never_modifies_contract(self):
  before=(self.root/'planning/stage-contracts.json').read_bytes();self.r['approved']=False
  with self.assertRaisesRegex(ValueError,'rejected'):self.register()
  self.assertEqual(before,(self.root/'planning/stage-contracts.json').read_bytes())
 def test_fake_success_command_rejected(self):
  self.r['checks'][0]['command']='invented green check'
  with self.assertRaisesRegex(ValueError,'not backed'):self.register()
 def test_stale_contract_rejected(self):
  p=self.root/'planning/tasks.json';p.write_text(p.read_text()+' ')
  with self.assertRaisesRegex(ValueError,'Frozen input'):self.register()
 def test_wrong_target_rejected(self):
  self.r['reopen_item_id']='B01-03'
  with self.assertRaisesRegex(ValueError,'target mismatch'):self.register()
 def test_second_reopen_disallowed(self):
  self.register();c,p,t=recovery.stages.load(self.root);p['stages']['B01']['items']['B01-02']['status']='BLOCKED';p['stages']['B01']['items']['B01-02']['rounds']=4
  self.save(self.root/'planning/stage-progress.json',p)
  with self.assertRaisesRegex(ValueError,'No eligible'):recovery.target(self.root,{'resolution':{'route':'REPLAN'}},json.loads((self.root/'planning/auto-recovery-policy.json').read_text()))
 def test_protected_mutation_rejected_analysis_script_allowed(self):
  self.assertIn('scripts/a.py',recovery.changes(self.root,{'scripts/a.py':'a'},{'scripts/a.py':'b'}))
  for name in ['vendor/a','planning/tasks.json','scripts/scheduler/runner.py','HANDOFF.md']:
   with self.assertRaisesRegex(ValueError,'protected'):recovery.changes(self.root,{name:'a'},{name:'b'})
 def test_failed_target_falls_through_to_other_eligible_package(self):
  c,p,t=recovery.stages.load(self.root)
  other=copy.deepcopy(c['stages'][0]['work_items'][0]);other['id']='B01-03';c['stages'][0]['work_items'].append(other)
  p['stages']['B01']['items']['B01-03']=copy.deepcopy(p['stages']['B01']['items']['B01-02'])
  self.save(self.root/'planning/stage-contracts.json',c);self.save(self.root/'planning/stage-progress.json',p)
  incident={'resolution':{'route':'REPLAN'},'repair_item_attempts':{'B01-02':2}}
  policy=json.loads((self.root/'planning/auto-recovery-policy.json').read_text())
  self.assertEqual(recovery.target(self.root,incident,policy)[1]['id'],'B01-03')
 def test_live_or_transaction_prevents_repair(self):
  for name in ['active.json','recovery-transaction.json']:
   (self.base/name).write_text('{}')
   with patch.object(recovery.blockers,'capture') as capture:recovery.handle(self.root,None);capture.assert_not_called()
   (self.base/name).unlink()
 def exercise_pipeline(self,user_pause=False,reject=False):
  policy=json.loads((self.root/'planning/auto-recovery-policy.json').read_text());policy.update(authorization='test authorization',allowed_routes=['REPLAN']);self.save(self.root/'planning/auto-recovery-policy.json',policy)
  config=self.root/'scripts/scheduler';config.mkdir(parents=True)
  for name in ('recovery-worker.txt','recovery-reviewer.txt'):(config/name).write_text('test prompt')
  (self.base/'PAUSED').write_text('exhausted')
  self.save(self.base/'state.json',{'status':'blocked','run':'failed'})
  folder=recovery.blockers.capture(self.root);incident=json.loads((folder/'incident.json').read_text());incident.update(status='action_required',resolution={'route':'REPLAN'});self.save(folder/'incident.json',incident)
  calls=[]
  def agent(role,work,**kw):
   calls.append((role,kw.get('sandbox')))
   if role=='repairer':self.save(work/'repairer-final.txt',{'status':'ready','reason':'verified method'})
   else:
    report=copy.deepcopy(self.r);report['approved']=not reject
    self.save(work/'repair_review-final.txt',report);self.save(work/'repair_review.jsonl',{'type':'item.completed','item':{'type':'command_execution','command':'real verification','exit_code':0}})
    if user_pause:(self.base/'PAUSED').write_text('Paused by user at test')
  with patch.object(recovery.check_rea,'check'),patch.object(recovery.subprocess,'run',return_value=type('Result',(),{'returncode':0,'stdout':'PASS','stderr':''})()),patch.object(recovery.stages,'select',return_value={'kind':'plan_audit'}):
   recovery.handle(self.root,agent)
   if not reject:recovery.handle(self.root,agent)
  self.assertEqual(calls,[('repairer',None),('repair_review','read-only')])
  return json.loads((folder/'incident.json').read_text())
 def test_pipeline_registers_then_resumes_once(self):
  result=self.exercise_pipeline();self.assertEqual(result['status'],'resolved_for_retry');self.assertFalse((self.base/'PAUSED').exists())
 def test_pipeline_never_overrides_new_user_pause(self):
  self.exercise_pipeline(user_pause=True);self.assertTrue((self.base/'PAUSED').read_text().startswith('Paused by user'))
 def test_pipeline_rejection_preserves_pause_and_blocked_package(self):
  result=self.exercise_pipeline(reject=True);self.assertEqual(result['status'],'repair_blocked');self.assertTrue((self.base/'PAUSED').exists())
  self.assertEqual(recovery.stages.load(self.root)[1]['stages']['B01']['items']['B01-02']['status'],'BLOCKED')
 def test_crash_during_contract_write_leaves_stop_marker(self):
  save=recovery.cards.save
  def fail(path,value):
   if path==self.root/'planning/stage-progress.json':raise OSError('simulated interruption')
   save(path,value)
  with patch.object(recovery.cards,'save',side_effect=fail):
   with self.assertRaises(OSError):self.register()
  self.assertTrue((self.base/'recovery-transaction.json').exists())

if __name__=='__main__':unittest.main()
