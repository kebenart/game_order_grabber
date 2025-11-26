"""
Runtime hook to fix WM_QUERYENDSESSION issue in PyInstaller
"""
import os
import sys

# 设置环境变量来避免Qt的WM_QUERYENDSESSION等待
os.environ['QT_QPA_PLATFORM'] = 'windows'
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'

# 禁用Qt的会话管理
os.environ['QT_QPA_NO_SESSION_MANAGER'] = '1'

# 设置快速退出
os.environ['PYINSTALLER_BOOTLOADER_IGNORE_SIGNALS'] = '1'