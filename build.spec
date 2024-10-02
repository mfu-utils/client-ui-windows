# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['client-ui'],
    pathex=[],
    binaries=[],
    datas=[('proto.yaml', '.')],
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
    a.binaries,
    a.datas,
    # FILES
    Tree('App', prefix='App'),
    Tree('assets', prefix='assets'),
    Tree('configs', prefix='configs'),
    # FILES
    name='MFUClient',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    version='ffi.txt',
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.ico'],
)
