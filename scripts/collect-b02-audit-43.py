import sys
from pathlib import Path
sys.path.insert(0,'scripts');from hwk_ecs import run_ps_stdin as run_ps
b=Path('evidence/stages/B02/B02-02/attempt-43')
s=Path('evidence/stages/B02/B02-02/attempt-42/source-audit/command.ps1').read_text()
s=s.split(';Errors=@')[0]+'}|ConvertTo-Json -Depth 7'
print(run_ps(s,b/'source-audit-retry',45)[:150])
