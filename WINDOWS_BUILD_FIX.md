# Windows Build Character Encoding Fix

## The Problem

When building on Windows, you see:
```
'charmap' codec can't encode characters in position 0-1: character maps to <undefined>
```

### Root Cause
- Windows Command Prompt uses **cp1252/charmap** encoding by default
- Build scripts use **Unicode characters** (✅, ⚠️, ❌) in print statements
- These characters can't be encoded with the default Windows encoding

---

## The Fix

I've updated both build scripts with UTF-8 encoding handling:

### Files Fixed
1. ✅ `build_cross_platform.py`
2. ✅ `download_poppler_windows.py`

### What Changed

Added at the top of each script:
```python
# Fix Windows encoding issues
if sys.platform == 'win32':
    # Set UTF-8 encoding for stdout/stderr
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # Set console to UTF-8
    os.system('chcp 65001 >nul 2>&1')
```

This:
- Forces UTF-8 encoding for output
- Handles encoding errors gracefully (`errors='replace'`)
- Sets Windows console to UTF-8 mode (code page 65001)

---

## Try Building Again

Now you can build without encoding errors:

```bash
python build_cross_platform.py
```

---

## If You Still Have Issues

### Option 1: Use Windows PowerShell (Better Encoding)

Instead of Command Prompt (cmd.exe), use PowerShell:
```powershell
python build_cross_platform.py
```

PowerShell has better UTF-8 support.

### Option 2: Set UTF-8 in Your Terminal

Before running the build:

**Command Prompt:**
```cmd
chcp 65001
python build_cross_platform.py
```

**PowerShell:**
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
python build_cross_platform.py
```

### Option 3: Use Windows Terminal

If you have Windows Terminal (Windows 10/11):
- It has better UTF-8 support by default
- Just run: `python build_cross_platform.py`

---

## Alternative: Plain Text Version

If emoji characters still cause issues, I can create a version without any special characters. Let me know!

---

## Verification

After the fix, the build should show:
```
[BUILD] Checking for Poppler bundle...
[OK] Poppler bundle found
[BUILD] Creating windows app bundle with PyInstaller...
...
```

Instead of crashing with encoding errors.

---

## Summary

✅ **Fixed:** Added UTF-8 encoding handling to build scripts  
✅ **Scripts Updated:** build_cross_platform.py, download_poppler_windows.py  
✅ **Ready:** You can now build on Windows without encoding errors  

**Try building again!** 🚀

