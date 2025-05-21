#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
语言工具模块，处理多语言支持
"""

from utils.constants import LANGUAGES
from utils.config import Config


class Language:
    """语言工具类，实现为单例模式"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Language, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # 获取配置中的语言设置
        self._config = Config()
        self._current_language = self._config.get("language", "en")
        
        # 初始化完成标志
        self._initialized = True
        
        # 注册配置变更事件
        self._config.config_changed.connect(self._on_config_changed)
    
    def get(self, key):
        """
        获取指定key的翻译文本
        
        Args:
            key: 翻译键值
            
        Returns:
            str: 翻译后的文本，如果未找到则返回键值本身
        """
        if self._current_language in LANGUAGES and key in LANGUAGES[self._current_language]:
            return LANGUAGES[self._current_language][key]
        
        # 如果当前语言没有对应翻译，尝试使用英语
        if "en" in LANGUAGES and key in LANGUAGES["en"]:
            return LANGUAGES["en"][key]
            
        # 如果都没有找到，返回键值本身
        return key
    
    def set_language(self, language):
        """
        设置当前语言
        
        Args:
            language: 语言代码(en/zh)
        """
        if language in LANGUAGES:
            self._current_language = language
            self._config.set("language", language)
            self._config.save_config()
    
    def get_current_language(self):
        """
        获取当前语言代码
        
        Returns:
            str: 当前语言代码
        """
        return self._current_language
    
    def _on_config_changed(self):
        """配置变更处理"""
        new_language = self._config.get("language", "en")
        if new_language != self._current_language:
            self._current_language = new_language 