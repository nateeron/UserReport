@echo off
REM Remove UserReport Windows Service. Run as Administrator.
setlocal

set NSSM=C:\nssm-2.24\win64\nssm.exe

echo Stopping UserReport service...
sc stop UserReport 2>nul

echo Removing UserReport service...
"%NSSM%" remove UserReport confirm 2>nul
if errorlevel 1 (
  echo If NSSM not found or service not installed, run: sc delete UserReport
  sc delete UserReport 2>nul
)

echo Done.
pause
