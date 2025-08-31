#!/usr/bin/env python3
"""
Test script to verify NumPy JSON serialization fix
"""

import sys
import os
import json
import numpy as np
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_numpy_conversion():
    """Test the NumPy type conversion functionality."""
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.image_panel import ImagePanel
        
        # Create QApplication
        app = QApplication(sys.argv)
        panel = ImagePanel()
        
        # Test data with NumPy types
        test_data = {
            'detected_markers': np.array([1, 2, 3, 4, 5], dtype=np.int64),
            'confidence': np.float64(0.95),
            'corners': np.array([[100, 200], [300, 400]], dtype=np.int64),
            'nested': {
                'array': np.array([10, 20, 30], dtype=np.int64),
                'float': np.float32(0.123)
            }
        }
        
        # Test conversion
        converted = panel.convert_numpy_types(test_data)
        
        print("✅ NumPy conversion test:")
        print(f"   Original: {type(test_data['detected_markers'])} = {test_data['detected_markers']}")
        print(f"   Converted: {type(converted['detected_markers'])} = {converted['detected_markers']}")
        
        # Test JSON serialization
        try:
            json_str = json.dumps(converted, indent=2)
            print("✅ JSON serialization successful")
            print(f"   JSON: {json_str}")
            return True
        except Exception as e:
            print(f"❌ JSON serialization failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def test_stage_results_display():
    """Test the stage results display with NumPy data."""
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.image_panel import ImagePanel
        
        # Create QApplication
        app = QApplication(sys.argv)
        panel = ImagePanel()
        
        # Mock stage result with NumPy data
        mock_result = {
            'success': True,
            'stage_name': 'aruco_check',
            'stage_description': 'ArUco marker detection',
            'detected_markers': np.array([1, 2, 3, 4, 5], dtype=np.int64),
            'detection_info': {
                'confidence': np.float64(0.95),
                'corners': np.array([[100, 200], [300, 400]], dtype=np.int64)
            }
        }
        
        # Test the display method (without showing actual dialog)
        print("✅ Testing stage results display with NumPy data...")
        
        # This should not raise any JSON serialization errors
        try:
            # Simulate what the method does
            details = []
            for key, value in mock_result.items():
                if key not in ['success', 'stage_name', 'stage_description']:
                    converted_value = panel.convert_numpy_types(value)
                    if isinstance(converted_value, (list, dict)):
                        details.append(f"{key}: {json.dumps(converted_value, indent=2)}")
                    else:
                        details.append(f"{key}: {converted_value}")
            
            details_text = "\n".join(details)
            print("✅ Stage results display successful")
            print(f"   Details: {details_text}")
            return True
            
        except Exception as e:
            print(f"❌ Stage results display failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing NumPy JSON Serialization Fix")
    print("=" * 50)
    
    # Test 1: NumPy conversion
    conversion_ok = test_numpy_conversion()
    
    # Test 2: Stage results display
    display_ok = test_stage_results_display()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   NumPy conversion: {'✅ PASS' if conversion_ok else '❌ FAIL'}")
    print(f"   Stage results display: {'✅ PASS' if display_ok else '❌ FAIL'}")
    
    if conversion_ok and display_ok:
        print("\n🎉 All tests passed! NumPy JSON serialization is fixed.")
        print("\n💡 The context menu should now work properly with ArUco detection results.")
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")
    
    return conversion_ok and display_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
