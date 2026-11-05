@echo off
setlocal
cd /d "%~dp0"
set "HEALTH_ENV=%USERPROFILE%\healthcare-app-env"
if not exist "%HEALTH_ENV%\Scripts\python.exe" (
    echo Run setup_windows.bat first.
    pause
    exit /b 1
)
"%HEALTH_ENV%\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 pause
