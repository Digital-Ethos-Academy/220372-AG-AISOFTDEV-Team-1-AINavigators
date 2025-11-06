@echo off
REM StaffAlloc Development Servers Startup Script
REM This batch file starts both the backend (FastAPI) and frontend (React) servers

cls
echo.
echo ================================================
echo   StaffAlloc - Development Servers Startup
echo ================================================
echo.

REM Get the script's directory (project root)
set projectRoot=%~dp0

REM Define paths
set backendPath=%projectRoot%Artifacts\backend
set reactappPath=%projectRoot%reactapp

REM Check if paths exist
if not exist "%backendPath%" (
    echo ERROR: Backend directory not found at %backendPath%
    pause
    exit /b 1
)

if not exist "%reactappPath%" (
    echo ERROR: Frontend directory not found at %reactappPath%
    pause
    exit /b 1
)

echo Starting backend server...
echo Backend path: %backendPath%
echo.

REM Start backend in a new window
start "StaffAlloc Backend" cmd /k "cd /d %backendPath% && venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

REM Wait a moment for the backend to start
timeout /t 3 /nobreak

echo Starting frontend server...
echo Frontend path: %reactappPath%
echo.

REM Start frontend in a new window
start "StaffAlloc Frontend" cmd /k "cd /d %reactappPath% && npm run dev"

echo.
echo ================================================
echo   Servers started successfully!
echo ================================================
echo.
echo Backend API:  http://localhost:8000
echo API Docs:     http://localhost:8000/api/docs
echo Frontend:     http://localhost:5173
echo.
echo TIP: Both servers are running in separate windows.
echo      Close either window to stop that server.
echo.
pause

