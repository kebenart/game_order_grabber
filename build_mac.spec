# -*- mode: python ; coding: utf-8 -*-

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
    ],
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
    [],
    exclude_binaries=True,
    name='游戏抢单系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 不显示控制台窗口
    argv_emulation=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='游戏抢单系统',
    strip=False,
    upx=True,
    upx_exclude=[],
)

app = BUNDLE(
    coll,
    name='游戏抢单系统.app',
    icon=None,  # 可以添加图标文件路径，如 'icon.icns'
    bundle_identifier='com.gameordergrabber.app',
    version='1.0.0',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2024',
    },
)

