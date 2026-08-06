@echo off
title Stop TechSoul Suite
echo Stopping TechSoul AI Audit Suite servers...

taskkill /FI "WINDOWTITLE eq TechSoul Backend*" /F /T >nul 2>&1
taskkill /FI "WINDOWTITLE eq TechSoul Frontend*" /F /T >nul 2>&1

:: Also kill python and node processes listening on ports 8000 and 3000 if any
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /PID %%a /F >nul 2>&1

echo Done! Servers stopped.
timeout /t 2 /nobreak >nul
