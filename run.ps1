# CSR App - Start Frontend and Backend (PowerShell)

Write-Host "==========================================" -ForegroundColor Green
Write-Host "CSR App - Starting Frontend and Backend" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Check if Node.js is installed
try {
    $null = node --version
} catch {
    Write-Host "ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Python is installed
try {
    $null = python --version
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 1: Setting up Python virtual environment..." -ForegroundColor Yellow

if (-Not (Test-Path ".\venv")) {
    python -m venv venv
    Write-Host "Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 2: Activating Python virtual environment and installing dependencies..." -ForegroundColor Yellow

& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt

Write-Host ""
Write-Host "Step 3: Installing Node.js dependencies..." -ForegroundColor Yellow

npm install

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Starting services..." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend (Flask) will run on: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Frontend (Next.js) will run on: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop services" -ForegroundColor Yellow
Write-Host ""

# Start backend in a new PowerShell window
Write-Host "Starting Backend (Flask)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PSScriptRoot'; .\venv\Scripts\Activate.ps1; python app.py`""

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend in a new PowerShell window
Write-Host "Starting Frontend (Next.js)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PSScriptRoot'; npm run dev`""

Write-Host ""
Write-Host "Both services are starting in new windows..." -ForegroundColor Green
Write-Host ""