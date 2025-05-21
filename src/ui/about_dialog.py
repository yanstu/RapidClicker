#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
关于对话框模块
"""

import webbrowser
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont, QCursor

from utils.constants import (
    APP_NAME, APP_VERSION, APP_AUTHOR, APP_GITHUB,
    APP_ICON_PATH, ABOUT_ICON_PATH
)
from utils.language import Language


class ClickableLabel(QLabel):
    """可点击的链接标签"""
    
    def __init__(self, text="", url="", parent=None):
        super(ClickableLabel, self).__init__(text, parent)
        self.url = url
        self.setStyleSheet("color: #0078d7; text-decoration: underline; cursor: pointer;")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setWordWrap(True)
        self.setFixedWidth(370)  # 增加宽度确保链接完整显示
        self.setMinimumHeight(40)  # 增加高度
    
    def mousePressEvent(self, event):
        """鼠标点击事件处理"""
        if event.button() == Qt.LeftButton and self.url:
            webbrowser.open(self.url)
        super(ClickableLabel, self).mousePressEvent(event)


class AboutDialog(QDialog):
    """关于对话框"""
    
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        
        # 初始化语言
        self._lang = Language()
        
        # 设置窗口属性
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        # 设置窗口标题和图标
        self.setWindowTitle(self._lang.get("about_title"))
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        
        # 设置窗口属性（无最大化最小化按钮）
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)  # 增加间距
        main_layout.setContentsMargins(25, 25, 25, 25)  # 增加边距
        
        # 顶部布局（图标和标题）
        top_layout = QHBoxLayout()
        
        # 图标
        icon_label = QLabel()
        icon_pixmap = QPixmap(ABOUT_ICON_PATH).scaled(QSize(80, 80), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_label.setPixmap(icon_pixmap)
        top_layout.addWidget(icon_label)
        
        # 标题和描述
        title_layout = QVBoxLayout()
        title_layout.setSpacing(12)  # 增加间距
        
        # 应用名称
        app_name_label = QLabel(APP_NAME)
        font = QFont()
        font.setPointSize(18)  # 增大字号
        font.setBold(True)
        app_name_label.setFont(font)
        title_layout.addWidget(app_name_label)
        
        # 应用描述
        self.desc_label = QLabel(self._lang.get("about_description"))
        self.desc_label.setWordWrap(True)
        self.desc_label.setMinimumHeight(60)  # 增加高度
        desc_font = QFont()
        desc_font.setPointSize(11)
        self.desc_label.setFont(desc_font)
        title_layout.addWidget(self.desc_label)
        
        top_layout.addLayout(title_layout)
        top_layout.addStretch()
        
        main_layout.addLayout(top_layout)
        
        # 信息组
        info_group = QGroupBox(self._lang.get("details"))
        info_group.setFont(QFont("", 10, QFont.Bold))
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(20, 25, 20, 20)  # 增加内边距
        info_layout.setSpacing(20)  # 增加间距
        
        # 版本信息
        version_layout = QHBoxLayout()
        self.version_title = QLabel(f"{self._lang.get('version')}:")
        self.version_title.setMinimumWidth(100)  # 增加宽度
        self.version_title.setMinimumHeight(35)  # 增加高度
        version_font = QFont()
        version_font.setPointSize(10)
        self.version_title.setFont(version_font)
        version_layout.addWidget(self.version_title)
        
        version_value = QLabel(APP_VERSION)
        version_value.setMinimumHeight(35)  # 增加高度
        version_value.setFont(version_font)
        version_layout.addWidget(version_value)
        version_layout.addStretch()
        
        info_layout.addLayout(version_layout)
        
        # 作者信息
        author_layout = QHBoxLayout()
        self.author_title = QLabel(f"{self._lang.get('author')}:")
        self.author_title.setMinimumWidth(100)  # 增加宽度
        self.author_title.setMinimumHeight(35)  # 增加高度
        self.author_title.setFont(version_font)
        author_layout.addWidget(self.author_title)
        
        author_value = QLabel(APP_AUTHOR)
        author_value.setMinimumHeight(35)  # 增加高度
        author_value.setFont(version_font)
        author_layout.addWidget(author_value)
        author_layout.addStretch()
        
        info_layout.addLayout(author_layout)
        
        # GitHub信息
        github_layout = QHBoxLayout()
        self.github_title = QLabel("GitHub:")
        self.github_title.setMinimumWidth(100)  # 增加宽度
        self.github_title.setMinimumHeight(35)  # 增加高度
        self.github_title.setFont(version_font)
        github_layout.addWidget(self.github_title)
        
        github_link = ClickableLabel(APP_GITHUB, APP_GITHUB)
        github_link.setFont(version_font)
        github_layout.addWidget(github_link)
        github_layout.addStretch()
        
        info_layout.addLayout(github_layout)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # 底部按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.ok_button = QPushButton(self._lang.get("ok"))
        self.ok_button.setMinimumWidth(130)  # 增加宽度
        self.ok_button.setMinimumHeight(40)  # 增加高度
        self.ok_button.clicked.connect(self.accept)
        
        buttons_layout.addWidget(self.ok_button)
        
        main_layout.addLayout(buttons_layout)
        
        # 设置主布局
        self.setLayout(main_layout)
        
        # 设置窗口尺寸
        self.setFixedSize(600, 460)  # 再次增加窗口尺寸
    
    def closeEvent(self, event):
        """重写关闭事件"""
        event.accept()
    
    def resizeEvent(self, event):
        """重写大小调整事件，防止窗口大小变化"""
        self.setFixedSize(600, 460)
        event.accept()
    
    def changeEvent(self, event):
        """处理语言变更事件"""
        if event.type() == event.LanguageChange:
            self._update_ui_texts()
        super(AboutDialog, self).changeEvent(event)
    
    def _update_ui_texts(self):
        """更新UI文本为当前语言"""
        self.setWindowTitle(self._lang.get("about_title"))
        self.desc_label.setText(self._lang.get("about_description"))
        
        # 更新组标题
        info_group = self.findChild(QGroupBox)
        if info_group:
            info_group.setTitle(self._lang.get("details"))
        
        # 更新标签
        self.version_title.setText(f"{self._lang.get('version')}:")
        self.author_title.setText(f"{self._lang.get('author')}:")
        
        # 更新按钮
        self.ok_button.setText(self._lang.get("ok")) 