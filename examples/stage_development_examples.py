#!/usr/bin/env python3
"""
Stage Development Examples

This file contains examples of how to use the stage development tools
for testing and developing individual pipeline stages.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.test_single_stage import SingleStageTester
from image_processor import ImageProcessor


def example_1_test_single_stage():
    """Example 1: Test a single stage with a real image."""
    print("="*60)
    print("EXAMPLE 1: Test Single Stage")
    print("="*60)
    
    # Initialize tester
    tester = SingleStageTester()
    
    # Use a test image (you can replace with your own image)
    image_path = "test_images/complete_markers.jpg"  # Adjust path as needed
    
    if not os.path.exists(image_path):
        print(f"❌ Test image not found: {image_path}")
        print("Please adjust the image path or create a test image.")
        return
    
    # Test ArUco check stage
    print("Testing ArUco check stage...")
    result = tester.test_stage('aruco_check', image_path)
    
    if result['success']:
        print(f"✅ ArUco check successful! Found {len(result['detected_markers'])} markers")
    else:
        print(f"❌ ArUco check failed: {result.get('error')}")


def example_2_test_with_mock_context():
    """Example 2: Test a stage with mock context data."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Test Stage with Mock Context")
    print("="*60)
    
    # Initialize tester
    tester = SingleStageTester()
    
    # Use a test image
    image_path = "test_images/complete_markers.jpg"  # Adjust path as needed
    
    if not os.path.exists(image_path):
        print(f"❌ Test image not found: {image_path}")
        return
    
    # Mock data simulating previous stages
    mock_context = {
        "detected_markers": [1, 2, 3, 4, 5],
        "rotation_applied": 0,
        "rotated_image_path": image_path,
        "roll_number": "123456"
    }
    
    # Test OMR processing stage with mock context
    print("Testing OMR processing stage with mock context...")
    result = tester.test_stage_with_mock_context('omr_processing', image_path, mock_context)
    
    if result['success']:
        print(f"✅ OMR processing successful!")
        print(f"   Roll number: {result['omr_data']['roll_number']}")
        print(f"   Detected markers: {result['omr_data']['detected_markers']}")
    else:
        print(f"❌ OMR processing failed: {result.get('error')}")


def example_3_test_stage_sequence():
    """Example 3: Test a sequence of stages."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Test Stage Sequence")
    print("="*60)
    
    # Initialize tester
    tester = SingleStageTester()
    
    # Use a test image
    image_path = "test_images/complete_markers.jpg"  # Adjust path as needed
    
    if not os.path.exists(image_path):
        print(f"❌ Test image not found: {image_path}")
        return
    
    # Test first 3 stages in sequence
    stages_to_test = ['aruco_check', 'orientation_check', 'roll_number_extraction']
    
    print(f"Testing stages: {' -> '.join(stages_to_test)}")
    results = tester.test_stage_sequence(image_path, stages_to_test)
    
    # Show summary
    print("\n📊 Sequence Results Summary:")
    for stage_name, result in results.items():
        status = "✅" if result['success'] else "❌"
        print(f"{status} {stage_name}: {result.get('error', 'Success')}")


def example_4_development_workflow():
    """Example 4: Development workflow for a new stage."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Development Workflow")
    print("="*60)
    
    # This example shows how you might develop a new stage
    
    # 1. Test existing stages to understand the interface
    tester = SingleStageTester()
    
    # 2. Create a simple test image
    import cv2
    import numpy as np
    
    # Create test image
    image = np.ones((400, 600, 3), dtype=np.uint8) * 255
    cv2.putText(image, "Development Test Image", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(image, "Roll No: 789012", (50, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    test_image_path = "dev_test_image.jpg"
    cv2.imwrite(test_image_path, image)
    
    print(f"📸 Created development test image: {test_image_path}")
    
    # 3. Test different stages with this image
    print("\n🧪 Testing stages with development image:")
    
    stages = ['aruco_check', 'roll_number_extraction']
    for stage_name in stages:
        print(f"\n--- Testing {stage_name} ---")
        result = tester.test_stage(stage_name, test_image_path)
        print(f"Result: {'Success' if result['success'] else 'Failed'}")
    
    # 4. Clean up
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
        print(f"🧹 Cleaned up test image: {test_image_path}")


def example_5_command_line_usage():
    """Example 5: Command line usage examples."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Command Line Usage")
    print("="*60)
    
    print("You can also use the test_single_stage.py script from command line:")
    print()
    print("1. Test a single stage:")
    print("   python tests/test_single_stage.py aruco_check test_images/complete_markers.jpg")
    print()
    print("2. Test with mock context:")
    print("   python tests/test_single_stage.py omr_processing test_images/complete_markers.jpg \\")
    print("   --mock-context '{\"detected_markers\": [1,2,3], \"roll_number\": \"123456\"}'")
    print()
    print("3. Test all stages in sequence:")
    print("   python tests/test_single_stage.py all test_images/complete_markers.jpg")
    print()
    print("4. Create a test image and test:")
    print("   python tests/test_single_stage.py aruco_check test.jpg --create-test-image")
    print()
    print("5. Use interactive development environment:")
    print("   python tests/develop_stage.py")


def main():
    """Run all examples."""
    print("🚀 PIPELINE STAGE DEVELOPMENT EXAMPLES")
    print("This file demonstrates how to test and develop individual pipeline stages.")
    print()
    
    # Run examples
    example_1_test_single_stage()
    example_2_test_with_mock_context()
    example_3_test_stage_sequence()
    example_4_development_workflow()
    example_5_command_line_usage()
    
    print("\n" + "="*60)
    print("✅ All examples completed!")
    print("="*60)
    print()
    print("💡 Tips for stage development:")
    print("1. Start by testing individual stages with simple images")
    print("2. Use mock context data to test stages that depend on previous stages")
    print("3. Test stage sequences to understand data flow")
    print("4. Use the interactive development environment for iterative development")
    print("5. Create test images with known characteristics for consistent testing")


if __name__ == "__main__":
    main()
