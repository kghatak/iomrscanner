# Windows Installer Guide (Tester)

Use this guide to build the Windows installer (`OMR_Exam_Reader_<version>_Setup.exe`) on a Windows machine.

## Prerequisites (one-time)
- Windows 10 or later
- Python 3.10+ installed with **“Add Python to PATH”** checked
- NSIS installed: https://nsis.sourceforge.io/Download (default options are fine)
- Git installed (for cloning)

## Build Steps
1) Clone and enter the project
```bat
git clone <REPO_URL>
cd pyqt
```

2) Create and activate a virtual environment
```bat
python -m venv qt_env
qt_env\Scripts\activate
```

3) Install dependencies
```bat
pip install --upgrade pip
pip install -r requirements.txt
```

4) Build the Windows installer
```bat
python build_cross_platform.py exe
```

5) Locate the output
- In the project root you should see: `OMR_Exam_Reader_<version>_Setup.exe`
- Example: `OMR_Exam_Reader_2.2.0_Setup.exe`

## What the installer does
- Shows as **“OMR Exam Reader <version>”** in Apps & Features and shortcuts.
- Auto-uninstalls any previous version before installing the new one.

## Quick test
- Double-click the generated `OMR_Exam_Reader_<version>_Setup.exe`.
- After install, launch via Start Menu or desktop shortcut named **“OMR Exam Reader <version>”**.

## Troubleshooting
- **NSIS not found**: Re-run NSIS installer from the link above; ensure `makensis` is on PATH.
- **Python not found**: Reinstall Python 3.10+ with “Add Python to PATH” checked.
- **Dependency install issues**: Run `pip install -r requirements.txt` again; ensure internet access.
- **Build script errors**: Confirm you are in the project root and that `main.py` exists there.

