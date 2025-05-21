#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyInstaller打包配置文件
"""

import sys
import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
from PyInstaller.utils.hooks import collect_submodules

# 获取Anaconda/Python安装路径中的DLL
python_dir = os.path.dirname(sys.executable)
dll_path = os.path.join(python_dir, "DLLs")

# 额外的二进制文件
extra_binaries = []
dll_files = ["liblzma.dll", "libffi-8.dll", "LIBBZ2.dll", 
            "api-ms-win-core-path-l1-1-0.dll"]

for dll in dll_files:
    dll_file = os.path.join(dll_path, dll)
    if os.path.exists(dll_file):
        extra_binaries.append((dll, dll_file, "BINARY"))
    else:
        system32_path = os.path.join(os.environ["WINDIR"], "System32", dll)
        if os.path.exists(system32_path):
            extra_binaries.append((dll, system32_path, "BINARY"))

# 定义入口点
a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=extra_binaries,
    datas=[
        ('assets/*', 'assets'),  # 复制assets目录下的所有文件
    ],
    hiddenimports=collect_submodules('pynput') + ['win32api', 'win32event', 'ctypes', 'PyQt5.sip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'scipy', 'pandas', 'numpy', 'PIL', 'tkinter', 'PySide2',
              'PyQt5.QtWebEngineWidgets', 'PyQt5.QtWebEngine', 'PyQt5.QtNetwork',
              'PyQt5.QtMultimedia', 'PyQt5.QtQml', 'PyQt5.QtWebEngineCore', 
              'PyQt5.QtPositioning', 'PyQt5.QtLocation', 'PyQt5.QtMultimediaWidgets'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# 创建PYZ归档
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RapidClicker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # 禁用strip，Windows不支持
    upx=False,    # 禁用UPX压缩
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app_icon.ico',
    uac_admin=False,
)

# 收集所有文件
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,  # 禁用strip，Windows不支持
    upx=False,    # 禁用UPX压缩
    upx_exclude=[],
    name='RapidClicker',
)

# 创建单文件版本
exe_onefile = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RapidClicker_OneFile',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # 禁用strip，Windows不支持
    upx=False,    # 禁用UPX压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app_icon.ico',
) 