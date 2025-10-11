#!/usr/bin/env python3
"""
Script to download Poppler binaries for Windows bundling.
This script downloads and extracts Poppler so it can be bundled with the application.
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path

# Poppler version and download URL
POPPLER_VERSION = "24.08.0-0"
POPPLER_URL = f"https://github.com/oschwartz10612/poppler-windows/releases/download/v{POPPLER_VERSION}/Release-{POPPLER_VERSION}.zip"
DOWNLOAD_DIR = "build_deps"
POPPLER_DIR = "poppler_bundle"

def download_file(url, dest_path):
    """Download a file with progress indicator"""
    print(f"Downloading from: {url}")
    print(f"Saving to: {dest_path}")
    
    try:
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, (downloaded / total_size) * 100)
            bar_length = 50
            filled = int(bar_length * percent / 100)
            bar = '=' * filled + '-' * (bar_length - filled)
            print(f'\r[{bar}] {percent:.1f}%', end='', flush=True)
        
        urllib.request.urlretrieve(url, dest_path, reporthook=report_progress)
        print("\n✅ Download completed!")
        return True
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        return False

def extract_poppler(zip_path, extract_to):
    """Extract Poppler from ZIP file"""
    print(f"\nExtracting Poppler to: {extract_to}")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("✅ Extraction completed!")
        return True
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return False

def organize_poppler_files(extract_dir, target_dir):
    """
    Organize Poppler files into a clean structure for bundling.
    We only need the Library/bin folder with executables and DLLs.
    """
    print(f"\nOrganizing Poppler files into: {target_dir}")
    
    # Find the Library/bin folder
    poppler_root = Path(extract_dir) / f"poppler-{POPPLER_VERSION}"
    library_bin = poppler_root / "Library" / "bin"
    
    if not library_bin.exists():
        # Try alternative structure
        for item in Path(extract_dir).rglob("Library/bin"):
            library_bin = item
            break
    
    if not library_bin.exists():
        print(f"❌ Could not find Library/bin folder in extracted files")
        print(f"Extracted to: {extract_dir}")
        print("Contents:")
        for item in Path(extract_dir).rglob("*"):
            print(f"  {item}")
        return False
    
    # Create target directory
    target_path = Path(target_dir)
    if target_path.exists():
        print(f"Removing existing: {target_path}")
        shutil.rmtree(target_path)
    
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Copy all files from Library/bin
    print(f"Copying files from: {library_bin}")
    shutil.copytree(library_bin, target_path / "bin")
    
    # Verify key executables exist
    key_files = ["pdfinfo.exe", "pdftoppm.exe", "pdftotext.exe"]
    bin_dir = target_path / "bin"
    
    print("\nVerifying Poppler executables:")
    all_found = True
    for key_file in key_files:
        file_path = bin_dir / key_file
        if file_path.exists():
            print(f"  ✅ {key_file}")
        else:
            print(f"  ❌ {key_file} NOT FOUND")
            all_found = False
    
    if all_found:
        print("\n✅ Poppler organized successfully!")
        print(f"Bundle directory: {target_path}")
        print(f"Files ready for PyInstaller bundling")
        return True
    else:
        print("\n❌ Some key files are missing!")
        return False

def create_readme():
    """Create a README for the bundled Poppler"""
    readme_content = f"""# Bundled Poppler {POPPLER_VERSION}

This folder contains Poppler binaries that are bundled with the application.

## Source
Downloaded from: {POPPLER_URL}

## License
Poppler is licensed under GPL v2. See: https://poppler.freedesktop.org/

## Contents
- bin/ - Poppler executables and DLLs

## Usage
The application will automatically detect and use these bundled binaries on Windows.
"""
    
    with open(f"{POPPLER_DIR}/README.txt", "w") as f:
        f.write(readme_content)
    
    print(f"✅ Created README.txt in {POPPLER_DIR}")

def main():
    """Main download and setup process"""
    print("=" * 60)
    print("Poppler Windows Bundle Downloader")
    print("=" * 60)
    
    # Create directories
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    zip_path = os.path.join(DOWNLOAD_DIR, f"poppler-{POPPLER_VERSION}.zip")
    extract_path = os.path.join(DOWNLOAD_DIR, "extracted")
    
    # Step 1: Download if not already downloaded
    if os.path.exists(zip_path):
        print(f"✅ Poppler ZIP already downloaded: {zip_path}")
    else:
        print("Downloading Poppler for Windows...")
        if not download_file(POPPLER_URL, zip_path):
            print("\n❌ Failed to download Poppler. Please download manually from:")
            print(f"   {POPPLER_URL}")
            print(f"   And place it at: {zip_path}")
            return 1
    
    # Step 2: Extract
    if os.path.exists(extract_path):
        print(f"Removing old extraction: {extract_path}")
        shutil.rmtree(extract_path)
    
    if not extract_poppler(zip_path, extract_path):
        return 1
    
    # Step 3: Organize files for bundling
    if not organize_poppler_files(extract_path, POPPLER_DIR):
        return 1
    
    # Step 4: Create README
    create_readme()
    
    # Step 5: Summary
    print("\n" + "=" * 60)
    print("✅ Poppler Download and Setup Complete!")
    print("=" * 60)
    print(f"Poppler bundled at: {POPPLER_DIR}")
    print("\nNext steps:")
    print("1. Run the build script: python build_cross_platform.py")
    print("2. Poppler will be automatically included in the Windows bundle")
    print("3. Users won't need to install Poppler separately!")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

