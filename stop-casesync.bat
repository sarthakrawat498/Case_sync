@echo off
title CaseSync - Service Stopper
color 0C

echo.
echo ================================
echo    CaseSync Service Stopper
echo ================================
echo.

echo 🛑 Stopping CaseSync services...
echo.

REM Kill Python processes (FastAPI backend)
echo Stopping Backend (Python/FastAPI)...
taskkill /f /im python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend stopped
) else (
    echo ⚠️  No backend processes found
)

REM Kill Node processes (Vite frontend)
echo Stopping Frontend (Node.js/Vite)...
taskkill /f /im node.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend stopped
) else (
    echo ⚠️  No frontend processes found
)

REM Kill any remaining CaseSync processes by window title
taskkill /f /fi "WindowTitle eq CaseSync Backend*" >nul 2>&1
taskkill /f /fi "WindowTitle eq CaseSync Frontend*" >nul 2>&1

echo.
echo 🔍 Checking for remaining processes...
netstat -ano | findstr ":8000" >nul
if %errorlevel% equ 0 (
    echo ⚠️  Port 8000 (Backend) may still be in use
    echo Running: netstat -ano | findstr ":8000"
    netstat -ano | findstr ":8000"
) else (
    echo ✅ Port 8000 (Backend) is free
)

netstat -ano | findstr ":5173" >nul  
if %errorlevel% equ 0 (
    echo ⚠️  Port 5173 (Frontend) may still be in use
    echo Running: netstat -ano | findstr ":5173"
    netstat -ano | findstr ":5173"
) else (
    echo ✅ Port 5173 (Frontend) is free
)

echo.
echo ================================
echo    All CaseSync services stopped
echo ================================
echo.
pause