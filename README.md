# 📝 Bignan Mancha OMR Reader

A modern PyQt5 desktop application for processing and analyzing OMR (Optical Mark Recognition) sheets with professional cross-platform build support.

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

4. **Install system dependencies** (see System Dependencies section below)

5. **Run the application**
   ```bash
   python main.py
   ```
   Or with venv activate:
   ```bash
   source qt_env1/bin/activate && python main.py
   ```

> **Windows Users:** See [docs/WINDOWS_SETUP_GUIDE.md](docs/WINDOWS_SETUP_GUIDE.md) for detailed setup instructions including Poppler installation.

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

For detailed build instructions, see [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md)

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
└── docs/                      # Documentation files
    ├── BUILD_GUIDE.md         # Detailed build instructions
    ├── WINDOWS_INSTALLER_GUIDE.md
    ├── PIPELINE_TESTING_GUIDE.md
    └── ...                    # Other documentation
```

## 🛠️ Development

### Requirements
- Python 3.9+
- PyQt5
- Pillow (PIL)

### System Dependencies

Some features require additional system-level dependencies:

#### **Tesseract OCR** (for OCR functionality)
- **Windows**: Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

#### **Poppler** (for PDF processing)
- **Windows**: 
  1. Download from [poppler-windows releases](https://github.com/oschwartz10612/poppler-windows/releases/)
  2. Extract to `C:\Program Files\poppler` or `C:\poppler`
  3. Add the `bin` folder to your system PATH
- **macOS**: `brew install poppler`
- **Linux**: `sudo apt-get install poppler-utils`

### Running in Development
```bash
source qt_env/bin/activate
python main.py
```

### Building for Distribution
See [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md) for platform-specific instructions.

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

Bignan Mancha OMR Reader - Built with ❤️ using PyQt5
