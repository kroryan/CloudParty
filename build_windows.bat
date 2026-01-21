@echo off
REM CloudParty Build Script for Windows
REM This script builds the CloudParty executable with tray app functionality

echo.
echo ============================================================
echo   CloudParty Build Script
echo ============================================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check for pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed
    pause
    exit /b 1
)

echo [1/5] Installing dependencies...
pip install pyinstaller pystray pillow jinja2 --quiet

echo [2/5] Installing copyparty in development mode...
pip install -e . --quiet

echo [3/5] Checking icon file...
if exist cloudparty.ico (
    echo Icon file found: cloudparty.ico
) else (
    echo Creating fallback icon...
    python scripts\create_icon.py 2>nul || echo Warning: Could not create icon, continuing without...
)

echo [4/5] Building executable with PyInstaller...
pyinstaller --clean --noconfirm cloudparty.spec

echo [5/5] Copying configuration files...
if exist dist\CloudParty.exe (
    copy cloudparty.example.conf dist\ >nul
    copy cloudparty.ico dist\ >nul
    copy copyparty\web\cloudparty.css dist\ >nul 2>nul
    
    echo.
    echo ============================================================
    echo   BUILD SUCCESSFUL!
    echo ============================================================
    echo.
    echo Output: dist\CloudParty.exe
    echo.
    echo To use:
    echo   1. Copy cloudparty.example.conf to cloudparty.conf
    echo   2. Edit cloudparty.conf with your settings
    echo   3. Double-click CloudParty.exe
    echo.
    echo The application will start in the system tray.
    echo Right-click the tray icon for options.
    echo.
) else (
    echo.
    echo ============================================================
    echo   BUILD FAILED!
    echo ============================================================
    echo.
    echo Check the error messages above.
    echo.
)

pause
