CaseSync - Batch File Automation
==================================

This folder contains batch files to automate running your full-stack CaseSync application.

📁 BATCH FILES:
--------------

🛠️  setup-casesync.bat
   - First-time setup for the project
   - Installs all Python and Node.js dependencies
   - Creates virtual environment
   - Sets up .env configuration
   - Run this ONCE before using the application

🚀 start-casesync.bat  
   - Complete launcher with full logging
   - Starts backend (FastAPI) and frontend (Vite)
   - Opens browser automatically
   - Shows service status and URLs
   - Best for development and demonstration

⚡ quick-start.bat
   - Minimal launcher for development
   - Starts services with minimal output
   - Faster startup, less verbose
   - Good for daily development workflow

🛑 stop-casesync.bat
   - Stops all CaseSync services
   - Kills Python and Node.js processes
   - Checks if ports are freed
   - Use when services don't stop properly

📋 USAGE INSTRUCTIONS:
---------------------

1. FIRST TIME SETUP:
   - Double-click: setup-casesync.bat
   - Follow the prompts
   - Edit .env file with your Deepgram API key

2. DAILY DEVELOPMENT:
   - Double-click: start-casesync.bat (full experience)
   - OR: quick-start.bat (faster startup)

3. STOPPING SERVICES:
   - Close the terminal windows
   - OR: double-click stop-casesync.bat

🌐 SERVICE URLS:
---------------
- Frontend Application: http://localhost:5173
- Backend API:         http://localhost:8000  
- API Documentation:   http://localhost:8000/docs
- Health Check:        http://localhost:8000/health

🔧 REQUIREMENTS:
---------------
- Python 3.10+
- Node.js 18+
- Deepgram API Key (from console.deepgram.com)

💡 TIPS:
-------
- Run setup-casesync.bat only once after downloading the project
- Use start-casesync.bat for demos and presentations
- Use quick-start.bat for daily development
- If ports are busy, run stop-casesync.bat first

🛠️ TROUBLESHOOTING:
------------------
- Port 8000 already in use: Run stop-casesync.bat
- Missing dependencies: Run setup-casesync.bat again
- API errors: Check DEEPGRAM_API_KEY in backend/.env
- Frontend won't start: Check if Node.js is installed

🎉 Happy coding with CaseSync!