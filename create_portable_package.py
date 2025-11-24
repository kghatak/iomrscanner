#!/usr/bin/env python3
"""
Create a portable ZIP package of the application for distribution.

This script creates a ZIP file containing:
- All source code
- run_app.bat launcher script
- README with instructions
- requirements.txt
- All necessary assets and configuration files

Usage:
    python create_portable_package.py [output_name]
    
Example:
    python create_portable_package.py Bignan_Mancha_OMR_Reader_v2.0.9_Portable
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# Files and folders to include
INCLUDE_PATTERNS = [
    '*.py',
    '*.txt',
    '*.md',
    '*.bat',
    '*.sh',
    '*.spec',
    'assets/**',
    'ui/**',
    'pipeline/**',
    'tools/**',
    'ml/**',
]

# Files and folders to exclude
EXCLUDE_PATTERNS = [
    '__pycache__',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.git',
    '.github',
    'venv',
    'env',
    'build',
    'dist',
    '*.egg-info',
    '.pytest_cache',
    'test_*.py',
    'tests/**',
    'pipeline_results_*',
    'test_input_pdf',
    'BU_test_input_pdf*',
    'sample_results.csv',
    '=2.25.0',
    'curl -X GET*',
]

def should_include(file_path, base_dir):
    """Check if a file should be included in the package."""
    rel_path = os.path.relpath(file_path, base_dir)
    
    # Always exclude these
    exclude_dirs = ['__pycache__', '.git', 'venv', 'env', 'build', 'dist', 
                    '.pytest_cache', 'pipeline_results_', 'test_input_pdf',
                    'BU_test_input_pdf', 'tests']
    
    # Check if in excluded directory
    for exclude_dir in exclude_dirs:
        if exclude_dir in rel_path.split(os.sep):
            return False
    
    # Exclude specific files
    exclude_files = ['.pyc', '.pyo', '.pyd', '.egg-info', 'sample_results.csv',
                    '=2.25.0', 'curl -X GET']
    for exclude_file in exclude_files:
        if exclude_file in rel_path:
            return False
    
    # Include Python files
    if rel_path.endswith('.py'):
        return True
    
    # Include config and data files
    if any(rel_path.endswith(ext) for ext in ['.txt', '.md', '.bat', '.sh', '.spec', '.json', '.csv']):
        return True
    
    # Include assets
    if rel_path.startswith('assets'):
        return True
    
    # Include UI files
    if rel_path.startswith('ui'):
        return True
    
    # Include pipeline files
    if rel_path.startswith('pipeline'):
        return True
    
    # Include tools
    if rel_path.startswith('tools'):
        return True
    
    # Include ML
    if rel_path.startswith('ml'):
        return True
    
    # Include docs
    if rel_path.startswith('docs'):
        return True
    
    return False

def create_readme_for_package(version="2.0.9"):
    """Create a README file for the portable package."""
    return f"""# Bignan Mancha OMR Reader v{version} - Portable Package

## Quick Start Guide

### For Windows Users:

1. **Extract this ZIP file** to any folder (e.g., `C:\\Bignan_Mancha_OMR_Reader`)

2. **Double-click `run_app.bat`** to launch the application
   - The script will automatically:
     - Check if Python is installed
     - Set up a virtual environment
     - Install all required dependencies
     - Launch the application

3. **First-time setup** (if Python is not installed):
   - Download Python 3.9 or later from: https://www.python.org/downloads/
   - During installation, make sure to check **"Add Python to PATH"**
   - Restart your computer after installation
   - Run `run_app.bat` again

### System Requirements:

- **Windows 10 or later**
- **Python 3.9 or later** (will be checked automatically)
- **Internet connection** (for first-time dependency installation)

### Optional Dependencies:

For full functionality, you may need:

1. **Tesseract OCR** (for text extraction):
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install and add to PATH

2. **Poppler** (for PDF processing):
   - Download from: https://github.com/oschwartz10612/poppler-windows/releases/
   - Extract to `C:\\Program Files\\poppler` or `C:\\poppler`
   - Add the `bin` folder to your system PATH

### Troubleshooting:

**Problem**: "Python is not installed or not in PATH"
- **Solution**: Install Python from https://www.python.org/downloads/ and make sure to check "Add Python to PATH"

**Problem**: "Failed to install dependencies"
- **Solution**: Check your internet connection and try again. You may need to run as Administrator.

