# Release Notes - Bignan Mancha OMR Reader v2.0.0

**Release Date:** October 11, 2025  
**Version:** 2.0.0  
**Type:** Major Release

---

## 🎉 What's New

### Application Rebranding
- **New Name:** Bignan Mancha OMR Reader (formerly Image Folder Analyzer)
- **Focus:** OMR (Optical Mark Recognition) sheet processing and analysis
- **Version:** Bumped to 2.0.0 to reflect major changes

### 🚀 Major Feature: Automatic Poppler Bundling for Windows

**Problem Solved:** Windows users no longer need to manually install Poppler to use PDF extraction features.

**What This Means:**
- ✅ PDF extraction works out of the box on Windows
- ✅ No manual Poppler installation required
- ✅ Seamless user experience
- ✅ Automatic detection and bundling during build

### New Components

1. **Automatic Poppler Download** (`download_poppler_windows.py`)
   - Downloads Poppler binaries automatically during build
   - One-time download (~15 MB)
   - Caches for future builds

2. **PDF Utilities Module** (`pdf_utils.py`)
   - Cross-platform Poppler detection
   - Intelligent path resolution
   - Priority: bundled → system PATH → user installation
   - Clear error messages with installation instructions

3. **Enhanced Build System**
   - Updated `build_cross_platform.py` with automatic Poppler handling
   - Updated PyInstaller spec to include Poppler bundle
   - Seamless integration into existing build workflow

4. **Comprehensive Documentation**
   - Windows Setup Guide
   - Windows Build with Poppler Guide
   - Complete troubleshooting sections
   - Step-by-step installation instructions

---

## 📦 Installation

### For End Users

**Windows:**
```
Download: Bignan_Mancha_OMR_Reader_v2.0_Setup.exe
Install: Double-click and follow the installer
Run: Start from desktop shortcut or Start Menu
```

**No additional dependencies needed!** PDF extraction works immediately.

### For Developers

