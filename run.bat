@echo off
title TechSoul AI Audit Suite
color 0A

echo ========================================================
echo        TechSoul AI Website Audit Suite
echo ========================================================
echo.

:: Change to script directory
cd /d "%~dp0"

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from https://www.python.org/
    echo (Make sure to check "Add Python to PATH" during setup)
    echo.
    pause
    exit /b 1
)

:: 2. Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js from https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...

:: 3. Install Python dependencies if needed
if not exist "backend\venv" (
    echo Creating Python virtual environment...
    python -m venv backend\venv
)

call backend\venv\Scripts\activate.bat
pip install -r backend\requirements.txt --quiet --disable-pip-version-check

:: 4. Install Node dependencies if needed
if not exist "frontend\node_modules" (
    echo Installing frontend Node.js packages...
    cd frontend
    call npm install --quiet
    cd ..
)

echo [2/3] Launching FastAPI Backend on http://localhost:8000...
start /min "TechSoul Backend" cmd /c "backend\venv\Scripts\activate.bat && cd backend && python main.py"

echo [3/3] Launching Next.js App on http://localhost:3000...
start /min "TechSoul Frontend" cmd /c "cd frontend && npm run dev"

echo.
echo Waiting for servers to initialize...
timeout /t 4 /nobreak >nul

echo Opening browser at http://localhost:3000...
start http://localhost:3000

echo.
echo ========================================================
echo   TechSoul Audit Suite is running!
echo   Do not close this window while using the application.
echo ========================================================
echo.
pause
