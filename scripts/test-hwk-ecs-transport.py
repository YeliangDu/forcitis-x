"""Transport regression: long Unicode payload, rejection logs, and timeout preservation."""
import json,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from hwk_ecs import run_ps_stdin
class Transport(unittest.TestCase):
 def test_unicode_long_payload(self):
  script="'示例'\n"*5000
  with tempfile.TemporaryDirectory() as d,patch('hwk_ecs.subprocess.run',return_value=subprocess.CompletedProcess([],0,b'OK',b'')) as run:
   self.assertEqual(run_ps_stdin(script,d),'OK')
   args,kwargs=run.call_args
   self.assertEqual(kwargs['input'],script.encode('utf-8'))
   self.assertLess(len(args[0][-1]),8191)
   self.assertIn(str(len(script.encode('utf-8'))),json.loads((Path(d)/'exit.json').read_text())['bootstrap'])
   self.assertEqual((Path(d)/'command.ps1').read_text(),script)
 def test_remote_failure(self):
  with tempfile.TemporaryDirectory() as d,patch('hwk_ecs.subprocess.run',return_value=subprocess.CompletedProcess([],1,b'partial',b'error')):
   with self.assertRaises(RuntimeError):run_ps_stdin('throw 1',d)
   self.assertEqual((Path(d)/'stderr').read_bytes(),b'error')
   self.assertEqual(json.loads((Path(d)/'exit.json').read_text())['exit_code'],1)
 def test_timeout(self):
  with tempfile.TemporaryDirectory() as d,patch('hwk_ecs.subprocess.run',side_effect=subprocess.TimeoutExpired('ssh',1,output=b'partial',stderr=b'pending')):
   with self.assertRaises(subprocess.TimeoutExpired):run_ps_stdin('probe',d,1)
   self.assertEqual((Path(d)/'stdout').read_bytes(),b'partial')
   self.assertEqual(json.loads((Path(d)/'exit.json').read_text())['status'],'TIMEOUT')
if __name__=='__main__':unittest.main()
