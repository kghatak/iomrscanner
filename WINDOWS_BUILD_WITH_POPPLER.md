# Building Windows Bundle with Poppler

This guide explains how to build a Windows executable that includes Poppler, eliminating the need for users to install it separately.

---

## Overview

With the automatic Poppler bundling feature:
- ✅ **Poppler is automatically downloaded** during the build process
- ✅ **Poppler is bundled into the executable**
- ✅ **Users don't need to install anything**
- ✅ **PDF extraction works out of the box**

---

## Quick Start (Automatic)

Simply run the build script - it will handle everything automatically:

```bash
python build_cross_platform.py
```

The build script will:
1. Detect that you're on Windows
2. Check if Poppler bundle exists
3. Download Poppler automatically if needed (~15 MB, one-time download)
4. Include Poppler in the Windows executable
5. Create the installer

**That's it!** The resulting executable will have Poppler bundled.

---

## Manual Poppler Download (Optional)

If the automatic download fails or you want to download Poppler separately:

```bash
python download_poppler_windows.py
```

This will:
- Download Poppler for Windows (latest version)
- Extract it to `poppler_bundle/`
- Prepare it for bundling

Then run the build:

```bash
python build_cross_platform.py
```

---

## Build Process Details

### What Happens During Build

1. **Poppler Check** (Windows only)
   - Checks if `poppler_bundle/` exists
   - If not found, downloads automatically
   - Asks for confirmation if download fails

2. **PyInstaller Bundling**
   - Uses `Image Folder Analyzer.spec` file
   - Includes `poppler_bundle/` in the bundle
   - Places Poppler files in `_internal/poppler_bundle/`

3. **Runtime Detection**
   - App checks for bundled Poppler first
   - Falls back to system installation if needed
   - Shows clear error if Poppler not found

### Directory Structure in Bundled App

```
Image Folder Analyzer/
├── Image Folder Analyzer.exe
└── _internal/
    ├── poppler_bundle/
    │   └── bin/
    │       ├── pdfinfo.exe
    │       ├── pdftoppm.exe
    │       ├── pdftotext.exe
    │       └── *.dll files
    ├── ui/
    └── other dependencies...
```

---

## File Changes Summary

### New Files Created

1. **`download_poppler_windows.py`**
   - Script to download and prepare Poppler
   - Downloads from official poppler-windows repo
   - Organizes files for bundling

2. **`poppler_bundle/`** (created during build)
   - Contains Poppler binaries
   - Automatically added to .gitignore
   - Included in executable bundle

### Modified Files

1. **`pdf_utils.py`**
   - Now checks for bundled Poppler first
   - Detects PyInstaller frozen state
   - Priority: bundled > system PATH > user installation

2. **`Image Folder Analyzer.spec`**
   - Updated to include `poppler_bundle/` in datas
   - Checks if bundle exists before including
   - Shows warning if bundle not found on Windows

3. **`build_cross_platform.py`**
   - Added `download_poppler_for_windows()` function
   - Automatically downloads Poppler if missing
   - Prompts user if download fails

4. **`.gitignore`**
   - Added `poppler_bundle/` and `build_deps/`
   - Removed `*.spec` so spec file is tracked

---

## Build Commands Reference

### Standard Build (Recommended)
```bash
python build_cross_platform.py
```
Builds for current platform with automatic Poppler handling.

### Build with Pre-downloaded Poppler
```bash
# Step 1: Download Poppler
python download_poppler_windows.py

# Step 2: Build
python build_cross_platform.py
```

### Using Spec File Directly
```bash
# Ensure Poppler is downloaded first
python download_poppler_windows.py

# Build with spec file
pyinstaller --clean --noconfirm "Image Folder Analyzer.spec"
```

---

## Testing the Bundled App

### Before Distribution
1. **Build the application**
   ```bash
   python build_cross_platform.py
   ```

2. **Find the executable**
   ```
   dist/Image Folder Analyzer/Image Folder Analyzer.exe
   ```

3. **Test on a clean machine** (important!)
   - Copy the entire `dist/Image Folder Analyzer/` folder
   - Test on a Windows machine WITHOUT Poppler installed
   - Try File → Open PDF with a test PDF
   - Should work without any errors

### Expected Behavior
- ✅ PDF opens without asking to install Poppler
- ✅ Images extracted successfully
- ✅ No error messages about missing Poppler
- ✅ Works on machines without Poppler in PATH

---

## Troubleshooting

### "Poppler bundle not found" During Build

**Problem:** Build script says Poppler bundle not found and automatic download failed.

**Solution:**
```bash
# Download manually
python download_poppler_windows.py

# Verify it was created
dir poppler_bundle

# Then build again
python build_cross_platform.py
```

### Build Succeeds but PDF Doesn't Work in Executable

**Problem:** Built exe shows "Poppler not found" error.

**Causes & Solutions:**

1. **Poppler wasn't included in bundle**
   - Check `dist/Image Folder Analyzer/_internal/poppler_bundle/`
   - Should contain `bin/` folder with .exe and .dll files
   - If missing, re-run: `python download_poppler_windows.py`

