$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$b='C:\hwk-modern\run-20261019-cwx'
$procs=@(Get-Process XWall -ErrorAction SilentlyContinue)
if($procs.Count -ne 1){throw ('Expected exactly one XWall, found ' + $procs.Count)}
$p=$procs[0]
if($p.Path -ne 'C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe' -or $p.SessionId -ne 4){throw 'Process identity changed'}

Add-Type @'
using System;using System.Runtime.InteropServices;using System.Text;
public class CwxMenu {
 [StructLayout(LayoutKind.Sequential)] public struct MENUITEMINFO {
  public uint cbSize; public uint fMask; public uint fType; public uint fState; public uint wID;
  public IntPtr hSubMenu; public IntPtr hbmpChecked; public IntPtr hbmpUnchecked; public IntPtr dwItemData;
  public IntPtr dwTypeData; public uint cch; public IntPtr hbmpItem;
 }
 [DllImport("user32.dll")] public static extern IntPtr GetMenu(IntPtr hWnd);
 [DllImport("user32.dll")] public static extern int GetMenuItemCount(IntPtr hMenu);
 [DllImport("user32.dll")] public static extern IntPtr GetSubMenu(IntPtr hMenu, int pos);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern bool GetMenuItemInfoW(IntPtr hMenu, uint item, bool byPos, ref MENUITEMINFO info);
 [DllImport("user32.dll")] public static extern uint GetMenuState(IntPtr hMenu, uint item, uint flags);
 [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);
 public static string Text(IntPtr hMenu, int pos) {
  MENUITEMINFO m = new MENUITEMINFO();
  m.cbSize = (uint)Marshal.SizeOf(typeof(MENUITEMINFO));
  m.fMask = 0x1; // MIIM_STATE
  m.dwTypeData = IntPtr.Zero; m.cch = 0;
  StringBuilder sb = new StringBuilder(256);
  m.dwTypeData = Marshal.AllocHGlobal(512);
  m.cch = 255;
  m.fMask = 0x2 | 0x1 | 0x4; // MIIM_STRING|STATE|ID
  bool ok = GetMenuItemInfoW(hMenu, (uint)pos, true, ref m);
  string s = ok ? Marshal.PtrToStringUni(m.dwTypeData) : null;
  Marshal.FreeHGlobal(m.dwTypeData);
  return s;
 }
}
'@
$hMenu=[CwxMenu]::GetMenu($p.MainWindowHandle)
$rows=@()
if($hMenu -eq [IntPtr]::Zero){
 $rows+=[ordered]@{Level=0;Index=-1;Text='NO_MENU_ATTACHED';Id=$null;State=$null;SubMenu=$false}
}else{
 $count=[CwxMenu]::GetMenuItemCount($hMenu)
 for($i=0;$i -lt $count;$i++){
  $txt=[CwxMenu]::Text($hMenu,$i)
  $sub=[CwxMenu]::GetSubMenu($hMenu,$i)
  $state=[CwxMenu]::GetMenuState($hMenu,[uint32]$i,0x400)
  $rows+=[ordered]@{Level=1;Index=$i;Text=$txt;State=$state;SubMenu=($sub -ne [IntPtr]::Zero);SubHandle=$sub.ToInt64()}
  if($sub -ne [IntPtr]::Zero){
   $sc=[CwxMenu]::GetMenuItemCount($sub)
   for($j=0;$j -lt $sc;$j++){
    $st=[CwxMenu]::Text($sub,$j)
    $ss=[CwxMenu]::GetMenuState($sub,[uint32]$j,0x400)
    $ssub=[CwxMenu]::GetSubMenu($sub,$j)
    $rows+=[ordered]@{Level=2;Parent=$txt;Index=$j;Text=$st;State=$ss;SubMenu=($ssub -ne [IntPtr]::Zero);SubHandle=$ssub.ToInt64()}
   }
  }
 }
}
$rows|ConvertTo-Json -Depth 5|Set-Content "$b\menu-dump.json" -Encoding UTF8
Write-Output ('menu_items=' + $rows.Count)
