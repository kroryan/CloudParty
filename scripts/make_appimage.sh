#!/bin/bash
# CloudParty AppImage Builder
# Creates an AppImage from the PyInstaller build

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_ROOT/dist"
APPDIR="$DIST_DIR/CloudParty.AppDir"
PYI_DIST_DIR="$PROJECT_ROOT/dist"
PYI_ONEFILE="$PYI_DIST_DIR/cloudparty"
PYI_ONEDIR_DIR="$PYI_DIST_DIR/cloudparty"
PYI_ONEDIR_BIN="$PYI_ONEDIR_DIR/cloudparty"

# Version from git or default
VERSION=$(git -C "$PROJECT_ROOT" describe --tags --always 2>/dev/null || echo "1.20.1")

echo "Creating CloudParty AppImage v$VERSION..."

# Clean up previous build
rm -rf "$APPDIR"
mkdir -p "$APPDIR"

# Copy PyInstaller output (supports onefile and onedir)
if [ -f "$PYI_ONEFILE" ]; then
    cp "$PYI_ONEFILE" "$APPDIR/cloudparty"
    chmod +x "$APPDIR/cloudparty"
elif [ -f "$PYI_ONEDIR_BIN" ]; then
    cp -r "$PYI_ONEDIR_DIR/"* "$APPDIR/" 2>/dev/null || true
    chmod +x "$APPDIR/cloudparty"
else
    echo "ERROR: Build output not found in $PYI_DIST_DIR"
    echo "Please run pyinstaller first: ./build_linux.sh"
    exit 1
fi

# Copy data files
cp "$PROJECT_ROOT/cloudparty.example.conf" "$APPDIR/" 2>/dev/null || true

# Copy icon
if [ -f "$PROJECT_ROOT/app-icon.png" ]; then
    cp "$PROJECT_ROOT/app-icon.png" "$APPDIR/cloudparty.png"
    cp "$PROJECT_ROOT/app-icon.png" "$APPDIR/.DirIcon"
elif [ -f "$PROJECT_ROOT/cloudparty.png" ]; then
    cp "$PROJECT_ROOT/cloudparty.png" "$APPDIR/cloudparty.png"
    cp "$PROJECT_ROOT/cloudparty.png" "$APPDIR/.DirIcon"
fi

# Create .desktop file
cat > "$APPDIR/cloudparty.desktop" << 'EOF'
[Desktop Entry]
Name=CloudParty
Comment=File sharing server with web interface
GenericName=File Server
Exec=cloudparty %F
Terminal=false
Type=Application
Icon=cloudparty
Categories=Network;FileTransfer;
Keywords=file;share;server;ftp;webdav;
StartupNotify=true
StartupWMClass=cloudparty
EOF

# Create AppRun launcher that sets up environment
cat > "$APPDIR/AppRun" << 'APPRUN_EOF'
#!/bin/bash
# CloudParty AppRun launcher

SELF=$(readlink -f "$0")
HERE=${SELF%/*}

# Set up XDG directories
export XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}"
export XDG_DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"

# Ensure config directory exists
mkdir -p "$XDG_CONFIG_HOME/cloudparty"
mkdir -p "$XDG_DATA_HOME/cloudparty"

# Copy default config if not exists
if [ ! -f "$XDG_CONFIG_HOME/cloudparty/cloudparty.conf" ]; then
    if [ -f "$HERE/cloudparty.example.conf" ]; then
        cp "$HERE/cloudparty.example.conf" "$XDG_CONFIG_HOME/cloudparty/cloudparty.conf"
    fi
fi

# Run the application
exec "$HERE/cloudparty" "$@"
APPRUN_EOF

chmod +x "$APPDIR/AppRun"

# Download appimagetool if not present
APPIMAGETOOL="$PROJECT_ROOT/build/appimagetool-x86_64.AppImage"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "Downloading appimagetool..."
    mkdir -p "$PROJECT_ROOT/build"
    wget -q --show-progress "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage" \
         -O "$APPIMAGETOOL"
    chmod +x "$APPIMAGETOOL"
fi

# Build AppImage (fallback to extract mode if FUSE is unavailable)
APPIMAGETOOL_BIN="$APPIMAGETOOL"
if ! ldconfig -p 2>/dev/null | grep -q "libfuse.so.2"; then
    echo "libfuse.so.2 not found; using extracted appimagetool..."
    APPIMAGE_EXTRACT_DIR="$PROJECT_ROOT/build/appimagetool-extract"
    rm -rf "$APPIMAGE_EXTRACT_DIR"
    mkdir -p "$APPIMAGE_EXTRACT_DIR"
    (cd "$APPIMAGE_EXTRACT_DIR" && "$APPIMAGETOOL" --appimage-extract > /dev/null)
    APPIMAGETOOL_BIN="$APPIMAGE_EXTRACT_DIR/squashfs-root/AppRun"
fi

ARCH=x86_64 "$APPIMAGETOOL_BIN" "$APPDIR" "$DIST_DIR/CloudParty-$VERSION-x86_64.AppImage"

echo ""
echo "============================================================"
echo "  APPIMAGE CREATED SUCCESSFULLY!"
echo "============================================================"
echo ""
echo "Output: $DIST_DIR/CloudParty-$VERSION-x86_64.AppImage"
echo ""
echo "To use:"
echo "  1. Make it executable: chmod +x CloudParty-$VERSION-x86_64.AppImage"
echo "  2. Run it: ./CloudParty-$VERSION-x86_64.AppImage"
echo "  3. Or install to system: ./CloudParty-$VERSION-x86_64.AppImage --install"
echo ""
