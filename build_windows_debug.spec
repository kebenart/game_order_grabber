# -*- mode: python ; coding: utf-8 -*-
# 调试版本打包配置 - 显示控制台窗口以便查看错误信息

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('donate_qr.png', '.'),  # 包含捐赠二维码
        ('config.example.json', '.'),  # 包含示例配置文件
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'PySide6.QtNetwork',
        'email.mime.text',
        'email.header',
        'smtplib',
        'requests',
        'game_searcher',
        'order_grabber',
        'gui',
        'asyncio',
        'concurrent.futures',
        'json',
        'threading',
        'time',
        'datetime',
        'os',
        'sys',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['hook_qt_fix.py'],
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
    name='游戏抢单系统_调试版',
    debug=True,  # 启用调试模式
    bootloader_ignore_signals=True,  # 忽略信号，避免WM_QUERYENDSESSION问题
    strip=False,
    upx=False,  # 调试时禁用压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口，可以看到错误信息
    icon=None,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

