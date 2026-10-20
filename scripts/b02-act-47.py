"""B02-02 attempt-47 UI actions on the single already-running isolated XWall client.

Usage: python3 scripts/b02-act-47.py <action>

Every action uploads one probe script into C:\\hwk-modern\\HWK-000048-B02-02, starts it
in the interactive Administrator session through a scheduled task of this card, then
pulls back <action>.json (+ <action>.png). The script never starts, closes or
reconfigures the client and never writes outside the card directory.
"""
import base64
import gzip
import json
import os
import sys
from pathlib import Path

from hwk_ecs import run_ps, run_ps_stdin

CARD = 'HWK-000048-B02-02'
REMOTE = r'C:\hwk-modern\HWK-000048-B02-02'
BASE = Path('evidence/stages/B02/B02-02/attempt-47')
TASK = 'HWKModern-000048-Probe'
# The interactive session owner on the ECS may change; the probe task must run in that
# user's session, otherwise the task starts and immediately does nothing.
RUNAS = os.environ.get('HWK_RUNAS', 'Administrator')

PRELUDE = r'''$ErrorActionPreference='Stop'
$card='C:\hwk-modern\HWK-000048-B02-02'
$client='C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;using System.Runtime.InteropServices;public class Hwk47Win {
[DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr h);
[DllImport("user32.dll")]public static extern bool SetCursorPos(int x,int y);
[DllImport("user32.dll")]public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);
[DllImport("user32.dll")]public static extern void keybd_event(byte vk,byte scan,uint flags,UIntPtr extra);
[DllImport("user32.dll")]public static extern IntPtr SendMessage(IntPtr h,uint m,IntPtr w,IntPtr l);
[DllImport("user32.dll",EntryPoint="SendMessageW",CharSet=CharSet.Unicode)]public static extern IntPtr SendMessageText(IntPtr h,uint m,IntPtr w,string l);
[DllImport("user32.dll")]public static extern bool PostMessage(IntPtr h,uint m,IntPtr w,IntPtr l);
[DllImport("kernel32.dll")]public static extern IntPtr GetConsoleWindow();
[DllImport("user32.dll")]public static extern bool ShowWindow(IntPtr h,int n);
}
'@
[void][Hwk47Win]::ShowWindow([Hwk47Win]::GetConsoleWindow(),0)
$script:p=@(Get-Process XWall -ErrorAction SilentlyContinue)
function Get-Target {
 for($i=0;$i -lt 12;$i++){
  $script:p=@(Get-Process XWall -ErrorAction SilentlyContinue)
  if($script:p.Count -eq 1){
   $path=''
   try{$path=$script:p[0].Path}catch{$path=''}
   if($path -and ($path -ieq $client) -and $script:p[0].Responding){return $script:p[0]}
  }
  Start-Sleep -Seconds 1
 }
 $found=@(Get-Process XWall -ErrorAction SilentlyContinue).Count
 throw "Client not usable after wait: count=$found"
}
function Focus-Target {
 $proc=Get-Target
 [void][Hwk47Win]::SetForegroundWindow([IntPtr]$proc.MainWindowHandle)
 Start-Sleep -Milliseconds 600
 return $proc
}
function Send-Vk([int]$vk){
 [Hwk47Win]::keybd_event([byte]$vk,0,0,[UIntPtr]::Zero)
 Start-Sleep -Milliseconds 90
 [Hwk47Win]::keybd_event([byte]$vk,0,2,[UIntPtr]::Zero)
 Start-Sleep -Milliseconds 250
}
function Send-Alt([int]$vk){
 [Hwk47Win]::keybd_event([byte]0x12,0,0,[UIntPtr]::Zero)
 Start-Sleep -Milliseconds 90
 Send-Vk $vk
 [Hwk47Win]::keybd_event([byte]0x12,0,2,[UIntPtr]::Zero)
 Start-Sleep -Milliseconds 500
}
function Send-Ctrl([int]$vk){
 [Hwk47Win]::keybd_event([byte]0x11,0,0,[UIntPtr]::Zero)
 Start-Sleep -Milliseconds 90
 Send-Vk $vk
 [Hwk47Win]::keybd_event([byte]0x11,0,2,[UIntPtr]::Zero)
 Start-Sleep -Milliseconds 500
}
function Send-KeyTo([IntPtr]$h,[int]$vk){
 [void][Hwk47Win]::SendMessage($h,0x0100,[IntPtr]$vk,[IntPtr]0)
 Start-Sleep -Milliseconds 70
 [void][Hwk47Win]::SendMessage($h,0x0101,[IntPtr]$vk,[IntPtr]0)
 Start-Sleep -Milliseconds 220
}
function Click-At([int]$x,[int]$y){
 [void][Hwk47Win]::SetCursorPos($x,$y)
 Start-Sleep -Milliseconds 200
 [Hwk47Win]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
 Start-Sleep -Milliseconds 80
 [Hwk47Win]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
 Start-Sleep -Milliseconds 600
}
function Get-UiObs {
 $proc=Get-Target
 $root=[Windows.Automation.AutomationElement]::RootElement
 $c=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
 $wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$c)
 $windows=@();$nodes=@()
 foreach($w in $wins){
  $windows+=[ordered]@{Name=$w.Current.Name;Handle=$w.Current.NativeWindowHandle;Class=$w.Current.ClassName;Offscreen=$w.Current.IsOffscreen}
  try{$els=$w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)}catch{continue}
  for($i=0;$i -lt [Math]::Min($els.Count,1500);$i++){$e=$els.Item($i).Current;$nodes+=[ordered]@{Name=$e.Name;Id=$e.AutomationId;Type=$e.ControlType.ProgrammaticName;Enabled=$e.IsEnabled;Offscreen=$e.IsOffscreen;Handle=$e.NativeWindowHandle;Class=$e.ClassName;Rect=@($e.BoundingRectangle.X,$e.BoundingRectangle.Y,$e.BoundingRectangle.Width,$e.BoundingRectangle.Height)}}
 }
 [ordered]@{
  At=[DateTime]::UtcNow.ToString('o');Session=[Diagnostics.Process]::GetCurrentProcess().SessionId
  Process=@($proc|Select-Object Id,Path,SessionId,Responding,MainWindowHandle,MainWindowTitle)
  Screen=@([Windows.Forms.SystemInformation]::VirtualScreen.Width,[Windows.Forms.SystemInformation]::VirtualScreen.Height)
  Windows=$windows;Nodes=$nodes
  TCP=@(Get-NetTCPConnection -OwningProcess $proc.Id -ErrorAction SilentlyContinue|Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,State)
  UDP=@(Get-NetUDPEndpoint -OwningProcess $proc.Id -ErrorAction SilentlyContinue|Select-Object LocalAddress,LocalPort)
 }
}
function Save-Shot([string]$name){
 $s=[Windows.Forms.SystemInformation]::VirtualScreen
 $bmp=New-Object Drawing.Bitmap($s.Width,$s.Height)
 $g=[Drawing.Graphics]::FromImage($bmp)
 $g.CopyFromScreen($s.X,$s.Y,0,0,$bmp.Size)
 $bmp.Save((Join-Path $card ($name+'.png')))
 $g.Dispose();$bmp.Dispose()
}
function Save-Obs([string]$name){
 Save-Only $name
 Save-Shot $name
}
function Save-Only([string]$name){
 $json=(Get-UiObs|ConvertTo-Json -Depth 8)
 $json=$json -replace '-Infinity','null' -replace 'Infinity','null' -replace 'NaN','null'
 [IO.File]::WriteAllText((Join-Path $card ($name+'.json')),$json,(New-Object Text.UTF8Encoding($false)))
}
'''

