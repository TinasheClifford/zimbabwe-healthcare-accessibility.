@echo off
setlocal
cd /d "%~dp0"
set "HEALTH_ENV=%USERPROFILE%\healthcare-app-env"
if not exist "%HEALTH_ENV%\Scripts\python.exe" (
    python -m venv "%HEALTH_ENV%"
    if errorlevel 1 goto failed
)
"%HEALTH_ENV%\Scripts\python.exe" -m pip install --timeout 120 --retries 10 -r requirements.txt
if errorlevel 1 goto failed
echo Setup complete. Double-click start_windows.bat to launch the dashboard.
pause
exit /b 0
:failed
echo Setup failed. Read the error above and the README troubleshooting instructions.
pause
exit /b 1
