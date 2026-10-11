' Runs a PowerShell script with no console window (the scheduled tasks call this).
' Usage: wscript.exe run-hidden.vbs "C:\path\to\script.ps1"
Set shell = CreateObject("WScript.Shell")
shell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File """ & WScript.Arguments(0) & """", 0, True
