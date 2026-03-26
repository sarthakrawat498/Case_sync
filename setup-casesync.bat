@echo off
title CaseSync - First Time Setup
color 0E

echo.
echo ================================
echo    CaseSync First Time Setup
echo ================================
echo.
echo This will install all dependencies for both backend and frontend.
echo Make sure you have Python 3.10+ and Node.js installed.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul
echo.

set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"

echo 🔧 Setting up CaseSync project...
echo.

REM Check Python
echo 📋 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Python not found! Please install Python 3.10 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo ✅ Python is installed
echo.

REM Check Node.js
echo 📋 Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERROR: Node.js not found! Please install Node.js 18+ or higher.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)
node --version
npm --version
echo ✅ Node.js is installed
echo.

REM Setup Backend
echo 🐍 Setting up Python Backend...
cd backend
if exist venv (
    echo Virtual environment already exists, removing...
    rmdir /s /q venv
)

echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to create virtual environment!
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to install Python dependencies!
    pause
    exit /b 1
)

echo ✅ Backend setup complete!
echo.

REM Setup Frontend  
echo ⚛️ Setting up React Frontend...
cd ..\frontend
if exist node_modules (
    echo Node modules already exist, removing...
    rmdir /s /q node_modules
)

echo Installing Node.js dependencies...
npm install
if %errorlevel% neq 0 (
    echo ❌ ERROR: Failed to install Node.js dependencies!
    pause
    exit /b 1
)

echo ✅ Frontend setup complete!
echo.

cd ..

REM Check .env file
echo 🔐 Checking environment configuration...
if not exist "backend\.env" (
    echo Creating .env file from sample...
    if exist "backend\.env.sample" (
        copy "backend\.env.sample" "backend\.env"
        echo ⚠️  IMPORTANT: Edit backend\.env and add your DEEPGRAM_API_KEY
    ) else (
        echo ❌ WARNING: No .env.sample found! You'll need to create backend\.env manually.
    )
) else (
    echo ✅ Environment file exists
)

echo.
echo ================================
echo    Setup Complete! 
echo ================================
echo.
echo 📋 Next Steps:
echo 1. Edit backend\.env and set your DEEPGRAM_API_KEY
echo    - Get API key from: https://console.deepgram.com
echo    - Add: DEEPGRAM_API_KEY=your_key_here
echo.
echo 2. Run the application:
echo    - Double-click: start-casesync.bat
echo    - Or run: quick-start.bat
echo.
echo 🌐 Application URLs (after starting):
echo    - Frontend: http://localhost:5173
echo    - Backend:  http://localhost:8000  
echo    - API Docs: http://localhost:8000/docs
echo.
echo Press any key to open the .env file for editing...
pause >nul

REM Open .env file for editing
if exist "backend\.env" (
    start notepad "backend\.env"
)

echo.
echo 🎉 CaseSync is ready to use!
echo Run start-casesync.bat to launch the application.
echo.
pause