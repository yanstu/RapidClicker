@echo off
echo ===== Building RapidClicker Python =====

echo Installing dependencies...
pip install -r requirements.txt --quiet
pip install pywin32-ctypes pyinstaller-hooks-contrib --quiet

if not exist build mkdir build
if not exist dist mkdir dist

echo Cleaning previous builds...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
mkdir build
mkdir dist

echo Building with PyInstaller...
pyinstaller --clean --noconfirm --log-level=WARN build.spec

echo Checking for missing DLLs...
set ANACONDA_DIR=%CONDA_PREFIX%
if "%ANACONDA_DIR%" == "" (
    for /f "tokens=*" %%i in ('where python') do set PYTHON_EXE=%%i
    for %%i in ("%PYTHON_EXE%") do set PYTHON_DIR=%%~dpi
) else (
    set PYTHON_DIR=%ANACONDA_DIR%
)

if not exist dist\RapidClicker_OneFile.exe.libs mkdir dist\RapidClicker_OneFile.exe.libs

echo Copying required DLLs...

if exist "%PYTHON_DIR%\DLLs\ffi-8.dll" (
    copy "%PYTHON_DIR%\DLLs\ffi-8.dll" dist\RapidClicker_OneFile.exe.libs\ >nul 2>&1
) else if exist "%PYTHON_DIR%\DLLs\libffi-8.dll" (
    copy "%PYTHON_DIR%\DLLs\libffi-8.dll" dist\RapidClicker_OneFile.exe.libs\ffi-8.dll >nul 2>&1
) else if exist "%PYTHON_DIR%\libs\libffi-8.dll" (
    copy "%PYTHON_DIR%\libs\libffi-8.dll" dist\RapidClicker_OneFile.exe.libs\ffi-8.dll >nul 2>&1
)

if exist "%PYTHON_DIR%\DLLs\liblzma.dll" (
    copy "%PYTHON_DIR%\DLLs\liblzma.dll" dist\RapidClicker_OneFile.exe.libs\ >nul 2>&1
) else if exist "%PYTHON_DIR%\libs\liblzma.dll" (
    copy "%PYTHON_DIR%\libs\liblzma.dll" dist\RapidClicker_OneFile.exe.libs\ >nul 2>&1
) else if exist "%SYSTEMROOT%\System32\liblzma.dll" (
    copy "%SYSTEMROOT%\System32\liblzma.dll" dist\RapidClicker_OneFile.exe.libs\ >nul 2>&1
)

if exist "%PYTHON_DIR%\DLLs\LIBBZ2.dll" (
    copy "%PYTHON_DIR%\DLLs\LIBBZ2.dll" dist\RapidClicker_OneFile.exe.libs\ >nul 2>&1
) else if exist "%PYTHON_DIR%\DLLs\libbz2.dll" (
    copy "%PYTHON_DIR%\DLLs\libbz2.dll" dist\RapidClicker_OneFile.exe.libs\LIBBZ2.dll >nul 2>&1
) else if exist "%PYTHON_DIR%\libs\libbz2.dll" (
    copy "%PYTHON_DIR%\libs\libbz2.dll" dist\RapidClicker_OneFile.exe.libs\LIBBZ2.dll >nul 2>&1
)

echo Copying files...
copy README.md dist\RapidClicker\ >nul 2>&1
copy README_ZH.md dist\RapidClicker\ >nul 2>&1
copy LICENSE dist\RapidClicker\ >nul 2>&1

if not exist dist\RapidClicker_OneFile.exe (
    echo ERROR: Build failed!
) else (
    for %%F in (dist\RapidClicker_OneFile.exe) do (
        echo Single file size: %%~zF bytes
        if %%~zF GTR 10000000 (
            echo WARNING: Executable size exceeds 10MB!
            echo Consider using more aggressive exclusions in build.spec.
        ) else (
            echo SUCCESS: Executable size is within 10MB limit.
        )
    )
)

echo Build complete!
echo Python application is in dist\RapidClicker\
echo Python single file version is dist\RapidClicker_OneFile.exe

pause
