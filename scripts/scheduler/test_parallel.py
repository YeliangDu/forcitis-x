import importlib.util,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
import parallel as p
import control

class IsolationTest(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  self.repo=self.root/'repo';self.repo.mkdir();self.work=self.root/'isolated';self.work.mkdir()
  (self.repo/'input.json').write_text('{"raw":1}')
  p.snapshot_inputs(self.repo,self.work,{'inputs':['input.json']})
  (self.work/'AGENTS.md').write_text('frozen');self.initial=p.inventory(self.work)
  (self.work/'evidence').mkdir();(self.work/'evidence/report.md').write_text('observed only')
  self.review={'verdict':'PASS','reason':'bounded','evidence':['evidence/report.md'],'checks':[{'command':'python3 test.py','exit_code':0}]}
 def test_valid_frozen_input_and_new_directory_import(self):
  submitted=p.validate(self.work,self.initial);dest=p.promote(self.repo,self.work,'HWK-000001',submitted,self.review)
  self.assertTrue((self.repo/dest/'evidence/report.md').exists());self.assertEqual((self.repo/'input.json').read_text(),'{"raw":1}')
 def test_frozen_input_mutation_rejected(self):
  (self.work/'inputs/input.json').write_text('changed')
  with self.assertRaisesRegex(ValueError,'Frozen'):p.validate(self.work,self.initial)
 def test_escape_input_rejected(self):
  with self.assertRaises(ValueError):p.snapshot_inputs(self.repo,self.work,{'inputs':['../secret']})
 def test_symlink_output_rejected(self):
  (self.work/'evidence/link.txt').symlink_to(self.repo/'input.json')
  with self.assertRaisesRegex(ValueError,'Symlink'):p.validate(self.work,self.initial)
 def test_unapproved_output_path_rejected(self):
  (self.work/'HANDOFF.md').write_text('changed')
  with self.assertRaisesRegex(ValueError,'outside'):p.validate(self.work,self.initial)
 def test_review_must_pass_and_have_actual_successful_checks(self):
  submitted=p.validate(self.work,self.initial)
  for review in (dict(self.review,verdict='PARTIAL'),dict(self.review,checks=[]),dict(self.review,checks=[{'exit_code':1}])):
   with self.assertRaises(ValueError):p.promote(self.repo,self.work,'HWK-000001',submitted,review)
 def test_post_submission_mutation_rejected(self):
  submitted=p.validate(self.work,self.initial);(self.work/'evidence/report.md').write_text('changed after review')
  with self.assertRaisesRegex(ValueError,'changed'):p.promote(self.repo,self.work,'HWK-000001',submitted,self.review)
 def test_review_evidence_escape_rejected(self):
  submitted=p.validate(self.work,self.initial)
  with self.assertRaises(ValueError):p.promote(self.repo,self.work,'HWK-000001',submitted,dict(self.review,evidence=['../secret']))
 def test_existing_import_never_overwritten(self):
  submitted=p.validate(self.work,self.initial);p.promote(self.repo,self.work,'HWK-000001',submitted,self.review)
  with self.assertRaisesRegex(ValueError,'overwrite'):p.promote(self.repo,self.work,'HWK-000001',submitted,self.review)
 def test_cancel_only_matching_owned_process_group(self):
  base=self.root/'scheduler';base.mkdir();script=self.root/'codex_cancel_probe.py';script.write_text('import time;time.sleep(120)')
  process=subprocess.Popen([sys.executable,str(script),str(base)],start_new_session=True)
  self.addCleanup(lambda:process.kill() if process.poll() is None else None)
  (base/'parallel-active.json').write_text(json.dumps({'pid':process.pid,'card_id':'HWK-000001','run':str(base)}))
  with patch.object(p,'BASE',base):p.cancel()
  self.assertNotEqual(process.wait(timeout=3),0)
  self.assertEqual((base/'PARALLEL_CANCEL').read_text(),'HWK-000001')
 def test_cancel_refuses_unrelated_pid(self):
  base=self.root/'scheduler';base.mkdir();(base/'parallel-active.json').write_text(json.dumps({'pid':1,'card_id':'HWK-000001','run':'unrelated'}))
  with patch.object(p,'BASE',base),patch.object(p.subprocess,'run',return_value=type('Result',(),{'stdout':'unrelated process'})()),patch.object(p.os,'killpg') as kill:
   with self.assertRaisesRegex(RuntimeError,'identity'):p.cancel()
   kill.assert_not_called()

 def test_enqueue_is_bounded_and_rejects_external_inputs(self):
  approval=patch.object(p.stages.assurance,'verified_plan',return_value=True);approval.start();self.addCleanup(approval.stop)
  root=self.repo;(root/'planning').mkdir();(root/'evidence/scheduler').mkdir(parents=True)
  (root/'planning/tasks.json').write_text(json.dumps({'tasks':[{'id':'B01','depends_on':[]}]}))
  path=root/'planning/parallel-cards.json';path.write_text(json.dumps({'enabled':True,'jobs':[]}))
  (root/'HANDOFF.md').write_text('snapshot')
  tasks_path=root/'planning/tasks.json';tasks_data=json.loads(tasks_path.read_text());tasks_data['active_task']='B01';tasks_path.write_text(json.dumps(tasks_data))
  (root/'planning/stage-contracts.json').write_text(json.dumps({'version':1,'stages':[{'id':'B01','work_items':[{'id':'B01-01','depends_on':[]}]}]}))
  (root/'planning/stage-progress.json').write_text(json.dumps({'contract_version':1,'stages':{'B01':{'items':{'B01-01':{'status':'NOT_RUN'}}}}}))
  job={'id':'B01-SLICE','parent_task':'B01','stage_item_id':'B01-01','goal':'bounded','scope':'declaration check','inputs':['HANDOFF.md'],'parallel_reason':'independent frozen source'}
  p.enqueue(root,job)
  with self.assertRaisesRegex(ValueError,'Duplicate'):p.enqueue(root,job)
  with self.assertRaisesRegex(ValueError,'outside'):p.enqueue(root,dict(job,id='B01-OTHER',inputs=['input.json']))
  with self.assertRaisesRegex((ValueError,p.stages.StageBlocked),'阶段|prerequisites'):p.enqueue(root,dict(job,id='B02-SLICE',parent_task='B02'))
  p.enqueue(root,dict(job,id='B01-SECOND',scope='different bounded check'))
  with self.assertRaisesRegex(ValueError,'full'):p.enqueue(root,dict(job,id='B01-THIRD',scope='third check'))

 def test_final_checks_match_actual_successful_commands(self):
  log=self.root/'reviewer.jsonl'
  events=[{'type':'item.completed','item':{'type':'command_execution','command':"/bin/zsh -lc 'setup attempt'",'exit_code':1}},{'type':'item.completed','item':{'type':'command_execution','command':"/bin/zsh -lc 'python3 test.py'",'exit_code':0}}]
  log.write_text('\n'.join(json.dumps(x) for x in events))
  self.assertTrue(p.verify_review_checks(self.review,log))
  with self.assertRaisesRegex(ValueError,'not backed'):p.verify_review_checks(dict(self.review,checks=[{'command':'setup attempt','exit_code':0}]),log)
  with self.assertRaisesRegex(ValueError,'not backed'):p.verify_review_checks(dict(self.review,checks=[{'command':'unrun command','exit_code':0}]),log)

 def test_recovery_retry_is_bounded_and_preserves_original(self):
  config={'jobs':[{'id':'B01-X','goal':'same scope','inputs':['HANDOFF.md']}]}
  new=control.retry_job(config,'B01-X')
  self.assertFalse(config['jobs'][0]['enabled']);self.assertTrue(new['enabled']);self.assertEqual(new['retry_of'],'B01-X')
  with self.assertRaisesRegex(ValueError,'already used'):control.retry_job(config,new['id'])
  self.assertEqual(len(config['jobs']),2)

 def test_processes_allocate_unique_linked_card_numbers(self):
  root=self.repo;(root/'planning').mkdir();(root/'evidence/scheduler').mkdir(parents=True)
  (root/'planning/tasks.json').write_text(json.dumps({'active_task':'B01','tasks':[{'id':'B01','goal':'test'}]}))
  module=str(Path(__file__).parent.resolve()); processes=[]
  for i in range(5):
   folder=root/'evidence/scheduler'/str(i);folder.mkdir()
   code=f'import sys;sys.path.insert(0,{module!r});from pathlib import Path;import cards;cards.create(Path({str(root)!r}),Path({str(folder)!r}))'
   processes.append(subprocess.Popen([sys.executable,'-c',code]))
  for process in processes:self.assertEqual(process.wait(timeout=15),0)
  cards=json.loads((root/'evidence/scheduler/cards.json').read_text())
  self.assertEqual([x['sequence'] for x in cards],[1,2,3,4,5]);self.assertEqual(cards[2]['previous'],cards[1]['id']);self.assertEqual(cards[2]['next'],cards[3]['id'])

if __name__=='__main__':unittest.main()
