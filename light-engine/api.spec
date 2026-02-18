# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
import os

# Collect all submodules from modules package
modules_hiddenimports = collect_submodules('modules')
playwright_hiddenimports = collect_submodules('playwright')

a = Analysis(
    ['api.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include the entire modules folder with all subfolders
        ('modules', 'modules'),
        ('API', 'API'),
    ],
    hiddenimports=[
        # FastAPI and dependencies
        'fastapi',
        'uvicorn',
        'pydantic',
        'starlette',
        'websockets',
        
        # SQLAlchemy
        'sqlalchemy',
        'sqlalchemy.orm',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.engine.url',
        
        # All modules package modules
        *modules_hiddenimports,
        
        # Explicitly add automation modules
        'modules.automations',
        
        # Playwright
        *playwright_hiddenimports,
        
        # Other dependencies
        'bs4',
        'requests',
        'psutil',
        'httpx',
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
    [('W ignore', None, 'OPTION')],
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='api',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to True for debugging build issues initially
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
