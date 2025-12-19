#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to bundle Tesseract OCR for Windows.
This script copies Tesseract from a local installation or downloads it for bundling.
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path
import subprocess

# Fix Windows encoding issues
if sys.platform == 'win32':
    # Set UTF-8 encoding for stdout/stderr
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    # Set console to UTF-8
    os.system('chcp 65001 >nul 2>&1')

# Tesseract configuration
TESSERACT_VERSION = "5.5.0"  # Update as needed
DOWNLOAD_DIR = "build_deps"
TESSERACT_DIR = "tesseract_bundle"

# Common installation paths to check
COMMON_INSTALL_PATHS = [
    r"C:\Program Files\Tesseract-OCR",
    r"C:\Program Files (x86)\Tesseract-OCR",
    r"C:\Tesseract-OCR",
    os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR"),
]

def find_installed_tesseract():
    """
    Find Tesseract installation on the system.
    Returns path to Tesseract installation directory or None.
    """
    # First check if tesseract is in PATH
    tesseract_exe = shutil.which("tesseract")
    if tesseract_exe:
        tesseract_path = os.path.dirname(tesseract_exe)
        # If it's in a bin folder, go up one level
        if os.path.basename(tesseract_path).lower() == 'bin':
            tesseract_path = os.path.dirname(tesseract_path)
        print(f"✅ Found Tesseract in PATH at: {tesseract_path}")
        return tesseract_path
    
    # Check common installation paths
    for install_path in COMMON_INSTALL_PATHS:
        tesseract_exe = os.path.join(install_path, "tesseract.exe")
        if os.path.exists(tesseract_exe):
            print(f"✅ Found Tesseract installation at: {install_path}")
            return install_path
        # Also check bin subdirectory
        bin_exe = os.path.join(install_path, "bin", "tesseract.exe")
        if os.path.exists(bin_exe):
            print(f"✅ Found Tesseract installation at: {install_path}")
            return install_path
    
    return None

def copy_tesseract_files(source_dir, target_dir):
    """
    Copy Tesseract files from source installation to target bundle directory.
    
    Args:
        source_dir: Path to Tesseract installation
        target_dir: Path where bundle should be created
    """
    print(f"\nCopying Tesseract from: {source_dir}")
    print(f"To bundle directory: {target_dir}")
    
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Remove existing bundle
    if target_path.exists():
        print(f"Removing existing bundle: {target_path}")
        shutil.rmtree(target_path)
    
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Key files and folders to copy
    items_to_copy = []
    
    # Check if tesseract.exe is in root or bin/
    tesseract_exe_root = source_path / "tesseract.exe"
    tesseract_exe_bin = source_path / "bin" / "tesseract.exe"
    
    if tesseract_exe_bin.exists():
        # Tesseract is in bin/ subdirectory structure
        bin_dir = source_path / "bin"
        target_bin = target_path / "bin"
        target_bin.mkdir(parents=True, exist_ok=True)
        
        # Copy all files from bin/
        print(f"Copying bin/ directory...")
        for item in bin_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, target_bin)
                items_to_copy.append(f"bin/{item.name}")
        
        # Copy tessdata folder
        tessdata_source = source_path / "tessdata"
        if tessdata_source.exists():
            print(f"Copying tessdata/ directory...")
            tessdata_target = target_path / "tessdata"
            shutil.copytree(tessdata_source, tessdata_target)
            items_to_copy.append("tessdata/")
        
        # Copy any DLL files from root if they exist
        for dll_file in source_path.glob("*.dll"):
            shutil.copy2(dll_file, target_path)
            items_to_copy.append(dll_file.name)
            
    elif tesseract_exe_root.exists():
        # Tesseract.exe is in root directory
        print(f"Copying tesseract.exe and related files...")
        
        # Copy tesseract.exe
        shutil.copy2(tesseract_exe_root, target_path)
        items_to_copy.append("tesseract.exe")
        
        # Copy all DLL files
        for dll_file in source_path.glob("*.dll"):
            shutil.copy2(dll_file, target_path)
            items_to_copy.append(dll_file.name)
        
        # Copy tessdata folder
        tessdata_source = source_path / "tessdata"
        if tessdata_source.exists():
            print(f"Copying tessdata/ directory...")
            tessdata_target = target_path / "tessdata"
            shutil.copytree(tessdata_source, tessdata_target)
            items_to_copy.append("tessdata/")
    else:
        print(f"❌ Could not find tesseract.exe in: {source_dir}")
        return False
    
    # Verify key files exist
    print("\nVerifying bundled Tesseract files:")
    key_files = ["tesseract.exe"]
    all_found = True
    
    # Check in bin/ or root
    for key_file in key_files:
        bin_path = target_path / "bin" / key_file
        root_path = target_path / key_file
        if bin_path.exists():
            print(f"  ✅ {bin_path.relative_to(target_path)}")
        elif root_path.exists():
            print(f"  ✅ {root_path.relative_to(target_path)}")
        else:
            print(f"  ❌ {key_file} NOT FOUND")
            all_found = False
    
    # Check tessdata
    tessdata_path = target_path / "tessdata"
    if tessdata_path.exists():
        tessdata_files = list(tessdata_path.glob("*.traineddata"))
        print(f"  ✅ tessdata/ ({len(tessdata_files)} language files)")
    else:
        print(f"  ⚠️  tessdata/ directory not found (OCR may have limited functionality)")
    
    if all_found:
        print(f"\n✅ Tesseract bundled successfully!")
        print(f"Bundle directory: {target_path}")
        print(f"Total items copied: {len(items_to_copy)}")
        return True
    else:
        print(f"\n❌ Some key files are missing!")
        return False

