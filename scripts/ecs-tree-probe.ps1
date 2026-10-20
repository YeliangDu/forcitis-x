$ErrorActionPreference='Stop';$b='C:\hwk-modern\run-20261018'
Add-Type @'
using System;using System.Runtime.InteropServices;public class HwkTree {
[DllImport("user32.dll")]public static extern IntPtr SendMessage(IntPtr h,uint msg,IntPtr w,IntPtr l);
[DllImport("user32.dll")]public static extern uint GetWindowThreadProcessId(IntPtr h,out uint pid);
}
'@
$ui=Get-Content "$b\ui.json" -Raw -Encoding UTF8|ConvertFrom-Json
$p=@(Get-Process XWall|Where-Object {$_.Path -like "$b\*"});if($p.Count -ne 1){throw 'Unique isolated app required'}
$rows=@()
foreach($n in $ui.Nodes|Where-Object {$_.Class -eq 'SysTreeView32'}){
 [uint32]$owner=0;[void][HwkTree]::GetWindowThreadProcessId([IntPtr]$n.Handle,[ref]$owner)
 if($owner -ne $p[0].Id){throw 'Tree ownership changed'}
 $count=[HwkTree]::SendMessage([IntPtr]$n.Handle,0x1105,[IntPtr]::Zero,[IntPtr]::Zero).ToInt64()
 $root=[HwkTree]::SendMessage([IntPtr]$n.Handle,0x110A,[IntPtr]::Zero,[IntPtr]::Zero)
 $script:expanded=0
 function Expand-HwkTree([IntPtr]$tree,[IntPtr]$item,[int]$depth){
  if($item -eq [IntPtr]::Zero -or $depth -gt 4 -or $script:expanded -ge 200){return}
  [void][HwkTree]::SendMessage($tree,0x1102,[IntPtr]2,$item);$script:expanded++
  $child=[HwkTree]::SendMessage($tree,0x110A,[IntPtr]4,$item)
  while($child -ne [IntPtr]::Zero -and $script:expanded -lt 200){Expand-HwkTree $tree $child ($depth+1);$child=[HwkTree]::SendMessage($tree,0x110A,[IntPtr]1,$child)}
 }
 Expand-HwkTree ([IntPtr]$n.Handle) $root 0
 $rows+=[PSCustomObject]@{Handle=$n.Handle;Count=$count;RootHandle=$root.ToInt64()}
}
$rows|ConvertTo-Json|Set-Content "$b\tree-counts.json" -Encoding UTF8
& "$b\ui-probe.ps1"
