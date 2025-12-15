#!/usr/bin/env python3
"""
Test script for Fetch Student Stage
"""

import os
import sys
import json

# Add parent directory to path to import pipeline modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.fetch_student_stage import FetchStudentStage


class MockProcessor:
    """Mock processor for testing"""
    pass


def test_fetch_student_stage():
    """Test the fetch student stage"""
    print("=" * 60)
    print("Testing Fetch Student Stage")
    print("=" * 60)
    
    # Create mock processor
    mock_processor = MockProcessor()
    
    # Create stage instance
    stage = FetchStudentStage(mock_processor)
    
    print(f"Stage Name: {stage.get_stage_name()}")
    print(f"Stage Description: {stage.get_stage_description()}")
    print()
    
    # Test 1: No roll number in context
    print("Test 1: No roll number in context")
    print("-" * 40)
    
    context = {}
    result = stage.process("test_image.jpg", context)
    
    print(f"Success: {result['success']}")
    print(f"Error: {result.get('error', 'None')}")
    print()
    
    # Test 2: With roll number
    print("Test 2: With roll number (SURI-I2507 - 0063)")
    print("-" * 40)
    
    context = {
        'roll_number': 'SURI-I2507 - 0063'
    }
    
    print("Making API call...")
    result = stage.process("test_image.jpg", context)
    
    print(f"Success: {result['success']}")
    if result['success']:
        print("✅ Student data fetched successfully!")
        student_data = result.get('student_data', {})
        print(f"Student data keys: {list(student_data.keys()) if isinstance(student_data, dict) else 'Not a dict'}")
        
        # Pretty print student data
        if student_data:
            print("\nStudent Data:")
            print(json.dumps(student_data, indent=2))
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        api_response = result.get('api_response', {})
        if api_response:
            print(f"API Response: {api_response}")
    
    print()
    
    # Test 3: Invalid roll number
    print("Test 3: Invalid roll number")
    print("-" * 40)
    
    context = {
        'roll_number': 'INVALID-ROLL-NUMBER'
    }
    
    print("Making API call with invalid roll number...")
    result = stage.process("test_image.jpg", context)
    
    print(f"Success: {result['success']}")
    if result['success']:
        print("✅ Student data fetched!")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")
        api_response = result.get('api_response', {})
        if api_response:
            print(f"API Response: {api_response}")
    
    print()
    print("=" * 60)
    print("Fetch Student Stage Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    test_fetch_student_stage()
