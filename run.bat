@echo off
title TechSoul AI Audit Suite
color 0A
setlocal enabledelayedexpansion

echo ========================================================
echo        TechSoul AI Website Audit Suite Launcher
echo ========================================================
echo.

:: 1. Navigate to script folder
cd /d "%~dp0"

:: 2. Find Python executable
set "PY_CMD="
where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python"
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        set "PY_CMD=py"
    )
)

if "%PY_CMD%"==" " (
    echo [ERROR] Python was not found on your system.
    echo Please install Python 3.10+ from https://www.python.org/
    echo ** IMPORTANT ** Check the box "Add Python to environment variables" during setup.
    echo.
    pause
    exit /b 1
)

echo [✓] Python found: %PY_CMD%
%PY_CMD% --version

:: 3. Find Node.js / NPM executable
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js was not found on your system.
    echo Please install Node.js (LTS version) from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [✓] Node.js found:
node --version

echo.
echo ========================================================
echo  Step 1: Setting up Python Environment
echo ========================================================

:: Create virtual environment if it doesn't exist
if not exist "backend\venv\Scripts\python.exe" (
    echo Creating virtual environment in backend\venv...
    %PY_CMD% -m venv backend\venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

set "VENV_PY=%~dp0backend\venv\Scripts\python.exe"
set "VENV_PIP=%~dp0backend\venv\Scripts\pip.exe"

echo Installing/Updating Python packages...
"%VENV_PIP%" install -r backend\requirements.txt --disable-pip-version-check

echo.
echo ========================================================
echo  Step 2: Setting up Frontend Environment
echo ========================================================

if not exist "frontend\node_modules" (
    echo Installing frontend packages (this may take 1-2 minutes)...
    cd /d "%~dp0frontend"
    call npm install
    cd /d "%~dp0"
)

echo.
echo ========================================================
echo  Step 3: Launching Application Servers
echo ========================================================

echo Starting FastAPI Backend (Port 8000)...
start "TechSoul-Backend" cmd /k "cd /d "%~dp0backend" && "%VENV_PY%" main.py"

echo Starting Next.js Frontend (Port 3000)...
start "TechSoul-Frontend" cmd /k "cd /d "%~dp0frontend" && call npm run dev"

echo.
echo Waiting 5 seconds for servers to start...
timeout /t 5 >nul

echo.
echo ========================================================
echo.
echo    SUCCESS! APP IS LIVE AT:
echo.
echo    >>>>  http://localhost:3000  <<<<
echo    >>>>  http://127.0.0.1:3000  <<<<
echo.
echo    Backend API: http://localhost:8000
echo.
echo ========================================================
echo.
echo Opening browser automatically...
start http://localhost:3000

echo.
echo Keep this console window open while using the application.
echo To stop all servers when done, double-click stop.bat.
echo.
pause
