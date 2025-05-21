#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
调试工具模块
"""

import os
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint, QObject, pyqtSignal

from utils.config import Config
from utils.language import Language


class Toast(QWidget):
    """悬浮提示窗口"""
    
    def __init__(self, parent=None):
        super(Toast, self).__init__(parent=parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # UI初始化
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 10, 15, 10)  # 增加内边距
        
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            color: white;
            padding: 12px;  /* 增加内边距 */
            border-radius: 6px;
            background-color: rgba(0, 0, 0, 200);
            font-size: 14px;  /* 增加字体大小 */
        """)
        
        self.layout.addWidget(self.label)
        
        # 自动关闭定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide)
    
    def show_message(self, message, duration=1500):
        """显示消息"""
        self.label.setText(message)
        self.adjustSize()
        
        # 移动到屏幕右下角，保持在任务栏上方
        screen_geo = QApplication.desktop().screenGeometry()
        taskbar_height = 40  # 估计任务栏高度
        x = screen_geo.width() - self.width() - 20
        y = screen_geo.height() - self.height() - taskbar_height - 15  # 任务栏上方15像素
        self.move(QPoint(x, y))
        
        self.show()
        
        # 设置自动关闭
        self.timer.start(duration)


class DebugHelper(QObject):
    """调试助手，单例模式实现"""
    
    _instance = None
    debug_message = pyqtSignal(str)  # 调试消息信号
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DebugHelper, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        super(DebugHelper, self).__init__()
        
        # 初始化
        self._config = Config()
        self._lang = Language()
        self._toast = None
        
        # 检查是否在开发环境中
        self._is_dev_env = not hasattr(sys, '_MEIPASS')
        
        # 初始化完成标志
        self._initialized = True
        
        # 连接调试消息信号
        self.debug_message.connect(self._on_debug_message)
    
    def is_debug_mode(self):
        """判断是否处于调试模式"""
        return self._is_dev_env or self._config.get("debug_mode", False)
    
    def log(self, message_key):
        """
        记录调试信息
        
        Args:
            message_key: 消息对应的语言键
        """
        if self.is_debug_mode():
            # 翻译消息
            message = self._lang.get(message_key)
            
            # 输出到控制台
            print(f"[DEBUG] {message}")
            
            # 发送消息信号
            self.debug_message.emit(message)
    
    def _on_debug_message(self, message):
        """处理调试消息"""
        # 懒加载Toast实例
        if self._toast is None:
            self._toast = Toast()
        
        # 显示悬浮提示
        self._toast.show_message(message, 2000)  # 增加显示时间为2秒 