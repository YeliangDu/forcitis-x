import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const root=fileURLToPath(new URL('../../',import.meta.url));
for (const suite of ['test_dashboard.py','test_runner.py','test_parallel.py','test_stages.py','test_assurance.py']) {
  const result=spawnSync('/usr/bin/python3',['scripts/scheduler/'+suite],{cwd:root,stdio:'inherit'});
  if (result.status!==0) process.exit(result.status??1);
}
