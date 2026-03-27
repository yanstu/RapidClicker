#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PyInstaller打包配置文件
"""

import sys
import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

PYQT_QT_PREFIX = os.path.join("PyQt5", "Qt5")
QT_BIN_DIR = os.path.join(PYQT_QT_PREFIX, "bin")
QT_PLUGIN_DIR = os.path.join(PYQT_QT_PREFIX, "plugins")
QT_TRANSLATION_DIR = os.path.join(PYQT_QT_PREFIX, "translations")

WINDOWS_PYNPUT_IMPORTS = [
    "pynput",
    "pynput._info",
    "pynput._util",
    "pynput._util.win32",
    "pynput._util.win32_vks",
    "pynput.mouse",
    "pynput.mouse._base",
    "pynput.mouse._win32",
]

ALLOWED_QT_BINARIES = {
    "Qt5Core.dll",
    "Qt5Gui.dll",
    "Qt5Widgets.dll",
    "python3.dll",
    "python39.dll",
    "qwindows.dll",
    "qwindowsvistastyle.dll",
    "qico.dll",
}

ALLOWED_QT_TRANSLATIONS = {
    "qt_zh_CN.qm",
    "qtbase_zh_CN.qm",
}

EXCLUDED_QT_BINARIES = {
    "Qt5DBus.dll",
    "Qt5Network.dll",
    "Qt5Qml.dll",
    "Qt5QmlModels.dll",
    "Qt5Quick.dll",
    "Qt5Svg.dll",
    "Qt5WebSockets.dll",
    "d3dcompiler_47.dll",
    "libEGL.dll",
    "libGLESv2.dll",
    "opengl32sw.dll",
}


def _should_keep_binary(entry):
    """仅保留 Widgets 桌面应用需要的 Qt 运行时。"""
    runtime_name = entry[0]
    src_name = entry[1]
    normalized_runtime = runtime_name.replace("/", "\\")
    base_name = os.path.basename(runtime_name)

    if f"{QT_BIN_DIR}\\" in normalized_runtime:
        return base_name in ALLOWED_QT_BINARIES

    if f"{QT_PLUGIN_DIR}\\" in normalized_runtime:
        return base_name in ALLOWED_QT_BINARIES

    return os.path.basename(src_name) not in EXCLUDED_QT_BINARIES and base_name not in EXCLUDED_QT_BINARIES


def _should_keep_data(entry):
    """去掉未使用的 Qt 多语言翻译资源。"""
    runtime_name = entry[0]
    normalized_runtime = runtime_name.replace("/", "\\")
    base_name = os.path.basename(runtime_name)

    if f"{QT_TRANSLATION_DIR}\\" in normalized_runtime:
        return base_name in ALLOWED_QT_TRANSLATIONS

    return True

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
    hiddenimports=WINDOWS_PYNPUT_IMPORTS + ['win32api', 'win32event', 'ctypes', 'PyQt5.sip'],
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

a.binaries = [entry for entry in a.binaries if _should_keep_binary(entry)]
a.datas = [entry for entry in a.datas if _should_keep_data(entry)]

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
    uac_admin=True,
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
    uac_admin=True,
) 
