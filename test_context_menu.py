#!/usr/bin/env python3
"""
Test script to verify context menu functionality in ImagePanel
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_context_menu_imports():
    """Test if the context menu functionality can be imported."""
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.image_panel import ImagePanel, ContextInputDialog
        
        print("✅ ImagePanel and ContextInputDialog imported successfully")
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create ImagePanel
        panel = ImagePanel()
        print("✅ ImagePanel created successfully")
        
        # Check if context menu methods exist
        required_methods = [
            'show_context_menu',
            'test_stage',
            'test_all_stages',
            'get_stage_context_requirements',
            'get_context_from_user',
            'show_stage_results',
            'show_all_stages_results'
        ]
        
        for method in required_methods:
            if hasattr(panel, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        # Test ContextInputDialog
        dialog = ContextInputDialog({}, "test_image.jpg")
        print("✅ ContextInputDialog created successfully")
        
        # Check if dialog methods exist
        if hasattr(dialog, 'get_context_data'):
            print("✅ ContextInputDialog.get_context_data method exists")
        else:
            print("❌ ContextInputDialog.get_context_data method missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def test_stage_context_requirements():
    """Test the stage context requirements logic."""
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.image_panel import ImagePanel
        
        # Create QApplication
        app = QApplication(sys.argv)
        panel = ImagePanel()
        
        # Test context requirements for each stage
        test_cases = [
            ("aruco_check", None),
            ("orientation_check", None),
            ("roll_number_extraction", {"rotated_image_path": "Path to rotated image (optional)", "detected_markers": "List of detected marker IDs (optional)"}),
            ("omr_processing", {"detected_markers": "List of detected marker IDs", "roll_number": "Extracted roll number", "rotated_image_path": "Path to rotated image (optional)"}),
            ("api_upload", {"omr_data": "OMR processing data dictionary"})
        ]
        
        for stage_name, expected_context in test_cases:
            context = panel.get_stage_context_requirements(stage_name)
            if context == expected_context:
                print(f"✅ {stage_name}: Context requirements correct")
            else:
                print(f"❌ {stage_name}: Context requirements incorrect")
                print(f"   Expected: {expected_context}")
                print(f"   Got: {context}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing context requirements: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Context Menu Functionality")
    print("=" * 50)
    
    # Test 1: Import and basic functionality
    import_ok = test_context_menu_imports()
    
    # Test 2: Stage context requirements
    context_ok = test_stage_context_requirements()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Imports and basic functionality: {'✅ PASS' if import_ok else '❌ FAIL'}")
    print(f"   Stage context requirements: {'✅ PASS' if context_ok else '❌ FAIL'}")
    
    if import_ok and context_ok:
        print("\n🎉 All tests passed! Context menu functionality is ready.")
        print("\n💡 How to use the context menu:")
        print("   1. Right-click on any image in the ImagePanel")
        print("   2. Select '🧪 Test Pipeline Stages' submenu")
        print("   3. Choose a specific stage to test")
        print("   4. If context is needed, a dialog will appear")
        print("   5. Enter the required context data")
        print("   6. View the test results")
        print("   7. Or select '🚀 Test All Stages' to test the complete pipeline")
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")
    
    return import_ok and context_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
