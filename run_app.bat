@echo off
REM ============================================================
REM Bignan Mancha OMR Reader - Easy Launcher for Windows
REM ============================================================
REM This script will automatically set up and run the application
REM for users who don't have Python installed or configured.
REM ============================================================

REM Check for uninstall request
if "%1"=="--uninstall" goto :uninstall
if "%1"=="-u" goto :uninstall

echo.
echo ============================================================
echo   Bignan Mancha OMR Reader - Launcher
echo ============================================================
echo.
echo   To uninstall, run: uninstall.bat
echo   Or run: run_app.bat --uninstall
echo.

REM ============================================================
REM Python Detection and Setup
REM ============================================================

REM First, check if bundled Python exists (portable Python)
set PYTHON_CMD=
if exist "python\python.exe" (
    set PYTHON_CMD=python\python.exe
    echo [OK] Found bundled Python (portable)
    python\python.exe --version
    goto :python_found
)

REM Check if system Python is available - try multiple commands (keep simple and reliable)
echo [INFO] Checking for Python installation...
set PYTHON_CMD=

echo [DEBUG] Trying 'python' command...
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    echo [OK] Found system Python
    python --version
    goto :python_found
)

echo [DEBUG] Trying 'python3' command...
python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    echo [OK] Found Python 3
    python3 --version
    goto :python_found
)

echo [DEBUG] Trying 'py -3' launcher...
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py -3
    echo [OK] Found Python via launcher
    py -3 --version
    goto :python_found
)

echo [DEBUG] No Python found via standard methods
set PYTHON_CMD=

REM Python not found - offer to download and set up automatically
echo.
echo [SETUP] Python is not installed or not in PATH.
echo.
echo Would you like to automatically download and set up Python?
echo This will download Python 3.12 embeddable (portable, no installation needed)
echo.
choice /C YN /M "Download Python automatically (Y/N)"
if errorlevel 2 goto :python_not_found
if errorlevel 1 goto :download_python
goto :python_not_found

:download_python
echo.
echo [SETUP] Downloading Python 3.12 embeddable...
echo This may take a few minutes depending on your internet speed...
echo.

REM Create python directory
if not exist "python" mkdir python

REM Download Python embeddable (Windows 64-bit)
REM Using Python 3.12.7 embeddable as it's stable and widely compatible
set PYTHON_URL=https://www.python.org/ftp/python/3.12.7/python-3.12.7-embed-amd64.zip
set PYTHON_ZIP=python-embed.zip

echo Downloading from: %PYTHON_URL%
echo.

REM Try using PowerShell to download (available on Windows 7+)
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%'}" >nul 2>&1

if not exist "%PYTHON_ZIP%" (
    echo [ERROR] Failed to download Python automatically.
    echo.
    echo Please download Python manually:
    echo 1. Go to: https://www.python.org/downloads/
    echo 2. Download Python 3.9 or later
    echo 3. Install it and check "Add Python to PATH"
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

echo [OK] Python downloaded successfully
echo [SETUP] Extracting Python...

REM Extract Python (requires PowerShell or 7-Zip)
powershell -Command "Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath 'python' -Force" >nul 2>&1

if not exist "python\python.exe" (
    echo [ERROR] Failed to extract Python.
    echo Please extract %PYTHON_ZIP% manually to the 'python' folder.
    pause
    exit /b 1
)

REM Clean up zip file
del "%PYTHON_ZIP%" >nul 2>&1

REM Enable pip in embeddable Python
echo [SETUP] Configuring Python...
if not exist "python\python312._pth.bak" (
    copy "python\python312._pth" "python\python312._pth.bak" >nul 2>&1
)
echo import site > python\python312._pth
echo. >> python\python312._pth

REM Download get-pip.py
echo [SETUP] Setting up pip...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'python\get-pip.py'}" >nul 2>&1

