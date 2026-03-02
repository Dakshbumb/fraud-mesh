@echo off
echo ========================================
echo Starting FraudMesh Platform
echo ========================================
echo.

REM Check if backend venv exists
if not exist "backend\venv" (
    echo [ERROR] Backend virtual environment not found!
    echo Please run: cd backend ^&^& python -m venv venv ^&^& venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

REM Check if frontend node_modules exists
if not exist "frontend\node_modules" (
    echo [ERROR] Frontend dependencies not installed!
    echo Please run: cd frontend ^&^& npm install
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo [WARNING] .env file not found! Copying from .env.example...
    copy .env.example .env
    echo Please edit .env and add your GEMINI_API_KEY
    pause
)

echo Starting Backend Server...
start "FraudMesh Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn main:app --reload --port 8000"

timeout /t 3 /nobreak > nul

echo Starting Frontend Server...
start "FraudMesh Frontend" cmd /k "cd frontend && npm run dev"

timeout /t 2 /nobreak > nul

echo.
echo ========================================
echo FraudMesh is starting up!
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to open the dashboard in your browser...
pause > nul

start http://localhost:5173

echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
