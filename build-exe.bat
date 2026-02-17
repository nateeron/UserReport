@echo off
REM Build UserReport.exe with PyInstaller. Requires Python installed on THIS machine.
echo Building UserReport.exe ...
echo.

REM Install PyInstaller if needed
pip install -r requirements-build.txt

REM Build one-file exe. At runtime the exe uses the folder it lives in for image/, data.json, *.html
pyinstaller --onefile --name UserReport --clean ^
  --hidden-import=werkzeug.security ^
  app.py

if errorlevel 1 (
  echo Build failed.
  exit /b 1
)

echo.
echo Done. Output: dist\UserReport.exe
echo.
echo Deploy: copy dist\UserReport.exe into a folder that also has:
echo   image-task-result.html, editimage.html, image\ (folder), data.json
echo Then run UserReport.exe from that folder (or register with NSSM using that folder as AppDirectory).
pause
