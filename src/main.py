#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RapidClicker - 自动连点工具
作者: yanstu
"""

import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from utils.singleton import SingletonApp
from utils.config import Config
from core.tray_icon import SystemTrayIcon
from utils.constants import APP_ICON_PATH


def check_admin():
    """检查程序是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def main():
    """主程序入口"""
    # 初始化配置
    Config()
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭所有窗口时不退出应用
    app.setWindowIcon(QIcon(APP_ICON_PATH))
    
    # 确保程序只能运行一个实例
    singleton = SingletonApp("RapidClicker_Singleton_Lock")
    if not singleton.is_single():
        print("Application is already running!")
        sys.exit(0)
    
    # 创建系统托盘图标
    tray_icon = SystemTrayIcon()
    tray_icon.show()
    
    # 启动应用
    sys.exit(app.exec_())


if __name__ == "__main__":
    # 判断是否需要以管理员权限运行（在某些系统上可能需要）
    # if not check_admin():
    #     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    #     sys.exit(0)
    
    main() 