def create_readme():
    """Create a README for the bundled Tesseract"""
    readme_content = f"""# Bundled Tesseract OCR

This folder contains Tesseract OCR binaries that are bundled with the application.

## Source
Tesseract OCR for Windows from UB-Mannheim
Download: https://github.com/UB-Mannheim/tesseract/wiki

## License
Tesseract is licensed under Apache 2.0 License.
See: https://github.com/tesseract-ocr/tesseract

## Contents
- bin/ - Tesseract executable and DLLs (or tesseract.exe in root)
- tessdata/ - Language data files

## Usage
The application will automatically detect and use these bundled binaries on Windows.
"""
    
    readme_path = Path(TESSERACT_DIR) / "README.txt"
    with open(readme_path, "w", encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Created README.txt in {TESSERACT_DIR}")

def main():
    """Main bundling process"""
    print("=" * 60)
    print("Tesseract OCR Windows Bundle Creator")
    print("=" * 60)
    
    # Check if bundle already exists
    if os.path.exists(TESSERACT_DIR):
        response = input(f"⚠️  {TESSERACT_DIR} already exists. Replace it? (y/n): ")
        if response.lower() != 'y':
            print("Keeping existing bundle.")
            return 0
    
    # Try to find installed Tesseract
    print("\nSearching for Tesseract installation...")
    tesseract_path = find_installed_tesseract()
    
    if tesseract_path:
        # Copy from installation
        if copy_tesseract_files(tesseract_path, TESSERACT_DIR):
            create_readme()
            print("\n" + "=" * 60)
            print("✅ Tesseract Bundle Created Successfully!")
            print("=" * 60)
            print(f"Tesseract bundled at: {TESSERACT_DIR}")
            print("\nNext steps:")
            print("1. Run the build script: python build_cross_platform.py")
            print("2. Tesseract will be automatically included in the Windows bundle")
            print("3. Users won't need to install Tesseract separately!")
            print("=" * 60)
            return 0
        else:
            print("\n❌ Failed to create Tesseract bundle from installation")
            return 1
    else:
        print("\n❌ Tesseract OCR not found on this system.")
        print("\nTo create the bundle, you need to install Tesseract first:")
        print("1. Download Tesseract OCR installer from:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install it to the default location (C:\\Program Files\\Tesseract-OCR)")
        print("3. Run this script again to create the bundle")
        print("\nAlternatively, you can manually copy Tesseract files to:")
        print(f"   {TESSERACT_DIR}/")
        print("   - bin/tesseract.exe (or tesseract.exe in root)")
        print("   - tessdata/ folder")
        return 1

if __name__ == "__main__":
    sys.exit(main())

