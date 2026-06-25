@echo off
chcp 65001 >nul
title Voice Dictation (tap ` to dictate, Ctrl+Alt+` to toggle on/off)
python "%~dp0dictate.py"
pause
