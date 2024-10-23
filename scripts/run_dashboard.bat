@echo off
title Dashboard Monitor

:: Change to the scripts directory where this batch file is located
cd /d "%~dp0"

:: Then move up and into the app directory where streamlit_check.py is
cd ..\app

:check_process
:: Check if Python/Streamlit is running
tasklist | find "python.exe" > nul
if errorlevel 1 (
    echo Restarting Streamlit...
    start /B streamlit run streamlit_check.py --server.address 0.0.0.0
)

:: Check internet connection
ping 8.8.8.8 -n 1 > nul
if errorlevel 1 (
    echo Internet down, waiting...
    timeout /t 60
)

:: Optional: Log to the logs directory
echo %date% %time%: Dashboard running >> ..\logs\status.log

timeout /t 300
goto check_process