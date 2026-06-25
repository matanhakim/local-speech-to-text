@echo off
chcp 65001 >nul
call "%~dp0stop.bat"
ping -n 2 127.0.0.1 >nul
wscript "%~dp0start_hidden.vbs"
echo Dictation restarted (hidden in background).
