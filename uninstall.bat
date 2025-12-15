@echo off
REM ============================================================
REM Bignan Mancha OMR Reader - Uninstaller
REM ============================================================
REM This script helps remove the application and all its components
REM ============================================================

echo.
echo ============================================================
echo   Bignan Mancha OMR Reader - Uninstaller
echo ============================================================
echo.

REM Check if we're in the right directory
if not exist "main.py" (
    echo [ERROR] main.py not found. Please run this script from the application folder.
    pause
    exit /b 1
)

echo This will help you remove:
echo   1. Virtual environment (venv folder)
echo   2. Bundled Python (python folder - if auto-downloaded)
echo   3. Temporary files and caches
echo.
echo NOTE: This will NOT remove:
echo   - System Python (if installed separately)
echo   - Application source files (you can delete the folder manually)
echo   - Files in success/error folders
echo.

choice /C YN /M "Do you want to proceed with cleanup (Y/N)"
if errorlevel 2 goto :cancel
if errorlevel 1 goto :start_cleanup

:start_cleanup
echo.
echo ============================================================
echo   Starting Cleanup...
echo ============================================================
echo.

REM 1. Remove virtual environment
if exist "venv" (
    echo [1/3] Removing virtual environment...
    rmdir /s /q venv 2>nul
    if exist "venv" (
        echo [WARNING] Could not fully remove venv folder. You may need to delete it manually.
    ) else (
        echo [OK] Virtual environment removed
    )
) else (
    echo [1/3] No virtual environment found (skipped)
)

REM 2. Remove bundled Python (only if it was auto-downloaded)
if exist "python" (
    echo.
    echo [2/3] Found bundled Python folder.
    choice /C YN /M "Remove bundled Python (downloaded automatically) (Y/N)"
    if errorlevel 2 (
        echo [SKIP] Keeping bundled Python
    ) else (
        echo [2/3] Removing bundled Python...
        rmdir /s /q python 2>nul
        if exist "python" (
            echo [WARNING] Could not fully remove python folder. You may need to delete it manually.
        ) else (
            echo [OK] Bundled Python removed
        )
    )
) else (
    echo [2/3] No bundled Python found (skipped)
)

REM 3. Clean up temporary files and caches
echo.
echo [3/3] Cleaning up temporary files...
set CLEANED=0

REM Remove __pycache__ folders
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        rmdir /s /q "%%d" 2>nul
        set /a CLEANED+=1
    )
)

REM Remove .pyc files
for /r . %%f in (*.pyc) do (
    if exist "%%f" (
        del /q "%%f" 2>nul
        set /a CLEANED+=1
    )
)

REM Remove .pyo files
for /r . %%f in (*.pyo) do (
    if exist "%%f" (
        del /q "%%f" 2>nul
        set /a CLEANED+=1
    )
)

if %CLEANED% GTR 0 (
    echo [OK] Removed %CLEANED% temporary files/folders
) else (
    echo [OK] No temporary files found
)

REM 4. Optional: Remove build artifacts
echo.
if exist "build" (
    choice /C YN /M "Remove build folder (Y/N)"
    if errorlevel 1 (
        echo Removing build folder...
        rmdir /s /q build 2>nul
        echo [OK] Build folder removed
    )
)

if exist "dist" (
    choice /C YN /M "Remove dist folder (Y/N)"
    if errorlevel 1 (
        echo Removing dist folder...
        rmdir /s /q dist 2>nul
        echo [OK] Dist folder removed
    )
)

REM 5. Summary
echo.
echo ============================================================
echo   Cleanup Complete!
echo ============================================================
echo.
echo The following have been removed:
if not exist "venv" echo   [OK] Virtual environment
if not exist "python" echo   [OK] Bundled Python
echo   [OK] Temporary files and caches
echo.
echo To completely remove the application:
echo   1. Close this window
echo   2. Delete the entire application folder
echo.
echo NOTE: If you want to keep the application but start fresh:
echo   - Just delete the 'venv' and 'python' folders
echo   - Run run_app.bat again to set up fresh
echo.
goto :end

:cancel
echo.
echo Cleanup cancelled. No changes made.
echo.

:end
pause


