@echo off
setlocal

echo ===== Building RapidClicker Native =====

set "VS_VCVARS="
if defined VSINSTALLDIR if exist "%VSINSTALLDIR%VC\Auxiliary\Build\vcvars64.bat" (
    set "VS_VCVARS=%VSINSTALLDIR%VC\Auxiliary\Build\vcvars64.bat"
)

if not defined VS_VCVARS (
    set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
    if exist "%VSWHERE%" (
        for /f "usebackq tokens=*" %%I in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do (
            if exist "%%~I\VC\Auxiliary\Build\vcvars64.bat" (
                set "VS_VCVARS=%%~I\VC\Auxiliary\Build\vcvars64.bat"
            )
        )
    )
)

if not defined VS_VCVARS (
    for %%I in (
        "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"
        "C:\Program Files\Microsoft Visual Studio\18\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
        "C:\Program Files\Microsoft Visual Studio\17\Community\VC\Auxiliary\Build\vcvars64.bat"
        "C:\Program Files\Microsoft Visual Studio\17\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
    ) do (
        if not defined VS_VCVARS if exist %%~I set "VS_VCVARS=%%~I"
    )
)

if not defined VS_VCVARS (
    echo ERROR: vcvars64.bat not found. Install Visual Studio Build Tools with Desktop C++ support.
    exit /b 1
)

call "%VS_VCVARS%"
if errorlevel 1 (
    echo ERROR: Failed to initialize Visual Studio build environment.
    exit /b 1
)

if not exist build-native mkdir build-native
if not exist dist mkdir dist

del /q build-native\RapidClickerNative.* 2>nul
del /q RapidClickerWin32.obj 2>nul
rmdir /s /q build 2>nul
rmdir /s /q dist\RapidClicker 2>nul
rmdir /s /q dist\RapidClicker_OneFile.exe.libs 2>nul
del /q dist\RapidClicker_OneFile.exe 2>nul
del /q dist\RapidClickerNative.exe 2>nul
del /q dist\RapidClicker.exe 2>nul

echo Compiling resource...
rc /nologo /fo build-native\RapidClickerNative.res native\RapidClicker.rc
if errorlevel 1 (
    echo ERROR: Resource compilation failed.
    exit /b 1
)

echo Compiling native application...
cl /nologo /std:c++17 /O2 /EHsc /DUNICODE /D_UNICODE /D_SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING /Fo"build-native\\" native\RapidClickerWin32.cpp /link /SUBSYSTEM:WINDOWS /ENTRY:wWinMainCRTStartup /OUT:dist\RapidClicker.exe build-native\RapidClickerNative.res comctl32.lib shell32.lib user32.lib gdi32.lib advapi32.lib
if errorlevel 1 (
    echo ERROR: Native build failed.
    exit /b 1
)

if exist native\RapidClicker.manifest (
    mt -nologo -manifest native\RapidClicker.manifest -outputresource:dist\RapidClicker.exe;#1
    if errorlevel 1 (
        echo ERROR: Manifest embedding failed.
        exit /b 1
    )
)

for %%F in (dist\RapidClicker.exe) do (
    echo Native executable size: %%~zF bytes
)

echo Build complete!
echo Native application is in dist\RapidClicker.exe

endlocal
