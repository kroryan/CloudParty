# -*- mode: python ; coding: utf-8 -*-

import os

# Include all web and res files from local copyparty directory
# This works with editable installs where collect_data_files fails
local_datas = [
    # Web files (HTML, CSS, JS, etc.)
    ('copyparty/web', 'copyparty/web'),
    # Resource files
    ('copyparty/res', 'copyparty/res'),
    # Config files
    ('cloudparty.example.conf', '.'),
    ('cloudparty.ico', '.'),
]

# Only add SECURITY_AUDIT_REPORT.md if it exists
if os.path.exists('SECURITY_AUDIT_REPORT.md'):
    local_datas.append(('SECURITY_AUDIT_REPORT.md', '.'))

a = Analysis(
    ['cloudparty_launcher.py'],
    pathex=[],
    binaries=[],
    datas=local_datas,
    hiddenimports=[
        'pystray._win32',
        'PIL._tkinter_finder',
        'argon2',
        'argon2.low_level',
        'argon2.exceptions',
    ],
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
    name='CloudParty',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console - runs as tray app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['cloudparty.ico'],
)
