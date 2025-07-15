#!/usr/bin/env python3
"""
Dependency checker for the PyQt Image Folder Analyzer
"""

import sys
import importlib

def check_dependency(module_name, required=True):
    """Check if a module can be imported and return version info"""
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'Unknown')
        print(f"✅ {module_name}: {version}")
        return True
    except ImportError as e:
        status = "❌" if required else "⚠️"
        print(f"{status} {module_name}: Not available - {e}")
        return False
    except Exception as e:
        print(f"❌ {module_name}: Error - {e}")
        return False

def main():
    print("🔍 Checking dependencies for PyQt Image Folder Analyzer...")
    print("=" * 60)
    
    # Core PyQt dependencies
    print("\n📱 PyQt Dependencies:")
    pyqt5_available = check_dependency('PyQt5')
    
    # PIL/Pillow
    print("\n🖼️ Image Processing:")
    pil_available = check_dependency('PIL')
    
    # NumPy (critical for ArUco)
    print("\n🔢 Numerical Computing:")
    numpy_available = check_dependency('numpy')
    
    # OpenCV (critical for ArUco)
    print("\n👁️ Computer Vision:")
    cv2_available = check_dependency('cv2')
    
    # OCR Dependencies
    print("\n📝 OCR Dependencies:")
    pytesseract_available = check_dependency('pytesseract')
    
    # Optional but may cause conflicts
    print("\n📊 Data Analysis (may cause conflicts):")
    pandas_available = check_dependency('pandas', required=False)
    
    print("\n" + "=" * 60)
    print("📋 Summary:")
    
    # Basic app functionality
    if pyqt5_available and pil_available:
        print("✅ Basic application functionality: Available")
    else:
        print("❌ Basic application functionality: Missing dependencies")
    
    # ArUco functionality
    if numpy_available and cv2_available and pytesseract_available:
        print("✅ ArUco marker processing: Available")
    else:
        print("❌ ArUco marker processing: Missing dependencies")
        
    print("\n💡 Recommendations:")
    
    if not numpy_available or not cv2_available or not pytesseract_available:
        print("📦 To install missing ArUco dependencies:")
        print("   pip install opencv-python pytesseract numpy")
        
    if pandas_available and not (numpy_available and cv2_available and pytesseract_available):
        print("⚠️  Pandas is installed but may cause numpy version conflicts")
        print("   Consider creating a clean virtual environment")
        print("   or updating packages: pip install --upgrade numpy pandas")
        
    print("\n🛠️ Virtual Environment Setup (Recommended):")
    print("   python -m venv qt_env")
    print("   source qt_env/bin/activate  # On Windows: qt_env\\Scripts\\activate")
    print("   pip install PyQt5 Pillow opencv-python pytesseract numpy")

if __name__ == "__main__":
    main()
