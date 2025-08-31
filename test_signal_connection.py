#!/usr/bin/env python3
"""
Test script to verify signal connection between ResultsPanel and ImagePanel
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_signal_connection():
    """Test if the signal connection works correctly."""
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer
        from ui.main_window import MainWindow
        
        print("🧪 Testing signal connection between ResultsPanel and ImagePanel...")
        
        # Create QApplication
        app = QApplication(sys.argv)
        
        # Create MainWindow
        window = MainWindow()
        
        # Check if signals are connected
        print("✅ MainWindow created successfully")
        
        # Check if the connection exists
        if hasattr(window.results_panel, 'folder_loaded'):
            print("✅ ResultsPanel has folder_loaded signal")
        else:
            print("❌ ResultsPanel missing folder_loaded signal")
            return False
        
        # Check if ImagePanel has load_folder method
        if hasattr(window.image_panel, 'load_folder'):
            print("✅ ImagePanel has load_folder method")
        else:
            print("❌ ImagePanel missing load_folder method")
            return False
        
        # Test the default folder loading
        default_folder = "test_input_pdf/OMR_300DPI_pages"
        if os.path.exists(default_folder):
            print(f"✅ Default folder exists: {default_folder}")
            
            # Manually trigger the default folder loading
            print("🔄 Triggering default folder loading...")
            window.results_panel.load_default_folder()
            
            # Check if ImagePanel received the folder
            if hasattr(window.image_panel, 'current_folder') and window.image_panel.current_folder:
                print(f"✅ ImagePanel received folder: {window.image_panel.current_folder}")
                return True
            else:
                print("❌ ImagePanel did not receive the folder")
                return False
        else:
            print(f"❌ Default folder not found: {default_folder}")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def main():
    """Run the test."""
    print("🚀 Testing Signal Connection")
    print("=" * 40)
    
    success = test_signal_connection()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Signal connection test PASSED!")
        print("✅ ResultsPanel will now update ImagePanel when default folder is loaded")
    else:
        print("❌ Signal connection test FAILED!")
        print("⚠️ ImagePanel may not be updated when default folder is loaded")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
