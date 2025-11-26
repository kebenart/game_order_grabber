#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏抢单系统主程序 - GUI版本
"""

import sys
import os
import time

# 设置环境变量来解决WM_QUERYENDSESSION问题
os.environ['QT_QPA_PLATFORM'] = 'windows'
os.environ['QT_QPA_NO_SESSION_MANAGER'] = '1'
os.environ['PYINSTALLER_BOOTLOADER_IGNORE_SIGNALS'] = '1'

def main():
    """主函数 - 直接启动GUI"""
    try:
        from gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"✗ 无法导入GUI模块: {e}")
        print("请确保PySide6已安装: pip install PySide6")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ GUI运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