if exist "python\get-pip.py" (
    python\python.exe python\get-pip.py --quiet
    if errorlevel 1 (
        echo [WARNING] Failed to install pip automatically
        echo You may need to install pip manually later
    )
    del python\get-pip.py >nul 2>&1
)

set PYTHON_CMD=python\python.exe
echo [OK] Python is ready to use
python\python.exe --version
goto :python_found

:python_not_found
echo.
echo [INFO] Python setup cancelled.
echo.
echo To install Python manually:
echo 1. Go to: https://www.python.org/downloads/
echo 2. Download Python 3.9 or later
echo 3. Install it and check "Add Python to PATH"
echo 4. Run this script again
echo.
pause
exit /b 1

:python_found
REM Validate that Python was actually found
if "%PYTHON_CMD%"=="" (
    echo.
    echo [ERROR] Python detection failed - PYTHON_CMD is empty
    echo.
    echo Please ensure Python is installed and in your PATH, then re-run this script.
    echo.
    pause
    exit /b 1
)

REM Use the detected Python command
REM Store the command - for commands with spaces like "py -3", we'll handle them specially
set PYTHON=%PYTHON_CMD%
REM Ensure Python output is unbuffered so logs appear immediately
set PYTHONUNBUFFERED=1

REM Verify Python actually works by testing the command
echo [DEBUG] Testing Python command: %PYTHON%
REM Check if command contains spaces (like "py -3")
echo %PYTHON_CMD% | findstr /C:" " >nul
if not errorlevel 1 (
    REM Command has spaces - use it directly without quotes
    %PYTHON_CMD% --version >nul 2>&1
    set PYTHON_EXEC=%PYTHON_CMD%
) else (
    REM Simple command - use directly
    %PYTHON_CMD% --version >nul 2>&1
    set PYTHON_EXEC=%PYTHON_CMD%
)
if errorlevel 1 (
    echo [ERROR] Python command '%PYTHON_CMD%' is not working
    echo Please check your Python installation.
    echo.
    echo Troubleshooting:
    echo 1. Try running: python --version
    echo 2. Try running: py -3 --version  
    echo 3. Make sure Python is installed and in PATH
    echo 4. Check if Python is in: C:\Python* or C:\Program Files\Python*
    echo.
    pause
    exit /b 1
)
echo [DEBUG] Python command verified successfully

REM If using bundled Python, add it to PATH for this session
if "%PYTHON_CMD%"=="python\python.exe" (
    rem Use safe quoting so existing PATH entries with parentheses/spaces don't break the batch block
    rem Check if python directory exists before adding to PATH
    if exist "python\python.exe" (
        set "PATH=%CD%\python;%CD%\python\Scripts;%PATH%"
    ) else (
        echo [WARNING] Bundled Python directory not found, skipping PATH update
    )
)

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
    echo [DEBUG] Running: %PYTHON_EXEC% -m venv venv
    %PYTHON_EXEC% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        echo [DEBUG] Python command used: %PYTHON_EXEC%
        echo [DEBUG] Please verify Python is installed correctly.
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
%PYTHON_EXEC% -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo [SETUP] Installing dependencies (this may take a few minutes)...
    echo.
    %PYTHON_EXEC% -m pip install --upgrade pip
    %PYTHON_EXEC% -m pip install -r requirements.txt
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
%PYTHON_EXEC% -c "import cv2" >nul 2>&1
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

%PYTHON_EXEC% main.py
set APP_EXIT_CODE=%ERRORLEVEL%

echo.
echo ============================================================
echo   Application has exited with code %APP_EXIT_CODE%.
echo   Review any log messages above.
echo   Press any key to close this window.
echo ============================================================
echo.
pause >nul
exit /b %APP_EXIT_CODE%

REM Uninstall section
:uninstall
if exist "uninstall.bat" (
    call uninstall.bat
    exit /b 0
) else (
    echo [ERROR] uninstall.bat not found.
    echo Please run uninstall.bat directly.
    pause
    exit /b 1
)

