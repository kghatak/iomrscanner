#!/bin/bash

# Fix Dependencies Script for Bignan Mancha OMR Reader
# This script fixes Flask/Werkzeug and numpy/pandas version conflicts

echo "================================================"
echo "Fixing Dependencies - Bignan Mancha OMR Reader"
echo "================================================"
echo ""

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  WARNING: No virtual environment detected!"
    echo ""
    echo "You should use a virtual environment to avoid conflicts."
    echo ""
    read -p "Do you want to create/activate a virtual environment? (y/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Check if venv exists
        if [ -d "venv" ]; then
            echo "Found existing venv, activating..."
            source venv/bin/activate
        else
            echo "Creating new virtual environment..."
            python3 -m venv venv
            source venv/bin/activate
            echo "✅ Virtual environment created and activated"
        fi
    else
        echo "⚠️  Continuing without virtual environment (not recommended)"
        echo ""
    fi
else
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
fi

echo ""
echo "Step 1: Upgrading pip..."
python -m pip install --upgrade pip
echo ""

echo "Step 2: Uninstalling conflicting packages..."
pip uninstall -y Flask Werkzeug numpy pandas 2>/dev/null
echo ""

echo "Step 3: Installing compatible versions..."
pip install "Flask>=2.3.0,<3.0.0" "Werkzeug>=2.3.0,<3.0.0"
pip install "numpy>=1.21.0,<2.0.0" "pandas>=1.3.0,<2.0.0"
echo ""

echo "Step 4: Installing all requirements..."
pip install -r requirements.txt
echo ""

echo "================================================"
echo "✅ Dependencies Fixed!"
echo "================================================"
echo ""
echo "You can now run the application:"
echo ""
echo "  python main.py"
echo ""
echo "Note: Always activate the virtual environment first:"
echo "  source venv/bin/activate"
echo ""