**Clone and Setup:**
```bash
git clone <repository-url>
cd pyqt
git checkout v2.0.0
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Build:**
```bash
python build_cross_platform.py
```

---

## 🔧 Technical Changes

### Core Application
- Application name changed to "Bignan Mancha OMR Reader"
- Version bumped to 2.0.0
- Bundle identifier updated: `com.bignanmancha.omr.reader`
- About dialog updated with new branding

### Build System
- PyInstaller spec file renamed and updated
- Automatic Poppler bundling for Windows builds
- Enhanced error handling and user messages
- Build script checks and downloads Poppler automatically

### PDF Processing
- New `pdf_utils.py` module for centralized PDF handling
- Automatic Poppler path detection (bundled, system, user)
- Better error messages with actionable instructions
- Cross-platform support (Windows, macOS, Linux)

### Files Added
- `download_poppler_windows.py` - Poppler download script
- `pdf_utils.py` - PDF utilities module
- `tests/test_pdf_utils.py` - Test suite for PDF utilities
- `docs/WINDOWS_SETUP_GUIDE.md` - Windows setup guide
- `WINDOWS_BUILD_WITH_POPPLER.md` - Build guide
- `WINDOWS_PDF_FIX.md` - Technical documentation
- `ANSWER_WINDOWS_BUNDLE_POPPLER.md` - Bundling explanation
- `CHANGELOG.md` - Version history
- `APP_NAME_CHANGE_SUMMARY.md` - Rebranding details

### Files Modified
- `build_config.py` - Updated app identity
- `main.py` - Updated app name and version
- `ui/main_window.py` - Updated UI text and branding
- `build_cross_platform.py` - Added Poppler handling
- `Bignan Mancha OMR Reader.spec` - Renamed and updated
- `README.md` - Updated documentation
- `.gitignore` - Added poppler_bundle/ and build_deps/
- `requirements.txt` - Added Poppler installation notes

### Files Renamed
- `Image Folder Analyzer.spec` → `Bignan Mancha OMR Reader.spec`

---

## 📊 Bundle Size

- **Without Poppler:** ~50-80 MB
- **With Poppler:** ~65-95 MB
- **Increase:** ~15 MB

**Trade-off:** Slightly larger download for significantly better user experience.

---

## 🐛 Bug Fixes

### Windows PDF Processing Error
**Issue:** "Failed to extract images: Unable to get page count. Is Poppler installed and in the path?"

**Fixed:** 
- Poppler now bundled with Windows executable
- Automatic detection of bundled Poppler
- Clear error messages if Poppler still not found
- Installation instructions provided in error dialogs

---

## 🔄 Migration Guide

### For Users Upgrading from v1.x

1. **Download v2.0 installer**
2. **(Optional)** Uninstall v1.x first
3. **Install v2.0**
4. **Enjoy!** PDF features now work without additional setup

**Note:** If you manually installed Poppler for v1.x, you can:
- Keep it (v2.0 will use bundled version)
- Remove it (no longer needed)

### For Developers

**Update your local repository:**
```bash
git pull origin main
git checkout v2.0.0
```

**Rebuild:**
```bash
python build_cross_platform.py
```

The build script will automatically download Poppler if needed.

---

## 🎯 Breaking Changes

**None!** This release is fully backward compatible.

The application name change is cosmetic and doesn't affect functionality.

---

## 📋 System Requirements

### Windows
- Windows 10 or later (64-bit recommended)
- 100 MB free disk space
- No additional dependencies (Poppler bundled)

### macOS
- macOS 10.14 (Mojave) or later
- Poppler: `brew install poppler`

### Linux
- Ubuntu 18.04+ / Debian 10+ / Fedora 30+
- Poppler: `sudo apt-get install poppler-utils`

---

## 🧪 Testing

Tested on:
- ✅ Windows 10/11
- ✅ macOS (Ventura, Sonoma)
- ✅ Ubuntu 22.04

**Test Cases:**
- ✅ PDF extraction with bundled Poppler
- ✅ PDF extraction with system Poppler
- ✅ Error handling when Poppler missing
- ✅ Cross-platform compatibility
- ✅ Build process automation

---

## 📚 Documentation

### New Documentation
- [Windows Setup Guide](docs/WINDOWS_SETUP_GUIDE.md)
- [Windows Build with Poppler](WINDOWS_BUILD_WITH_POPPLER.md)
- [Windows PDF Fix Details](WINDOWS_PDF_FIX.md)
- [Bundling Explanation](ANSWER_WINDOWS_BUNDLE_POPPLER.md)
- [App Name Change Summary](APP_NAME_CHANGE_SUMMARY.md)

### Updated Documentation
- [README](README.md) - Added system dependencies
- [CHANGELOG](CHANGELOG.md) - Added v2.0.0 details
- [Requirements](requirements.txt) - Added Poppler notes

---

## 🙏 Credits

- **Poppler:** https://poppler.freedesktop.org/
- **Poppler Windows Binaries:** https://github.com/oschwartz10612/poppler-windows
- **PyQt5:** https://www.riverbankcomputing.com/software/pyqt/
- **pdf2image:** https://github.com/Belval/pdf2image

---

## 📞 Support

### Issues?
- Check [WINDOWS_SETUP_GUIDE.md](docs/WINDOWS_SETUP_GUIDE.md)
- Review troubleshooting sections
- Open an issue on GitHub

### Questions?
- Read the documentation
- Check [WINDOWS_BUILD_WITH_POPPLER.md](WINDOWS_BUILD_WITH_POPPLER.md)
- Contact: support@bignanmancha.com

---

## ⚖️ License

**Application:** MIT License (see LICENSE.txt)

**Note:** Poppler is licensed under GPL v2. Since this application bundles Poppler, consider the GPL implications for your use case.

---

## 🔜 What's Next (v2.1.0 Preview)

Planned for next minor release:
- Enhanced OMR sheet detection
- Batch processing improvements
- Performance optimizations
- Additional export formats
- UI/UX enhancements

Stay tuned!

---

## 📥 Download

**Windows:** [Bignan_Mancha_OMR_Reader_v2.0_Setup.exe](releases/v2.0.0)  
**macOS:** [Bignan_Mancha_OMR_Reader_v2.0.dmg](releases/v2.0.0)  
**Linux:** [Bignan_Mancha_OMR_Reader_v2.0.AppImage](releases/v2.0.0)

**Source Code:**
- [ZIP](archive/v2.0.0.zip)
- [TAR.GZ](archive/v2.0.0.tar.gz)

---

**Release Status:** ✅ Stable  
**Recommended:** Yes  
**Upgrade Priority:** High (Windows users with PDF processing needs)

---

**Thank you for using Bignan Mancha OMR Reader!** 🎉

