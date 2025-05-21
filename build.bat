@echo off
echo ===== Building RapidClicker =====

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet
pip install pywin32-ctypes pyinstaller-hooks-contrib --quiet

:: Create directories
if not exist build mkdir build
if not exist dist mkdir dist

:: Clean previous builds
echo Cleaning previous builds...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
mkdir build
mkdir dist

:: Use PyInstaller to package
echo Building with PyInstaller...
pyinstaller --clean --noconfirm --log-level=WARN build.spec

:: Add missing DLLs
echo Checking for missing DLLs...
set ANACONDA_DIR=%CONDA_PREFIX%
if "%ANACONDA_DIR%" == "" (
    for /f "tokens=*" %%i in ('where python') do set PYTHON_EXE=%%i
    for %%i in ("%PYTHON_EXE%") do set PYTHON_DIR=%%~dpi
) else (
    set PYTHON_DIR=%ANACONDA_DIR%
)

:: Create libs directory if it doesn't exist
if not exist dist\RapidClicker_OneFile.exe.libs mkdir dist\RapidClicker_OneFile.exe.libs

:: Check common DLL locations and copy required DLLs
echo Copying required DLLs...
set DLLS_FOUND=0

:: Check for ffi-8.dll or libffi-8.dll
if exist "%PYTHON_DIR%\DLLs\ffi-8.dll" (
    copy "%PYTHON_DIR%\DLLs\ffi-8.dll" dist\RapidClicker_OneFile.exe.libs\ >nul 2>&1
    set DLLS_FOUND=1
    echo Found ffi-8.dll
) else if exist "%PYTHON_DIR%\DLLs\libffi-8.dll" (
    copy "%PYTHON_DIR%\DLLs\libffi-8.dll" dist\RapidClicker_OneFile.exe.libs\ffi-8.dll >nul 2>&1
    set DLLS_FOUND=1
    echo Found libffi-8.dll
) else if exist "%PYTHON_DIR%\libs\libffi-8.dll" (
    copy "%PYTHON_DIR%\libs\libffi-8.dll" dist\RapidClicker_OneFile.exe.libs\ffi-8.dll >nul 2>&1
    set DLLS_FOUND=1
    echo Found libffi-8.dll in libs
)

:: Check for liblzma.dll
if exist "%PYTHON_DIR%\DLLs\liblzma.dll" (
    copy "%PYTHON_DIR%\DLLs\liblzma.dll" dist\RapidClicker_OneFile.exe.libs\ >nul 2>&1
    set DLLS_FOUND=1
    echo Found liblzma.dll
) else if exist "%PYTHON_DIR%\libs\liblzma.dll" (
    copy "%PYTHON_DIR%\libs\liblzma.dll" dist\RapidClicker_OneFile.exe.libs\ >nul 2>&1
    set DLLS_FOUND=1
    echo Found liblzma.dll in libs
) else if exist "%SYSTEMROOT%\System32\liblzma.dll" (
    copy "%SYSTEMROOT%\System32\liblzma.dll" dist\RapidClicker_OneFile.exe.libs\ >nul 2>&1
    set DLLS_FOUND=1
    echo Found liblzma.dll in System32
)

:: Check for LIBBZ2.dll
if exist "%PYTHON_DIR%\DLLs\LIBBZ2.dll" (
    copy "%PYTHON_DIR%\DLLs\LIBBZ2.dll" dist\RapidClicker_OneFile.exe.libs\ >nul 2>&1
    set DLLS_FOUND=1
    echo Found LIBBZ2.dll
) else if exist "%PYTHON_DIR%\DLLs\libbz2.dll" (
    copy "%PYTHON_DIR%\DLLs\libbz2.dll" dist\RapidClicker_OneFile.exe.libs\LIBBZ2.dll >nul 2>&1
    set DLLS_FOUND=1
    echo Found libbz2.dll
) else if exist "%PYTHON_DIR%\libs\libbz2.dll" (
    copy "%PYTHON_DIR%\libs\libbz2.dll" dist\RapidClicker_OneFile.exe.libs\LIBBZ2.dll >nul 2>&1
    set DLLS_FOUND=1
    echo Found libbz2.dll in libs
)

:: Copy necessary files to output directory
echo Copying files...
copy README.md dist\RapidClicker\ >nul 2>&1
copy README_ZH.md dist\RapidClicker\ >nul 2>&1
copy LICENSE dist\RapidClicker\ >nul 2>&1

:: Check build result
if not exist dist\RapidClicker_OneFile.exe (
    echo ERROR: Build failed!
) else (
    :: Check file size
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

:: Done
echo Build complete!
echo Application is in dist\RapidClicker\
echo Single file version is dist\RapidClicker_OneFile.exe

pause 