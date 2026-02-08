@echo off
cd /d %~dp0

echo Activating virtual environment...
call venv\Scripts\activate

echo Starting Robot 2...
python robots\robot2.py

pause
