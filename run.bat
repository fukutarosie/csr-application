@echo off
REM CSR App - Start Frontend and Backend

echo ==========================================
echo CSR App - Starting Frontend and Backend
echo ==========================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo.
echo Step 1: Setting up Python virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo.
echo Step 2: Activating Python virtual environment and installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo Step 3: Installing Node.js dependencies...
npm install

echo.
echo ==========================================
echo Starting services...
echo ==========================================
echo.
echo Backend (Flask) will run on: http://localhost:5000
echo Frontend (Next.js) will run on: http://localhost:3000
echo.
echo Press Ctrl+C to stop all services
echo.

REM Start both servers in parallel
start "CSR App - Backend (Flask)" cmd /k "venv\Scripts\activate.bat && python app.py"
timeout /t 3 /nobreak
start "CSR App - Frontend (Next.js)" cmd /k "npm run dev"

echo.
echo Both services are starting...
pause