@echo off
echo ========================================
echo Starting ML Project - Backend and Frontend
echo ========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Start backend in a new window
echo Starting Backend Server...
start "ML-Project-Backend" cmd /k "cd /d %SCRIPT_DIR%backend && set PYTHONPATH=%CD% && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

REM Wait a bit for backend to start
ping 127.0.0.1 -n 4 >nul

REM Start frontend in a new window
echo Starting Frontend Server...
start "ML-Project-Frontend" cmd /k "cd /d %SCRIPT_DIR%frontend && npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo ========================================
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit this window (servers will continue running)...
pause >nul
