@echo off
title CaseSync - Quick Start
color 0B

REM Quick development launcher - minimal output
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo Starting CaseSync...

REM Start services
start /min "CaseSync Backend" cmd /c "cd backend && venv\Scripts\activate && python main.py"
timeout /t 3 /nobreak >nul
start /min "CaseSync Frontend" cmd /c "cd frontend && npm run dev"
timeout /t 5 /nobreak >nul

echo ✅ Services started!
echo 🌐 Opening http://localhost:5173
start http://localhost:5173

exit