2. **Spec file didn't include Poppler**
   - Check `Image Folder Analyzer.spec`
   - Should have `(poppler_bundle', 'poppler_bundle')` in datas
   - Rebuild with clean: `pyinstaller --clean "Image Folder Analyzer.spec"`

3. **Wrong directory structure**
   - Verify: `dist/Image Folder Analyzer/_internal/poppler_bundle/bin/pdfinfo.exe` exists
   - If not, check `download_poppler_windows.py` output

### Manual Verification

**Check bundled Poppler files:**
```bash
# After build, check if Poppler is included
dir "dist\Image Folder Analyzer\_internal\poppler_bundle\bin"

# Should show:
# pdfinfo.exe
# pdftoppm.exe
# pdftotext.exe
# Various .dll files
```

**Check spec file:**
```bash
# Look for poppler in spec file
findstr /C:"poppler_bundle" "Image Folder Analyzer.spec"

# Should show:
# if os.path.exists(poppler_bundle_path) and sys.platform == 'win32':
#     datas_list.append((poppler_bundle_path, 'poppler_bundle'))
```

---

## Distribution

### What to Distribute

**Option 1: Directory Bundle (Recommended for testing)**
```
dist/Image Folder Analyzer/
```
The entire folder - just zip it and distribute.

**Option 2: NSIS Installer (Recommended for end users)**
```
Image_Folder_Analyzer_v1.0_Setup.exe
```
Created automatically by build script if NSIS is installed.

### Size Information

- **Without bundled Poppler:** ~50-80 MB
- **With bundled Poppler:** ~65-95 MB
- **Poppler bundle alone:** ~15 MB

The extra 15 MB ensures users don't need to install anything.

---

## User Experience Comparison

### Before (Without Bundled Poppler)
1. User downloads and installs your app
2. User tries to open PDF
3. ❌ Error: "Poppler not found"
4. User must:
   - Download Poppler separately
   - Extract to specific location
   - Add to PATH or configure manually
   - Restart app
5. ✅ PDF finally works

### After (With Bundled Poppler)
1. User downloads and installs your app
2. User tries to open PDF
3. ✅ PDF works immediately
4. No additional steps needed

**Much better user experience!**

---

## Developer Notes

### Poppler Detection Priority (Windows)

```python
1. System PATH (shutil.which)
2. Bundled in executable (_internal/poppler_bundle/bin)
3. Next to executable (poppler_bundle/bin)
4. User installation (C:\poppler\...)
5. Program Files installation
6. Error: Not found
```

### Adding Custom Poppler Version

To use a different Poppler version:

1. Edit `download_poppler_windows.py`:
   ```python
   POPPLER_VERSION = "24.08.0-0"  # Change this
   ```

2. Download and rebuild:
   ```bash
   python download_poppler_windows.py
   python build_cross_platform.py
   ```

### Updating Poppler

To update to a newer Poppler version:

```bash
# Remove old bundle
rmdir /s /q poppler_bundle
rmdir /s /q build_deps

# Download new version (update version in script first)
python download_poppler_windows.py

# Rebuild
python build_cross_platform.py
```

---

## CI/CD Integration

For automated builds with CI/CD:

```yaml
# Example: GitHub Actions
- name: Download Poppler for Windows
  if: runner.os == 'Windows'
  run: python download_poppler_windows.py

- name: Build Windows Executable
  if: runner.os == 'Windows'
  run: python build_cross_platform.py
```

This ensures Poppler is downloaded and bundled in automated builds.

---

## FAQ

### Q: Do I need to download Poppler every time I build?
**A:** No, once downloaded, `poppler_bundle/` persists. Only needs downloading once (or after deleting the folder).

### Q: Can I commit poppler_bundle to git?
**A:** Not recommended. The bundle is 15+ MB and platform-specific. It's in .gitignore by default. Download during build instead.

### Q: What if automatic download fails?
**A:** The build script will ask if you want to continue without bundled Poppler. You can also manually download from: https://github.com/oschwartz10612/poppler-windows/releases/

### Q: Does this work on macOS/Linux?
**A:** Poppler bundling is Windows-only. On macOS/Linux, users install Poppler via package manager (brew/apt), which is easier.

### Q: How do I verify Poppler is bundled correctly?
**A:** After building, check `dist/Image Folder Analyzer/_internal/poppler_bundle/bin/` contains .exe files. Or test on a machine without Poppler.

### Q: Can I use a different Poppler source?
**A:** Yes! Place Poppler binaries in `poppler_bundle/bin/` before building. The spec file will include whatever's there.

---

## License Note

**Poppler License:** GPL v2

Since you're bundling Poppler (which is GPL), be aware of GPL implications:
- Your application may need to be GPL-compatible
- Consider consulting a legal expert for commercial use
- See: https://poppler.freedesktop.org/

**Alternative:** Don't bundle Poppler, let users install separately (original approach).

---

## Summary

✅ **Build with automatic Poppler bundling:**
```bash
python build_cross_platform.py
```

✅ **Result:** Windows executable with PDF support built-in

✅ **Users:** Don't need to install anything

✅ **Distribution:** Just distribute the exe or installer

---

**Last Updated:** October 2025

