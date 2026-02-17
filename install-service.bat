@echo off
REM Install UserReport as Windows Service via NSSM. Run as Administrator.
setlocal

set NSSM=C:\nssm-2.24\win64\nssm.exe
set PROJECT=%~dp0
set PROJECT=%PROJECT:~0,-1%
set PYTHON=python

REM Use full path if python not on PATH, e.g. set PYTHON=C:\Python311\python.exe

if not exist "%NSSM%" (
  echo NSSM not found at %NSSM%
  echo Use win64 or win32 from NSSM install, not the src folder.
  exit /b 1
)

echo Installing UserReport service...
echo Project: %PROJECT%
echo Python:  %PYTHON%

"%NSSM%" install UserReport "%PYTHON%" "app.py"
"%NSSM%" set UserReport AppDirectory "%PROJECT%"
"%NSSM%" set UserReport DisplayName "UserReport"
"%NSSM%" set UserReport Description "Image Task & Result web app"

echo.
echo Service installed. Start with: sc start UserReport
echo Or: "%NSSM%" start UserReport
pause
