import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import blockers

class BlockersTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  preflight=patch.object(blockers.check_rea,'check');preflight.start();self.addCleanup(preflight.stop)
  self.root=Path(self.tmp.name);self.base=self.root/'evidence/scheduler';self.base.mkdir(parents=True)
  (self.base/'PAUSED').write_text('invalid report')
  (self.base/'state.json').write_text(json.dumps({'status':'error','run':'failed-run'}))
  (self.root/'scripts/scheduler').mkdir(parents=True)
  (self.root/'scripts/scheduler/blocker.txt').write_text('readonly diagnosis')
 def test_pending_deduplicates_and_retains_pause(self):
  a=blockers.capture(self.root);b=blockers.capture(self.root)
  self.assertEqual(a,b);self.assertTrue((self.base/'PAUSED').exists())
 def test_user_pause_and_completion_do_not_launch(self):
  (self.base/'PAUSED').write_text('Paused by user at now')
  self.assertIsNone(blockers.capture(self.root))
  (self.base/'PAUSED').write_text('finished')
  (self.base/'state.json').write_text('{"status":"complete"}')
  self.assertIsNone(blockers.capture(self.root))
 def test_readonly_once_failure_is_durable(self):
  calls=[]
  def agent(role,folder,**kw):
   calls.append(kw);raise RuntimeError('auth unavailable')
  with patch.object(blockers.cards,'create'),patch.object(blockers.cards,'finish'):
   blockers.diagnose(self.root,agent);blockers.diagnose(self.root,agent)
  self.assertEqual(len(calls),1);self.assertEqual(calls[0]['sandbox'],'read-only')
  incident=json.loads((blockers.capture(self.root)/'incident.json').read_text())
  self.assertEqual(incident['status'],'diagnosis_failed')
 def test_live_session_blocks_diagnosis(self):
  (self.base/'active.json').write_text('{}')
  with patch.object(blockers,'capture') as capture:blockers.diagnose(self.root,None);capture.assert_not_called()
 def test_success_never_resumes_or_modifies_stage(self):
  def agent(role,folder,**kw):
   (folder/'diagnostician-final.txt').write_text(json.dumps({'route':'REPLAN','reason':'exhausted','next_actions':['review bounded scope'],'release_conditions':['independent approval'],'questions':[],'evidence':['evidence/scheduler/PAUSED']}))
  with patch.object(blockers.cards,'create'),patch.object(blockers.cards,'finish'):blockers.diagnose(self.root,agent)
  self.assertEqual(json.loads((blockers.capture(self.root)/'incident.json').read_text())['status'],'action_required')
  self.assertTrue((self.base/'PAUSED').exists())
 def test_absolute_inside_root_normalized_outside_and_symlink_rejected(self):
  report={'route':'LOCAL_FIX','reason':'x','next_actions':['x'],'release_conditions':['x'],'evidence':[str(self.base/'PAUSED')]}
  self.assertEqual(blockers.validate_report(self.root,report)['evidence'],['evidence/scheduler/PAUSED'])
  for raw in ['/etc/passwd',str(self.root/'../outside')]:
   with self.assertRaises(ValueError):blockers.validate_report(self.root,dict(report,evidence=[raw]))
  (self.base/'link').symlink_to(self.base/'PAUSED')
  with self.assertRaises(ValueError):blockers.validate_report(self.root,dict(report,evidence=['evidence/scheduler/link']))
 def test_close_event_preserves_failure_and_updates_source_and_diagnostic_cards(self):
  folder=blockers.capture(self.root);before=json.loads((folder/'incident.json').read_text())
  (self.base/'cards.json').write_text(json.dumps([{'id':'HWK-000001','run':'failed-run'},{'id':'HWK-000002','run':str(folder)}]))
  blockers.close_event(self.root,folder/'incident.json',status='resolved',reason='network now independently verified',evidence=['evidence/scheduler/PAUSED'],by='primary')
  after=json.loads((folder/'incident.json').read_text());self.assertEqual(after['source_state'],before['source_state']);self.assertEqual(after['reason'],before['reason']);self.assertEqual(after['status'],'resolved')
  ledger=json.loads((self.base/'issue-closures.json').read_text());self.assertEqual(set(ledger['cards']),{'HWK-000001','HWK-000002'});self.assertIn('package acceptance unchanged',after['closure']['scope'])
 def test_close_event_requires_existing_evidence(self):
  folder=blockers.capture(self.root);before=(folder/'incident.json').read_bytes()
  with self.assertRaises(ValueError):blockers.close_event(self.root,folder/'incident.json',status='resolved',reason='claim only',evidence=['evidence/missing'],by='primary')
  self.assertEqual(before,(folder/'incident.json').read_bytes())
 def test_traversal_rejected(self):
  def agent(role,folder,**kw):
   (folder/'diagnostician-final.txt').write_text(json.dumps({'route':'LOCAL_FIX','reason':'x','next_actions':['x'],'release_conditions':['x'],'evidence':['../outside']}))
  with patch.object(blockers.cards,'create'),patch.object(blockers.cards,'finish'):blockers.diagnose(self.root,agent)
  self.assertEqual(json.loads((blockers.capture(self.root)/'incident.json').read_text())['status'],'diagnosis_failed')

if __name__=='__main__':unittest.main()
