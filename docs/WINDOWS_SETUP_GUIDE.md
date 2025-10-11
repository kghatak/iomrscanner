# Windows Setup Guide

This guide will help you set up the Image Folder Analyzer application on Windows, including all required system dependencies.

---

## 📋 Prerequisites

- **Python 3.9+** - Download from [python.org](https://www.python.org/downloads/)
- **Git** (optional) - Download from [git-scm.com](https://git-scm.com/download/win)

---

## 🚀 Quick Setup

### Step 1: Install Python Dependencies

1. **Open Command Prompt or PowerShell** as Administrator

2. **Navigate to the project directory**
   ```powershell
   cd C:\path\to\pyqt
   ```

3. **Create a virtual environment**
   ```powershell
   python -m venv venv
   ```

4. **Activate the virtual environment**
   ```powershell
   .\venv\Scripts\activate
   ```

5. **Install Python packages**
   ```powershell
   pip install -r requirements.txt
   ```

---

## 🛠️ System Dependencies

### 1. Tesseract OCR (Required for OCR functionality)

**Installation:**

1. Download the Tesseract installer from:
   - [UB-Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki)
   - Direct link: [tesseract-ocr-w64-setup-5.x.x.exe](https://github.com/UB-Mannheim/tesseract/wiki)

2. Run the installer and install to the default location:
   ```
   C:\Program Files\Tesseract-OCR
   ```

3. **Add Tesseract to PATH:**
   - Open **System Properties** → **Environment Variables**
   - Under **System Variables**, find **Path** and click **Edit**
   - Click **New** and add:
     ```
     C:\Program Files\Tesseract-OCR
     ```
   - Click **OK** to save

4. **Verify installation:**
   ```powershell
   tesseract --version
   ```

---

### 2. Poppler (Required for PDF processing)

**⚠️ Important:** Without Poppler, the "Open PDF" feature will not work.

**Installation:**

1. **Download Poppler for Windows:**
   - Go to [poppler-windows releases](https://github.com/oschwartz10612/poppler-windows/releases/)
   - Download the latest release (e.g., `Release-24.08.0-0.zip`)

2. **Extract the archive:**
   - Extract to one of these locations:
     - `C:\Program Files\poppler` (recommended)
     - `C:\poppler`
     - Any other location of your choice

3. **Add Poppler to PATH:**
   - The application will automatically detect Poppler in common locations, but adding it to PATH is recommended
   - Open **System Properties** → **Environment Variables**
   - Under **System Variables**, find **Path** and click **Edit**
   - Click **New** and add the path to the `bin` folder, for example:
     ```
     C:\Program Files\poppler\Library\bin
     ```
     Or if you extracted directly:
     ```
     C:\Program Files\poppler-24.08.0\Library\bin
     ```
   - Click **OK** to save

4. **Verify installation:**
   ```powershell
   pdfinfo -v
   ```
   or
   ```powershell
   pdftoppm -v
   ```

**Alternative locations the app will check automatically:**
- `C:\Program Files\poppler-*\Library\bin`
- `C:\Program Files (x86)\poppler-*\Library\bin`
- `C:\poppler\Library\bin`
- In the application directory: `.\poppler\Library\bin`

---

## ▶️ Running the Application

1. **Activate the virtual environment** (if not already activated):
   ```powershell
   .\venv\Scripts\activate
   ```

2. **Run the application:**
   ```powershell
   python main.py
   ```

---

## 🔧 Troubleshooting

### "Poppler is not found" Error

**Symptoms:** When trying to open a PDF, you see an error message:
```
Failed to extract images: Unable to get page count
Is Poppler installed and in the path?
```

**Solutions:**

1. **Verify Poppler is installed:**
   - Check if the folder `C:\Program Files\poppler\Library\bin` (or your installation path) exists
   - Verify it contains files like `pdfinfo.exe` and `pdftoppm.exe`

2. **Check PATH:**
   - Open Command Prompt and run:
     ```powershell
     where pdfinfo
     ```
   - If it doesn't find the file, Poppler is not in your PATH

3. **Restart the application:**
   - After adding Poppler to PATH, you MUST restart the application
   - Changes to PATH require a restart to take effect

4. **Use a fixed location:**
   - Place Poppler in one of these locations (the app checks these automatically):
     - `C:\Program Files\poppler-24.08.0\Library\bin`
     - `C:\poppler\Library\bin`

### "Tesseract not found" Error

**Solutions:**

1. **Verify Tesseract is installed:**
   ```powershell
   tesseract --version
   ```

2. **If not found, check installation path:**
   - Default: `C:\Program Files\Tesseract-OCR\tesseract.exe`

3. **Add to PATH if needed** (see Tesseract installation steps above)

### Python Package Installation Issues

**Problem:** `pip install` fails with SSL or network errors

**Solution:**
```powershell
python -m pip install --upgrade pip
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

## 📦 Building a Windows Executable

If you want to create a standalone `.exe` file:

1. **Install PyInstaller:**
   ```powershell
   pip install pyinstaller
   ```

2. **Run the build script:**
   ```powershell
   python build_installer.py
   ```

3. **Find the executable:**
   - The `.exe` will be in the `dist/` folder

**Note:** To bundle Poppler with the executable, copy the Poppler folder into the dist directory after building.

---

## ✅ Verification Checklist

Before running the application, verify:

- [ ] Python 3.9+ is installed: `python --version`
- [ ] Virtual environment is activated: Look for `(venv)` in prompt
- [ ] All Python packages installed: `pip list`
- [ ] Tesseract is in PATH: `tesseract --version`
- [ ] Poppler is in PATH or in a known location: `pdfinfo -v`
- [ ] Application starts without errors: `python main.py`

---

## 📞 Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Verify all system dependencies are properly installed
3. Check the error messages in the application for specific guidance
4. Consult the main [README.md](../README.md) for general information

---

**Last Updated:** October 2025

