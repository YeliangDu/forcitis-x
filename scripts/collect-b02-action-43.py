import sys,base64
from pathlib import Path
sys.path.insert(0,'scripts');from hwk_ecs import run_ps_stdin
b=Path('evidence/stages/B02/B02-02/attempt-43');label=sys.argv[1];x,y=map(int,sys.argv[2:4]);s=Path('scripts/ecs-b02-menu-43.ps1').read_text().replace('SetCursorPos(380,35)',f'SetCursorPos({x},{y})')
s=s.replace('[void][Hwk42Window]::SetCursorPos(426,56)', '[void][Hwk42Window]::SetCursorPos(380,35)\n[Hwk42Window]::mouse_event(2,0,0,0,[UIntPtr]::Zero)\n[Hwk42Window]::mouse_event(4,0,0,0,[UIntPtr]::Zero)\nStart-Sleep -Milliseconds 400\n[void][Hwk42Window]::SetCursorPos(426,56)')
# Capture nodes after action as well
s=s.replace("$s=[Windows.Forms.SystemInformation]", "$windows=@();$nodes=@();$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$c);foreach($w in $wins){$windows+=[ordered]@{Name=$w.Current.Name;Handle=$w.Current.NativeWindowHandle;Class=$w.Current.ClassName};$els=$w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition);foreach($el in $els){$e=$el.Current;$nodes+=[ordered]@{Name=$e.Name;Id=$e.AutomationId;Type=$e.ControlType.ProgrammaticName;Handle=$e.NativeWindowHandle}}}\n$s=[Windows.Forms.SystemInformation]")
(b/(label+'.ps1')).write_text(s)
r=r'C:\hwk-modern\HWK-000043-B02-02'
cmd="$b='"+r+"';[IO.File]::WriteAllBytes(\"$b\\action.ps1\",[Convert]::FromBase64String('"+base64.b64encode(s.encode('utf-8-sig')).decode()+"'));$a=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -WindowStyle Hidden -File "+r+"\\action.ps1';Set-ScheduledTask -TaskName 'HWKModern-000043-Probe' -Action $a|Select TaskName,State;Start-ScheduledTask -TaskName 'HWKModern-000043-Probe'"
print(run_ps_stdin(cmd,b/(label+'-schedule'),25))
