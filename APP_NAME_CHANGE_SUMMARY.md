# Application Name Change Summary

## Change Details

**Previous Name:** Image Folder Analyzer  
**New Name:** Bignan Mancha OMR Reader  
**Version:** 2.0.0  
**Date:** October 11, 2025

---

## What Changed

### Application Identity
- **Application Name:** "Bignan Mancha OMR Reader"
- **Bundle ID:** `com.bignanmancha.omr.reader`
- **Author:** Bignan Mancha
- **Description:** OMR (Optical Mark Recognition) sheet processing and analysis tool

### Files Updated

1. **`build_config.py`** ✅
   - `APP_NAME = "Bignan Mancha OMR Reader"`
   - `APP_VERSION = "2.0.0"`
   - `APP_BUNDLE_ID = "com.bignanmancha.omr.reader"`
   - `APP_AUTHOR = "Bignan Mancha"`
   - Updated description to reflect OMR focus

2. **`ui/main_window.py`** ✅
   - Window title: "Bignan Mancha OMR Reader"
   - About dialog updated with new name
   - Description: "OMR (Optical Mark Recognition) sheet processing and analysis tool"

3. **`main.py`** ✅
   - `app.setApplicationName("Bignan Mancha OMR Reader")`
   - `app.setApplicationVersion("2.0")`
   - Flask server message updated

4. **Spec File** ✅
   - Renamed: `Image Folder Analyzer.spec` → `Bignan Mancha OMR Reader.spec`
   - Updated executable name
   - Updated bundle name for macOS
   - Updated bundle identifier

5. **`README.md`** ✅
   - Updated title and description
   - Focus on OMR sheet processing

6. **`CHANGELOG.md`** ✅
   - Added rebranding details
   - Noted previous name for reference

---

## Build Implications

### When You Build

The build will now create:

**Windows:**
```
Bignan_Mancha_OMR_Reader_v2.0_Setup.exe
```

**macOS:**
```
Bignan_Mancha_OMR_Reader_v2.0.dmg
```

**Directory Structure:**
```
dist/
└── Bignan Mancha OMR Reader/
    ├── Bignan Mancha OMR Reader.exe (Windows)
    └── _internal/...
```

### Build Command

No changes needed! Still use:
```bash
python build_cross_platform.py
```

The build script reads from `build_config.py` automatically.

---

## User Impact

### What Users Will See

1. **Application Window Title:**
   - Old: "Image Folder Analyzer"
   - New: "Bignan Mancha OMR Reader"

2. **About Dialog:**
   - Old: "Image Folder Analyzer v1.0"
   - New: "Bignan Mancha OMR Reader v2.0"

3. **Installer Name:**
   - Old: `Image_Folder_Analyzer_v1.0_Setup.exe`
   - New: `Bignan_Mancha_OMR_Reader_v2.0_Setup.exe`

4. **Installation Directory (Windows):**
   - Old: `C:\Program Files\Image Folder Analyzer\`
   - New: `C:\Program Files\Bignan Mancha OMR Reader\`

### For Existing Users

If upgrading from v1.x:
- Old installation can remain (different directory)
- Or uninstall old version first
- No data migration needed (separate installations)

---

## Technical Details

### PyInstaller Spec File

The spec file was renamed and updated:
- **Old:** `Image Folder Analyzer.spec`
- **New:** `Bignan Mancha OMR Reader.spec`

**Contents updated:**
```python
exe = EXE(
    name='Bignan Mancha OMR Reader',  # Executable name
    ...
)
coll = COLLECT(
    name='Bignan Mancha OMR Reader',  # Bundle folder name
    ...
)
app = BUNDLE(
    name='Bignan Mancha OMR Reader.app',  # macOS app name
    bundle_identifier='com.bignanmancha.omr.reader',  # macOS bundle ID
)
```

### Build Configuration

All build settings now read from `build_config.py`:
```python
APP_NAME = "Bignan Mancha OMR Reader"
APP_VERSION = "2.0.0"
APP_BUNDLE_ID = "com.bignanmancha.omr.reader"
APP_AUTHOR = "Bignan Mancha"
```

---

## Verification Checklist

Before building and distributing:

- [ ] Run the application: `python main.py`
- [ ] Check window title shows "Bignan Mancha OMR Reader"
- [ ] Check Help → About shows correct name and version
- [ ] Build the installer: `python build_cross_platform.py`
- [ ] Verify installer filename includes "Bignan_Mancha_OMR_Reader"
- [ ] Install and verify installation directory name
- [ ] Test PDF extraction still works
- [ ] Check About dialog in installed version

---

## Documentation

### Files That Reference Old Name

The following documentation files may still reference "Image Folder Analyzer":
- Various `.md` guide files (historical context OK)
- Build guides (referring to old versions)
- License file (if it mentions the app name)

These can be updated as needed, but aren't critical for functionality.

---

## Quick Reference

### New Application Identity

| Property | Value |
|----------|-------|
| **Name** | Bignan Mancha OMR Reader |
| **Version** | 2.0.0 |
| **Bundle ID** | com.bignanmancha.omr.reader |
| **Author** | Bignan Mancha |
| **Description** | OMR sheet processing and analysis tool |
| **Platform** | Windows, macOS, Linux |

### Key Files Changed

| File | Status | Change |
|------|--------|--------|
| `build_config.py` | ✅ Updated | All app identity fields |
| `ui/main_window.py` | ✅ Updated | Window title, About dialog |
| `main.py` | ✅ Updated | Qt app name and version |
| Spec file | ✅ Renamed & Updated | All references |
| `README.md` | ✅ Updated | Title and description |
| `CHANGELOG.md` | ✅ Updated | Added rebranding details |

---

## Next Steps

### Immediate
1. ✅ All core files updated
2. ✅ Spec file renamed
3. ✅ Version bumped to 2.0.0
4. ✅ Ready to build!

### Before Release
- Update any remaining documentation references (optional)
- Create release notes mentioning name change
- Update any website/marketing materials
- Inform existing users about the rebrand

### Build & Distribute
```bash
# Build with new name
python build_cross_platform.py

# The output will be:
# Windows: Bignan_Mancha_OMR_Reader_v2.0_Setup.exe
# macOS: Bignan_Mancha_OMR_Reader_v2.0.dmg
```

---

## Summary

✅ **Application successfully rebranded to "Bignan Mancha OMR Reader"**  
✅ **Version updated to 2.0.0**  
✅ **All critical files updated**  
✅ **Ready to build and distribute**

The application will now be distributed as "Bignan Mancha OMR Reader v2.0" with automatic Poppler bundling for Windows!

---

**Date:** October 11, 2025  
**Status:** ✅ Complete  
**Ready for:** Build & Distribution

