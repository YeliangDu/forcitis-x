"""Build a guarded UI action from current capture template; coordinates require visual review."""
import sys
from pathlib import Path
name,x,y,button=sys.argv[1:];x=int(x);y=int(y);assert button in ['left','right','double']
b=Path('evidence/stages/B02/B02-02/attempt-46');s=(b/'probe.ps1').read_text()
a=f'[void][Hwk42Window]::SetCursorPos({x},{y})\n'
for _ in range(2 if button=='double' else 1):
 a+=f'[Hwk42Window]::mouse_event({8 if button=="right" else 2},0,0,0,[UIntPtr]::Zero)\n[Hwk42Window]::mouse_event({16 if button=="right" else 4},0,0,0,[UIntPtr]::Zero)\nStart-Sleep -Milliseconds 80\n'
a+='Start-Sleep -Seconds 2\n$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$c)\n'
start=s.index('$windows=@();$nodes=@()');end=s.index('Add-Type @\'');a+=s[start:end]
s=s.replace('$s=[Windows.Forms.SystemInformation]',a+'\n$s=[Windows.Forms.SystemInformation]');(b/(name+'.ps1')).write_text(s)
