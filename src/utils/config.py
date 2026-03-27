#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模块
"""

import os
import json
import sys
import winreg
import subprocess
from PyQt5.QtCore import QObject, pyqtSignal

from utils.constants import DEFAULT_CONFIG, APP_NAME


class Config(QObject):
    """配置管理类，单例模式实现"""
    
    _instance = None
    config_changed = pyqtSignal()  # 配置变更信号
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        super(Config, self).__init__()
        
        # 初始化配置
        self._config_file = os.path.join(os.path.expanduser("~"), f".{APP_NAME.lower()}.json")
        self._config = self._load_config()
        self._initialized = True
    
    def _load_config(self):
        """从配置文件加载配置"""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 确保新添加的配置项也加入
                    for key, value in DEFAULT_CONFIG.items():
                        if key not in config:
                            config[key] = value
                    return config
        except Exception as e:
            print(f"Error loading config: {e}")
        
        # 如果配置文件不存在或加载失败，返回默认配置
        return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4)
                
            # 保存自启动设置
            self._set_auto_start(self._config.get("auto_start", False))
            
            # 发送配置变更信号
            self.config_changed.emit()
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key, default=None):
        """获取配置项"""
        return self._config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        self._config[key] = value
    
    def update(self, new_config):
        """批量更新配置"""
        self._config.update(new_config)
    
    def get_all(self):
        """获取所有配置"""
        return self._config.copy()
    
    def _set_auto_start(self, enabled):
        """设置开机自启动（管理员模式下改用计划任务）"""
        try:
            task_name = APP_NAME
            try:
                reg_key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0,
                    winreg.KEY_SET_VALUE,
                )
                try:
                    winreg.DeleteValue(reg_key, APP_NAME)
                except FileNotFoundError:
                    pass
                finally:
                    winreg.CloseKey(reg_key)
            except OSError:
                pass

            if enabled:
                if hasattr(sys, '_MEIPASS'):  # PyInstaller打包情况
                    launch_command = f'"{os.path.abspath(sys.executable)}"'
                else:
                    python_exe = os.path.abspath(sys.executable)
                    entry_script = os.path.abspath(sys.argv[0])
                    launch_command = f'"{python_exe}" "{entry_script}"'

                command = [
                    "schtasks",
                    "/Create",
                    "/SC", "ONLOGON",
                    "/TN", task_name,
                    "/TR", launch_command,
                    "/RL", "HIGHEST",
                    "/F",
                ]
            else:
                command = ["schtasks", "/Delete", "/TN", task_name, "/F"]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                check=False,
            )

            if not enabled and result.returncode == 1:
                not_found_text = (result.stdout or "") + (result.stderr or "")
                if "cannot find the file specified" in not_found_text.lower() or "找不到指定的文件" in not_found_text:
                    return True

            return result.returncode == 0
        except Exception as e:
            print(f"Error setting auto start: {e}")
            return False 
