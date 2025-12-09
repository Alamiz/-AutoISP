# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
import os

# Collect all submodules from modules package
modules_hiddenimports = collect_submodules('modules')

a = Analysis(
    ['api.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include the entire modules folder with all subfolders
        ('modules', 'modules'),
    ],
    hiddenimports=[
        # FastAPI and dependencies
        'fastapi',
        'uvicorn',
        'pydantic',
        'starlette',
        'websockets',
        
        # SQLAlchemy (if used)
        'sqlalchemy',
        'sqlalchemy.orm',
        
        # All modules package modules
        *modules_hiddenimports,
        
        # Explicitly add automation modules for dynamic imports just in case
        'modules.automations',
        
        # Playwright
        'playwright',
        'playwright.sync_api',
        'playwright._impl',
        'playwright._impl._driver',
        
        # Other dependencies
        'bs4',
        'requests',
        'httpx',
        'PySide6',
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
    name='api',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for background execution
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
