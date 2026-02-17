# Deploy as Windows Service with NSSM

Use NSSM (Non-Sucking Service Manager) to run the app as a Windows service so it starts on boot and restarts on failure.

## 1. Prerequisites

- **NSSM**: Use the executable from `C:\nssm-2.24\win64\nssm.exe` (64-bit) or `C:\nssm-2.24\win32\nssm.exe` (32-bit). The `src` folder contains source code, not the executable.
- **On the server** you can either:
  - **Option A – Python**: Install Python and run `python app.py` (or register with NSSM).
  - **Option B – No Python**: Build a `.exe` once (on a machine that has Python), then copy the exe + files to the server; no Python needed on the server.

---

## 1b. Build .exe (no Python needed on server)

Build the exe **on a Windows machine that has Python** (e.g. your dev PC).

1. Open Command Prompt in the project folder:
   ```bat
   cd /d G:\M_save\UserReport
   ```
2. Run:
   ```bat
   build-exe.bat
   ```
   This installs PyInstaller (if needed) and creates `dist\UserReport.exe`.

3. **Deploy folder on the server**: create a folder (e.g. `C:\UserReport`) and copy into it:
   - `dist\UserReport.exe`
   - `image-task-result.html`
   - `editimage.html`
   - `data.json` (or leave empty; the app will create it on first run)
   - Folder `image\` (can be empty)

4. **Run the exe**: Double-click `UserReport.exe` or run from command line. The app uses the **folder where the exe lives** for HTML, `image/`, and `data.json`.

5. **Register as NSSM service** (see below): use **Path** = `C:\UserReport\UserReport.exe`, **Startup directory** = `C:\UserReport`, no arguments.

---

## 2. Install the service (GUI)

1. Open **Command Prompt or PowerShell as Administrator**.
2. Run:
   ```bat
   C:\nssm-2.24\win64\nssm.exe install UserReport
   ```
3. In the NSSM GUI:
   - **Application** tab:
     - **Path**: `C:\Python311\python.exe` (or `python` if on PATH).
     - **Startup directory**: `G:\M_save\UserReport` (your project folder).
     - **Arguments**: `app.py`
   - **Details** tab:
     - **Display name**: `UserReport`
     - **Description**: `Image Task & Result web app`
   - **I/O** tab (optional): set stdout/stderr log paths, e.g. `G:\M_save\UserReport\logs\service.log`.
4. Click **Install service**.

## 3. Install the service (command line)

Run in **elevated** Command Prompt (replace paths if needed).

**If using Python on the server:**
```bat
set NSSM=C:\nssm-2.24\win64\nssm.exe
set PROJECT=G:\M_save\UserReport
set PYTHON=C:\Python311\python.exe

%NSSM% install UserReport "%PYTHON%" "app.py"
%NSSM% set UserReport AppDirectory "%PROJECT%"
%NSSM% set UserReport DisplayName "UserReport"
%NSSM% set UserReport Description "Image Task & Result web app"
```

**If using the .exe (no Python):**
```bat
set NSSM=C:\nssm-2.24\win64\nssm.exe
set PROJECT=C:\UserReport

%NSSM% install UserReport "%PROJECT%\UserReport.exe"
%NSSM% set UserReport AppDirectory "%PROJECT%"
%NSSM% set UserReport DisplayName "UserReport"
%NSSM% set UserReport Description "Image Task & Result web app"
```
(Do not pass any arguments to the exe.)

Then start the service:

```bat
sc start UserReport
```

## 4. Useful commands

| Action        | Command |
|---------------|--------|
| Start         | `sc start UserReport` or `nssm start UserReport` |
| Stop          | `sc stop UserReport` or `nssm stop UserReport` |
| Restart       | `nssm restart UserReport` |
| Remove service | `C:\nssm-2.24\win64\nssm.exe remove UserReport confirm` |
| Edit service  | `C:\nssm-2.24\win64\nssm.exe edit UserReport` |
| Status        | `sc query UserReport` |

## 5. Optional: log directory

Create a log folder so NSSM can write stdout/stderr:

```bat
mkdir G:\M_save\UserReport\logs
```

In NSSM GUI → **I/O** tab set:
- **Output (stdout)**: `G:\M_save\UserReport\logs\service.log`
- **Error (stderr)**: `G:\M_save\UserReport\logs\service-error.log`

Or via CLI:

```bat
%NSSM% set UserReport AppStdout "G:\M_save\UserReport\logs\service.log"
%NSSM% set UserReport AppStderr "G:\M_save\UserReport\logs\service-error.log"
%NSSM% set UserReport AppStdoutCreationDisposition 4
%NSSM% set UserReport AppStderrCreationDisposition 4
```
(4 = append to existing file)

## 6. If using Node (server.js) instead of Flask

```bat
set NSSM=C:\nssm-2.24\win64\nssm.exe
set PROJECT=G:\M_save\UserReport
set NODE=C:\Program Files\nodejs\node.exe

%NSSM% install UserReport "%NODE%" "server.js"
%NSSM% set UserReport AppDirectory "%PROJECT%"
%NSSM% set UserReport DisplayName "UserReport"
sc start UserReport
```

## 7. Troubleshooting

- **Service won't start**: Check Event Viewer → Windows Logs → Application, or run from command line first: `cd /d G:\M_save\UserReport` then `python app.py` (or run `UserReport.exe`) to see errors.
- **Wrong Python**: Use full path to the same Python where you installed requirements (`pip install -r requirements.txt`).
- **.exe “file not found” for HTML/data**: Ensure the exe is in the same folder as `image-task-result.html`, `editimage.html`, `image\`, and `data.json`, and that NSSM **AppDirectory** is set to that folder.
- **Port 5000 in use**: Change port in `app.py` (e.g. `app.run(host="0.0.0.0", port=5001)`) and restart the service (rebuild exe if you use the exe).
