@echo off
cd /d "%~dp0"
title midiplay — MuseScore Bridge
call .venv\Scripts\activate.bat
python run.py
pause
