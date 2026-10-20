import importlib.util, json, tempfile, threading, unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
spec=importlib.util.spec_from_file_location('dashboard',Path(__file__).with_name('dashboard.py'))
d=importlib.util.module_from_spec(spec); spec.loader.exec_module(d)

class DashboardTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.base=self.root/'evidence/scheduler';self.base.mkdir(parents=True)
  self.folder=self.base/'run';self.folder.mkdir()
  (self.root/'planning').mkdir()
  self.put(self.root/'planning/tasks.json',{'active_task':'B01','tasks':[{'id':'B01','goal':'baseline','status':'PARTIAL','depends_on':[],'blockers':[],'evidence':[]},{'id':'B02','goal':'runtime','status':'NOT_RUN','depends_on':['B01'],'blockers':[],'evidence':[]}]})
  self.card={'id':'HWK-000001','sequence':1,'task_id':'B01','goal':'baseline','run':str(self.folder),'sessions':{'worker':{'title':'worker'},'reviewer':{'title':'reviewer'}}}
  self.put(self.folder/'task-card.json',self.card)
 def put(self,p,x):p.write_text(json.dumps(x))
 def active(self,role):
  self.put(self.base/'active.json',{'run':str(self.folder),'card_id':self.card['id'],'role':role,'pid':__import__('os').getpid()})
 def row(self): return next(c for c in d.snapshot(self.root)['cards'] if c['id']==self.card['id'])
 def test_lifecycle_from_files(self):
  self.assertEqual(self.row()['lane'],'queued')
  self.active('worker');self.assertEqual(self.row()['lane'],'working')
  self.active('reviewer');self.assertEqual(self.row()['lane'],'review')
  (self.base/'active.json').unlink()
  self.put(self.folder/'reviewer-final.txt',{'outcome':'continue','reason':'slice verified','evidence':[]})
  self.assertEqual(self.row()['lane'],'finished')
  self.assertEqual(d.snapshot(self.root)['tasks'][0]['status'],'PARTIAL')
 def test_parallel_and_main_cards_visible_together(self):
  self.active('reviewer')
  folder=self.base/'side';folder.mkdir();side=dict(self.card,id='HWK-000002',sequence=2,run=str(folder),track='parallel')
  self.put(folder/'task-card.json',side)
  self.put(self.base/'parallel-active.json',{'card_id':'HWK-000002','run':str(folder),'role':'worker','pid':__import__('os').getpid()})
  snap=d.snapshot(self.root);lanes={c['id']:c['lane'] for c in snap['cards']}
  self.assertEqual(lanes['HWK-000001'],'review');self.assertEqual(lanes['HWK-000002'],'working')
  self.assertEqual(len(snap['scheduler']['actives']),2)

 def test_stage_goals_and_work_packages_are_projected(self):
  self.put(self.root/'planning/stage-contracts.json',{'goal':{'id':'HWK-G001','outcome':'full replacement'},'stages':[{'id':'B01','outcome':'verified baseline','work_items':[{'id':'B01-01','title':'identity'}]}]})
  self.put(self.root/'planning/stage-progress.json',{'stages':{'B01':{'items':{'B01-01':{'status':'PARTIAL','rounds':1,'evidence':[]}}}}})
  self.card['stage_item_id']='B01-01';self.put(self.folder/'task-card.json',self.card);self.active('worker')
  snapshot=d.snapshot(self.root);self.assertEqual(snapshot['overall_goal']['id'],'HWK-G001')
  self.assertEqual(snapshot['stage_contracts'][0]['work_items'][0]['active_role'],'worker')
  self.assertEqual(snapshot['stage_contracts'][0]['work_items'][0]['cards'],['HWK-000001'])
  self.assertEqual(snapshot['stage_contracts'][0]['work_items'][0]['progress']['status'],'PARTIAL')

 def test_assessor_is_separate_review_role(self):
  self.card['track']='assurance';self.card['sessions']={'assessor':{'title':'goal audit'}};self.put(self.folder/'task-card.json',self.card)
  self.active('assessor');self.put(self.folder/'assessor.jsonl',{'type':'item.completed','item':{'type':'agent_message','text':'goal evidence'}})
  self.put(self.root/'planning/goal-assurance.json',{'plan':{'approved':False},'stages':{}})
  self.assertEqual(self.row()['lane'],'review');self.assertEqual(self.row()['activity']['assessor']['events'][0]['text'],'goal evidence')
  self.assertFalse(d.snapshot(self.root)['goal_assurance']['plan']['approved'])

 def test_old_card_recovers_completion_without_status(self):
  self.put(self.base/'cards.json',[self.card]); self.put(self.folder/'reviewer-final.txt',{'outcome':'continue','reason':'legacy result','evidence':['evidence/one.json']})
  self.assertEqual(self.row()['lane'],'finished')
 def test_dead_active_is_blocked_not_running(self):
  self.put(self.base/'active.json',{'card_id':self.card['id'],'pid':99999999,'role':'worker'})
  self.assertEqual(self.row()['lane'],'blocked')
 def test_blocked_result_and_pause_visible(self):
  self.put(self.folder/'reviewer-final.txt',{'outcome':'blocked','reason':'Windows unavailable','evidence':[]});(self.base/'PAUSED').write_text('Windows unavailable')
  result=d.snapshot(self.root);self.assertTrue(result['scheduler']['paused']);self.assertEqual(self.row()['lane'],'blocked')
 def test_resolved_failure_moves_to_history_without_changing_original_verdict(self):
  self.card.update(status='error',finished_at='old',review_result={'outcome':'blocked','reason':'old SSH failure','evidence':[]});self.put(self.folder/'task-card.json',self.card)
  self.put(self.base/'state.json',{'status':'ready','run':str(self.folder)})
  self.put(self.base/'issue-closures.json',{'cards':{self.card['id']:{'status':'resolved','reason':'SSH independently reverified','evidence':['evidence/proof'],'scope':'execution channel only'}}})
  row=self.row();self.assertEqual(row['lane'],'finished');self.assertEqual(row['result']['outcome'],'blocked');self.assertEqual(row['closure']['status'],'resolved')
 def test_historical_failed_attempt_does_not_remain_an_active_incident(self):
  self.card.update(status='error',finished_at='old');self.put(self.folder/'task-card.json',self.card)
  self.put(self.base/'state.json',{'status':'running','run':str(self.base/'new-run')})
  self.assertEqual(self.row()['lane'],'finished')
 def test_open_current_incident_stays_blocked(self):
  self.card.update(track='blocker',status='action_required',finished_at='old');self.put(self.folder/'task-card.json',self.card)
  self.put(self.folder/'incident.json',{'status':'action_required','reason':'needs real external input'})
  self.put(self.base/'state.json',{'status':'running','run':str(self.base/'new-run')})
  self.assertEqual(self.row()['lane'],'blocked')
 def test_log_tail_skips_partial_json_and_retains_messages(self):
  (self.folder/'worker.jsonl').write_text('{"type":"item.completed","item":{"type":"agent_message","text":"new evidence"}}\n{"type":')
  self.assertEqual(self.row()['activity']['worker']['events'][0]['text'],'new evidence')
 def server(self):
  s=d.serve(self.root,0);threading.Thread(target=s.serve_forever,daemon=True).start();self.addCleanup(s.server_close);self.addCleanup(s.shutdown);return 'http://127.0.0.1:'+str(s.server_port)
 def test_live_api_sees_new_cards_and_completion(self):
  url=self.server()
  def get():return json.load(urlopen(url+'/api/snapshot'))
  self.assertEqual(get()['cards'][0]['lane'],'queued')
  self.active('worker');self.assertEqual(get()['cards'][0]['lane'],'working')
  self.put(self.folder/'reviewer-final.txt',{'outcome':'continue','reason':'done','evidence':[]});(self.base/'active.json').unlink()
  self.assertEqual(get()['cards'][0]['lane'],'finished')
  self.card['id']='HWK-000002';self.card['sequence']=2;self.put(self.folder/'task-card.json',self.card)
  self.assertEqual(get()['cards'][0]['id'],'HWK-000002')
 def test_evidence_only_and_host_guard(self):
  url=self.server();(self.root/'evidence/ok.txt').write_text('proof');(self.root/'secret.txt').write_text('hidden')
  self.assertEqual(urlopen(url+'/api/file?path=evidence/ok.txt').read(),b'proof')
  for path in ('../secret.txt','.codex-runtime/auth.json','evidence/../../secret.txt'):
   with self.assertRaises(HTTPError) as err:urlopen(url+'/api/file?path='+path)
   self.assertEqual(err.exception.code,403)
  (self.root/'evidence/link.txt').symlink_to(self.root/'secret.txt')
  with self.assertRaises(HTTPError):urlopen(url+'/api/file?path=evidence/link.txt')
  with self.assertRaises(HTTPError) as err:urlopen(Request(url+'/api/snapshot',headers={'Host':'external.example'}))
  self.assertEqual(err.exception.code,403)

if __name__=='__main__':unittest.main()
