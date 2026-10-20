$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$b='C:\hwk-modern\run-20261019-cwx'
$procs=@(Get-Process XWall -ErrorAction SilentlyContinue)
if($procs.Count -ne 1){throw ('Expected exactly one XWall, found ' + $procs.Count)}
$p=$procs[0]
if($p.Path -ne 'C:\hwk-modern\HWK-000041-B02-01\client\XWall.exe' -or $p.SessionId -ne 4){throw 'Process identity changed'}
if($p.MainWindowTitle -notlike '*a.cwx*'){throw 'Expected document a.cwx to be active'}

Add-Type @'
using System;using System.Runtime.InteropServices;using System.Text;using System.Collections.Generic;
public class CwxIn2 {
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
 [DllImport("user32.dll")] public static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);
 [DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int n);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern int GetWindowTextW(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll")] public static extern int GetClassNameW(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
 [DllImport("user32.dll")] public static extern IntPtr GetWindow(IntPtr h, uint cmd);
 [DllImport("user32.dll")] public static extern IntPtr GetParent(IntPtr h);
 [DllImport("user32.dll")] public static extern int GetDlgCtrlID(IntPtr h);
 [DllImport("user32.dll")] public static extern int SendMessageW(IntPtr h, uint msg, IntPtr w, IntPtr l);
 public delegate bool EnumProc(IntPtr h, IntPtr l);
 [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
 [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr parent, EnumProc cb, IntPtr l);
 [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
 public static List<string> Top(uint want) {
  List<string> rows = new List<string>();
  EnumWindows((h, l) => {
   uint pid; GetWindowThreadProcessId(h, out pid);
   if (pid != want || !IsWindowVisible(h)) return true;
   StringBuilder t = new StringBuilder(512); GetWindowTextW(h, t, 512);
   StringBuilder c = new StringBuilder(256); GetClassNameW(h, c, 256);
   RECT r; GetWindowRect(h, out r);
   rows.Add(string.Format("{0}|{1}|{2}|{3},{4},{5},{6}|owner={7}|parent={8}", h.ToInt64(), c.ToString(), t.ToString(), r.Left, r.Top, r.Right - r.Left, r.Bottom - r.Top, GetWindow(h, 4).ToInt64(), GetParent(h).ToInt64()));
   return true;
  }, IntPtr.Zero);
  return rows;
 }
 public static List<string> Kids(IntPtr parent) {
  List<string> rows = new List<string>();
  EnumChildWindows(parent, (h, l) => {
   StringBuilder t = new StringBuilder(512); GetWindowTextW(h, t, 512);
   StringBuilder c = new StringBuilder(256); GetClassNameW(h, c, 256);
   RECT r; GetWindowRect(h, out r);
   rows.Add(string.Format("{0}|{1}|{2}|id={3}|{4},{5},{6},{7}", h.ToInt64(), c.ToString(), t.ToString(), GetDlgCtrlID(h), r.Left, r.Top, r.Right - r.Left, r.Bottom - r.Top));
   return true;
  }, IntPtr.Zero);
  return rows;
 }
}
'@
[void][CwxIn2]::ShowWindow([CwxIn2]::GetConsoleWindow(),0)
[void][CwxIn2]::SetForegroundWindow($p.MainWindowHandle)
Start-Sleep -Milliseconds 500
# Close any menu that is currently open, then reopen the File menu deterministically.
[Windows.Forms.SendKeys]::SendWait('{ESC}')
Start-Sleep -Milliseconds 800
[void][CwxIn2]::SetCursorPos(18,35)
[CwxIn2]::mouse_event(2,0,0,0,[UIntPtr]::Zero)
[CwxIn2]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
Start-Sleep -Milliseconds 1500
$before=[CwxIn2]::Top([uint32]$p.Id)
# 另存为(A) mnemonic inside the open File menu.
[Windows.Forms.SendKeys]::SendWait('a')
Start-Sleep -Seconds 3
$after=[CwxIn2]::Top([uint32]$p.Id)
$kids=@()
foreach($row in $after){
 $handle=[IntPtr][int64]($row.Split('|')[0])
 if($row -match '\|#32770\|'){ $kids+=@{dialog=$row;controls=[CwxIn2]::Kids($handle)} }
}
$s=[Windows.Forms.SystemInformation]::VirtualScreen
$bmp=New-Object Drawing.Bitmap($s.Width,$s.Height);$g=[Drawing.Graphics]::FromImage($bmp);$g.CopyFromScreen($s.X,$s.Y,0,0,$bmp.Size);$bmp.Save("$b\saveas-dialog.png");$g.Dispose();$bmp.Dispose()
[ordered]@{
 At=(Get-Date).ToUniversalTime().ToString('o')
 Session=[Diagnostics.Process]::GetCurrentProcess().SessionId
 Process=@($p|Select-Object Id,Path,SessionId,MainWindowTitle,Responding)
 Foreground=([CwxIn2]::GetForegroundWindow()).ToInt64()
 BeforeMenu=$before
 AfterKey=$after
 Dialogs=$kids
 Files=@(Get-ChildItem $b -Filter *.cwx -Force|Select-Object Name,Length,LastWriteTime)
}|ConvertTo-Json -Depth 6|Set-Content "$b\saveas-dialog.json" -Encoding UTF8
