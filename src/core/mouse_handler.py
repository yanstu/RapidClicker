#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
鼠标事件处理核心模块
"""

import time
import threading
from collections import deque
from PyQt5.QtCore import QObject, pyqtSignal
from pynput import mouse

from utils.config import Config
from utils.debug import DebugHelper
from utils.language import Language


class MouseClickEvent:
    """鼠标点击事件数据类"""
    
    def __init__(self, button, pressed, time, is_program_click=False):
        self.button = button
        self.pressed = pressed
        self.time = time
        self.is_program_click = is_program_click  # 标记是否是程序生成的点击


class MouseHandler(QObject):
    """鼠标事件处理器，实现为单例模式"""
    
    _instance = None
    
    # 信号定义
    rapid_click_started = pyqtSignal()
    rapid_click_stopped = pyqtSignal()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MouseHandler, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        super(MouseHandler, self).__init__()
        
        # 初始化配置和调试工具
        self._config = Config()
        self._debug = DebugHelper()
        self._lang = Language()
        
        # 注册配置变更事件
        self._config.config_changed.connect(self._on_config_changed)
        
        # 初始化参数
        self._trigger_click_count = self._config.get("trigger_click_count", 5)
        self._trigger_click_interval = self._config.get("trigger_click_interval", 300) / 1000.0  # 转换为秒
        self._auto_click_interval = self._config.get("auto_click_interval", 500) / 1000.0  # 转换为秒
        
        # 鼠标事件监听器
        self._listener = None
        self._controller = mouse.Controller()
        
        # 点击事件队列
        self._click_events = deque(maxlen=50)  # 增加队列大小
        self._press_times = deque(maxlen=50)   # 增大时间记录队列容量
        
        # 状态标志
        self._rapid_clicking = False       # 是否正在自动连点
        self._stop_rapid_click = threading.Event()
        self._rapid_click_thread = None
        self._rapid_click_ready = False    # 标记是否已满足快速点击条件
        self._button_held = False          # 标记左键是否正在被按住
        self._last_press_time = 0          # 记录最后一次点击时间，用于判断是否超时
        self._program_clicking = False     # 标记是否是程序在点击
        self._button_state_lock = threading.Lock()  # 用于保护按钮状态
        
        # 初始化完成标志
        self._initialized = True
        
        # 开始监听鼠标事件
        self.start_listening()
        
        # 打印初始配置
        print(f"[DEBUG] {self._lang.get('debug_initial_config')}: {self._trigger_click_count}, {self._trigger_click_interval*1000}ms, {self._auto_click_interval*1000}ms")
    
    def start_listening(self):
        """开始监听鼠标事件"""
        if self._listener is None or not self._listener.running:
            self._listener = mouse.Listener(on_click=self._on_click)
            self._listener.daemon = True
            self._listener.start()
    
    def stop_listening(self):
        """停止监听鼠标事件"""
        if self._listener and self._listener.running:
            self._listener.stop()
            self._listener = None
    
    def _on_click(self, x, y, button, pressed):
        """
        鼠标点击事件处理
        
        Args:
            x, y: 鼠标点击坐标
            button: 点击的按钮
            pressed: 是否按下(True为按下，False为释放)
        """
        # 仅处理左键事件
        if button != mouse.Button.left:
            return
            
        # 如果是程序生成的点击，忽略
        if self._program_clicking:
            return
        
        # 当前时间
        current_time = time.time()
        
        # 记录当前事件
        event = MouseClickEvent(button, pressed, current_time)
        self._click_events.append(event)
        
        # 使用锁保护按钮状态更新
        with self._button_state_lock:
            # 按下处理
            if pressed:
                # 如果超过了时间间隔，则重置计数
                if self._last_press_time > 0 and (current_time - self._last_press_time) > self._trigger_click_interval:
                    self._press_times.clear()
                    self._rapid_click_ready = False
                    print(f"[DEBUG] {self._lang.get('debug_click_timeout')}, 重置计数")
                
                self._button_held = True
                self._last_press_time = current_time
                self._press_times.append(current_time)
                self._debug.log("debug_click_detected")
                print(f"[DEBUG] {self._lang.get('debug_click_recorded')}: {len(self._press_times)}")
                
                # 检查是否满足快速点击条件 (大于等于阈值次数)
                if self._check_rapid_click_conditions():
                    self._rapid_click_ready = True
                    print(f"[DEBUG] {self._lang.get('debug_rapid_mode_activated')}! (点击次数: {len(self._press_times)})")
                    self._debug.log("debug_rapid_click_triggered")
                    
                    # 如果满足条件且按下左键，开始连点
                    if not self._rapid_clicking:
                        print(f"[DEBUG] 开始自动点击")
                        self._start_rapid_clicking()
            
            # 鼠标释放处理
            elif not pressed:
                # 更新按钮状态
                self._button_held = False
                print(f"[DEBUG] 检测到鼠标释放")
                
                # 如果正在连点则停止
                if self._rapid_clicking:
                    print(f"[DEBUG] {self._lang.get('debug_release_detected')}")
                    self._debug.log("debug_rapid_click_stopped")
                    # 强制停止连点
                    self._stop_rapid_click.set()
                    self._rapid_clicking = False
                    self._stop_rapid_clicking()
    
    def _check_rapid_click_conditions(self):
        """
        检查是否满足快速点击条件 - 点击次数是否达到或超过阈值
        
        Returns:
            bool: 是否满足条件
        """
        # 如果点击次数不足，直接返回False
        if len(self._press_times) < self._trigger_click_count:
            print(f"[DEBUG] 点击次数不足: {len(self._press_times)}/{self._trigger_click_count}")
            return False
        
        # 获取所有点击的时间
        click_times = list(self._press_times)
        
        # 检查最近trigger_click_count次点击是否在时间窗口内
        recent_clicks = click_times[-self._trigger_click_count:]
        first_time = recent_clicks[0]
        last_time = recent_clicks[-1]
        time_window = last_time - first_time
        
        # 判断是否在触发时间窗口内
        result = time_window <= self._trigger_click_interval
        
        if result:
            print(f"[DEBUG] 满足快速点击条件: {self._trigger_click_count}次点击在{time_window:.3f}秒内 (阈值: {self._trigger_click_interval:.3f}秒)")
        else:
            print(f"[DEBUG] 不满足时间条件: {self._trigger_click_count}次点击在{time_window:.3f}秒内 (阈值: {self._trigger_click_interval:.3f}秒)")
        
        return result
    
    def _start_rapid_clicking(self):
        """开始自动连点"""
        if self._rapid_clicking:
            return
            
        self._rapid_clicking = True
        self._stop_rapid_click.clear()
        
        # 创建并启动连点线程
        self._rapid_click_thread = threading.Thread(target=self._rapid_click_worker)
        self._rapid_click_thread.daemon = True
        self._rapid_click_thread.start()
        
        # 发送开始连点信号
        self.rapid_click_started.emit()
        print(f"[DEBUG] {self._lang.get('debug_auto_clicking_started')}!")
    
    def _stop_rapid_clicking(self):
        """停止自动连点"""
        if not self._rapid_clicking:
            return
            
        self._rapid_clicking = False
        self._stop_rapid_click.set()
        
        # 确保程序点击标记被取消
        self._program_clicking = False
        
        if self._rapid_click_thread and self._rapid_click_thread.is_alive():
            self._rapid_click_thread.join(0.5)  # 等待线程结束，但最多等待0.5秒
        
        self._rapid_click_thread = None
        
        # 发送停止连点信号
        self.rapid_click_stopped.emit()
        print(f"[DEBUG] {self._lang.get('debug_auto_clicking_stopped')}!")
    
    def _rapid_click_worker(self):
        """自动连点工作线程"""
        count = 0
        start_time = time.time()
        
        while self._rapid_clicking and not self._stop_rapid_click.is_set():
            # 检查用户是否仍然按住按钮
            with self._button_state_lock:
                if not self._button_held:
                    print("[DEBUG] 用户已释放按钮，停止自动点击")
                    self._stop_rapid_clicking()
                    break  # 使用break而不是return确保最后的清理代码执行
            
            try:
                # 标记为程序点击
                self._program_clicking = True
                
                # 模拟鼠标点击
                self._controller.click(mouse.Button.left)
                count += 1
                
                # 每10次点击打印一次状态
                if count % 10 == 0:
                    elapsed = time.time() - start_time
                    avg_ms = elapsed / count * 1000
                    debug_msg = self._lang.get('debug_clicks_performed')
                    print(f"[DEBUG] {debug_msg.replace('{count}', str(count)).replace('{avg}', f'{avg_ms:.1f}')}")
                
                # 取消程序点击标记
                self._program_clicking = False
                
                # 等待指定间隔
                time.sleep(self._auto_click_interval)
                
                # 再次检查按钮状态
                with self._button_state_lock:
                    if not self._button_held:
                        print("[DEBUG] 用户已释放按钮，停止自动点击")
                        self._stop_rapid_clicking()
                        break  # 使用break而不是return确保最后的清理代码执行
            except Exception as e:
                print(f"Error during rapid clicking: {e}")
                self._program_clicking = False
        
        # 确保程序点击标记被取消
        self._program_clicking = False
    
    def _on_config_changed(self):
        """配置变更处理"""
        # 更新配置参数
        self._trigger_click_count = self._config.get("trigger_click_count", 5)
        self._trigger_click_interval = self._config.get("trigger_click_interval", 300) / 1000.0
        self._auto_click_interval = self._config.get("auto_click_interval", 500) / 1000.0
        
        print(f"[DEBUG] {self._lang.get('debug_config_updated')}: {self._trigger_click_count}, {self._trigger_click_interval*1000}ms, {self._auto_click_interval*1000}ms")
    
    def get_status(self):
        """
        获取当前状态
        
        Returns:
            bool: 是否正在自动连点
        """
        return self._rapid_clicking
    
    def __del__(self):
        """析构函数，确保资源正确释放"""
        self._stop_rapid_clicking()
        self.stop_listening() 