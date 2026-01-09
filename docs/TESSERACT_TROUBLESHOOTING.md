# Tesseract OCR Troubleshooting Guide (Windows)

If you see the error: **"OCR Error: tesseract is not installed or it's not in your PATH"**

## Quick Fix Checklist (Minimal Steps)

### Step 1: Verify Bundle Was Created During Build

**On your BUILD machine** (where you created the installer):
1. Before building, check if `tesseract_bundle` folder exists in project root
2. If it doesn't exist, run:
   ```bat
   python download_tesseract_windows.py
   ```
3. Verify the folder contains:
   - `bin/tesseract.exe` (or `tesseract.exe` in root)
   - `tessdata/` folder with `.traineddata` files

### Step 2: Rebuild the Installer

After ensuring `tesseract_bundle` exists:
```bat
python build_cross_platform.py exe
```

### Step 3: Verify Installation on Test Machine

**On the TEST machine** (where you installed the app):
1. Navigate to installation directory (usually: `C:\Program Files\Bignan Mancha OMR Reader\`)
2. Check if these folders exist:
   - `tesseract_bundle/` or `_internal/tesseract_bundle/`
   - Look for `tesseract.exe` in: `tesseract_bundle/bin/` or `tesseract_bundle/`

### Step 4: Quick Test - Manual Path Check

If bundle exists but still not working, add debug output:

**Temporary fix**: Create a test file `test_tesseract.py` in the installation directory:
```python
import os
import sys

app_dir = os.path.dirname(sys.executable)
possible_paths = [
    os.path.join(app_dir, "tesseract_bundle", "bin"),
    os.path.join(app_dir, "_internal", "tesseract_bundle", "bin"),
    os.path.join(app_dir, "tesseract_bundle"),
]

print("Checking Tesseract paths:")
for path in possible_paths:
    exe_path = os.path.join(path, "tesseract.exe")
    print(f"  {exe_path}: {'EXISTS' if os.path.exists(exe_path) else 'NOT FOUND'}")
```

Run it: `python test_tesseract.py` to see what paths exist.

## Common Issues & Solutions

### Issue 1: Bundle Not Included in Installer
**Symptom**: `tesseract_bundle` folder missing from installation directory

**Fix**: 
- Ensure `tesseract_bundle` exists before building
- Check `.spec` file includes: `('tesseract_bundle', 'tesseract_bundle')`
- Rebuild installer

### Issue 2: Wrong Path Detection
**Symptom**: Bundle exists but wrong location

**Fix**: Check `image_processor.py` line ~140-142 - should set:
```python
pytesseract.pytesseract.tesseract_cmd = tesseract_exe
```

### Issue 3: Missing tessdata
**Symptom**: `tesseract.exe` found but OCR still fails

**Fix**: Ensure `tessdata/` folder was bundled with language files

## Verification Commands

**On BUILD machine** (before building):
```bat
# Check if Tesseract is installed
where tesseract
tesseract --version

# Create bundle manually
python download_tesseract_windows.py

# Verify bundle structure
dir tesseract_bundle /s
```

**On TEST machine** (after installation):
```bat
# Navigate to install directory
cd "C:\Program Files\Bignan Mancha OMR Reader"

# Check for bundle
dir tesseract_bundle /s
dir _internal\tesseract_bundle /s
```

## Most Likely Fix

**90% of cases**: The bundle wasn't created during build.

**Solution**:
1. Install Tesseract on build machine: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default: `C:\Program Files\Tesseract-OCR`
3. Run: `python download_tesseract_windows.py`
4. Verify `tesseract_bundle/` folder exists
5. Rebuild: `python build_cross_platform.py exe`
6. Test new installer

---

**Still not working?** Check `image_processor.py` logs - the `configure_tesseract()` function should print which path it's using.

