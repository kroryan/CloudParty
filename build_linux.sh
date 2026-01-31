#!/bin/bash
# CloudParty Build Script for Linux
# This script builds the CloudParty executable with tray app functionality

set -e

echo ""
echo "============================================================"
echo "  CloudParty Linux Build Script"
echo "============================================================"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from your package manager"
    exit 1
fi

# Create and use a local virtual environment to avoid PEP 668 issues
VENV_DIR="${VENV_DIR:-.venv-build}"
if [ ! -d "$VENV_DIR" ]; then
    echo "[1/6] Creating virtual environment..."
    python3 -m venv "$VENV_DIR" || {
        echo "ERROR: Failed to create venv. Install python3-venv and try again."
        exit 1
    }
fi

PIP_CMD="$VENV_DIR/bin/pip"
PY_CMD="$VENV_DIR/bin/python"

echo "[2/6] Installing dependencies..."
$PIP_CMD install pyinstaller pystray pillow jinja2 argon2-cffi --quiet

echo "[3/6] Installing copyparty in development mode..."
$PIP_CMD install -e . --quiet

echo "[4/6] Checking icon file..."
if [ -f "app-icon.png" ]; then
    echo "Icon file found: app-icon.png"
else
    echo "Warning: app-icon.png not found, will use fallback icon"
fi

echo "[5/6] Building executable with PyInstaller..."
"$VENV_DIR/bin/pyinstaller" --clean --noconfirm cloudparty_linux.spec

echo "[6/6] Copying configuration files..."
if [ -f "dist/cloudparty" ]; then
    cp cloudparty.example.conf dist/ > /dev/null 2>&1 || true
    cp app-icon.png dist/ > /dev/null 2>&1 || true

    echo ""
    echo "============================================================"
    echo "  BUILD SUCCESSFUL!"
    echo "============================================================"
    echo ""
    echo "Output: dist/cloudparty"
    echo ""
    echo "To use:"
    echo "  1. Make the executable: chmod +x dist/cloudparty"
    echo "  2. Run it: ./dist/cloudparty"
    echo ""
    echo "The application will start in the system tray (if supported)."
    echo "Note: Linux tray icon requires AppIndicator support."
    echo ""
else
    echo ""
    echo "============================================================"
    echo "  BUILD FAILED!"
    echo "============================================================"
    echo ""
    echo "Check the error messages above."
    echo ""
    exit 1
fi
