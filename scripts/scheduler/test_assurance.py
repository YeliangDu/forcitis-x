"""Goal release tests use real temporary reports, files and command event logs."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import assurance,stages

class AssuranceTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  for d in ('planning','evidence'): (self.root/d).mkdir()
  self.contracts={'version':1,'goal':{'id':'HWK-G001'},'stages':[{'id':'B01','work_items':[{'id':'I','outputs':['evidence/proof.json']}]}]}
  self.progress={'contract_version':1,'stages':{'B01':{'items':{'I':{'status':'PASS','reviewer':'HWK-000001','evidence':['evidence/proof.json']}}}}}
  self.tasks={'active_task':'B01','tasks':[{'id':'B01','status':'PARTIAL','depends_on':[]}]}
  for name,data in [('stage-contracts',self.contracts),('stage-progress',self.progress),('tasks',self.tasks),('goal-assurance-policy',{'goal_id':'HWK-G001','requirements':[{'id':'G1','stages':['B01']},{'id':'G2','stages':['B01']}]})]:self.write('planning/'+name+'.json',data)
  self.write('evidence/proof.json',{'source':'fixture, not runtime evidence'})
  self.log=self.root/'evidence/commands.jsonl';self.command(0)
 def write(self,path,value): (self.root/path).write_text(json.dumps(value))
 def command(self,code):self.write('evidence/commands.jsonl',{'type':'item.completed','item':{'type':'command_execution','command':'verify fixture','exit_code':code}})
 def assignment(self,kind='stage_audit'):return assurance.assignment(self.root,self.contracts,self.progress,self.tasks,kind,'B01')
 def report(self,kind='stage_audit'):
  return dict(kind=kind,stage_id='B01',stage_achievement='PASS',goal_contribution='PASS',composition_status='PASS',overall_goal_achievement='PARTIAL',decision='CONTINUE',next_step_justified=True,reason='fixture audit',composition_argument='coverage examined',counterexamples=['missing runtime remains later work'],claims=[dict(requirement_id=i,status='PASS',reason='checked fixture',evidence_type='STATIC',evidence=['evidence/proof.json']) for i in ('G1','G2')],gaps=[],checks=[dict(command='verify fixture',exit_code=0)],evidence=['evidence/proof.json'])
 def apply(self,a,r):return assurance.apply(self.root,a,r,'HWK-000002',self.log)
 def test_handoff_is_allowed_but_traversal_and_symlink_are_rejected(self):
  (self.root/'HANDOFF.md').write_text('handoff')
  self.assertIn('HANDOFF.md',assurance.file_hashes(self.root,['HANDOFF.md']))
  for path in ['../HANDOFF.md','/etc/passwd']:
   with self.assertRaises(ValueError):assurance.file_hashes(self.root,[path])
  (self.root/'evidence/link').symlink_to(self.root/'HANDOFF.md')
  with self.assertRaises(ValueError):assurance.file_hashes(self.root,['evidence/link'])
 def test_stage_release_chooses_runtime_priority_without_marking_static_complete(self):
  self.contracts['stages'] += [{'id':'B02','work_items':[]},{'id':'B03','work_items':[]}]
  self.progress['stages'].update(B02={'items':{}},B03={'items':{}})
  self.tasks['tasks'] += [{'id':'B02','status':'PARTIAL','depends_on':[],'schedule_priority':100},{'id':'B03','status':'NOT_RUN','depends_on':['B01'],'schedule_priority':10}]
  for name,data in [('stage-contracts',self.contracts),('stage-progress',self.progress),('tasks',self.tasks)]:self.write('planning/'+name+'.json',data)
  self.apply(self.assignment(),self.report())
  tasks=json.loads((self.root/'planning/tasks.json').read_text())
  self.assertEqual(tasks['active_task'],'B03');self.assertEqual(tasks['tasks'][1]['status'],'PARTIAL')
 def test_packages_do_not_bypass_plan_audit(self):
  self.assertEqual(assurance.next_assignment(self.root,self.contracts,self.progress,self.tasks)['kind'],'plan_audit')
  with self.assertRaisesRegex(stages.StageBlocked,'独立审查'):stages.ready_item(self.root,'B01','I')
 def test_empty_stage_cannot_pass(self):self.assertFalse(stages.all_passed(self.root,{'work_items':[]},{'items':{}}))
 def test_stage_pass_but_contribution_fail_blocks(self):
  r=self.report();r['goal_contribution']='FAIL';self.assertEqual(self.apply(self.assignment(),r)['outcome'],'blocked')
  self.assertEqual(json.loads((self.root/'planning/tasks.json').read_text())['tasks'][0]['status'],'PARTIAL')
 def test_all_obligations_required(self):
  r=self.report();r['claims'].pop()
  with self.assertRaisesRegex(ValueError,'逐项'):self.apply(self.assignment(),r)
 def test_checks_must_match_actual_execution(self):
  self.command(1)
  with self.assertRaisesRegex(ValueError,'Final check'):self.apply(self.assignment(),self.report())
 def test_negative_review_preserves_failed_check_and_unassigned_gap(self):
  self.command(1);r=self.report();r.update(decision='REPLAN',goal_contribution='FAIL',checks=[dict(command='verify fixture',exit_code=1)],gaps=[dict(owner_stage='UNKNOWN',verification='',blocks_next_step=True,description='missing ownership')])
  self.assertEqual(self.apply(self.assignment(),r)['outcome'],'blocked');self.assertTrue(assurance.state(self.root)['history'])
 def test_annotated_evidence_path_rejected_without_release(self):
  r=self.report();r['claims'][0]['evidence']=['evidence/proof.json: explanation']
  with self.assertRaisesRegex(ValueError,'审查证据不存在'):self.apply(self.assignment(),r)
  self.assertFalse((self.root/'planning/goal-assurance.json').exists())
 def test_changed_subject_rejected(self):
  a=self.assignment();self.write('evidence/proof.json',{'changed':True})
  with self.assertRaisesRegex(ValueError,'陈旧'):self.apply(a,self.report())
 def test_same_package_review_session_rejected(self):
  with self.assertRaisesRegex(ValueError,'新审查会话'):assurance.apply(self.root,self.assignment(),self.report(),'HWK-000001',self.log)
 def test_plan_cannot_claim_overall_completion(self):
  r=self.report('plan_audit');r.update(overall_goal_achievement='PASS',decision='COMPLETE')
  with self.assertRaises(ValueError):self.apply(self.assignment('plan_audit'),r)
 def test_cached_report_and_command_log_integrity(self):
  a=self.assignment('plan_audit');self.apply(a,self.report('plan_audit'))
  self.assertTrue(assurance.verified_plan(self.root,self.contracts,self.tasks))
  original=self.log.read_text();self.command(1)
  self.assertFalse(assurance.verified_plan(self.root,self.contracts,self.tasks));self.log.write_text(original)
  record=assurance.state(self.root)['plan'];self.write(record['report'],{'tampered':True})
  self.assertFalse(assurance.verified_plan(self.root,self.contracts,self.tasks))
 def test_support_change_invalidates_plan(self):
  self.apply(self.assignment('plan_audit'),self.report('plan_audit'));self.write('evidence/proof.json',{'changed':True})
  self.assertFalse(assurance.verified_plan(self.root,self.contracts,self.tasks))
 def final_fixture(self):
  self.contracts['stages'][0]['id']='R01';self.progress['stages']['R01']=self.progress['stages'].pop('B01');self.tasks['active_task']='R01';self.tasks['tasks'][0]['id']='R01'
  for name,value in [('stage-contracts',self.contracts),('stage-progress',self.progress),('tasks',self.tasks)]:self.write('planning/'+name+'.json',value)
  policy=assurance.policy(self.root)
  for requirement in policy['requirements']:requirement['stages']=['R01']
  self.write('planning/goal-assurance-policy.json',policy)
  a=assurance.assignment(self.root,self.contracts,self.progress,self.tasks,'stage_audit','R01')
  r=self.report();r.update(stage_id='R01',overall_goal_achievement='PASS',decision='COMPLETE')
  return a,r
 def test_final_plan_argument_rejected_even_with_green_gate(self):
  a,r=self.final_fixture();r['claims'][0]['evidence_type']='PLAN_ARGUMENT'
  with patch.object(assurance.subprocess,'run') as gate:
   gate.return_value.returncode=0
   self.assertEqual(self.apply(a,r)['outcome'],'blocked')
 def test_final_business_gate_failure_blocks_completion(self):
  a,r=self.final_fixture()
  with patch.object(assurance.subprocess,'run') as gate:
   gate.return_value.returncode=1
   self.assertEqual(self.apply(a,r)['outcome'],'blocked');gate.assert_called_once()
 def test_final_unfinished_requirement_blocks_completion(self):
  a,r=self.final_fixture();r['claims'][0]['status']='NOT_RUN'
  with patch.object(assurance.subprocess,'run') as gate:
   gate.return_value.returncode=0
   self.assertEqual(self.apply(a,r)['outcome'],'blocked')
 def test_final_unreviewed_prior_stage_blocks_completion(self):
  a,r=self.final_fixture();self.tasks['tasks'].append({'id':'B01','status':'PASS','depends_on':[]});self.contracts['stages'].append({'id':'B01','work_items':[]});self.progress['stages']['B01']={'items':{}}
  for name,value in [('stage-contracts',self.contracts),('stage-progress',self.progress),('tasks',self.tasks)]:self.write('planning/'+name+'.json',value)
  a=assurance.assignment(self.root,self.contracts,self.progress,self.tasks,'stage_audit','R01')
  with patch.object(assurance.subprocess,'run') as gate:
   gate.return_value.returncode=0
   self.assertEqual(self.apply(a,r)['outcome'],'blocked')
if __name__=='__main__':unittest.main()
