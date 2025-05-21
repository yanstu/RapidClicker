#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
常量定义文件
"""

import os
import sys

# 应用基本信息
APP_NAME = "RapidClicker"
APP_VERSION = "1.0.0"
APP_AUTHOR = "yanstu"
APP_GITHUB = "https://github.com/yanstu/RapidClicker"

# 资源文件路径
def resource_path(relative_path):
    """获取资源文件路径（支持PyInstaller打包）"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 图标路径
APP_ICON_PATH = resource_path(os.path.join("assets", "app_icon.ico"))
ABOUT_ICON_PATH = resource_path(os.path.join("assets", "about_icon.png"))
EXIT_ICON_PATH = resource_path(os.path.join("assets", "exit_icon.png"))
SETTINGS_ICON_PATH = resource_path(os.path.join("assets", "settings_icon.png"))

# 默认配置
DEFAULT_CONFIG = {
    # 鼠标连点设置
    "trigger_click_count": 5,         # 触发连点的点击次数
    "trigger_click_interval": 300,    # 触发连点的时间间隔(毫秒)
    "auto_click_interval": 500,        # 自动连点的间隔时间(毫秒)
    
    # 应用设置
    "language": "en",                # 默认语言(en/zh)
    "auto_start": False,             # 开机自启动
    
    # 调试设置
    "debug_mode": False,             # 调试模式
}

# 语言设置
LANGUAGES = {
    "en": {
        # 通用
        "language": "Language",
        "english": "English",
        "chinese": "Chinese",
        "save": "Save",
        "cancel": "Cancel",
        "ok": "OK",
        "auto_start": "Auto Start",
        
        # 托盘菜单
        "settings": "Settings",
        "about": "About",
        "exit": "Exit",
        
        # 设置窗口
        "settings_title": "Settings",
        "mouse_settings": "Mouse Settings",
        "app_settings": "Application Settings",
        "trigger_click_count": "Trigger Click Count",
        "trigger_click_interval": "Trigger Time Window",
        "auto_click_interval": "Auto Click Interval",
        "ms": "ms",  # 毫秒单位
        "times": " times",  # 次数单位
        "settings_saved": "Settings saved successfully!",
        
        # 关于窗口
        "about_title": "About RapidClicker",
        "about_description": "RapidClicker is a tool for automatic mouse clicking.",
        "version": "Version",
        "author": "Author",
        "github": "GitHub",
        "details": "Details",
        
        # 调试信息
        "debug_click_detected": "Click detected",
        "debug_rapid_click_triggered": "Rapid click triggered",
        "debug_rapid_click_stopped": "Rapid click stopped",
        "debug_initial_config": "Initial config: trigger count={0}, trigger window={1}ms, click interval={2}ms",
        "debug_click_recorded": "Mouse click recorded: queue size={0}",
        "debug_rapid_mode_activated": "Rapid click mode activated",
        "debug_rapid_click_started": "Long press detected, auto-clicking started",
        "debug_release_detected": "Mouse release detected, stopping auto-click",
        "debug_click_check": "Click detection: {0} clicks in {1}s (threshold: {2}s), result",
        "debug_result": "result",
        "debug_using_relaxed_condition": "Using relaxed trigger conditions",
        "debug_using_persistence_condition": "Using persistence-based trigger condition",
        "debug_auto_clicking_started": "Auto-clicking started",
        "debug_auto_clicking_stopped": "Auto-clicking stopped",
        "debug_clicks_performed": "Performed {count} clicks, average interval: {avg}ms",
        "debug_config_updated": "Config updated: trigger count={0}, trigger window={1}ms, click interval={2}ms",
        "debug_mode_timeout": "Rapid click mode timed out due to inactivity",
        
        # 错误消息
        "error_invalid_input": "Invalid input value",
        "error_already_running": "Application is already running!",
    },
    "zh": {
        # 通用
        "language": "语言",
        "english": "英文",
        "chinese": "中文",
        "save": "保存",
        "cancel": "取消",
        "ok": "确定",
        "auto_start": "开机自启动",
        
        # 托盘菜单
        "settings": "设置",
        "about": "关于",
        "exit": "退出",
        
        # 设置窗口
        "settings_title": "设置",
        "mouse_settings": "鼠标设置",
        "app_settings": "应用设置",
        "trigger_click_count": "触发点击次数",
        "trigger_click_interval": "触发时间窗口",
        "auto_click_interval": "自动点击间隔",
        "ms": "毫秒",  # 毫秒单位
        "times": " 次",  # 次数单位
        "settings_saved": "设置保存成功！",
        
        # 关于窗口
        "about_title": "关于 RapidClicker",
        "about_description": "RapidClicker 是一个自动鼠标连点工具。",
        "version": "版本",
        "author": "作者",
        "github": "GitHub",
        "details": "详细信息",
        
        # 调试信息
        "debug_click_detected": "检测到点击",
        "debug_rapid_click_triggered": "已触发连点",
        "debug_rapid_click_stopped": "连点已停止",
        "debug_initial_config": "初始配置: 触发点击次数={0}, 触发时间窗口={1}毫秒, 点击间隔={2}毫秒",
        "debug_click_recorded": "记录鼠标点击: 当前队列大小={0}",
        "debug_rapid_mode_activated": "快速点击模式已激活",
        "debug_rapid_click_started": "检测到长按，开始自动连点",
        "debug_release_detected": "检测到鼠标释放，停止连点",
        "debug_click_check": "点击检测: {0}{1}在{2}秒内 (阈值: {3}秒), {4}",
        "debug_result": "结果",
        "debug_using_relaxed_condition": "使用宽松的触发条件",
        "debug_using_persistence_condition": "使用持久性触发条件",
        "debug_auto_clicking_started": "开始自动连点",
        "debug_auto_clicking_stopped": "停止自动连点",
        "debug_clicks_performed": "已连点{count}次, 平均间隔: {avg}毫秒",
        "debug_config_updated": "配置已更新: 触发点击次数={0}, 触发时间窗口={1}毫秒, 点击间隔={2}毫秒",
        "debug_mode_timeout": "快速点击模式因长时间不活动而超时",
        
        # 错误消息
        "error_invalid_input": "输入值无效",
        "error_already_running": "应用程序已在运行！",
    }
} 