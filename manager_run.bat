@echo off
cd /d %~dp0

echo Activating virtual environment...
call venv\Scripts\activate

echo Starting Manager...
python -m uvicorn manager.main:app --host 0.0.0.0 --port 8000 --reload

pause
