' Launch the dictation daemon hidden (no console window).
' Portable: runs dictate.py from this script's own folder, using pythonw on PATH.
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh = CreateObject("WScript.Shell")
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
sh.Run "pythonw """ & scriptDir & "\dictate.py""", 0, False
