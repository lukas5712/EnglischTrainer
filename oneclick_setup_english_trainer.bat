@echo off
setlocal EnableExtensions

cd /d "%~dp0"

set "APP_FILE=english_trainer.py"
set "VENV_DIR=.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "PYTHON_URL=https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe"
set "PYTHON_INSTALLER=%TEMP%\python-3.12.9-amd64.exe"
set "BASE_PY="

echo ================================
echo   English Trainer 
echo ================================
echo.

if not exist "%APP_FILE%" (
    echo FEHLER: "%APP_FILE%" wurde nicht gefunden.
    echo Diese BAT-Datei muss im selben Ordner wie %APP_FILE% liegen.
    echo.
    pause
    exit /b 1
)

rem Vorhandene .venv pruefen
if exist "%VENV_PY%" (
    "%VENV_PY%" -V >nul 2>nul
    if not errorlevel 1 goto RUN_APP

    echo Vorhandene .venv ist defekt oder stammt von einem anderen Rechner.
    echo Sie wird geloescht und neu erstellt...
    echo.
    rmdir /s /q "%VENV_DIR%" >nul 2>nul
)

call :FIND_PYTHON
if defined BASE_PY goto SETUP_ENV

echo Python wurde nicht gefunden.
echo Python wird jetzt automatisch heruntergeladen und installiert...
echo.

where powershell >nul 2>nul
if errorlevel 1 (
    echo FEHLER: PowerShell wurde nicht gefunden.
    echo Bitte Python manuell installieren und die Datei danach erneut starten.
    echo.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "try { Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%' } catch { exit 1 }"
if errorlevel 1 (
    echo FEHLER: Python konnte nicht heruntergeladen werden.
    echo Bitte Internetverbindung oder Firewall pruefen.
    echo.
    pause
    exit /b 1
)

if not exist "%PYTHON_INSTALLER%" (
    echo FEHLER: Die Python-Installationsdatei wurde nicht gefunden.
    echo.
    pause
    exit /b 1
)

echo Python wird installiert...
"%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_launcher=1 SimpleInstall=1
if errorlevel 1 (
    echo FEHLER: Python konnte nicht installiert werden.
    echo.
    pause
    exit /b 1
)

call :FIND_PYTHON
if not defined BASE_PY (
    echo FEHLER: Python wurde installiert, aber nicht gefunden.
    echo Starte den PC neu und versuche es erneut.
    echo.
    pause
    exit /b 1
)

:SETUP_ENV
echo Erstelle Python-Umgebung...
"%BASE_PY%" -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo FEHLER: .venv konnte nicht erstellt werden.
    echo.
    pause
    exit /b 1
)

if not exist "%VENV_PY%" (
    echo FEHLER: "%VENV_PY%" wurde nicht erstellt.
    echo.
    pause
    exit /b 1
)

echo Installiere Pakete...
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 (
    echo FEHLER: pip konnte nicht aktualisiert werden.
    echo.
    pause
    exit /b 1
)

if exist "requirements.txt" (
    "%VENV_PY%" -m pip install -r requirements.txt
) else (
    "%VENV_PY%" -m pip install openai
)

if errorlevel 1 (
    echo FEHLER: Pakete konnten nicht installiert werden.
    echo.
    pause
    exit /b 1
)

:RUN_APP
echo.
echo Starte Anwendung...
"%VENV_PY%" "%APP_FILE%"
if errorlevel 1 (
    echo.
    echo FEHLER: Die Anwendung wurde mit einem Fehler beendet.
    pause
    exit /b 1
)

exit /b 0

:FIND_PYTHON
set "BASE_PY="

where python >nul 2>nul
if not errorlevel 1 (
    python --version >nul 2>nul
    if not errorlevel 1 set "BASE_PY=python"
)

if not defined BASE_PY (
    where py >nul 2>nul
    if not errorlevel 1 (
        py --version >nul 2>nul
        if not errorlevel 1 set "BASE_PY=py"
    )
)

if not defined BASE_PY (
    if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "BASE_PY=%LocalAppData%\Programs\Python\Python312\python.exe"
)

exit /b 0
