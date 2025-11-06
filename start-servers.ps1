# StaffAlloc Development Servers Startup Script
# This script starts both the backend (FastAPI) and frontend (React) servers

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  StaffAlloc - Development Servers Startup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Get the script's directory (project root)
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# Define paths
$backendPath = Join-Path $projectRoot "Artifacts\backend"
$reactappPath = Join-Path $projectRoot "reactapp"

# Check if paths exist
if (-not (Test-Path $backendPath)) {
    Write-Host "ERROR: Backend directory not found at $backendPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $reactappPath)) {
    Write-Host "ERROR: Frontend directory not found at $reactappPath" -ForegroundColor Red
    exit 1
}

Write-Host "Starting backend server..." -ForegroundColor Yellow
Write-Host "Backend path: $backendPath" -ForegroundColor Gray
Write-Host ""

# Start backend in a new PowerShell window
$backendCommand = "cd '$backendPath'; & '.\venv\Scripts\python.exe' -m uvicorn app.main:app --reload --port 8000"
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $backendCommand -WindowStyle Normal

# Wait a moment for the backend to start
Start-Sleep -Seconds 3

Write-Host "Starting frontend server..." -ForegroundColor Yellow
Write-Host "Frontend path: $reactappPath" -ForegroundColor Gray
Write-Host ""

# Start frontend in a new PowerShell window
$frontendCommand = "cd '$reactappPath'; npm run dev"
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $frontendCommand -WindowStyle Normal

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  Servers started successfully!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs:     http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host "Frontend:     http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "TIP: Both servers are running in separate windows." -ForegroundColor Gray
Write-Host "     Close either window to stop that server." -ForegroundColor Gray
Write-Host ""

