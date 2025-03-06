@echo off
setlocal EnableDelayedExpansion

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found. Installing...
    powershell -Command "(New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe', 'python_installer.exe')"
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe

    if not defined PYTHON_PATH (
        if exist "C:\Program Files\Python312\python.exe" (
            set PYTHON_PATH=C:\Program Files\Python312\python.exe
        ) else if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" (
            set PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe
        )
    )

    if not defined PYTHON_PATH (
        echo Error: Could not locate Python after installation.
        exit /b 1
    )

    for %%I in ("%PYTHON_PATH%") do set PYTHON_DIR=%~dpI
    set PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%

    python --version >nul 2>nul
    if %errorlevel% neq 0 (
        echo Error: Python is not functional after installation.
        exit /b 1
    )

    echo Python successfully installed and configured.
) else (
    echo Python is already installed.
)

python -m pip --version >nul 2>nul
if %errorlevel% neq 0 (
    python -m ensurepip
)
python -m pip install --upgrade pip

if not exist requirements.txt (
    echo Warning: requirements.txt file not found. Skipping dependency installation.
) else (
    python -m pip install -r requirements.txt
)

echo #@python.exe %~dp0finding_copies.py %* > finding_copies_tmp.py
type finding_copies.py >> finding_copies_tmp.py
move /Y finding_copies_tmp.py finding_copies.py
if %errorlevel% neq 0 (
    echo Error: Failed to update finding_copies.py!
    exit /b 1
)

echo Done!
endlocal