ACTIONS = {
    # open the 输出 menu with its Alt mnemonic and capture what it exposes
    'menu-o': r'''
$null=Focus-Target
Send-Alt 0x4F
Save-Obs 'menu-o'
Write-Output 'ok'
''',
    # open the standard file dialog (Ctrl+O) on the running client
    'open-dialog': r'''
$null=Focus-Target
Send-Ctrl 0x4F
Start-Sleep -Seconds 2
Save-Obs 'open-dialog'
Write-Output 'ok'
''',
    # fill the open dialog's filename edit with the frozen working sample and confirm
    'open-sample': r"""
$null=Focus-Target
$sample='C:\hwk-modern\HWK-000041-B02-01\projects\sample-working.cwx'
$proc=Get-Target
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
$ec=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ControlTypeProperty,[Windows.Automation.ControlType]::Edit)
$found=$null;$info=@()
foreach($w in $wins){
 foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,$ec)){
  $c=$e.Current
  $info+=[pscustomobject]@{Window=$w.Current.Name;Name=$c.Name;Id=$c.AutomationId;Class=$c.ClassName;Focused=$c.HasKeyboardFocus;Offscreen=$c.IsOffscreen}
  if($null -eq $found -and $c.ClassName -eq 'Edit' -and ($c.HasKeyboardFocus -or $c.AutomationId -eq '1148' -or $c.Name -like '*文件名*')){$found=$e}
 }
}
if($null -eq $found){foreach($w in $wins){foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,$ec)){if($null -eq $found -and $e.Current.ClassName -eq 'Edit' -and $e.Current.IsOffscreen -eq $false){$found=$e}}}}
$report=[pscustomobject]@{At=[DateTime]::UtcNow.ToString('o');Found=($null -ne $found);Edits=@($info);Set=$false;Confirmed=$false;Sample=$sample}
if($null -ne $found){
 try{$vp=$found.GetCurrentPattern([Windows.Automation.ValuePattern]::Pattern);$vp.SetValue($sample);$report.Set=$true}catch{$report | Add-Member -NotePropertyName SetError -NotePropertyValue $_.Exception.Message}
 if($report.Set){Start-Sleep -Milliseconds 600;Send-Vk 0x0D;$report.Confirmed=$true;Start-Sleep -Seconds 8}
}
$json=($report|ConvertTo-Json -Depth 5) -replace '-Infinity','null' -replace 'Infinity','null' -replace 'NaN','null'
[IO.File]::WriteAllText((Join-Path $card 'open-sample.json'),$json,(New-Object Text.UTF8Encoding($false)))
Save-Shot 'open-sample'
Write-Output ('found=' + $report.Found + ' set=' + $report.Set)
""",
    # 输出 menu mnemonic then Enter on 计算书输出(B): opens the output settings dialog
    'output-enter': r'''
$null=Focus-Target
Send-Alt 0x4F
Send-Vk 0x0D
Start-Sleep -Seconds 4
Save-Obs 'output-enter'
Write-Output 'ok'
''',
    # invoke 文件保存路径(P) (id 1065) in the output settings dialog
    'path-dialog': r'''
$proc=Get-Target
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
$target=$null
foreach($w in $wins){
 foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
  $c=$e.Current
  if($c.AutomationId -eq '1065' -and $c.ClassName -eq 'Button'){$target=$e;break}
 }
 if($null -ne $target){break}
}
if($null -eq $target){throw 'path button 1065 not found'}
$h=[IntPtr]$target.Current.NativeWindowHandle
if($h -eq [IntPtr]::Zero){throw 'path button has no window handle'}
[void][Hwk47Win]::PostMessage($h,0x00F5,[IntPtr]::Zero,[IntPtr]::Zero)
Start-Sleep -Seconds 2
Save-Obs 'path-dialog'
Write-Output 'ok'
''',
    # navigate the shell folder browse tree by keyboard with MSAA feedback, then 确定
    'path-goto': r"""
$proc=Get-Target
Add-Type -AssemblyName Accessibility
Add-Type @'
using System;using System.Runtime.InteropServices;
public class Hwk47Acc {
[DllImport("oleacc.dll")]public static extern int AccessibleObjectFromWindow(IntPtr h,uint id,ref Guid iid,[MarshalAs(UnmanagedType.Interface)] out object acc);
}
'@
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
$tree=$null;$dialogName='';$fallback=$null;$fallbackDialog=''
foreach($w in $wins){
 foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
  $c=$e.Current
  if($c.ClassName -ne 'SysTreeView32' -or $c.IsOffscreen -ne $false){continue}
  if($c.AutomationId -eq '14145'){$tree=$e;$dialogName=$w.Current.Name}
  if($c.AutomationId -eq '1067'){continue}
  if($null -eq $fallback){$fallback=$e;$fallbackDialog=$w.Current.Name}
 }
}
if($null -eq $tree){$tree=$fallback;$dialogName=$fallbackDialog}
if($null -eq $tree){throw 'browse tree not found'}
$info+=@()
$th=[IntPtr]$tree.Current.NativeWindowHandle
$iid=[Accessibility.IAccessible].GUID
$acc=$null
$hr=[Hwk47Acc]::AccessibleObjectFromWindow($th,[uint32]4294967292,[ref]$iid,[ref]$acc)
if($hr -ne 0 -or $null -eq $acc){throw ('AccessibleObjectFromWindow failed hr=' + $hr)}
function SelName {
 try{
  $sel=$acc.accSelection
  if($null -eq $sel){return ''}
  if($sel -is [int]){return $acc.accName($sel)}
  return $sel.accName(0)
 }catch{return ''}
}
$trace=@()
$initial=SelName
$trace+=("initial=" + $initial)
for($i=0;$i -lt 40;$i++){
 $before=SelName
 Send-KeyTo $th 0x26
 $after=SelName
 if($after -eq $before){$trace+=("root-stop=" + $after);break}
}
foreach($part in @('hwk-modern','HWK-000048-B02-02','reports')){
 Send-KeyTo $th 0x27
 $found=$false
 for($i=0;$i -lt 80;$i++){
  $now=SelName
  if($now -eq $part){$found=$true;$trace+=("found=" + $part);break}
  Send-KeyTo $th 0x28
  $nxt=SelName
  if($nxt -eq $now){$trace+=("stuck-at=" + $now + ' seeking=' + $part);break}
 }
 if(-not $found){break}
}
$final=SelName
$trace+=("final=" + $final)
$report=[pscustomobject]@{At=[DateTime]::UtcNow.ToString('o');Dialog=$dialogName;TreeHandle=$th.ToInt64();Initial=$initial;Final=$final;Trace=@($trace);Confirmed=($final -eq 'reports')}
if($report.Confirmed){
 $btn=$null
 foreach($w in $wins){
  if($w.Current.Name -ne $dialogName){continue}
  foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
   $c=$e.Current
   if($c.ClassName -eq 'Button' -and $c.AutomationId -eq '1' -and $c.IsOffscreen -eq $false){$btn=[IntPtr]$c.NativeWindowHandle}
  }
 }
 if($btn -eq $null){throw 'confirm button not found'}
 [void][Hwk47Win]::PostMessage([IntPtr]$btn,0x00F5,[IntPtr]::Zero,[IntPtr]::Zero)
 $report | Add-Member -NotePropertyName ConfirmSent -NotePropertyValue $true
 Start-Sleep -Seconds 3
}
$json=($report|ConvertTo-Json -Depth 5) -replace '-Infinity','null' -replace 'Infinity','null' -replace 'NaN','null'
[IO.File]::WriteAllText((Join-Path $card 'path-goto.json'),$json,(New-Object Text.UTF8Encoding($false)))
Save-Shot 'path-goto'
Write-Output ('final=' + $final)
""",
    # confirm the output settings dialog: click 确定 (id 1) and let the app generate
    'generate': r"""
$proc=Get-Target
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
$path='';$confirm=$null;$buttons=@()
foreach($w in $wins){
 foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
  $c=$e.Current
  if($c.AutomationId -eq '1066' -and $c.ClassName -eq 'Static'){$path=$c.Name}
  if($c.ClassName -eq 'Button' -and $c.AutomationId -eq '1' -and $c.IsOffscreen -eq $false -and $c.IsEnabled -eq $true){
    $buttons+=[pscustomobject]@{Window=$w.Current.Name;Name=$c.Name;Handle=$c.NativeWindowHandle;Rect=@($c.BoundingRectangle.X,$c.BoundingRectangle.Y,$c.BoundingRectangle.Width,$c.BoundingRectangle.Height)}
    if($null -eq $confirm){$confirm=[IntPtr]$c.NativeWindowHandle}
  }
 }
}
$report=[pscustomobject]@{At=[DateTime]::UtcNow.ToString('o');PathText=$path;Buttons=@($buttons);Clicked=$false;ConfirmHandle=$(if($confirm){$confirm.ToInt64()}else{0})}
if($path -ne 'C:\hwk-modern\HWK-000048-B02-02\reports'){
 $report | Add-Member -NotePropertyName Refused -NotePropertyValue ('path-not-authorized:' + $path)
}else{
 if($null -eq $confirm){throw 'confirm button not found'}
 [void][Hwk47Win]::PostMessage([IntPtr]$confirm,0x00F5,[IntPtr]::Zero,[IntPtr]::Zero)
 $report.Clicked=$true
 Start-Sleep -Seconds 15
}
$json=($report|ConvertTo-Json -Depth 5) -replace '-Infinity','null' -replace 'Infinity','null' -replace 'NaN','null'
[IO.File]::WriteAllText((Join-Path $card 'generate.json'),$json,(New-Object Text.UTF8Encoding($false)))
Save-Shot 'generate'
Write-Output ('clicked=' + $report.Clicked + ' path=' + $path)
""",
    # click 确定 inside the browse-folder dialog by its own window, then verify
    'confirm-browse': r"""
$proc=Get-Target
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
$target=$null
foreach($w in $wins){
 if($w.Current.NativeWindowHandle -eq $proc.MainWindowHandle){continue}
 if($null -eq $target){$target=$w}
}
if($null -eq $target){throw 'no dialog window besides the main window'}
$name=$target.Current.Name
$btn=$null
foreach($e in $target.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
 $c=$e.Current
 if($c.ClassName -eq 'Button' -and $c.AutomationId -eq '1' -and $c.IsEnabled -eq $true -and $c.IsOffscreen -eq $false){$btn=[IntPtr]$c.NativeWindowHandle;break}
}
$report=[pscustomobject]@{At=[DateTime]::UtcNow.ToString('o');Window=$name;Button=$(if($btn){$btn.ToInt64()}else{0});Posted=$false}
if($null -ne $btn){
 [void][Hwk47Win]::PostMessage([IntPtr]$btn,0x00F5,[IntPtr]::Zero,[IntPtr]::Zero)
 $report.Posted=$true
 Start-Sleep -Seconds 3
}
$json=($report|ConvertTo-Json -Depth 4) -replace '-Infinity','null' -replace 'Infinity','null' -replace 'NaN','null'
[IO.File]::WriteAllText((Join-Path $card 'confirm-browse.json'),$json,(New-Object Text.UTF8Encoding($false)))
Save-Shot 'confirm-browse'
Write-Output ('window=' + $name + ' posted=' + $report.Posted)
""",
    # point the app's save-calculation-book dialog at this card's reports directory
    'save-as': r"""
$proc=Get-Target
$targetPath='C:\hwk-modern\HWK-000048-B02-02\reports\各种样式栏杆计算样例常规栏杆1[产品结构].rtf'
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
$main=$null
foreach($w in $wins){if($w.Current.NativeWindowHandle -eq $proc.MainWindowHandle){$main=$w}}
if($null -eq $main){$main=$wins.Item(0)}
$walker=[Windows.Automation.TreeWalker]::ControlViewWalker
$edit=$null
foreach($e in $main.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
 $c=$e.Current
 if($c.ClassName -eq 'Edit' -and $c.AutomationId -eq '1001' -and $c.IsOffscreen -eq $false){$edit=$e;break}
}
$report=[pscustomobject]@{At=[DateTime]::UtcNow.ToString('o');EditFound=($null -ne $edit);Dialog='';Set=$false;Value='';Saved=$false}
if($null -eq $edit){throw 'filename edit 1001 not found under the app window'}
$dlg=$edit
for($i=0;$i -lt 8;$i++){$p=$walker.GetParent($dlg);if($null -eq $p){break};$dlg=$p;if($dlg.Current.ClassName -eq '#32770'){break}}
$report.Dialog=$dlg.Current.Name
$eh=[IntPtr]$edit.Current.NativeWindowHandle
if($eh -eq [IntPtr]::Zero){throw 'filename edit has no window handle'}
[void][Hwk47Win]::SendMessageText($eh,0x000C,[IntPtr]::Zero,$targetPath)
Start-Sleep -Milliseconds 700
$report.Value=$edit.Current.Name
$report.Set=($report.Value -eq $targetPath)
if($report.Set){
 $btn=$null
 foreach($e in $dlg.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
  $c=$e.Current
  if($c.ClassName -eq 'Button' -and $c.AutomationId -eq '1' -and $c.IsEnabled -eq $true -and $c.IsOffscreen -eq $false){$btn=[IntPtr]$c.NativeWindowHandle;break}
 }
 if($null -eq $btn){throw 'save button not found'}
 [void][Hwk47Win]::PostMessage([IntPtr]$btn,0x00F5,[IntPtr]::Zero,[IntPtr]::Zero)
 $report.Saved=$true
 Start-Sleep -Seconds 20
}
$json=($report|ConvertTo-Json -Depth 4) -replace '-Infinity','null' -replace 'Infinity','null' -replace 'NaN','null'
[IO.File]::WriteAllText((Join-Path $card 'save-as.json'),$json,(New-Object Text.UTF8Encoding($false)))
Save-Shot 'save-as'
Write-Output ('dialog=' + $report.Dialog + ' set=' + $report.Set + ' saved=' + $report.Saved)
""",
    # dump every UIA node of the app with class/id/focus to identify dialog controls
    'dump-dialog': r"""
$proc=Get-Target
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
$rows=@()
foreach($w in $wins){
 foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
  $c=$e.Current
  if($c.ClassName -in @('Edit','Button','Static','SysTreeView32','ComboBox','ListBox','SysListView32','#32770','DirectUIHWND')){
   $rows+=[pscustomobject]@{Win=$w.Current.Name;Name=$c.Name;Id=$c.AutomationId;Class=$c.ClassName;Type=$c.ControlType.ProgrammaticName;Enabled=$c.IsEnabled;Offscreen=$c.IsOffscreen;Focused=$c.HasKeyboardFocus;Handle=$c.NativeWindowHandle}
  }
 }
}
[pscustomobject]@{At=[DateTime]::UtcNow.ToString('o');Rows=@($rows)} | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $card 'dump-dialog.json') -Encoding UTF8
Save-Shot 'dump-dialog'
Write-Output ('rows=' + $rows.Count)
""",

    'menu-h': r'''
$null=Focus-Target
Send-Alt 0x48
Save-Obs 'menu-h'
Write-Output 'ok'
''',

    # record the product's own "report created" modal, dismiss it, then open 帮助
    'report-done': r'''
Save-Obs 'report-done'
$proc=Get-Target
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
$btn=$null;$texts=@()
foreach($w in $wins){
 foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
  $c=$e.Current
  if($c.ClassName -eq 'Static' -and $c.Name -ne ''){$texts+=$c.Name}
  if($c.ClassName -eq 'Button' -and $c.AutomationId -eq '1' -and $c.IsEnabled -eq $true -and $c.IsOffscreen -eq $false -and $null -eq $btn){$btn=[IntPtr]$c.NativeWindowHandle}
 }
}
$dismissed=$false
if($null -ne $btn){
 [void][Hwk47Win]::PostMessage([IntPtr]$btn,0x00F5,[IntPtr]::Zero,[IntPtr]::Zero)
 $dismissed=$true
 Start-Sleep -Seconds 2
}
[pscustomobject]@{At=[DateTime]::UtcNow.ToString('o');DialogTexts=@($texts);Dismissed=$dismissed} | ConvertTo-Json -Depth 4 | Set-Content "$card\report-done-summary.json" -Encoding UTF8
$null=Focus-Target
Send-Alt 0x48
Save-Obs 'help-menu'
Write-Output ('dismissed=' + $dismissed)
''',

    # dismiss the product's modal confirmation and capture the resulting state
    'dismiss': r"""
$proc=Get-Target
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
$btn=$null;$found=@()
foreach($w in $wins){
 foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
  $c=$e.Current
  if($c.ClassName -eq '#32770'){$found+=$c.Name}
  if($c.ClassName -eq 'Button' -and $c.Name -like '*确定*' -and $c.IsEnabled -and -not $c.IsOffscreen -and $null -eq $btn){$btn=[IntPtr]$c.NativeWindowHandle}
 }
}
$report=[pscustomobject]@{At=[DateTime]::UtcNow.ToString('o');Dialogs=@($found);Button=$(if($btn){$btn.ToInt64()}else{0});Clicked=$false}
if($null -ne $btn){
 [void][Hwk47Win]::PostMessage([IntPtr]$btn,0x00F5,[IntPtr]::Zero,[IntPtr]::Zero)
 $report.Clicked=$true
 Start-Sleep -Seconds 2
}
$json=($report|ConvertTo-Json -Depth 4) -replace '-Infinity','null' -replace 'Infinity','null' -replace 'NaN','null'
[IO.File]::WriteAllText((Join-Path $card 'dismiss.json'),$json,(New-Object Text.UTF8Encoding($false)))
Save-Obs 'dismiss'
Write-Output ('clicked=' + $report.Clicked + ' dialogs=' + ($found -join ','))
""",

    # click the modal's 确定 with a real mouse click at its reported rectangle
    'click-modal-ok': r"""
$proc=Get-Target
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
$hit=$null
foreach($w in $wins){
 foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
  $c=$e.Current
  if($c.ClassName -eq 'Button' -and $c.Name -like '*确定*' -and $c.IsEnabled -and -not $c.IsOffscreen){$hit=$c;break}
 }
 if($null -ne $hit){break}
}
$report=[pscustomobject]@{At=[DateTime]::UtcNow.ToString('o');Found=($null -ne $hit);Rect=$null;Clicked=$false}
if($null -ne $hit){
 $r=$hit.BoundingRectangle
 $x=[int]($r.X + $r.Width/2);$y=[int]($r.Y + $r.Height/2)
 $report.Rect=@([int]$r.X,[int]$r.Y,[int]$r.Width,[int]$r.Height)
 Click-At $x $y
 $report.Clicked=$true
 Start-Sleep -Seconds 2
}
$json=($report|ConvertTo-Json -Depth 4) -replace '-Infinity','null' -replace 'Infinity','null' -replace 'NaN','null'
[IO.File]::WriteAllText((Join-Path $card 'click-modal-ok.json'),$json,(New-Object Text.UTF8Encoding($false)))
Save-Obs 'click-modal-ok'
Write-Output ('found=' + $report.Found + ' rect=' + ($report.Rect -join ','))
""",

    # cancel the follow-up save dialog so nothing is written to the historical directory
    'cancel-save': r"""
$proc=Get-Target
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
$hit=$null
foreach($w in $wins){
 foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
  $c=$e.Current
  if($c.ClassName -eq 'Button' -and $c.Name -like '*取消*' -and $c.IsEnabled -and -not $c.IsOffscreen){$hit=$c;break}
 }
 if($null -ne $hit){break}
}
$report=[pscustomobject]@{At=[DateTime]::UtcNow.ToString('o');Found=($null -ne $hit);Rect=$null;Clicked=$false;HookOutAfter=-1;ReportsAfter=-1}
if($null -ne $hit){
 $r=$hit.BoundingRectangle
 $report.Rect=@([int]$r.X,[int]$r.Y,[int]$r.Width,[int]$r.Height)
 Click-At ([int]($r.X + $r.Width/2)) ([int]($r.Y + $r.Height/2))
 $report.Clicked=$true
 Start-Sleep -Seconds 3
}
$report.HookOutAfter=@(Get-ChildItem -LiteralPath 'C:\hwk\hook-out' -Recurse -File -ErrorAction SilentlyContinue|Where-Object {$_.LastWriteTime.ToUniversalTime() -gt [datetime]'2026-10-19T19:45:00Z'}).Count
$report.ReportsAfter=@(Get-ChildItem -LiteralPath "$card\reports" -File -ErrorAction SilentlyContinue).Count
$json=($report|ConvertTo-Json -Depth 4) -replace '-Infinity','null' -replace 'Infinity','null' -replace 'NaN','null'
[IO.File]::WriteAllText((Join-Path $card 'cancel-save.json'),$json,(New-Object Text.UTF8Encoding($false)))
Save-Obs 'cancel-save'
Write-Output ('clicked=' + $report.Clicked + ' hookout=' + $report.HookOutAfter + ' reports=' + $report.ReportsAfter)
""",

    # escape the remaining per-point save dialogs (never save into the default dir)
    'esc-loop': r"""
$proc=Get-Target
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
function Count-Save {
 $wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
 $n=0
 foreach($w in $wins){
  foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
   $c=$e.Current
   if($c.ClassName -eq '#32770' -and $c.Name -eq '保存计算书文件' -and -not $c.IsOffscreen){$n++}
  }
 }
 return $n
}
$trace=@()
for($i=0;$i -lt 8;$i++){
 $before=Count-Save
 if($before -eq 0){$trace+=("done-after-$i");break}
 $trace+=("save-dialog=$before")
 Send-Vk 0x1B
 Start-Sleep -Seconds 2
}
$after=Count-Save
$report=[pscustomobject]@{At=[DateTime]::UtcNow.ToString('o');Trace=@($trace);SaveDialogsAfter=$after;HookOutRecent=@(Get-ChildItem -LiteralPath 'C:\hwk\hook-out' -Recurse -File -ErrorAction SilentlyContinue|Where-Object {$_.LastWriteTime.ToUniversalTime() -gt [datetime]'2026-10-19T19:45:00Z'}).Count;Reports=@(Get-ChildItem -LiteralPath "$card\reports" -File).Count}
$json=($report|ConvertTo-Json -Depth 4) -replace '-Infinity','null' -replace 'Infinity','null' -replace 'NaN','null'
[IO.File]::WriteAllText((Join-Path $card 'esc-loop.json'),$json,(New-Object Text.UTF8Encoding($false)))
Save-Obs 'esc-loop'
Write-Output ('dialogsAfter=' + $after + ' hookout=' + $report.HookOutRecent + ' reports=' + $report.Reports)
""",

    # cancel the remaining per-point save dialogs with the dialog itself foregrounded
    'cancel-loop': r"""
$proc=Get-Target
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
function Get-Save {
 $wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
 foreach($w in $wins){
  foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
   $c=$e.Current
   if($c.ClassName -eq '#32770' -and $c.Name -eq '保存计算书文件' -and -not $c.IsOffscreen){return $e}
  }
 }
 return $null
}
$trace=@()
for($i=0;$i -lt 10;$i++){
 $dlg=Get-Save
 if($null -eq $dlg){$trace+=("clear-at-$i");break}
 $trace+=("dialog-$i")
 [void][Hwk47Win]::SetForegroundWindow([IntPtr]$dlg.Current.NativeWindowHandle)
 Start-Sleep -Milliseconds 400
 Send-Vk 0x1B
 Start-Sleep -Seconds 2
}
$open=($null -ne (Get-Save))
$report=[pscustomobject]@{At=[DateTime]::UtcNow.ToString('o');Trace=@($trace);StillOpen=$open;HookOutRecent=@(Get-ChildItem -LiteralPath 'C:\hwk\hook-out' -Recurse -File -ErrorAction SilentlyContinue|Where-Object {$_.LastWriteTime.ToUniversalTime() -gt [datetime]'2026-10-19T19:45:00Z'}).Count;Reports=@(Get-ChildItem -LiteralPath "$card\reports" -File).Count}
($report|ConvertTo-Json -Depth 4) | Set-Content "$card\cancel-loop-report.json" -Encoding UTF8
Save-Shot 'cancel-loop'
Write-Output ('stillOpen=' + $open + ' hookout=' + $report.HookOutRecent + ' reports=' + $report.Reports)
""",

    # complete the whole 计算书 output: every calc point saved under the authorized dir
    'export-all': r"""
$proc=Get-Target
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
function Find-Elements([string]$class,[string]$nameLike){
 $wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
 $hits=@()
 foreach($w in $wins){
  foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
   $c=$e.Current
   if($c.ClassName -ne $class -or $c.IsOffscreen){continue}
   if($nameLike -ne '' -and $c.Name -notlike $nameLike){continue}
   $hits+=$e
  }
 }
 return $hits
}
function Click-Element($e){
 $r=$e.Current.BoundingRectangle
 if($r.Width -le 0 -or $r.Height -le 0){return $false}
 Click-At ([int]($r.X + $r.Width/2)) ([int]($r.Y + $r.Height/2))
 return $true
}
$trace=@();$saved=@()
$settings=@(Find-Elements '#32770' '输出设置对话框')
if($settings.Count -eq 0){
 $null=Focus-Target
 Send-Alt 0x4F
 Send-Vk 0x0D
 Start-Sleep -Seconds 3
 $settings=@(Find-Elements '#32770' '输出设置对话框')
}
if($settings.Count -eq 0){throw 'output settings dialog did not open'}
$trace+=('settings=' + $settings[0].Current.Name)
$okButtons=@(Find-Elements 'Button' '*确定*')
if($okButtons.Count -eq 0){throw 'settings confirm not found'}
[void](Click-Element $okButtons[0])
Start-Sleep -Seconds 4
for($i=1;$i -le 15;$i++){
 $saves=@(Find-Elements '#32770' '保存计算书文件')
 if($saves.Count -eq 0){
  $confirms=@(Find-Elements 'Button' '*确定*')
  if($confirms.Count -gt 0){
   $trace+=("confirm-modal-$i")
   [void](Click-Element $confirms[0])
   Start-Sleep -Seconds 2
   continue
  }
  $trace+=("no-dialog-$i")
  break
 }
 $dlg=$saves[0]
 $edits=@($dlg.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition) | Where-Object {$_.Current.ClassName -eq 'Edit' -and $_.Current.AutomationId -eq '1001'})
 if($edits.Count -lt 1){$trace+=("no-edit-$i");break}
 $target=Join-Path $card ('reports\report-point-' + $i.ToString('00') + '.rtf')
 $eh=[IntPtr]$edits[0].Current.NativeWindowHandle
 [void][Hwk47Win]::SendMessageText($eh,0x000C,[IntPtr]::Zero,$target)
 Start-Sleep -Milliseconds 400
 $value=$edits[0].Current.Name
 if(-not $value.StartsWith($card + '\reports\')){$trace+=("guard-refused:$value");break}
 $saveButtons=@($dlg.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition) | Where-Object {$_.Current.ClassName -eq 'Button' -and $_.Current.AutomationId -eq '1' -and -not $_.Current.IsOffscreen})
 if($saveButtons.Count -lt 1){$trace+=("no-save-$i");break}
 $bh=[IntPtr]$saveButtons[0].Current.NativeWindowHandle
 [void][Hwk47Win]::PostMessage($bh,0x00F5,[IntPtr]::Zero,[IntPtr]::Zero)
 Start-Sleep -Seconds 3
 $saved+=$target
 $trace+=("saved-$i")
}
$files=@(Get-ChildItem -LiteralPath "$card\reports" -File -Force | ForEach-Object {[ordered]@{Name=$_.Name;Length=$_.Length;SHA256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash}})
$report=[pscustomobject]@{At=[DateTime]::UtcNow.ToString('o');Trace=@($trace);Saved=@($saved);FileCount=$files.Count;Files=$files;HookOutRecent=@(Get-ChildItem -LiteralPath 'C:\hwk\hook-out' -Recurse -File -ErrorAction SilentlyContinue|Where-Object {$_.LastWriteTime.ToUniversalTime() -gt [datetime]'2026-10-19T19:45:00Z'}).Count;Errors=@(Get-WinEvent -FilterHashtable @{LogName='Application';Id=1000,1001,1026;StartTime=[datetime]'2026-10-19T20:40:00Z'} -ErrorAction SilentlyContinue|Where-Object {$_.Message -match 'XWall'}).Count}
($report|ConvertTo-Json -Depth 5) | Set-Content "$card\export-all.json" -Encoding UTF8
Save-Shot 'export-all'
Write-Output ('saved=' + $saved.Count + ' files=' + $files.Count + ' hookout=' + $report.HookOutRecent)
""",

    # relaunch the isolated client with the frozen working sample after the exit incident
    'launch': r"""
$client='C:\hwk-modern\HWK-000041-B02-01\client'
$sample='C:\hwk-modern\HWK-000041-B02-01\projects\sample-working.cwx'
if(@(Get-Process XWall -ErrorAction SilentlyContinue).Count){throw 'Refuse: an XWall process already exists'}
if((Get-FileHash -LiteralPath "$client\XWall.exe" -Algorithm SHA256).Hash -ne '76838A839C5EF262499D6315570DA26FFD59DA7BB29ED616ADAA6B4BFE7221E5'){throw 'exe hash mismatch'}
if((Get-FileHash -LiteralPath $sample -Algorithm SHA256).Hash -ne '2FFA32CB256324AE610C2215BFE554DDB42BA0CBB06108188C6727B2F060FBE3'){throw 'sample hash mismatch'}
$p=Start-Process -FilePath "$client\XWall.exe" -ArgumentList ('"'+$sample+'"') -WorkingDirectory $client -PassThru
Start-Sleep -Seconds 18
[pscustomobject]@{At=[DateTime]::UtcNow.ToString('o');Id=$p.Id;Session=$p.SessionId;Exited=$p.HasExited;Input=$sample} | ConvertTo-Json | Set-Content "$card\launch.json" -Encoding UTF8
Save-Obs 'launch'
Write-Output ('pid=' + $p.Id + ' exited=' + $p.HasExited)
""",

    # walk the 输出 menu and record each item's status-bar hint
    'menu-scan': r"""
$null=Focus-Target
$proc=Get-Target
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
function Status-Text {
 foreach($w in $wins){
  foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
   $c=$e.Current
   if($c.AutomationId -eq '59393'){return $c.Name}
  }
 }
 return ''
}
$trace=@()
Send-Alt 0x4F
$trace+=@('open=' + (Status-Text))
for($i=1;$i -le 8;$i++){
 Send-Vk 0x28
 $trace+=("down$i=" + (Status-Text))
}
Send-Vk 0x1B
Save-Shot 'menu-scan'
$json=(@($trace)|ConvertTo-Json -Depth 3)
[IO.File]::WriteAllText((Join-Path $card 'menu-scan.json'),$json,(New-Object Text.UTF8Encoding($false)))
Write-Output ('steps=' + $trace.Count)
""",

    # try the app's Save-As accelerator and report which dialog appears
    'saveas-try': r"""
$null=Focus-Target
$proc=Get-Target
[Hwk47Win]::keybd_event([byte]0x11,0,0,[UIntPtr]::Zero)
[Hwk47Win]::keybd_event([byte]0x10,0,0,[UIntPtr]::Zero)
Start-Sleep -Milliseconds 80
Send-Vk 0x53
[Hwk47Win]::keybd_event([byte]0x10,0,2,[UIntPtr]::Zero)
[Hwk47Win]::keybd_event([byte]0x11,0,2,[UIntPtr]::Zero)
Start-Sleep -Seconds 2
$root=[Windows.Automation.AutomationElement]::RootElement
$pc=New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty,$proc.Id)
$wins=$root.FindAll([Windows.Automation.TreeScope]::Children,$pc)
$dialogs=@();$edits=@()
foreach($w in $wins){
 foreach($e in $w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)){
  $c=$e.Current
  if($c.ClassName -eq '#32770' -and -not $c.IsOffscreen){$dialogs+=$c.Name}
  if($c.ClassName -eq 'Edit' -and $c.AutomationId -eq '1001'){$edits+=$c.Name}
 }
}
[pscustomobject]@{At=[DateTime]::UtcNow.ToString('o');Dialogs=@($dialogs);EditValues=@($edits);Title=$proc.MainWindowTitle} | ConvertTo-Json -Depth 4 | Set-Content "$card\saveas-try.json" -Encoding UTF8
Save-Shot 'saveas-try'
Write-Output ('dialogs=' + ($dialogs -join ';'))
""",
    # close the shell rename warning and the open dialog by clicking their buttons
    'close-dialogs': r'''
$null=Focus-Target
Click-At 613 373
Start-Sleep -Milliseconds 800
Click-At 882 500
Start-Sleep -Milliseconds 800
Save-Shot 'close-dialogs'
[IO.File]::WriteAllText((Join-Path $card 'close-dialogs.json'),('{"At":"' + [DateTime]::UtcNow.ToString('o') + '"}'),(New-Object Text.UTF8Encoding($false)))
''',
    # keys only: two Escapes, no UIA (safe while shell dialogs are unstable)
    'esc-min': r'''
$null=Focus-Target
Send-Vk 0x1B
Start-Sleep -Milliseconds 800
Send-Vk 0x1B
Start-Sleep -Milliseconds 800
[IO.File]::WriteAllText((Join-Path $card 'esc-min.json'),('{"At":"' + [DateTime]::UtcNow.ToString('o') + '"}'),(New-Object Text.UTF8Encoding($false)))
'''
    ,
    # screenshot only, no UIA tree walk
    'shot': r'''
$null=Focus-Target
Save-Shot 'shot'
[IO.File]::WriteAllText((Join-Path $card 'shot.json'),('{"At":"' + [DateTime]::UtcNow.ToString('o') + '"}'),(New-Object Text.UTF8Encoding($false)))
'''
    ,
    # dismiss any open popup without choosing an item
    'esc': r'''
$null=Focus-Target
Send-Vk 0x1B
Start-Sleep -Milliseconds 800
Send-Vk 0x1B
Start-Sleep -Milliseconds 800
Save-Obs 'esc'
Write-Output 'ok'
''',
}


