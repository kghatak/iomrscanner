# Image Folder Analyzer - macOS Installer

This script creates a macOS installer for the Image Folder Analyzer application.

## Quick Start

1. **Make sure you're in the virtual environment:**
   ```bash
   source qt_env/bin/activate
   ```

2. **Run the build script:**
   ```bash
   python build_installer.py
   ```

## What the installer creates:

### Option 1: DMG Installer (Preferred)
- Creates a `.dmg` file that users can double-click
- Professional-looking installer with drag-to-Applications
- Automatically handles app signing (if certificates are available)

### Option 2: ZIP Installer (Fallback)
- Creates a `.zip` file with the app and instructions
- Simple and reliable
- No additional dependencies required

## Build Process:

1. **Installs PyInstaller** - Converts Python app to macOS bundle
2. **Creates App Bundle** - Packages everything into `AppName.app`
3. **Creates Installer** - Either DMG or ZIP format
4. **Includes Instructions** - User-friendly installation guide

## Output Files:

- `Image_Folder_Analyzer.app` - The standalone application
- `Image_Folder_Analyzer_v1.0.0.dmg` - DMG installer (if successful)
- `Image_Folder_Analyzer_v1.0.0_macOS.zip` - ZIP installer (fallback)

## Distribution:

Users can install by:
1. **DMG**: Double-click, drag app to Applications
2. **ZIP**: Extract, drag app to Applications

## Troubleshooting:

### If build fails:
- Ensure all dependencies are installed in virtual environment
- Check that `main.py` exists in current directory
- Try the ZIP installer option if DMG creation fails

### For end users:
- First run may require right-click → "Open" due to macOS security
- App will be available in Applications folder after installation
