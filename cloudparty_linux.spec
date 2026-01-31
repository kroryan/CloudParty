# -*- mode: python ; coding: utf-8 -*-

import importlib.util
import os
import sys
from PyInstaller.utils.hooks import collect_submodules

# Include all web and res files from local copyparty directory
# This works with editable installs where collect_data_files fails
local_datas = [
    # Web files (HTML, CSS, JS, etc.)
    ('copyparty/web', 'copyparty/web'),
    # Resource files
    ('copyparty/res', 'copyparty/res'),
    # Config files
    ('cloudparty.example.conf', '.'),
]

# Add PNG icon for Linux
if os.path.exists('app-icon.png'):
    local_datas.append(('app-icon.png', '.'))

# Only add SECURITY_AUDIT_REPORT.md if it exists
if os.path.exists('SECURITY_AUDIT_REPORT.md'):
    local_datas.append(('SECURITY_AUDIT_REPORT.md', '.'))

# Linux-specific hidden imports (optional based on installed backends)
def _optional_hidden(name):
    return [name] if importlib.util.find_spec(name) else []

linux_hiddenimports = (
    _optional_hidden('pystray._appindicator')  # Linux AppIndicator backend
    + _optional_hidden('pystray._dbus')        # Linux DBus backend
)

a = Analysis(
    ['cloudparty_launcher.py'],
    pathex=[],
    binaries=[],
    datas=local_datas,
    hiddenimports=[
        'PIL._tkinter_finder',
        'argon2',
        'argon2.low_level',
        'argon2.exceptions',
    ] + linux_hiddenimports + collect_submodules('copyparty'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='cloudparty',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Linux: keep console visible for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
