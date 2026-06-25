@echo off
chcp 65001 >nul
if exist "%~dp0dictate.pid" (
  for /f "usebackq tokens=*" %%i in ("%~dp0dictate.pid") do taskkill /PID %%i /F >nul 2>&1
  del "%~dp0dictate.pid" >nul 2>&1
  echo Dictation stopped.
) else (
  echo No dictate.pid found - daemon not running.
)
