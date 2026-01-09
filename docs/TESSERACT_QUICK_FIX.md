# Tesseract Quick Fix Guide

## Error: "OCR Error: tesseract is not installed or it's not in your PATH"

### Minimal Fix Steps (3 steps)

#### On BUILD Machine (where you create the installer):

**Step 1: Verify Tesseract is installed**
```bat
tesseract --version
```
If this fails, install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
Install to default location: `C:\Program Files\Tesseract-OCR`

**Step 2: Create the bundle**
```bat
python download_tesseract_windows.py
```
This creates `tesseract_bundle/` folder in your project root.

**Step 3: Rebuild installer**
```bat
python build_cross_platform.py exe
```

---

### Quick Verification

**After building**, check that `tesseract_bundle` exists:
```bat
dir tesseract_bundle
```

**After installing on test machine**, check installation directory:
```
C:\Program Files\Bignan Mancha OMR Reader\tesseract_bundle\bin\tesseract.exe
```
or
```
C:\Program Files\Bignan Mancha OMR Reader\_internal\tesseract_bundle\bin\tesseract.exe
```

---

### If Still Not Working

**Check application logs** - The application now prints where it's looking for Tesseract:
- Look for lines starting with `[Tesseract]` in console output or logs
- This tells you which path is being checked

**Manual verification** on test machine:
1. Navigate to: `C:\Program Files\Bignan Mancha OMR Reader\`
2. Check if `tesseract_bundle` folder exists
3. Check if `tesseract.exe` is in `tesseract_bundle\bin\` or `_internal\tesseract_bundle\bin\`

If bundle is missing → Build process didn't include it. Go back to Step 2.
If bundle exists but app can't find it → Check logs for path detection issues.

