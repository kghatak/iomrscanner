@echo off
REM ============================================================
REM Bignan Mancha OMR Reader - Easy Launcher for Windows
REM ============================================================
REM This script will automatically set up and run the application
REM for users who don't have Python installed or configured.
REM ============================================================

echo.
echo ============================================================
echo   Bignan Mancha OMR Reader - Launcher
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo.
    echo Please install Python 3.9 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version

REM Check if we're in the right directory
if not exist "main.py" (
    echo [ERROR] main.py not found. Please run this script from the application folder.
    pause
    exit /b 1
)

REM Check if virtual environment exists, create if not
if not exist "venv" (
    echo.
    echo [SETUP] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo [SETUP] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Check if requirements are installed
echo.
echo [SETUP] Checking dependencies...
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo [SETUP] Installing dependencies (this may take a few minutes)...
    echo.
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies.
        echo Please check your internet connection and try again.
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies are already installed
)

REM Check for optional dependencies
echo.
echo [INFO] Checking optional dependencies...
python -c "import cv2" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] OpenCV not found. Some features may not work.
    echo You can install it later with: pip install opencv-python
) else (
    echo [OK] OpenCV is installed
)

REM Run the application
echo.
echo ============================================================
echo   Starting Bignan Mancha OMR Reader...
echo ============================================================
echo.
echo The application window should open shortly.
echo You can close this window after the application starts.
echo.
echo ============================================================
echo.

python main.py

REM If application exits, pause to see any error messages
if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with an error.
    echo Please check the error messages above.
    echo.
    pause
)

