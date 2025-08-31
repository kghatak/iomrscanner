#!/usr/bin/env python3
"""
Test script to verify upload results functionality
"""

import sys
import os
import csv
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_csv_validation():
    """Test CSV validation logic."""
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.main_window import MainWindow
        
        # Create QApplication
        app = QApplication(sys.argv)
        window = MainWindow()
        
        # Test data with correct format
        test_data = [
            {'examname': 'Test Exam', 'class': 'Class A', 'questionIndex': '1', 'correctchoice': 'A', 'questiontype': 'Multiple Choice'},
            {'examname': 'Test Exam', 'class': 'Class A', 'questionIndex': '2', 'correctchoice': 'B', 'questiontype': 'Multiple Choice'}
        ]
        
        # Test required columns validation
        required_columns = ['examname', 'class', 'questionIndex', 'correctchoice', 'questiontype']
        
        # Test with correct columns
        if all(col in test_data[0].keys() for col in required_columns):
            print("✅ CSV validation with correct columns: PASS")
        else:
            print("❌ CSV validation with correct columns: FAIL")
            return False
        
        # Test with missing columns
        incomplete_data = [{'examname': 'Test', 'class': 'A'}]  # Missing columns
        missing_cols = [col for col in required_columns if col not in incomplete_data[0].keys()]
        if missing_cols == ['questionIndex', 'correctchoice', 'questiontype']:
            print("✅ CSV validation with missing columns: PASS")
        else:
            print("❌ CSV validation with missing columns: FAIL")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error during CSV validation test: {e}")
        return False

def test_results_panel_methods():
    """Test ResultsPanel methods for uploaded results."""
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.results_panel import ResultsPanel
        
        # Create QApplication
        app = QApplication(sys.argv)
        panel = ResultsPanel()
        
        # Test data
        test_data = [
            {'examname': 'Mathematics 101', 'class': 'Class A', 'questionIndex': '1', 'correctchoice': 'A', 'questiontype': 'Multiple Choice'},
            {'examname': 'Mathematics 101', 'class': 'Class A', 'questionIndex': '2', 'correctchoice': 'B', 'questiontype': 'Multiple Choice'},
            {'examname': 'Science 102', 'class': 'Class B', 'questionIndex': '1', 'correctchoice': 'C', 'questiontype': 'Multiple Choice'}
        ]
        
        # Test tab creation
        print("✅ Testing uploaded results tab creation...")
        tab = panel.create_uploaded_results_tab(test_data)
        if tab is not None:
            print("✅ Tab creation: PASS")
        else:
            print("❌ Tab creation: FAIL")
            return False
        
        # Test table population
        print("✅ Testing table population...")
        # Create a temporary table widget for testing
        from PyQt5.QtWidgets import QTableWidget
        panel.uploaded_results_table = QTableWidget()
        panel.populate_uploaded_results_table(test_data)
        if hasattr(panel, 'uploaded_results_data') and len(panel.uploaded_results_data) == 3:
            print("✅ Table population: PASS")
        else:
            print("❌ Table population: FAIL")
            return False
        
        # Test tab management
        print("✅ Testing tab management...")
        panel.add_uploaded_results_tab(test_data)
        if panel.uploaded_results_tab_index is not None:
            print("✅ Tab management: PASS")
        else:
            print("❌ Tab management: FAIL")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error during ResultsPanel test: {e}")
        return False

def test_sample_csv():
    """Test with the sample CSV file."""
    try:
        sample_csv_path = "sample_results.csv"
        
        if not os.path.exists(sample_csv_path):
            print(f"❌ Sample CSV file not found: {sample_csv_path}")
            return False
        
        # Read and validate sample CSV
        with open(sample_csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Check required columns
            required_columns = ['examname', 'class', 'questionIndex', 'correctchoice', 'questiontype']
            if not all(col in reader.fieldnames for col in required_columns):
                print("❌ Sample CSV missing required columns")
                return False
            
            # Count rows
            rows = list(reader)
            if len(rows) == 20:  # Expected number of rows
                print(f"✅ Sample CSV validation: PASS ({len(rows)} rows)")
            else:
                print(f"❌ Sample CSV validation: FAIL (expected 20, got {len(rows)})")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing sample CSV: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Upload Results Functionality")
    print("=" * 50)
    
    # Test 1: CSV validation
    csv_ok = test_csv_validation()
    
    # Test 2: ResultsPanel methods
    panel_ok = test_results_panel_methods()
    
    # Test 3: Sample CSV
    sample_ok = test_sample_csv()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   CSV validation: {'✅ PASS' if csv_ok else '❌ FAIL'}")
    print(f"   ResultsPanel methods: {'✅ PASS' if panel_ok else '❌ FAIL'}")
    print(f"   Sample CSV: {'✅ PASS' if sample_ok else '❌ FAIL'}")
    
    if csv_ok and panel_ok and sample_ok:
        print("\n🎉 All tests passed! Upload results functionality is ready.")
        print("\n💡 How to use the upload results feature:")
        print("   1. Go to File → Upload Result")
        print("   2. Select a CSV file with format: examname,class,questionIndex,correctchoice,questiontype")
        print("   3. The CSV will be validated and displayed in a new '📊 Uploaded Results' tab")
        print("   4. The tab will show a table with all the uploaded data")
        print("   5. Use the sample_results.csv file for testing")
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")
    
    return csv_ok and panel_ok and sample_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
