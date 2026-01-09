# Cross-Platform Build Guide

This guide explains how to build the Image Folder Analyzer for different platforms.

## 🖥️ Building for Windows (EXE)

### Prerequisites
1. **Python 3.9+** with PyQt5
2. **NSIS** (Nullsoft Scriptable Install System)
   - Download from: https://nsis.sourceforge.io/Download
   - Install to default location

### Steps to Build Windows EXE

1. **On Windows machine** (or Windows VM):
   ```bash
   # Clone repository
   git clone <your-repo-url>
   cd pyqt

   # Create virtual environment
   python -m venv qt_env
   qt_env\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Build Windows EXE
   python build_cross_platform.py
   ```

2. **Output files**:
   - `Image_Folder_Analyzer_v1.0.0_Setup.exe` - Professional installer
   - `dist/Image Folder Analyzer/` - Standalone app folder

### Alternative: Cross-compile from macOS/Linux
```bash
# Install Wine (for running Windows tools)
# On macOS with Homebrew:
brew install wine

# Then run the build script
python build_cross_platform.py
```

## 🍎 Building for macOS (DMG)

### Prerequisites
1. **macOS** with Xcode command line tools
2. **Python 3.9+** with PyQt5

### Steps
```bash
# Use existing build script
python build_installer.py
# OR use cross-platform script
python build_cross_platform.py
```

## 🐧 Building for Linux (AppImage)

### Prerequisites
1. **Linux** distribution
2. **Python 3.9+** with PyQt5
3. **AppImageTool** (optional, for AppImage creation)

### Steps
```bash
# Install AppImageTool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool

# Build
python build_cross_platform.py
```

## 📁 Asset Files (Optional)

Create an `assets/` folder with platform-specific icons:

```
assets/
├── app_icon.ico     # Windows icon (256x256)
├── app_icon.icns    # macOS icon bundle
├── app_icon.png     # Linux icon (256x256)
└── dmg_background.png  # macOS DMG background
```

### Creating Icons

1. **Start with a high-resolution PNG** (512x512 or 1024x1024)

2. **Windows ICO**:
   - Use online converter or tools like GIMP
   - Include multiple sizes: 16x16, 32x32, 48x48, 256x256

3. **macOS ICNS**:
   ```bash
   # Create iconset folder
   mkdir MyIcon.iconset
   # Add different sizes (16x16 to 1024x1024)
   # Convert to icns
   iconutil -c icns MyIcon.iconset
   ```

4. **Linux PNG**:
   - Simple 256x256 PNG file

## 🚀 Automated CI/CD Builds

### GitHub Actions (example)
```yaml
name: Build Cross-Platform

on: [push, pull_request]

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    
    runs-on: ${{ matrix.os }}
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Build application
      run: |
        python build_cross_platform.py
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: ${{ matrix.os }}-build
        path: |
          *.exe
          *.dmg
          *.zip
```

## 📋 Platform-Specific Notes

### Windows
- **Requires NSIS** for professional installers
- **Antivirus software** may flag unsigned executables
- **Code signing** recommended for distribution
- **Admin rights** may be required for installation

### macOS
- **Notarization** required for distribution outside App Store
- **Developer ID** certificate needed for signing
- **Gatekeeper** may block unsigned apps

### Linux
- **Distribution-specific** package managers preferred
- **AppImage** provides universal compatibility
- **Dependencies** may vary between distributions

## 🔧 Troubleshooting

### Common Issues

1. **Missing dependencies**:
   ```bash
   pip install --upgrade pyinstaller pillow PyQt5
   ```

2. **Permission errors**:
   - Run as administrator (Windows)
   - Use `sudo` where needed (Linux/macOS)

3. **Large file sizes**:
   - Use `--exclude-module` in PyInstaller
   - Optimize images and assets

4. **Startup issues**:
   - Test in clean environment
   - Check for missing DLLs/libraries

### Build Optimization

```python
# Add to PyInstaller command for smaller builds
--exclude-module matplotlib
--exclude-module numpy.random._examples
--exclude-module tkinter
```

## 📦 Distribution

### File Naming Convention
- Windows: `AppName_v1.0.0_Setup.exe`
- macOS: `AppName_v1.0.0.dmg`
- Linux: `AppName_v1.0.0_linux.zip` or `AppName_v1.0.0.AppImage`

### Upload Locations
- **GitHub Releases** - For open source projects
- **Company server** - For internal distribution
- **App stores** - For commercial distribution
