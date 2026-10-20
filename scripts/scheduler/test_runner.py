import importlib.util, json, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('runner',Path(__file__).with_name('runner.py'))
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)

REAL_SELECT=r.stages.select

class RunnerTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
  root=Path(self.tmp.name); self.root=root
  self.patches=[patch.object(r,'ROOT',root),patch.object(r,'BASE',root/'evidence/scheduler'),patch.object(r.check_rea,'check',return_value={'status':'PASS'}),patch.object(r.stages,'select',return_value=None),patch.object(r.assurance,'next_assignment',return_value=None)]
  for p in self.patches: p.start(); self.addCleanup(p.stop)
  (root/'evidence').mkdir(); (root/'scripts').mkdir()
  (root/'planning').mkdir(); (root/'planning/tasks.json').write_text(json.dumps({'active_task':'B01','tasks':[{'id':'B01','goal':'核查版本和组件'}]}))
  (root/'scripts/verify-installer.py').write_text('raise SystemExit(0)')
  (root/'scripts/check-acceptance.py').write_text('raise SystemExit(1)')
 def call(self,action='tick'):
  with patch.object(sys,'argv',['runner',action]): r.main()
 def fake(self,outcome='continue',change=True):
  def run(role,folder):
   if role=='worker' and change: (self.root/'evidence/new.txt').write_text(folder.name)
   if role=='reviewer': (folder/'reviewer-final.txt').write_text(json.dumps(dict(outcome=outcome,new_evidence=True,reason='test',evidence=['evidence/new.txt'])))
  return run
 def test_sequence_links_and_titles(self):
  with patch.object(r,'run_agent',side_effect=self.fake()): self.call(); self.call()
  rows=json.loads((r.BASE/'cards.json').read_text())
  self.assertEqual([x['id'] for x in rows],['HWK-000001','HWK-000002'])
  self.assertEqual(rows[0]['next'],rows[1]['id'])
  self.assertEqual(rows[1]['previous'],rows[0]['id'])
  self.assertEqual(rows[1]['sessions']['worker']['title'],'HWK-000002-B01-执行｜核查版本和组件')

 def test_missing_stage_contract_stops_before_creating_card(self):
  with patch.object(r.stages,'select',side_effect=REAL_SELECT),patch.object(r,'run_agent') as agent:
   self.call();agent.assert_not_called()
  self.assertFalse((r.BASE/'cards.json').exists());self.assertTrue((r.BASE/'PAUSED').exists())
 def test_real_wbs_assignment_and_progress_integrate_with_runner(self):
  item={'id':'B01-01','title':'版本基线','goal':'lock identity','done_when':'source audit','inputs':['source'],'outputs':['evidence/delivery.json'],'depends_on':[],'max_rounds_before_review':2}
  (self.root/'planning/stage-contracts.json').write_text(json.dumps({'version':1,'stages':[{'id':'B01','outcome':'package baseline','not_in_scope':['runtime'],'block_when':['missing source'],'work_items':[item]}]}))
  (self.root/'planning/stage-progress.json').write_text(json.dumps({'contract_version':1,'stages':{'B01':{'items':{'B01-01':{'status':'NOT_RUN','rounds':0,'evidence':[],'reviewer':None}}}}}))
  def fake(role,folder):
   if role=='worker':(self.root/'evidence/delivery.json').write_text('actual delivery')
   if role=='reviewer':
    (self.root/'evidence/review.json').write_text('independent review')
    (folder/'reviewer-final.txt').write_text(json.dumps({'outcome':'continue','new_evidence':True,'reason':'bounded actual audit','evidence':['evidence/review.json'],'stage_item_id':'B01-01','stage_item_status':'PASS','stage_item_evidence':['evidence/review.json'],'breakdown':[]}))
  with patch.object(r.stages,'select',side_effect=REAL_SELECT),patch.object(r,'run_agent',side_effect=fake):self.call()
  card=json.loads((r.BASE/'cards.json').read_text())[0]
  self.assertEqual(card['stage_item_id'],'B01-01');self.assertIn('版本基线',card['goal'])
  progress=json.loads((self.root/'planning/stage-progress.json').read_text());self.assertEqual(progress['stages']['B01']['items']['B01-01']['status'],'PASS')

 def test_assurance_routes_only_to_readonly_assessor(self):
  a={'kind':'plan_audit','stage_id':'B01'}
  def fake(role,folder,**kwargs):
   self.assertEqual(role,'assessor');self.assertEqual(kwargs['sandbox'],'read-only')
   (folder/'assessor-final.txt').write_text('{}')
  result={'outcome':'blocked','reason':'missing goal coverage','evidence':[]}
  with patch.object(r.stages,'select',return_value=a),patch.object(r,'run_agent',side_effect=fake) as agent,patch.object(r.assurance,'apply',return_value=result):self.call()
  self.assertEqual(agent.call_count,1);self.assertIn('missing goal coverage',(r.BASE/'PAUSED').read_text())
  card=json.loads((r.BASE/'cards.json').read_text())[0];self.assertEqual(set(card['sessions']),{'assessor'});self.assertEqual(card['track'],'assurance')
 def test_assurance_preflight_failure_prevents_assessor(self):
  with patch.object(r.stages,'select',return_value={'kind':'plan_audit','stage_id':'B01'}),patch.object(r.check_rea,'check',side_effect=RuntimeError('REA drift')),patch.object(r,'run_agent') as agent:
   self.call();agent.assert_not_called()
  self.assertIn('REA drift',(r.BASE/'PAUSED').read_text())

 def test_success_orders_worker_then_review(self):
  with patch.object(r,'run_agent',side_effect=self.fake()) as agent: self.call()
  self.assertEqual([c.args[0] for c in agent.call_args_list],['worker','reviewer'])
  self.assertEqual(json.loads((r.BASE/'state.json').read_text())['no_progress'],0)
 def test_pause_prevents_launch(self):
  self.call('pause')
  with patch.object(r,'run_agent') as agent: self.call(); agent.assert_not_called()
 def test_two_empty_cycles_pause(self):
  with patch.object(r,'run_agent',side_effect=self.fake(change=False)): self.call(); self.call()
  self.assertTrue((r.BASE/'PAUSED').exists())
 def test_convergence_stagnation_requests_agent_instead_of_pause(self):
  (self.root/'planning/convergence-policy.json').write_text('{"enabled":true}')
  with patch.object(r,'run_agent',side_effect=self.fake(change=False)):
   self.call();self.call()
  self.assertFalse((r.BASE/'PAUSED').exists())
  with patch.object(r.convergence,'assignment',return_value={'kind':'continuation_plan','stage_id':'B01'}),patch.object(r.convergence,'plan') as planner:
   self.call();planner.assert_called_once()
 def test_network_profiles_keep_filesystem_scope_and_parallel_boundary(self):
  for role,mode,parent in [('worker','workspace-write',':workspace'),('assessor','read-only',':read-only')]:
   options=r.agent_permissions(role,mode,r.ROOT)
   self.assertTrue(any('network.enabled=true' in x for x in options));self.assertTrue(any(parent in x for x in options));self.assertNotIn('danger-full-access',str(options))
  self.assertEqual(r.agent_permissions('worker','workspace-write',self.root/'isolated'),['-s','workspace-write'])
 def test_old_rea_prevents_agent_launch(self):
  with patch.object(r.check_rea,'check',side_effect=RuntimeError('REA version drift')),patch.object(r,'run_agent') as agent:
   self.call();agent.assert_not_called()
  self.assertIn('REA version drift',(r.BASE/'PAUSED').read_text())

 def test_failure_pauses(self):
  with patch.object(r,'run_agent',side_effect=RuntimeError('auth failure')): self.call()
  self.assertIn('auth failure',(r.BASE/'PAUSED').read_text())
 def test_false_completion_rejected(self):
  with patch.object(r,'run_agent',side_effect=self.fake('complete')): self.call()
  self.assertEqual(json.loads((r.BASE/'state.json').read_text())['status'],'error')
 def test_unclean_run_stops(self):
  r.BASE.mkdir(); (r.BASE/'active.json').write_text('{"pid":1}')
  with patch.object(r,'run_agent') as agent: self.call(); agent.assert_not_called()
  self.assertTrue((r.BASE/'PAUSED').exists())

if __name__=='__main__': unittest.main()
