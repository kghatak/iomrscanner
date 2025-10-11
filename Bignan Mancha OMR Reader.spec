# -*- mode: python ; coding: utf-8 -*-


import os
import sys

# Check if poppler_bundle exists (for Windows bundling)
poppler_bundle_path = 'poppler_bundle'
datas_list = [('ui', 'ui')]

if os.path.exists(poppler_bundle_path) and sys.platform == 'win32':
    print(f"✅ Including Poppler bundle from: {poppler_bundle_path}")
    datas_list.append((poppler_bundle_path, 'poppler_bundle'))
else:
    if sys.platform == 'win32':
        print("⚠️  Warning: poppler_bundle not found. Run download_poppler_windows.py first for bundled Poppler.")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas_list,
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='Bignan Mancha OMR Reader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Bignan Mancha OMR Reader',
)
app = BUNDLE(
    coll,
    name='Bignan Mancha OMR Reader.app',
    icon=None,
    bundle_identifier='com.bignanmancha.omr.reader',
)
