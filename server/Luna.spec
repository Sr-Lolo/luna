# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\Infinity Tech\\Desktop\\Mis Cosas\\Proyecto Luna\\LunaDeck v1.7.55\\server\\src\\gui.py'],
    pathex=[],
    binaries=[],
    datas=[('web', 'web'), ('web_ad', 'web_ad'), ('app.ico', '.'), ('..\\docs\\Luna.apk', 'apk')],
    hiddenimports=['zeroconf', 'zeroconf._utils.ipaddress', 'zeroconf._handlers.answers', 'queue', 'ctypes', 'winreg', 'urllib.request'],
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
    name='Luna',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app.ico',
)
