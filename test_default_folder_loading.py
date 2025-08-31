#!/usr/bin/env python3
"""
Test script to verify default folder loading functionality
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_default_folder_exists():
    """Test if the default folder exists and contains images."""
    default_folder = "test_input_pdf/OMR_300DPI_pages"
    
    print("🧪 Testing default folder loading functionality...")
    print(f"📁 Checking folder: {default_folder}")
    
    if not os.path.exists(default_folder):
        print(f"❌ Default folder not found: {default_folder}")
        return False
    
    print(f"✅ Default folder exists: {default_folder}")
    
    # Check if it contains image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    image_files = []
    
    try:
        for file in os.listdir(default_folder):
            file_path = os.path.join(default_folder, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file.lower())[1]
                if ext in image_extensions:
                    image_files.append(file)
    except Exception as e:
        print(f"❌ Error scanning folder: {e}")
        return False
    
    print(f"📊 Found {len(image_files)} image files")
    
    if len(image_files) > 0:
        print("✅ Default folder contains images - ready for auto-loading!")
        print("📋 Sample files:")
        for i, file in enumerate(sorted(image_files)[:5]):
            print(f"   {i+1}. {file}")
        if len(image_files) > 5:
            print(f"   ... and {len(image_files) - 5} more files")
        return True
    else:
        print("❌ No image files found in default folder")
        return False

def test_ui_import():
    """Test if the UI module can be imported with the new changes."""
    try:
        from ui.results_panel import ResultsPanel
        print("✅ UI module imports successfully")
        
        # Test creating an instance
        panel = ResultsPanel()
        print("✅ ResultsPanel instance created successfully")
        
        # Test the load_default_folder method exists
        if hasattr(panel, 'load_default_folder'):
            print("✅ load_default_folder method exists")
        else:
            print("❌ load_default_folder method not found")
            return False
        
        # Test the analyze_folder method with recursive parameter
        if hasattr(panel, 'analyze_folder'):
            print("✅ analyze_folder method exists")
        else:
            print("❌ analyze_folder method not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing UI module: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Default Folder Loading Functionality")
    print("=" * 50)
    
    # Test 1: Check if default folder exists
    folder_ok = test_default_folder_exists()
    
    # Test 2: Check if UI imports correctly
    ui_ok = test_ui_import()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Default folder: {'✅ PASS' if folder_ok else '❌ FAIL'}")
    print(f"   UI module: {'✅ PASS' if ui_ok else '❌ FAIL'}")
    
    if folder_ok and ui_ok:
        print("\n🎉 All tests passed! Default folder loading should work correctly.")
        print("\n💡 When you run the application:")
        print("   1. The UI will automatically load test_input_pdf/OMR_300DPI_pages")
        print("   2. Only files in that folder (not subdirectories) will be loaded")
        print("   3. You'll see the folder info in the overview tab")
        print("   4. You can immediately start processing without manual folder selection")
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")
    
    return folder_ok and ui_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
