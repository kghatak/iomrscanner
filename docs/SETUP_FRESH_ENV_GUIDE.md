# Fresh Environment Setup Guide

## 🚀 Quick Start - Run setup_fresh_env.sh

This script will create a clean Python virtual environment with all dependencies installed.

---

## 📋 What the Script Does

1. **Cleans up** any old virtual environments (venv, env, qt_env, etc.)
2. **Removes** Python cache files (\__pycache__, *.pyc)
3. **Creates** a fresh virtual environment named `venv`
4. **Installs** all dependencies from requirements.txt
5. **Tests** all critical imports (OpenCV, PyQt5, ML libraries, etc.)

---

## 🏃 Step-by-Step Instructions

### Step 1: Make the Script Executable

```bash
cd /Users/kaghatak/dev/July2025/pyqt
chmod +x setup_fresh_env.sh
```

### Step 2: Run the Setup Script

```bash
./setup_fresh_env.sh
```

**OR** if you prefer using bash explicitly:

```bash
bash setup_fresh_env.sh
```

### Step 3: Wait for Installation

The script will:
- Remove old environments (~10 seconds)
- Create new environment (~5 seconds)
- Install all dependencies (~2-5 minutes depending on internet speed)
- Test all imports (~10 seconds)

**Total time: ~3-6 minutes**

### Step 4: Activate the Environment

After the script completes:

```bash
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal prompt.

---

## ✅ Expected Output

```bash
=========================================
🧹 Cleaning up old virtual environments
=========================================
🗑️  Removing old environment: venv
   ✅ Removed: venv

🧹 Cleaning Python cache files...
   ✅ Cache cleaned

=========================================
🆕 Creating fresh virtual environment
=========================================
📦 Creating new environment: venv
   ✅ Environment created

=========================================
📥 Installing dependencies
=========================================
✅ Activated: venv

⬆️  Upgrading pip...
   ✅ pip upgraded

📦 Installing build tools...
   ✅ Build tools installed

📦 Installing project requirements...
   [Installing packages... this may take a few minutes]
   ✅ All requirements installed

=========================================
🧪 Testing dependencies
=========================================
Testing OpenCV...
   ✅ OpenCV 4.10.0
Testing NumPy...
   ✅ NumPy 1.24.3
Testing PyQt5...
   ✅ PyQt5 5.15.9
Testing Pytesseract...
   ✅ Pytesseract imported successfully
Testing Pillow...
   ✅ Pillow imported successfully

=========================================
🤖 Testing ML Pipeline Dependencies
=========================================
Testing Pandas...
   ✅ Pandas 2.0.3
Testing PyTorch...
   ✅ PyTorch 2.1.0
Testing scikit-learn...
   ✅ scikit-learn 1.3.0
Testing Matplotlib...
   ✅ Matplotlib 3.7.2

=========================================
✅ Setup Complete!
=========================================

📝 Next steps:
   1. Activate the environment:
      source venv/bin/activate

   2. Run your application:
      python main.py

   3. Deactivate when done:
      deactivate

=========================================
🎉 Fresh environment ready at: /Users/kaghatak/dev/July2025/pyqt/venv
=========================================
```

---

## 🔍 Verify Installation

After activating the environment, test everything:

```bash
# Activate environment
source venv/bin/activate

# Test core dependencies
python -c "import cv2, numpy, PyQt5; print('✅ Core deps OK')"

# Test ML dependencies
python -c "import pandas, torch, sklearn, matplotlib; print('✅ ML deps OK')"

# Run the main application
python main.py
```

---

## 🐛 Troubleshooting

### Issue: "Permission denied" when running script

**Solution:**
```bash
chmod +x setup_fresh_env.sh
```

### Issue: "python3: command not found"

**Solution:**
```bash
# Check your Python installation
which python3

# If not found, install Python 3:
# macOS:
brew install python3

# or use system Python
python --version  # Should be 3.9+
```

### Issue: numpy/pandas binary incompatibility error

**Solution:**
The fresh environment setup should fix this. If it persists:
```bash
pip uninstall numpy pandas -y
pip install numpy==1.24.3 pandas==2.0.3 --no-cache-dir
```

### Issue: PyTorch installation fails (large download)

**Solution:**
PyTorch is large (~2GB). On slow internet:
```bash
# Install CPU-only version (smaller, faster)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### Issue: "ImportError" when running application

**Solution:**
Make sure you activated the environment:
```bash
source venv/bin/activate
# You should see (venv) in your prompt
```

---

## 📦 What Gets Installed

### Core Dependencies (for OMR processing)
- **PyQt5**: GUI framework
- **OpenCV**: Image processing
- **NumPy**: Numerical operations
- **pytesseract**: OCR for text extraction
- **pdf2image**: PDF to image conversion
- **Pillow**: Image handling
- **Flask**: Web server (if needed)

### ML Pipeline Dependencies (for circle classification)
- **pandas**: Dataset management
- **PyTorch**: Deep learning framework
- **torchvision**: Computer vision utilities
- **matplotlib**: Plotting training curves
- **scikit-learn**: ML utilities (train/test split, metrics)

### Build Tools (for distribution)
- **pyinstaller**: Create standalone executables
- **dmgbuild**: Create macOS .dmg files (macOS only)

---

## 🎯 After Setup - What's Next?

### 1. Run the Main Application
```bash
source venv/bin/activate
python main.py
```

### 2. Test ML Pipeline
```bash
source venv/bin/activate
python test_ml_dataset_generator.py
```

### 3. Review Labels (if you generated a dataset)
```bash
source venv/bin/activate
python tools/manual_review_tool.py
```

### 4. Train Your First Model
```bash
source venv/bin/activate
python ml/train_circle_classifier.py path/to/dataset
```

---

## 🔄 When to Run setup_fresh_env.sh Again

Re-run the setup script when:
- ✅ You have dependency conflicts
- ✅ You updated requirements.txt
- ✅ You want a completely clean environment
- ✅ You're experiencing import errors
- ✅ You're switching between projects

---

## 💡 Pro Tips

### Tip 1: Always Activate the Environment
```bash
# Add this to your .bashrc or .zshrc for convenience
alias pyqt='cd /Users/kaghatak/dev/July2025/pyqt && source venv/bin/activate'
```

### Tip 2: Check Environment is Active
```bash
# Should show path inside venv
which python

# Should show (venv) in prompt
# (venv) user@machine:~/pyqt$
```

### Tip 3: Deactivate When Done
```bash
deactivate
```

### Tip 4: Update Dependencies
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

## 🎉 You're Ready!

After running `setup_fresh_env.sh` successfully, you have:
- ✅ Clean Python environment
- ✅ All core dependencies installed
- ✅ All ML dependencies installed
- ✅ Verified all imports work
- ✅ Ready to run the application
- ✅ Ready to train ML models

**Happy coding! 🚀**

