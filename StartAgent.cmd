@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Create the project virtual environment first. See AgentSetup.md.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" agent_watch.py --doctor
if errorlevel 1 (
  echo Complete the setup shown above, then start this launcher again.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" agent_watch.py
pause
