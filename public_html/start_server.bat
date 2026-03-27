@echo off
REM Start IVYSTUDY development server (Windows)

echo Starting IVYSTUDY development server...

REM Check if we're in the right directory
if not exist "dev_server.py" (
    echo Error: Please run this script from the public_html directory
    echo Expected to find dev_server.py in current directory
    pause
    exit /b 1
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3 is required but not found
    echo Please install Python 3 to run the development server
    pause
    exit /b 1
)

REM Start the server
echo Starting server on http://localhost:8080
echo Press Ctrl+C to stop
python dev_server.py