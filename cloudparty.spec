# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for CloudParty
Builds a Windows executable with tray app functionality
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all copyparty data files (web resources, etc.)
datas = []
datas += collect_data_files('copyparty')

# Add our custom files
datas += [
    ('cloudparty.example.conf', '.'),
    ('copyparty/web/cloudparty.css', 'copyparty/web'),
    ('cloudparty.ico', '.'),  # Include icon for tray
]

# Collect all hidden imports that copyparty might need
hiddenimports = collect_submodules('copyparty')
hiddenimports += [
    'pystray',
    'pystray._win32',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'jinja2',
    'sqlite3',
    'ssl',
    'hashlib',
    'json',
    'ctypes',
    'ctypes.wintypes',
    'threading',
    'queue',
    'argparse',
    'socket',
    'select',
    'errno',
    'uuid',
    'base64',
    'time',
    'datetime',
    'logging',
    'traceback',
    're',
    'shlex',
    'shutil',
    'gzip',
    'zlib',
]

a = Analysis(
    ['cloudparty_launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CloudParty',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for now, we hide it programmatically
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='cloudparty.ico' if os.path.exists('cloudparty.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)
