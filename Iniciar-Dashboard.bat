@echo off
rem Python Learning Dashboard: doble clic para abrirlo en este PC.
rem La primera vez crea el entorno e instala las dependencias (1-2 minutos).
setlocal EnableExtensions
title Python Learning Dashboard
cd /d "%~dp0"

set "VENV=.venv-local"
set "VPY=%VENV%\Scripts\python.exe"

if exist "%VPY%" goto deps

echo [1/3] Buscando Python 3.11 o superior...
set "PY="
where py >nul 2>nul && py -3 -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && python -c "import sys; sys.exit(sys.version_info < (3, 11))" >nul 2>nul && set "PY=python"
if not defined PY goto nopython

echo [1/3] Creando el entorno virtual, solo la primera vez...
%PY% -m venv "%VENV%"
if errorlevel 1 goto error

:deps
fc /b "backend\requirements.txt" "%VENV%\requirements.installed" >nul 2>nul
if not errorlevel 1 goto run
echo [2/3] Instalando dependencias, solo cuando cambian...
"%VPY%" -m pip install --disable-pip-version-check -q -r "backend\requirements.txt"
if errorlevel 1 goto error
copy /y "backend\requirements.txt" "%VENV%\requirements.installed" >nul

:run
echo [3/3] Arrancando el Python Learning Dashboard...
"%VPY%" "scripts\run_local.py"
if errorlevel 1 goto error
exit /b 0

:nopython
echo.
echo No se ha encontrado Python 3.11 o superior.
echo Instalalo con este comando y vuelve a abrir este archivo:
echo.
echo     winget install --id Python.Python.3.12
echo.
pause
exit /b 1

:error
echo.
echo Algo ha fallado. Revisa los mensajes de arriba o consulta docs\EJECUTAR-EN-WINDOWS.md
pause
exit /b 1
