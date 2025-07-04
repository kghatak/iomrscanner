#!/bin/bash

# Image Folder Analyzer - Cross-Platform Build Script
# This script builds installers for the current platform

echo "🚀 Building Image Folder Analyzer for $(uname)..."
echo "=============================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not detected. Activating qt_env..."
    source qt_env/bin/activate
fi

# Install/update build dependencies
echo "📦 Installing build dependencies..."
pip install --upgrade pyinstaller

# For macOS, also install dmgbuild
if [[ "$(uname)" == "Darwin" ]]; then
    pip install --upgrade dmgbuild
fi

# Run the cross-platform build script
echo "🔨 Starting cross-platform build process..."
python build_cross_platform.py

echo ""
echo "✅ Build process completed!"
echo "📁 Check the current directory for installer files."
