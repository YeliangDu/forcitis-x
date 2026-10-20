import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import convergence,stages
class ConvergenceTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  for name in ['planning','evidence']:(self.root/name).mkdir()
  self.folder=self.root/'evidence/judgment';self.folder.mkdir()
  self.item={'id':'I','goal':'full goal','done_when':'all real outputs verified','inputs':['real'],'outputs':['evidence/delivery'],'depends_on':[],'max_rounds_before_review':2}
  c={'version':1,'goal':{'id':'HWK-G001'},'stages':[{'id':'B02','outcome':'runtime','not_in_scope':[],'block_when':[],'work_items':[self.item]}]}
  p={'contract_version':1,'stages':{'B02':{'items':{'I':{'status':'BLOCKED','rounds':1,'reviewer':'old','reason':'network unavailable','evidence':['evidence/failure']}}}}}
  t={'active_task':'B02','tasks':[{'id':'B02','status':'PARTIAL','depends_on':[]}]}
  for name,data in [('stage-contracts',c),('stage-progress',p),('tasks',t),('convergence-policy',{'enabled':True})]:self.save(self.root/'planning'/(name+'.json'),data)
  (self.root/'evidence/failure').write_text('real connection failure');(self.root/'evidence/delivery').write_text('partial outputs')
  self.save(self.folder/'planner.jsonl',{'type':'item.completed','item':{'type':'command_execution','command':'check actual input','exit_code':0}})
  self.report={'decision':'CONTINUE','stage_item_id':'I','reason':'new ability verified, retry existing work','execution_focus':'verify live connection then collect only missing environment fields','evidence':['evidence/failure'],'checks':[{'command':'check actual input','exit_code':0}]}
 def save(self,path,data):path.write_text(json.dumps(data))
 def select(self):
  with patch.object(stages.assurance,'next_assignment',return_value=None):return stages.select(self.root)
 def test_unexhausted_failure_goes_to_agent_not_global_pause(self):self.assertEqual(self.select()['kind'],'continuation_plan')
 def test_agent_schedule_keeps_failure_and_rounds(self):
  a=convergence.assignment(self.root);before=copy.deepcopy(a)
  convergence.apply(self.root,a,self.report,self.folder)
  state=stages.load(self.root)[1]['stages']['B02']['items']['I']
  self.assertEqual(state['status'],'BLOCKED');self.assertEqual(state['rounds'],1);self.assertEqual(state['dispatch_status'],'ready')
  self.assertEqual(self.select()['item']['id'],'I');self.assertEqual(a,before)
 def test_round_hint_never_stops_partial_progress(self):
  c,p,t=stages.load(self.root);e=p['stages']['B02']['items']['I'];e.update(status='PARTIAL',rounds=200,dispatch_status='ready');self.save(self.root/'planning/stage-progress.json',p)
  a=self.select();result={'outcome':'continue','stage_item_id':'I','stage_item_status':'PARTIAL','stage_item_evidence':['evidence/failure'],'reason':'one actual gap closed','continuation':{'decision':'CONTINUE','reason':'verified incremental result','execution_focus':'next missing field'}}
  with patch.object(stages.assurance,'next_assignment',return_value=None):stages.apply(self.root,a,result,'new')
  state=stages.load(self.root)[1]['stages']['B02']['items']['I'];self.assertEqual(state['status'],'PARTIAL');self.assertEqual(state['rounds'],201)
  self.assertEqual(self.select()['item']['id'],'I')
 def test_invented_check_rejected(self):
  self.report['checks'][0]['command']='fake success'
  with self.assertRaisesRegex(ValueError,'not backed'):convergence.apply(self.root,convergence.assignment(self.root),self.report,self.folder)
 def test_wait_external_never_grants_pass_or_dispatch(self):
  self.report['decision']='WAIT_EXTERNAL';a=convergence.assignment(self.root)
  self.assertEqual(convergence.apply(self.root,a,self.report,self.folder),'WAIT_EXTERNAL');self.assertEqual(stages.load(self.root)[1]['stages']['B02'],a['progress'])
 def test_stale_progress_rejected(self):
  a=convergence.assignment(self.root);c,p,t=stages.load(self.root);p['stages']['B02']['items']['I']['rounds']=2;self.save(self.root/'planning/stage-progress.json',p)
  with self.assertRaisesRegex(ValueError,'inputs changed'):convergence.apply(self.root,a,self.report,self.folder)
 def test_unknown_leaf_rejected(self):
  self.report['stage_item_id']='other'
  with self.assertRaisesRegex(ValueError,'concrete executable'):convergence.apply(self.root,convergence.assignment(self.root),self.report,self.folder)
 def test_successful_resume_automatically_closes_dispatch_incident(self):
  base=self.root/'evidence/scheduler';base.mkdir();incident_folder=base/'blockers/incident';incident_folder.mkdir(parents=True)
  incident_path=incident_folder/'incident.json';self.save(incident_path,{'id':'incident','status':'action_required','reason':'old network refusal','source_state':{'run':'old-run'}})
  (base/'PAUSED').write_text('old network refusal')
  config=self.root/'scripts/scheduler';config.mkdir(parents=True);(config/'convergence-plan.txt').write_text('readonly continuation')
  a=convergence.assignment(self.root);a['incident']=str(incident_path.relative_to(self.root))
  def agent(role,folder,**kw):
   self.assertEqual(kw['sandbox'],'read-only');self.save(folder/'planner-final.txt',self.report)
   self.save(folder/'planner.jsonl',{'type':'item.completed','item':{'type':'command_execution','command':'check actual input','exit_code':0}})
  with patch.object(convergence.check_rea,'check'),patch.object(convergence.subprocess,'run',return_value=type('Result',(),{'returncode':0,'stdout':'PASS','stderr':''})()):convergence.plan(self.root,agent,a,'old network refusal')
  self.assertEqual(json.loads(incident_path.read_text())['status'],'resolved');self.assertFalse((base/'PAUSED').exists())
  self.assertEqual(stages.load(self.root)[1]['stages']['B02']['items']['I']['status'],'BLOCKED')
 def test_dependencies_cannot_be_bypassed(self):
  c,p,t=stages.load(self.root);c['stages'][0]['work_items'][0]['depends_on']=['D'];p['stages']['B02']['items']['D']={'status':'BLOCKED'};self.save(self.root/'planning/stage-contracts.json',c);self.save(self.root/'planning/stage-progress.json',p)
  with self.assertRaisesRegex(ValueError,'bypass dependencies'):convergence.apply(self.root,convergence.assignment(self.root),self.report,self.folder)
if __name__=='__main__':unittest.main()