**Problem**: Application window doesn't open
- **Solution**: Check the console window for error messages. Make sure all dependencies are installed.

**Problem**: PDF extraction doesn't work
- **Solution**: Install Poppler (see Optional Dependencies above)

### Manual Installation (Advanced):

If you prefer to set up manually:

1. Open Command Prompt in this folder
2. Create virtual environment: `python -m venv venv`
3. Activate it: `venv\\Scripts\\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run application: `python main.py`

### Features:

- ✅ OMR Sheet Processing
- ✅ PDF Extraction (with Poppler)
- ✅ Image Analysis
- ✅ Batch Processing
- ✅ Serial Processing (one file at a time)
- ✅ Roll Number Extraction with validation
- ✅ Student Data Fetching from API
- ✅ Results Upload and Validation

### Support:

For issues or questions, please check the main README.md file or contact support.

---
**Package created**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Version**: {version}
"""

def create_portable_package(output_name=None):
    """Create a portable ZIP package of the application."""
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    
    # Determine output name
    if output_name is None:
        from build_config import APP_VERSION
        version = APP_VERSION
        output_name = f"Bignan_Mancha_OMR_Reader_v{version}_Portable"
    
    output_zip = f"{output_name}.zip"
    
    print("=" * 60)
    print("Creating Portable Package")
    print("=" * 60)
    print(f"Project root: {project_root}")
    print(f"Output file: {output_zip}")
    print()
    
    # Create a temporary directory for packaging
    temp_dir = project_root / f"_{output_name}_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    print("[1/4] Copying files...")
    files_copied = 0
    
    # Copy files and directories
    for root, dirs, files in os.walk(project_root):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not any(exclude in d for exclude in [
            '__pycache__', '.git', 'venv', 'env', 'build', 'dist', 
            '.pytest_cache', 'pipeline_results_', 'test_input_pdf',
            'BU_test_input_pdf', 'tests', '.github'
        ])]
        
        rel_root = os.path.relpath(root, project_root)
        
        # Skip root-level excluded directories
        if any(exclude in rel_root.split(os.sep) for exclude in [
            '__pycache__', '.git', 'venv', 'env', 'build', 'dist',
            'pipeline_results_', 'test_input_pdf', 'BU_test_input_pdf', 'tests'
        ]):
            continue
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, project_root)
            
            # Skip excluded files
            if should_include(file_path, project_root):
                dest_path = temp_dir / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(file_path, dest_path)
                    files_copied += 1
                except Exception as e:
                    print(f"   ⚠ Skipped {rel_path}: {e}")
    
    print(f"   ✓ Copied {files_copied} files")
    
    # Copy instruction files
    instruction_files = ["START_HERE.txt", "QUICK_START_GUIDE.txt"]
    for inst_file in instruction_files:
        if (project_root / inst_file).exists():
            shutil.copy2(project_root / inst_file, temp_dir / inst_file)
            print(f"   ✓ {inst_file} included")
    
    # Create README for package
    print("[2/4] Creating README...")
    from build_config import APP_VERSION
    readme_content = create_readme_for_package(APP_VERSION)
    readme_path = temp_dir / "README_PORTABLE.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("   ✓ README created")
    
    # Ensure run_app.bat exists
    print("[3/4] Checking launcher script...")
    if not (temp_dir / "run_app.bat").exists():
        print("   ⚠ run_app.bat not found, copying from project root...")
        if (project_root / "run_app.bat").exists():
            shutil.copy2(project_root / "run_app.bat", temp_dir / "run_app.bat")
        else:
            print("   ⚠ run_app.bat not found in project root either")
    else:
        print("   ✓ Launcher script found")
    
    # Create ZIP file
    print("[4/4] Creating ZIP archive...")
    zip_path = project_root / output_zip
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    # Clean up temp directory
    shutil.rmtree(temp_dir)
    
    # Get file size
    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    
    print()
    print("=" * 60)
    print("✅ Package Created Successfully!")
    print("=" * 60)
    print(f"Output file: {output_zip}")
    print(f"Size: {zip_size_mb:.2f} MB")
    print()
    print("This ZIP file can be shared with users who don't have")
    print("Python installed. They just need to:")
    print("1. Extract the ZIP file")
    print("2. Double-click run_app.bat")
    print("=" * 60)
    
    return str(zip_path)

if __name__ == "__main__":
    output_name = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        create_portable_package(output_name)
    except Exception as e:
        print(f"\n❌ Error creating package: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

