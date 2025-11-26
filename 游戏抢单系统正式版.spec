# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('gui.py', '.'), ('game_searcher.py', '.'), ('order_grabber.py', '.'), ('donate_qr.png', '.'), ('config.example.json', '.')],
    hiddenimports=['gui', 'game_searcher', 'order_grabber', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'PySide6.QtNetwork', 'requests', 'smtplib', 'email.mime.text', 'email.header', 'appdirs'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hook_qt_fix.py'],
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
    name='游戏抢单系统正式版',
    debug=False,
    bootloader_ignore_signals=True,
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
)
