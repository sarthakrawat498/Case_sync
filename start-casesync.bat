@echo off
title CaseSync - Full Stack Launcher
color 0A

echo.
echo ================================
echo    CaseSync Full Stack Launcher
echo ================================
echo.
echo Starting backend and frontend services...
echo.

REM Get the directory where this batch file is located
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

REM Check if backend directory exists
if not exist "backend" (
    echo ❌ ERROR: Backend directory not found!
    echo Make sure you're running this from the project root directory.
    pause
    exit /b 1
)

REM Check if frontend directory exists
if not exist "frontend" (
    echo ❌ ERROR: Frontend directory not found!
    echo Make sure you're running this from the project root directory.
    pause
    exit /b 1
)

REM Check if backend virtual environment exists
if not exist "backend\venv\Scripts\activate.bat" (
    echo ❌ ERROR: Backend virtual environment not found!
    echo Please run: cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if frontend node_modules exists
if not exist "frontend\node_modules" (
    echo ⚠️  WARNING: Frontend dependencies not installed!
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    if errorlevel 1 (
        echo ❌ ERROR: Failed to install frontend dependencies!
        pause
        exit /b 1
    )
    cd ..
    echo ✅ Frontend dependencies installed successfully!
    echo.
)

echo 🚀 Starting CaseSync services...
echo.

REM Start backend server in new window
echo 📡 Starting Backend Server (FastAPI)...
start "CaseSync Backend" cmd /k "cd /d "%PROJECT_DIR%backend" && venv\Scripts\activate && echo Backend server starting... && python main.py"

REM Wait a moment for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start frontend server in new window  
echo 🌐 Starting Frontend Server (Vite)...
start "CaseSync Frontend" cmd /k "cd /d "%PROJECT_DIR%frontend" && echo Frontend server starting... && npm run dev"

REM Wait for frontend to start
echo Waiting for frontend to initialize...
timeout /t 8 /nobreak >nul

echo.
echo ✅ Services are starting up!
echo.
echo 📋 Service URLs:
echo    Backend API: http://localhost:8000
echo    Frontend:    http://localhost:5173  
echo    API Docs:    http://localhost:8000/docs
echo.
echo 🌐 Opening application in browser...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo ================================
echo    CaseSync Services Running
echo ================================
echo.
echo 📊 Service Status:
echo    ✅ Backend:  http://localhost:8000
echo    ✅ Frontend: http://localhost:5173
echo.
echo 🔧 Management Commands:
echo    - Check backend health: curl http://localhost:8000/health
echo    - View API documentation: http://localhost:8000/docs
echo    - Stop services: Close the terminal windows
echo.
echo Press any key to open service monitoring dashboard...
pause >nul

REM Open monitoring URLs
start http://localhost:8000/docs
start http://localhost:8000/health

echo.
echo 🎉 CaseSync is now running!
echo.
echo To stop all services:
echo 1. Close the backend terminal window
echo 2. Close the frontend terminal window  
echo 3. Or press Ctrl+C in each window
echo.
echo Happy coding! 🚀
echo.
pause