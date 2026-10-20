"""Review the authorized reorder without claiming any HWK business acceptance."""
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class WorkflowResetTest(unittest.TestCase):
 def test_preserves_goal_and_static_obligations(self):
  old=json.loads((ROOT/'evidence/workflow-reset/20261018-runtime-first/stage-contracts-before.json').read_text())
  new=json.loads((ROOT/'planning/stage-contracts.json').read_text())
  self.assertEqual(new['goal'],old['goal'])
  a=next(s for s in old['stages'] if s['id']=='B01');b=next(s for s in new['stages'] if s['id']=='B01')
  self.assertEqual({i['id']:i['done_when'] for i in a['work_items']},{i['id']:i['done_when'] for i in b['work_items']})
 def test_runtime_has_identity_gate_and_final_retains_static_dependency(self):
  contracts=json.loads((ROOT/'planning/stage-contracts.json').read_text());tasks=json.loads((ROOT/'planning/tasks.json').read_text())
  b2=next(s for s in contracts['stages'] if s['id']=='B02')
  self.assertIn({'stage_id':'B01','item_id':'B01-01'},b2['entry_work_items']);self.assertTrue(b2['entry_evidence'])
  task={t['id']:t for t in tasks['tasks']}
  self.assertEqual(task['B02']['depends_on'],[]);self.assertEqual(task['B03']['depends_on'],['B02'])
  self.assertIn('B01',task['R01']['depends_on']);self.assertIn('E01',task['R01']['depends_on'])
  self.assertLess(task['B03']['schedule_priority'],task['B01']['schedule_priority'])
 def test_dependency_graph_acyclic_and_all_original_stages_present(self):
  tasks=json.loads((ROOT/'planning/tasks.json').read_text());graph={t['id']:t['depends_on'] for t in tasks['tasks']}
  self.assertEqual(set(graph),set(['B01','B02','B03','B04','P01','P02','P03','P04','E01','R01']))
  visiting=set();done=set()
  def visit(s):
   self.assertNotIn(s,visiting)
   if s in done:return
   visiting.add(s)
   for dep in graph[s]:self.assertIn(dep,graph);visit(dep)
   visiting.remove(s);done.add(s)
  for s in graph:visit(s)
if __name__=='__main__':unittest.main()
