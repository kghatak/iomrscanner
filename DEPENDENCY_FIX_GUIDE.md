# Dependency Fix Guide

## The Problem

You're seeing these errors:
1. **Flask/Werkzeug Error:** `cannot import name 'url_quote' from 'werkzeug.urls'`
2. **NumPy Warning:** `numpy.dtype size changed, may indicate binary incompatibility`

### Root Cause
- You're using the **system/anaconda Python** instead of the **virtual environment**
- Flask and Werkzeug versions are incompatible
- NumPy and Pandas versions are incompatible

---

## Quick Fix (Recommended)

### Option 1: Automated Script

```bash
./fix_dependencies.sh
```

This script will:
- Create/activate virtual environment
- Install compatible versions
- Fix all dependency conflicts

### Option 2: Manual Fix

```bash
# 1. Activate virtual environment (IMPORTANT!)
source venv/bin/activate

# 2. Upgrade pip
pip install --upgrade pip

# 3. Uninstall conflicting packages
pip uninstall -y Flask Werkzeug numpy pandas

# 4. Install compatible versions
pip install "Flask>=2.3.0,<3.0.0" "Werkzeug>=2.3.0,<3.0.0"
pip install "numpy>=1.21.0,<2.0.0" "pandas>=1.3.0,<2.0.0"

# 5. Install all requirements
pip install -r requirements.txt

# 6. Run the application
python main.py
```

---

## Detailed Explanation

### Why Virtual Environment?

Your error shows:
```
/Users/kaghatak/opt/anaconda3/lib/python3.9/site-packages/...
```

This means you're using **anaconda3** Python, which has:
- ❌ Conflicting package versions
- ❌ System-wide installations
- ❌ Hard to manage dependencies

**Virtual environment** gives you:
- ✅ Isolated dependencies
- ✅ Project-specific versions
- ✅ No conflicts with system Python

### Version Compatibility

**Old (Broken):**
```
Flask>=2.0.0        # Too broad, includes v3.x
Werkzeug (any)      # Causes url_quote error
numpy>=1.24.0       # Incompatible with pandas
```

**New (Fixed):**
```
Flask>=2.3.0,<3.0.0     # Compatible range
Werkzeug>=2.3.0,<3.0.0  # Matches Flask
numpy>=1.21.0,<2.0.0    # Compatible with pandas
pandas>=1.3.0,<2.0.0    # Matches numpy
```

---

## Step-by-Step Fix

### Step 1: Check Current Environment

```bash
# Check which Python you're using
which python

# Should show something like:
# /Users/kaghatak/dev/July2025/pyqt/venv/bin/python
#
# If it shows anaconda3, you're NOT in the venv!
```

### Step 2: Create/Activate Virtual Environment

```bash
# If venv doesn't exist, create it:
python3 -m venv venv

# Activate it (IMPORTANT!)
source venv/bin/activate

# Your prompt should now show: (venv)
```

### Step 3: Clean Install

```bash
# Upgrade pip
pip install --upgrade pip

# Uninstall problematic packages
pip uninstall -y Flask Werkzeug numpy pandas

# Install fixed versions
pip install -r requirements.txt
```

### Step 4: Verify

```bash
# Check Flask version
pip show Flask

# Should show version 2.3.x or 2.4.x (not 3.x)

# Check Werkzeug version
pip show Werkzeug

# Should show version 2.3.x or 2.4.x (not 3.x)
```

### Step 5: Run Application

```bash
python main.py
```

---

## Troubleshooting

### Problem: "Still using anaconda Python"

**Solution:**
```bash
# Deactivate any conda environment
conda deactivate

# Activate project venv
source venv/bin/activate

# Verify
which python
# Should show: .../pyqt/venv/bin/python
```

### Problem: "venv/bin/activate: No such file or directory"

**Solution:**
```bash
# Create virtual environment first
python3 -m venv venv

# Then activate
source venv/bin/activate
```

### Problem: "pip command not found"

**Solution:**
```bash
# Use python -m pip instead
python -m pip install -r requirements.txt
```

### Problem: "Still getting Flask/Werkzeug error"

**Solution:**
```bash
# Force reinstall with specific versions
pip install --force-reinstall "Flask==2.3.3" "Werkzeug==2.3.7"
```

---

## Avoiding Future Issues

### Always Activate Virtual Environment

Add to your workflow:

```bash
# Before running the app
cd /Users/kaghatak/dev/July2025/pyqt
source venv/bin/activate
python main.py
```

### Add to .bashrc or .zshrc (Optional)

```bash
# Add alias for easy activation
alias pyqt="cd /Users/kaghatak/dev/July2025/pyqt && source venv/bin/activate"
```

Then just type: `pyqt` to activate!

### Check Before Running

```bash
# Quick check script
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated!"
    source venv/bin/activate
fi
```

---

## What Changed in requirements.txt

### Before (Broken)
```txt
Flask>=2.0.0              # Too permissive
PyQt5>=5.15.0
numpy>=1.24.0             # Incompatible
pandas>=1.3.0             # Incompatible
```

### After (Fixed)
```txt
Flask>=2.3.0,<3.0.0       # Specific compatible range
Werkzeug>=2.3.0,<3.0.0    # Added explicit version
PyQt5>=5.15.0
numpy>=1.21.0,<2.0.0      # Compatible range
pandas>=1.3.0,<2.0.0      # Compatible range
```

---

## Quick Reference

### Check Environment
```bash
which python              # Should show venv path
pip show Flask Werkzeug   # Check versions
```

### Activate Venv
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Fix Dependencies
```bash
./fix_dependencies.sh     # Automated
# OR
pip install -r requirements.txt  # Manual
```

### Run Application
```bash
python main.py
```

---

## Summary

✅ **Problem:** Flask/Werkzeug incompatibility + wrong Python environment  
✅ **Solution:** Use virtual environment + compatible versions  
✅ **Fixed:** Updated requirements.txt with version constraints  
✅ **Script:** `fix_dependencies.sh` for automatic fix  

**Always remember:** `source venv/bin/activate` before running!

---

**Need help?** See the error messages for specific guidance.

