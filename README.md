# 📁 Image Folder Analyzer

A modern PyQt5 desktop application for analyzing OMR sheets folders with professional cross-platform build support.

## ✨ Features

- **📁 Folder Analysis** - Get comprehensive statistics about image folders
- **🖼️ Image Preview** - View images with detailed metadata and EXIF data
- **🔍 Scan Mode** - Automatic slideshow through all images (20-second intervals)
- **📊 Format Breakdown** - Detailed analysis of image formats and sizes
- **⬆️ Export Results** - Save analysis reports to text files
- **🎨 Modern UI** - Clean, responsive interface with resizable panels

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd pyqt
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv qt_env
   source qt_env/bin/activate  # On Windows: qt_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```
4.1 **Run the application witn venv activate**
   ```
   source qt_env1/bin/activate && python main.py
   ```

## 📦 Building Installers

### Quick Build (Current Platform)
```bash
./build.sh
```

### Cross-Platform Builds
```bash
python build_cross_platform.py
```

**Supported Platforms:**
- 🖥️ **Windows** - EXE with NSIS installer
- 🍎 **macOS** - DMG installer
- 🐧 **Linux** - AppImage (planned)

For detailed build instructions, see [BUILD_GUIDE.md](BUILD_GUIDE.md)

## 📁 Project Structure

```
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── build_cross_platform.py     # Cross-platform build script
├── build_config.py            # Build configuration
├── build.sh                   # Quick build script
├── ui/                        # UI components
│   ├── main_window.py         # Main application window
│   ├── image_panel.py         # Left panel - image list
│   └── results_panel.py       # Right panel - analysis results
└── BUILD_GUIDE.md            # Detailed build instructions
```

## 🛠️ Development

### Requirements
- Python 3.9+
- PyQt5
- Pillow (PIL)

### Running in Development
```bash
source qt_env/bin/activate
python main.py
```

### Building for Distribution
See [BUILD_GUIDE.md](BUILD_GUIDE.md) for platform-specific instructions.

## 📋 Usage

1. **Open Folder** - Use File → Open Folder or Ctrl+O
2. **Browse Images** - Click images in the left panel to view details
3. **Scan All** - Use "Scan All Images" for automatic slideshow
4. **Export Results** - Save analysis reports with "Upload Results"

## 🎯 UI Layout

- **Left Panel (20%, max 300px)** - Image thumbnails and list
- **Right Panel (80%)** - Analysis results and image preview
- **Two-tab Interface**:
  - **Folder Overview** - Statistics and format breakdown
  - **Image Details** - Large preview and properties

## 📄 License

MIT License - see [LICENSE.txt](LICENSE.txt) for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

Built with ❤️ using PyQt5
