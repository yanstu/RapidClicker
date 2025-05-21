#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
单例模式实现模块，确保应用只能有一个实例运行
"""

import sys
import os
import tempfile
import win32api
import win32event


class SingletonApp:
    """单例应用类，确保应用只能有一个实例运行"""
    
    def __init__(self, app_id):
        """
        初始化单例检查
        
        Args:
            app_id: 应用唯一标识符
        """
        self.app_id = app_id
        self.mutex_name = f'Global\\{self.app_id}'
        self.mutex = None
    
    def is_single(self):
        """
        检查是否为唯一实例
        
        Returns:
            bool: 如果是唯一实例返回True，否则返回False
        """
        try:
            # 尝试创建命名互斥量
            self.mutex = win32event.CreateMutex(None, False, self.mutex_name)
            # 获取上一个错误
            last_error = win32api.GetLastError()
            
            # 如果互斥量已经存在，说明已经有一个实例在运行
            if last_error == 183:  # ERROR_ALREADY_EXISTS
                self.mutex = None
                return False
                
            return True
        except Exception as e:
            print(f"Error checking singleton: {e}")
            # 出错时返回True，避免阻止程序启动
            return True
    
    def __del__(self):
        """清理互斥量"""
        try:
            if self.mutex:
                win32api.CloseHandle(self.mutex)
        except Exception:
            pass 