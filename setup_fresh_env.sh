#!/bin/bash
# Script to create a fresh Python virtual environment
# This removes all old environments and creates a clean one

set -e  # Exit on error

PROJECT_DIR="/Users/kaghatak/dev/July2025/pyqt"
NEW_ENV_NAME="venv"

echo "========================================="
echo "🧹 Cleaning up old virtual environments"
echo "========================================="

cd "$PROJECT_DIR"

# Deactivate any active virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "📌 Deactivating current virtual environment: $VIRTUAL_ENV"
    deactivate 2>/dev/null || true
fi

# List of common virtual environment names to remove
ENV_NAMES=(
    "venv"
    "env"
    "qt_env"
    "qt_env1"
    "qt_env_clean"
    ".venv"
    "python-env"
)

# Remove old virtual environments
for env_name in "${ENV_NAMES[@]}"; do
    if [ -d "$env_name" ]; then
        echo "🗑️  Removing old environment: $env_name"
        rm -rf "$env_name"
        echo "   ✅ Removed: $env_name"
    fi
done

# Also remove any __pycache__ directories for clean slate
echo ""
echo "🧹 Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "   ✅ Cache cleaned"

echo ""
echo "========================================="
echo "🆕 Creating fresh virtual environment"
echo "========================================="

# Create new virtual environment
echo "📦 Creating new environment: $NEW_ENV_NAME"
python3 -m venv "$NEW_ENV_NAME"
echo "   ✅ Environment created"

echo ""
echo "========================================="
echo "📥 Installing dependencies"
echo "========================================="

# Activate the new environment
source "$NEW_ENV_NAME/bin/activate"
echo "✅ Activated: $NEW_ENV_NAME"

# Upgrade pip first
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip
echo "   ✅ pip upgraded"

# Install wheel and setuptools
echo ""
echo "📦 Installing build tools..."
pip install --upgrade wheel setuptools
echo "   ✅ Build tools installed"

# Install requirements
echo ""
echo "📦 Installing project requirements..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "   ✅ All requirements installed"
else
    echo "   ⚠️  Warning: requirements.txt not found"
fi

echo ""
echo "========================================="
echo "🧪 Testing dependencies"
echo "========================================="

# Test critical imports
echo "Testing OpenCV..."
python -c "import cv2; print(f'   ✅ OpenCV {cv2.__version__}')" || echo "   ❌ OpenCV failed"

echo "Testing NumPy..."
python -c "import numpy as np; print(f'   ✅ NumPy {np.__version__}')" || echo "   ❌ NumPy failed"

echo "Testing PyQt5..."
python -c "from PyQt5 import QtCore; print(f'   ✅ PyQt5 {QtCore.PYQT_VERSION_STR}')" || echo "   ❌ PyQt5 failed"

echo "Testing Pytesseract..."
python -c "import pytesseract; print('   ✅ Pytesseract imported successfully')" || echo "   ❌ Pytesseract failed (check if Tesseract OCR is installed)"

echo "Testing Pillow..."
python -c "from PIL import Image; print('   ✅ Pillow imported successfully')" || echo "   ❌ Pillow failed"

echo ""
echo "========================================="
echo "🤖 Testing ML Pipeline Dependencies"
echo "========================================="

echo "Testing Pandas..."
python -c "import pandas as pd; print(f'   ✅ Pandas {pd.__version__}')" || echo "   ❌ Pandas failed"

echo "Testing openpyxl..."
python -c "import openpyxl; print(f'   ✅ openpyxl {openpyxl.__version__}')" || echo "   ❌ openpyxl failed"

echo "Testing PyTorch..."
python -c "import torch; print(f'   ✅ PyTorch {torch.__version__}')" || echo "   ❌ PyTorch failed"

echo "Testing scikit-learn..."
python -c "import sklearn; print(f'   ✅ scikit-learn {sklearn.__version__}')" || echo "   ❌ scikit-learn failed"

echo "Testing Matplotlib..."
python -c "import matplotlib; print(f'   ✅ Matplotlib {matplotlib.__version__}')" || echo "   ❌ Matplotlib failed"

echo ""
echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "📝 Next steps:"
echo "   1. Activate the environment:"
echo "      source $NEW_ENV_NAME/bin/activate"
echo ""
echo "   2. Run your application:"
echo "      python main.py"
echo ""
echo "   3. Deactivate when done:"
echo "      deactivate"
echo ""
echo "========================================="
echo "🎉 Fresh environment ready at: $PROJECT_DIR/$NEW_ENV_NAME"
echo "========================================="