def remote_script(name):
    return REMOTE + '\\probe-' + name + '.ps1'


def upload(local, remote):
    """Copy with scp first; the ssh stdin bridge stalls intermittently on this host."""
    import subprocess

    remote_posix = remote.replace('\\', '/')
    cmd = [
        'scp', '-i', str(Path.home() / '.ssh/hwk-win-test'),
        '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes',
        '-o', 'StrictHostKeyChecking=yes',
        '-o', 'UserKnownHostsFile=evidence/runtime/ecs-20261018/known_hosts',
        str(local), f'Administrator@8.149.129.78:{remote_posix}',
    ]
    try:
        done = subprocess.run(cmd, capture_output=True, timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise SystemExit(f'scp upload failed: {error}') from error
    if done.returncode == 0:
        return 'scp-ok'
    try:
        payload = base64.b64encode(gzip.compress(Path(local).read_bytes())).decode()
    except OSError as error:
        raise SystemExit(f'cannot read probe script {local}: {error}') from error
    script = (
        "$p='" + remote.replace("'", "''") + "';"
        "$raw=[Convert]::FromBase64String('" + payload + "');"
        "$ms=New-Object IO.MemoryStream(,$raw);"
        "$gz=New-Object IO.Compression.GZipStream($ms,[IO.Compression.CompressionMode]::Decompress);"
        "$sr=New-Object IO.StreamReader($gz);"
        "[IO.File]::WriteAllText($p,$sr.ReadToEnd(),(New-Object Text.UTF8Encoding($true)));"
        "$sr.Dispose();$gz.Dispose();$ms.Dispose();"
        "(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash"
    )
    return run_ps_stdin(script, BASE / (Path(local).stem + '-upload'), timeout=180)


def start_task(name, remote):
    script = (
        f"Stop-ScheduledTask -TaskName '{TASK}' -ErrorAction SilentlyContinue;Start-Sleep -Seconds 2;"
        "$b='" + REMOTE + "';foreach($n in @('" + name + ".json','" + name + ".png','" + name + "-error.json')){Remove-Item -LiteralPath (Join-Path $b $n) -Force -ErrorAction SilentlyContinue};"
        "$a=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -WindowStyle Hidden -File "
        + remote + "';"
        f"$p=New-ScheduledTaskPrincipal -UserId '{RUNAS}' -LogonType Interactive -RunLevel Highest;"
        f"Register-ScheduledTask -Force -TaskName '{TASK}' -Action $a -Principal $p|Out-Null;"
        f"schtasks /run /tn '{TASK}' | Out-Null"
    )
    return run_ps(script, BASE / (name + '-schedule'))


def fetch(name):
    script = (
        "$b='" + REMOTE + "';"
        "for($i=0;$i -lt 90;$i++){if((Test-Path (\"$b\\" + name + ".json\")) -or (Test-Path (\"$b\\" + name + "-error.json\"))){break};Start-Sleep -Seconds 1};"
        f"[ordered]@{{Task=(Get-ScheduledTaskInfo -TaskName '{TASK}'|Select-Object LastTaskResult,LastRunTime);"
        "Image=$(if(Test-Path (\"$b\\" + name + ".png\")){[Convert]::ToBase64String([IO.File]::ReadAllBytes(\"$b\\" + name + ".png\"))}else{''});"
        "UI=$(if(Test-Path (\"$b\\" + name + ".json\")){[IO.File]::ReadAllText(\"$b\\" + name + ".json\")}else{''});"
        "Err=$(if(Test-Path (\"$b\\" + name + "-error.json\")){[IO.File]::ReadAllText(\"$b\\" + name + "-error.json\")}else{''})}|ConvertTo-Json -Depth 5"
    )
    out = run_ps(script, BASE / (name + '-capture'), timeout=240)
    try:
        data = json.loads(out)
    except json.JSONDecodeError as error:
        raise SystemExit(f'unexpected capture payload: {error}') from error
    if data.get('Image'):
        (BASE / (name + '.png')).write_bytes(base64.b64decode(data['Image']))
    for key, suffix in (('UI', '.json'), ('Err', '-error.json')):
        if data.get(key):
            text = data[key].lstrip('\ufeff')
            for token in ('-Infinity', 'Infinity', 'NaN'):
                text = text.replace(token, 'null')
            (BASE / (name + suffix)).write_text(text, encoding='utf-8')
    if data.get('Err'):
        raise SystemExit(f'action failed remotely: {data["Err"][:400]}')
    return data['Task']


def main(name):
    BASE.mkdir(parents=True, exist_ok=True)
    local = BASE / (name + '.ps1')
    body = ACTIONS[name]
    guarded = PRELUDE + '\ntry{\n' + body + '\n}catch{[ordered]@{At=[DateTime]::UtcNow.ToString(\'o\');Error=$_.Exception.Message;Line=$_.InvocationInfo.ScriptLineNumber;Command=$_.InvocationInfo.MyCommand}|ConvertTo-Json|Set-Content "$card\\' + name + '-error.json" -Encoding UTF8;exit 1}\n'
    local.write_text(guarded, encoding='utf-8-sig')
    remote = remote_script(name)
    print(upload(local, remote))
    print(start_task(name, remote))
    print(fetch(name))
    try:
        data = json.loads((BASE / (name + '.json')).read_text(encoding='utf-8-sig'))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f'action capture unreadable: {error}') from error
    print('screen:', data.get('Screen'), 'session:', data.get('Session'))
    print('windows:', json.dumps([w['Name'] for w in data.get('Windows', [])], ensure_ascii=False))
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in ACTIONS:
        raise SystemExit('actions: ' + ', '.join(ACTIONS))
    sys.exit(main(sys.argv[1]))
