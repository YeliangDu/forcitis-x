import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import stages
class StageTest(unittest.TestCase):
 def setUp(self):
  guard=patch.object(stages.assurance,'next_assignment',return_value=None);guard.start();self.addCleanup(guard.stop)
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);(self.root/'planning').mkdir();(self.root/'evidence').mkdir()
  self.items=[{'id':'B01-01','title':'identity','goal':'lock identity','done_when':'actual hash/version audit','inputs':['locked inputs'],'outputs':['evidence/delivery.json'],'depends_on':[],'max_rounds_before_review':2},{'id':'B01-02','title':'review','goal':'review stage','done_when':'independent review','inputs':['first proof'],'outputs':['evidence/delivery.json'],'depends_on':['B01-01'],'max_rounds_before_review':2}]
  self.contract={'version':1,'stages':[{'id':'B01','outcome':'verified package','not_in_scope':['runtime'],'block_when':['missing identity'],'work_items':self.items},{'id':'B02','outcome':'runtime','not_in_scope':[],'block_when':[],'work_items':[dict(self.items[0],id='B02-01')]}]}
  self.progress={'contract_version':1,'stages':{s['id']:{'items':{i['id']:{'status':'NOT_RUN','rounds':0,'evidence':[],'reviewer':None,'reason':'pending'} for i in s['work_items']}} for s in self.contract['stages']}}
  self.tasks={'active_task':'B01','tasks':[{'id':'B01','status':'PARTIAL','depends_on':[]},{'id':'B02','status':'NOT_RUN','depends_on':['B01']}]}
  self.save()
 def save(self):
  for name,value in [('stage-contracts',self.contract),('stage-progress',self.progress),('tasks',self.tasks)]: (self.root/'planning'/(name+'.json')).write_text(json.dumps(value))
 def result(self,id,status='PASS'):
  return {'outcome':'continue','new_evidence':True,'reason':'actual evidence','stage_item_id':id,'stage_item_status':status,'stage_item_evidence':['evidence/review.json'],'evidence':['evidence/review.json'],'breakdown':[]}
 def proof(self):
  (self.root/'evidence/review.json').write_text('{"review":"actual"}');(self.root/'evidence/delivery.json').write_text('{"delivery":"actual"}')
 def test_runtime_entry_uses_verified_identity_without_passing_static_stage(self):
  self.proof();self.tasks['active_task']='B02';self.tasks['tasks'][1]['depends_on']=[]
  self.contract['stages'][1]['entry_work_items']=[{'stage_id':'B01','item_id':'B01-01'}]
  self.progress['stages']['B01']['items']['B01-01'].update(status='PASS',reviewer='independent',evidence=['evidence/review.json'])
  self.progress['stages']['B01']['items']['B01-02'].update(status='BLOCKED',rounds=2)
  self.save();self.assertEqual(stages.select(self.root)['item']['id'],'B02-01')
  self.progress['stages']['B01']['items']['B01-01']['status']='PARTIAL';self.save()
  with self.assertRaisesRegex(stages.StageBlocked,'入口工作包'):stages.select(self.root)
 def test_runtime_entry_evidence_change_blocks_dispatch(self):
  import hashlib
  self.proof();self.tasks['active_task']='B02';self.tasks['tasks'][1]['depends_on']=[]
  self.contract['stages'][1]['entry_evidence']=[{'path':'evidence/review.json','sha256':hashlib.sha256((self.root/'evidence/review.json').read_bytes()).hexdigest()}]
  self.save();self.assertEqual(stages.select(self.root)['item']['id'],'B02-01')
  (self.root/'evidence/review.json').write_text('changed')
  with self.assertRaisesRegex(stages.StageBlocked,'入口证据变化'):stages.select(self.root)
 def test_specific_item_selected_not_generic_stage(self):
  self.assertEqual(stages.select(self.root)['item']['id'],'B01-01')
 def test_partial_slice_cannot_advance_stage(self):
  a=stages.select(self.root);stages.apply(self.root,a,self.result('B01-01','PARTIAL'),'reviewer-1')
  self.assertEqual(json.loads((self.root/'planning/tasks.json').read_text())['active_task'],'B01')
 def test_pass_requires_evidence_and_deliverable(self):
  a=stages.select(self.root)
  with self.assertRaises(ValueError):stages.apply(self.root,a,self.result('B01-01'),'reviewer-1')
  (self.root/'evidence/review.json').write_text('proof')
  with self.assertRaisesRegex(ValueError,'交付'):stages.apply(self.root,a,self.result('B01-01'),'reviewer-1')
 def test_wrong_package_and_unsafe_evidence_rejected(self):
  a=stages.select(self.root);self.proof()
  with self.assertRaises(ValueError):stages.apply(self.root,a,self.result('B01-02'),'reviewer-1')
  r=self.result('B01-01');r['stage_item_evidence']=['../secret']
  with self.assertRaises(ValueError):stages.apply(self.root,a,r,'reviewer-1')
 def test_all_packages_only_nominate_candidate_not_advance_stage(self):
  self.proof();a=stages.select(self.root);stages.apply(self.root,a,self.result('B01-01'),'reviewer-1')
  a=stages.select(self.root);self.assertEqual(a['item']['id'],'B01-02');stages.apply(self.root,a,self.result('B01-02'),'reviewer-2')
  tasks=json.loads((self.root/'planning/tasks.json').read_text());self.assertEqual(tasks['active_task'],'B01');self.assertEqual(tasks['tasks'][0]['status'],'PARTIAL')
  self.assertTrue(json.loads((self.root/'planning/stage-progress.json').read_text())['stages']['B01']['candidate_ready'])
 def test_budget_exhaustion_triggers_review_not_pass(self):
  for _ in range(2):
   a=stages.select(self.root);stages.apply(self.root,a,self.result('B01-01','PARTIAL'),'reviewer')
  with self.assertRaises(stages.StageBlocked):stages.select(self.root)
  self.assertNotEqual(json.loads((self.root/'planning/tasks.json').read_text())['tasks'][0]['status'],'PASS')
 def test_blocked_package_can_yield_to_independent_package(self):
  self.items[1]['depends_on']=[];self.save()
  a=stages.select(self.root);result=self.result('B01-01','BLOCKED');stages.apply(self.root,a,result,'reviewer')
  self.assertEqual(stages.select(self.root)['item']['id'],'B01-02')

 def test_legacy_pass_marker_cannot_unlock_next_stage(self):
  self.tasks['active_task']='B02';self.tasks['tasks'][0]['status']='PASS';self.save()
  with self.assertRaises(stages.StageBlocked):stages.select(self.root)
 def test_partial_stage_cannot_claim_project_complete(self):
  a=stages.select(self.root);self.proof();result=self.result('B01-01');result['outcome']='complete'
  with self.assertRaisesRegex(ValueError,'全产品'):stages.apply(self.root,a,result,'reviewer')
 def test_changed_contract_version_requires_review(self):
  self.progress['contract_version']=99;self.save()
  with self.assertRaises(stages.StageBlocked):stages.select(self.root)

 def test_container_not_executable_and_inventory_coverage_required(self):
  parent=dict(self.items[1],requires_decomposition=True,planned_by='B01-01',coverage_source={'path':'planning/scope.json','key':'features','id_field':'id','closed_flag':'inventory_complete'})
  contract=dict(self.contract['stages'][0],work_items=[self.items[0],parent]);state=copy.deepcopy(self.progress['stages']['B01']);a={'item':self.items[0]}
  (self.root/'planning/scope.json').write_text(json.dumps({'inventory_complete':True,'features':[{'id':'F1'},{'id':'F2'}]}))
  child={'id':'B01-02-A','parent_id':'B01-02','title':'input','goal':'input chain','inputs':['original'],'outputs':['evidence/child.json'],'done_when':'case input parity','depends_on':[],'coverage_ids':['F1']}
  with self.assertRaisesRegex(ValueError,'完整覆盖'):stages.register_breakdown(self.root,contract,state,a,[child])
  child['coverage_ids'].append('F2');stages.register_breakdown(self.root,contract,state,a,[child]);self.assertEqual(contract['work_items'][-1]['id'],'B01-02-A')
if __name__=='__main__':unittest.main()
