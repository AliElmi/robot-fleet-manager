@echo off
cd /d %~dp0

echo Activating virtual environment...
call venv\Scripts\activate

echo Starting Robot 1...
python robots\robot1.py

pause
