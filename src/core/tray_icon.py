#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
系统托盘图标模块
"""

import sys
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

from utils.constants import APP_NAME, APP_ICON_PATH, SETTINGS_ICON_PATH, ABOUT_ICON_PATH, EXIT_ICON_PATH
from utils.language import Language
from utils.config import Config
from core.mouse_handler import MouseHandler
from ui.settings_dialog import SettingsDialog
from ui.about_dialog import AboutDialog


class SystemTrayIcon(QSystemTrayIcon):
    """系统托盘图标类"""
    
    def __init__(self, parent=None):
        super(SystemTrayIcon, self).__init__(parent)
        
        # 初始化
        self._config = Config()
        self._lang = Language()
        self._mouse_handler = MouseHandler()
        
        # 设置图标
        self.setIcon(QIcon(APP_ICON_PATH))
        self.setToolTip(APP_NAME)
        
        # 创建右键菜单
        self.menu = QMenu()
        self._settings_dialog = None
        self._about_dialog = None
        
        # 创建菜单项
        self._create_menu()
        
        # 设置菜单
        self.setContextMenu(self.menu)
        
        # 连接信号
        self.activated.connect(self._on_tray_activated)
        self._config.config_changed.connect(self._on_config_changed)
    
    def _create_menu(self):
        """创建托盘右键菜单"""
        # 清空菜单
        self.menu.clear()
        
        # 设置选项
        self.settings_action = QAction(QIcon(SETTINGS_ICON_PATH), self._lang.get("settings"), self)
        self.settings_action.triggered.connect(self._show_settings_dialog)
        self.menu.addAction(self.settings_action)
        
        # 关于选项
        self.about_action = QAction(QIcon(ABOUT_ICON_PATH), self._lang.get("about"), self)
        self.about_action.triggered.connect(self._show_about_dialog)
        self.menu.addAction(self.about_action)
        
        # 分隔线
        self.menu.addSeparator()
        
        # 退出选项
        self.exit_action = QAction(QIcon(EXIT_ICON_PATH), self._lang.get("exit"), self)
        self.exit_action.triggered.connect(self._exit_app)
        self.menu.addAction(self.exit_action)
    
    def _on_tray_activated(self, reason):
        """
        托盘图标激活事件处理
        
        Args:
            reason: 激活原因
        """
        # 双击打开设置
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_settings_dialog()
    
    def _show_settings_dialog(self):
        """显示设置对话框"""
        # 确保设置窗口只能打开一个
        if self._settings_dialog is None:
            self._settings_dialog = SettingsDialog()
            self._settings_dialog.finished.connect(self._on_settings_dialog_closed)
        
        if not self._settings_dialog.isVisible():
            self._settings_dialog.show()
        
        # 确保窗口在前台显示
        self._settings_dialog.activateWindow()
    
    def _on_settings_dialog_closed(self):
        """设置对话框关闭事件处理"""
        self._settings_dialog = None
    
    def _show_about_dialog(self):
        """显示关于对话框"""
        # 确保关于窗口只能打开一个
        if self._about_dialog is None:
            self._about_dialog = AboutDialog()
            self._about_dialog.finished.connect(self._on_about_dialog_closed)
        
        if not self._about_dialog.isVisible():
            self._about_dialog.show()
        
        # 确保窗口在前台显示
        self._about_dialog.activateWindow()
    
    def _on_about_dialog_closed(self):
        """关于对话框关闭事件处理"""
        self._about_dialog = None
    
    def _exit_app(self):
        """退出应用程序"""
        # 停止鼠标监听
        self._mouse_handler.stop_listening()
        
        # 隐藏托盘图标并退出
        self.hide()
        sys.exit(0)
    
    def _on_config_changed(self):
        """配置变更事件处理"""
        # 更新菜单文本
        self.settings_action.setText(self._lang.get("settings"))
        self.about_action.setText(self._lang.get("about"))
        self.exit_action.setText(self._lang.get("exit")) 