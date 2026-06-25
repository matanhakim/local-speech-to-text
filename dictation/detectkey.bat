@echo off
chcp 65001 >nul
title Detect dictation key (Esc to quit)
python "%~dp0detectkey.py"
pause
