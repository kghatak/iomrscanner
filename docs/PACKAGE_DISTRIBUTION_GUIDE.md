# Package Distribution Guide

## Creating a Portable ZIP Package

When GitHub artifact upload fails or you want to share the application directly, you can create a portable ZIP package that any Windows user can run.

### Step 1: Create the Package

Run the package creation script:

```bash
python create_portable_package.py
```

This will create a ZIP file named: `Bignan_Mancha_OMR_Reader_v2.1.0_Portable.zip`

You can also specify a custom name:

```bash
python create_portable_package.py My_Custom_Package_Name
```

### Step 2: What's Included

The ZIP package includes:
- ✅ All source code
- ✅ `run_app.bat` - One-click launcher
- ✅ `START_HERE.txt` - Simple instructions
- ✅ `QUICK_START_GUIDE.txt` - Detailed guide
- ✅ `README_PORTABLE.txt` - Full documentation
- ✅ `requirements.txt` - Dependencies list
- ✅ All assets and configuration files

### Step 3: Share the Package

You can share the ZIP file via:
- Email
- Cloud storage (Google Drive, Dropbox, OneDrive)
- USB drive
- File sharing services
- Direct download link

**File size**: Typically 0.2-0.5 MB (source code only, dependencies downloaded on first run)

### Step 4: User Instructions

Tell users to:
1. Extract the ZIP file to any folder
2. Double-click `run_app.bat`
3. Wait for first-time setup (5-10 minutes)
4. Application will launch automatically

## What the Package Does

The `run_app.bat` script automatically:
1. ✅ Checks if Python is installed
2. ✅ Creates a virtual environment
3. ✅ Installs all dependencies from requirements.txt
4. ✅ Launches the application
5. ✅ Handles errors gracefully with helpful messages

## Requirements for Users

- **Windows 10 or later**
- **Python 3.9+** (script will guide installation if missing)
- **Internet connection** (for first-time dependency installation)

## Advantages Over EXE

- ✅ Smaller file size (0.2-0.5 MB vs 50-100 MB for EXE)
- ✅ Always up-to-date (users get latest code)
- ✅ Easy to update (just replace files)
- ✅ No compilation needed
- ✅ Works even if GitHub Actions fails

## Troubleshooting Package Creation

**Problem**: Package is too small or missing files
- **Solution**: Check that all source files are in the project directory

**Problem**: Package creation fails
- **Solution**: Make sure you have write permissions in the project directory

## Best Practices

1. **Test the package** before sharing:
   - Extract to a new folder
   - Run `run_app.bat`
   - Verify it works

2. **Include version in filename**:
   - Example: `Bignan_Mancha_OMR_Reader_v2.1.0_Portable.zip`

3. **Share instructions**:
   - Tell users to read `START_HERE.txt` first
   - Provide link to Python download if needed

4. **Update regularly**:
   - Create new package when you make significant changes
   - Update version number in filename

