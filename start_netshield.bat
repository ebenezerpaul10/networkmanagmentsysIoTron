@echo off
REM ========================================================
REM NetShield-IoT: Windows One-Click Launcher
REM ========================================================

echo ==========================================================
echo         🛡️  STARTING NETSHIELD-IoT FOR WINDOWS...
echo ==========================================================

cd /d "%~dp0"

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.8+ from https://python.org and check "Add to PATH".
    pause
    exit /b 1
)

REM Launch via universal launcher
python start_netshield.py
pause
