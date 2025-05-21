#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
设置对话框模块
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QSpinBox, QCheckBox, QRadioButton,
    QPushButton, QButtonGroup, QGroupBox, QSizePolicy,
    QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

from utils.constants import APP_ICON_PATH, APP_NAME
from utils.config import Config
from utils.language import Language


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        
        # 初始化
        self._config = Config()
        self._lang = Language()
        
        # 设置窗口属性
        self._init_ui()
        self._load_settings()
        
        # 连接信号
        self._connect_signals()
    
    def _init_ui(self):
        """初始化UI"""
        # 设置窗口标题和图标
        self.setWindowTitle(self._lang.get("settings_title"))
        self.setWindowIcon(QIcon(APP_ICON_PATH))
        
        # 设置窗口属性（无最大化最小化按钮）
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)  # 增加间距
        main_layout.setContentsMargins(20, 20, 20, 20)  # 增加边距
        
        # 鼠标设置组
        mouse_group = QGroupBox(self._lang.get("mouse_settings"))
        mouse_group.setFont(QFont("", 10, QFont.Bold))
        mouse_layout = QFormLayout()
        mouse_layout.setContentsMargins(20, 25, 20, 20)  # 增加内边距
        mouse_layout.setSpacing(20)  # 增加间距
        mouse_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # 设置表单标签对齐方式
        mouse_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        mouse_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # 触发点击次数
        self.trigger_count_label = QLabel(f"{self._lang.get('trigger_click_count')} ({self._lang.get('times')})")
        self.trigger_count_label.setMinimumWidth(200)  # 增加标签宽度
        self.trigger_count_label.setWordWrap(True)  # 允许标签换行
        
        self.trigger_count_spin = QSpinBox()
        self.trigger_count_spin.setRange(2, 10)
        self.trigger_count_spin.setSingleStep(1)
        self.trigger_count_spin.setMinimumHeight(35)  # 增加高度
        self.trigger_count_spin.setFixedWidth(150)    # 固定宽度
        
        mouse_layout.addRow(self.trigger_count_label, self.trigger_count_spin)
        
        # 触发时间窗口
        self.trigger_interval_label = QLabel(f"{self._lang.get('trigger_click_interval')} ({self._lang.get('ms')})")
        self.trigger_interval_label.setMinimumWidth(200)  # 增加标签宽度
        self.trigger_interval_label.setWordWrap(True)  # 允许标签换行
        
        self.trigger_interval_spin = QSpinBox()
        self.trigger_interval_spin.setRange(100, 1000)
        self.trigger_interval_spin.setSingleStep(50)
        self.trigger_interval_spin.setMinimumHeight(35)  # 增加高度
        self.trigger_interval_spin.setFixedWidth(150)    # 固定宽度
        
        mouse_layout.addRow(self.trigger_interval_label, self.trigger_interval_spin)
        
        # 自动点击间隔
        self.auto_click_interval_label = QLabel(f"{self._lang.get('auto_click_interval')} ({self._lang.get('ms')})")
        self.auto_click_interval_label.setMinimumWidth(200)  # 增加标签宽度
        self.auto_click_interval_label.setWordWrap(True)  # 允许标签换行
        
        self.auto_click_interval_spin = QSpinBox()
        self.auto_click_interval_spin.setRange(10, 500)
        self.auto_click_interval_spin.setSingleStep(10)
        self.auto_click_interval_spin.setMinimumHeight(35)  # 增加高度
        self.auto_click_interval_spin.setFixedWidth(150)    # 固定宽度
        
        mouse_layout.addRow(self.auto_click_interval_label, self.auto_click_interval_spin)
        
        mouse_group.setLayout(mouse_layout)
        main_layout.addWidget(mouse_group)
        
        # 应用设置组
        app_group = QGroupBox(self._lang.get("app_settings"))
        app_group.setFont(QFont("", 10, QFont.Bold))
        app_layout = QVBoxLayout()
        app_layout.setContentsMargins(20, 25, 20, 20)  # 增加内边距
        app_layout.setSpacing(20)  # 增加间距
        
        # 语言设置
        language_layout = QHBoxLayout()
        self.language_label = QLabel(self._lang.get("language"))
        self.language_label.setMinimumHeight(35)  # 增加高度
        self.language_label.setMinimumWidth(120)  # 增加宽度
        language_layout.addWidget(self.language_label)
        
        self.language_group = QButtonGroup(self)
        self.english_radio = QRadioButton(self._lang.get("english"))
        self.english_radio.setMinimumHeight(35)  # 增加高度
        self.chinese_radio = QRadioButton(self._lang.get("chinese"))
        self.chinese_radio.setMinimumHeight(35)  # 增加高度
        self.language_group.addButton(self.english_radio, 1)
        self.language_group.addButton(self.chinese_radio, 2)
        
        language_layout.addWidget(self.english_radio)
        language_layout.addWidget(self.chinese_radio)
        language_layout.addStretch()
        
        app_layout.addLayout(language_layout)
        
        # 自启动设置
        self.auto_start_check = QCheckBox(self._lang.get("auto_start"))
        self.auto_start_check.setMinimumHeight(35)  # 增加高度
        app_layout.addWidget(self.auto_start_check)
        
        app_group.setLayout(app_layout)
        main_layout.addWidget(app_group)
        
        # 底部按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.save_button = QPushButton(self._lang.get("save"))
        self.save_button.setMinimumWidth(130)
        self.save_button.setMinimumHeight(40)  # 增加按钮高度
        self.cancel_button = QPushButton(self._lang.get("cancel"))
        self.cancel_button.setMinimumWidth(130)
        self.cancel_button.setMinimumHeight(40)  # 增加按钮高度
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
        # 设置主布局
        self.setLayout(main_layout)
        
        # 设置窗口尺寸
        self.setFixedSize(550, 450)  # 再次增加窗口尺寸
    
    def _connect_signals(self):
        """连接信号"""
        self.save_button.clicked.connect(self._save_settings)
        self.cancel_button.clicked.connect(self.reject)
    
    def _load_settings(self):
        """加载设置"""
        # 鼠标设置
        self.trigger_count_spin.setValue(self._config.get("trigger_click_count", 5))
        self.trigger_interval_spin.setValue(self._config.get("trigger_click_interval", 300))
        self.auto_click_interval_spin.setValue(self._config.get("auto_click_interval", 500))
        
        # 应用设置
        language = self._config.get("language", "en")
        if language == "en":
            self.english_radio.setChecked(True)
        else:
            self.chinese_radio.setChecked(True)
            
        self.auto_start_check.setChecked(self._config.get("auto_start", False))
        
        # 更新标签文本
        self._update_ui_texts()
    
    def _update_ui_texts(self):
        """更新UI文本为当前语言"""
        self.setWindowTitle(self._lang.get("settings_title"))
        
        # 更新组标题
        self.findChild(QGroupBox, "", Qt.FindDirectChildrenOnly).setTitle(self._lang.get("mouse_settings"))
        app_group = self.findChildren(QGroupBox, "", Qt.FindDirectChildrenOnly)[1]
        app_group.setTitle(self._lang.get("app_settings"))
        
        # 更新标签
        self.trigger_count_label.setText(f"{self._lang.get('trigger_click_count')} ({self._lang.get('times')})")
        self.trigger_interval_label.setText(f"{self._lang.get('trigger_click_interval')} ({self._lang.get('ms')})")
        self.auto_click_interval_label.setText(f"{self._lang.get('auto_click_interval')} ({self._lang.get('ms')})")
        
        # 更新语言选项
        self.language_label.setText(self._lang.get("language"))
        self.english_radio.setText(self._lang.get("english"))
        self.chinese_radio.setText(self._lang.get("chinese"))
        
        # 更新自启动选项
        self.auto_start_check.setText(self._lang.get("auto_start"))
        
        # 更新按钮
        self.save_button.setText(self._lang.get("save"))
        self.cancel_button.setText(self._lang.get("cancel"))
    
    def _save_settings(self):
        """保存设置"""
        # 获取表单数据
        trigger_count = self.trigger_count_spin.value()
        trigger_interval = self.trigger_interval_spin.value()
        auto_click_interval = self.auto_click_interval_spin.value()
        
        language = "en" if self.english_radio.isChecked() else "zh"
        auto_start = self.auto_start_check.isChecked()
        
        # 更新配置
        self._config.update({
            "trigger_click_count": trigger_count,
            "trigger_click_interval": trigger_interval,
            "auto_click_interval": auto_click_interval,
            "language": language,
            "auto_start": auto_start
        })
        
        # 保存配置
        if self._config.save_config():
            # 显示保存成功消息
            QMessageBox.information(
                self, 
                APP_NAME, 
                self._lang.get("settings_saved"),
                QMessageBox.Ok
            )
            self.accept()
        else:
            # 显示保存失败消息
            QMessageBox.warning(
                self, 
                APP_NAME, 
                "Failed to save settings.",
                QMessageBox.Ok
            )
    
    def closeEvent(self, event):
        """重写关闭事件"""
        event.accept()
        
    def resizeEvent(self, event):
        """重写大小调整事件，防止窗口大小变化"""
        self.setFixedSize(550, 450)
        event.accept() 