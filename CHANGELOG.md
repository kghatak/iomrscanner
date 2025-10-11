# Changelog

All notable changes to Bignan Mancha OMR Reader (formerly Image Folder Analyzer) will be documented in this file.

## [2.0.0] - 2025-10-11

### 🎉 Major Release - Rebranding & Windows PDF Support

**Application Rebranding:**
- Application renamed to **"Bignan Mancha OMR Reader"**
- Updated to reflect focus on OMR (Optical Mark Recognition) sheet processing
- New bundle identifier: `com.bignanmancha.omr.reader`

This release focuses on making PDF processing seamless for Windows users by automatically bundling Poppler with the application.

### Added
- **Automatic Poppler Bundling** - Poppler binaries are now automatically bundled with Windows installers
- **`download_poppler_windows.py`** - Automated script to download and prepare Poppler for bundling
- **`pdf_utils.py`** - New utility module for cross-platform PDF processing with automatic Poppler detection
- **Intelligent Poppler Detection** - Application now checks bundled Poppler first, then system installation
- **Enhanced Error Messages** - Clear, actionable error messages with installation instructions when Poppler is missing
- **Comprehensive Documentation**:
  - `WINDOWS_BUILD_WITH_POPPLER.md` - Complete guide for building with bundled Poppler
  - `ANSWER_WINDOWS_BUNDLE_POPPLER.md` - Detailed explanation of the bundling solution
  - `WINDOWS_PDF_FIX.md` - Technical documentation of the PDF processing fix
  - `docs/WINDOWS_SETUP_GUIDE.md` - User setup guide for Windows
- **Test Suite** - `tests/test_pdf_utils.py` for testing PDF utilities and Poppler detection

### Changed
- **Build Process** - `build_cross_platform.py` now automatically downloads Poppler for Windows builds
- **PyInstaller Spec** - Updated to include Poppler bundle in Windows distributions
- **PDF Processing** - Refactored to use new `pdf_utils` module with automatic Poppler path detection
- **About Dialog** - Updated to show version 2.0 and new features
- **README.md** - Added system dependencies section with installation instructions
- **requirements.txt** - Added comprehensive notes about Poppler installation for all platforms

### Fixed
- **Windows PDF Error** - Fixed "Unable to get page count" error on Windows machines
- **Missing Poppler** - Users no longer need to manually install Poppler on Windows
- **PDF Extraction** - PDF to image conversion now works out of the box on Windows

### Technical Details

#### Bundle Size
- Application with bundled Poppler: ~65-95 MB (increase of ~15 MB)
- Trade-off: Larger download for seamless user experience

#### Poppler Detection Priority (Windows)
1. Bundled with executable (`_internal/poppler_bundle/bin`)
2. System PATH
3. Common installation directories (`C:\Program Files\poppler`, `C:\poppler`)
4. User installation paths

#### Supported Platforms
- **Windows**: Poppler automatically bundled ✅
- **macOS**: Users install via Homebrew (`brew install poppler`)
- **Linux**: Users install via package manager (`apt-get install poppler-utils`)

### Migration Guide

#### For Developers
No migration needed! The build process is backward compatible:
```bash
# Just build as usual
python build_cross_platform.py
```

#### For End Users
If upgrading from v1.x:
1. Uninstall v1.x (optional - won't conflict)
2. Install v2.0
3. PDF extraction now works without additional setup

If you previously installed Poppler manually:
- It still works! The app will use bundled version first
- You can remove manual Poppler installation if desired

### Breaking Changes
None. This release is fully backward compatible.

### Known Issues
- Poppler bundling is Windows-only (macOS/Linux use system Poppler)
- Poppler is GPL-licensed - consider license implications for commercial use
- Initial build requires ~15 MB download of Poppler (one-time, cached for future builds)

### Credits
- Poppler: https://poppler.freedesktop.org/
- poppler-windows: https://github.com/oschwartz10612/poppler-windows

---

## [1.0.0] - Previous Release

### Initial Release
- Folder analysis with comprehensive statistics
- Image preview with metadata and EXIF data
- Scan mode with automatic slideshow
- Format breakdown and analysis
- Export results functionality
- Modern, responsive UI with resizable panels
- Cross-platform support (Windows, macOS, Linux)
- PDF extraction support (manual Poppler installation required)

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- **Major version** (X.0.0): Breaking changes or major new features
- **Minor version** (0.X.0): New features, backward compatible
- **Patch version** (0.0.X): Bug fixes, backward compatible

---

**Current Version:** 2.0.0  
**Release Date:** October 11, 2025  
**License:** MIT (see LICENSE.txt)

