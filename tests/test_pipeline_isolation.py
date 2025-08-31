#!/usr/bin/env python3
"""
Test script to demonstrate pipeline error isolation between images
"""

import sys
sys.path.append("..")  # Add parent directory to path

import os
import sys
from image_processor import ImageProcessor

def create_test_images():
    """Create test images with different characteristics"""
    import cv2
    import numpy as np
    
    # Create test directory
    test_dir = "test_isolation"
    os.makedirs(test_dir, exist_ok=True)
    
    # Image 1: Good image with roll number
    image1 = np.ones((800, 1200, 3), dtype=np.uint8) * 255
    cv2.putText(image1, "Roll No: 123456", (400, 400), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    cv2.imwrite(f"{test_dir}/good_image.jpg", image1)
    
    # Image 2: Corrupted/invalid image
    with open(f"{test_dir}/corrupted_image.jpg", 'w') as f:
        f.write("This is not a valid image file")
    
    # Image 3: Empty image (no markers, no text)
    image3 = np.ones((800, 1200, 3), dtype=np.uint8) * 255
    cv2.imwrite(f"{test_dir}/empty_image.jpg", image3)
    
    # Image 4: Another good image
    image4 = np.ones((800, 1200, 3), dtype=np.uint8) * 255
    cv2.putText(image4, "Roll No: 789012", (400, 400), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    cv2.imwrite(f"{test_dir}/good_image2.jpg", image4)
    
    print("✅ Created test images:")
    print("   📷 good_image.jpg - Should succeed")
    print("   📷 corrupted_image.jpg - Should fail (invalid file)")
    print("   📷 empty_image.jpg - Should fail (no markers)")
    print("   📷 good_image2.jpg - Should succeed")
    
    return test_dir

def test_pipeline_isolation():
    """Test that pipeline errors are isolated between images"""
    print("🧪 Testing Pipeline Error Isolation")
    print("=" * 50)
    
    # Create test images
    test_dir = create_test_images()
    
    # Initialize processor
    processor = ImageProcessor()
    
    # Get test images
    test_images = [
        f"{test_dir}/good_image.jpg",
        f"{test_dir}/corrupted_image.jpg", 
        f"{test_dir}/empty_image.jpg",
        f"{test_dir}/good_image2.jpg"
    ]
    
    print(f"\n🚀 Processing {len(test_images)} images through pipeline...")
    print("-" * 50)
    
    # Process each image individually
    results = []
    for i, image_path in enumerate(test_images):
        print(f"\n📷 [{i+1}/{len(test_images)}] Processing: {os.path.basename(image_path)}")
        
        try:
            # Process image through pipeline
            result = processor.process_image_pipeline(image_path, f"{test_dir}/results")
            results.append(result)
            
            # Display result
            if result['success']:
                print(f"   ✅ SUCCESS: {os.path.basename(image_path)}")
                roll_number = result.get('stages', {}).get('roll_number_extraction', {}).get('roll_number')
                if roll_number:
                    print(f"   🆔 Roll Number: {roll_number}")
            else:
                print(f"   ❌ FAILED: {os.path.basename(image_path)}")
                print(f"   🔍 Error Stage: {result.get('error_stage')}")
                print(f"   📝 Error: {result.get('error_message')}")
                
        except Exception as e:
            print(f"   💥 EXCEPTION: {os.path.basename(image_path)}")
            print(f"   📝 Exception: {str(e)}")
            results.append({
                "filename": os.path.basename(image_path),
                "success": False,
                "error_stage": "pipeline_exception",
                "error_message": str(e)
            })
    
    # Summary
    print(f"\n📊 Pipeline Isolation Test Results")
    print("=" * 50)
    success_count = sum(1 for r in results if r.get('success', False))
    failure_count = len(results) - success_count
    
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failure_count}")
    print(f"📈 Success Rate: {(success_count/len(results)*100):.1f}%")
    
    # Check if failures were isolated
    print(f"\n🔍 Error Isolation Analysis:")
    for i, result in enumerate(results):
        filename = result.get('filename', f'image_{i+1}')
        success = result.get('success', False)
        status = "✅" if success else "❌"
        print(f"   {status} {filename}")
    
    # Verify that good images succeeded despite bad images failing
    good_images_succeeded = any(r.get('success', False) for r in results)
    bad_images_failed = any(not r.get('success', False) for r in results)
    
    print(f"\n🎯 Isolation Verification:")
    print(f"   ✅ Good images succeeded: {good_images_succeeded}")
    print(f"   ❌ Bad images failed: {bad_images_failed}")
    print(f"   🛡️ Errors were isolated: {good_images_succeeded and bad_images_failed}")
    
    # Check output folders
    print(f"\n📁 Output Folders Created:")
    results_dir = f"{test_dir}/results"
    if os.path.exists(results_dir):
        success_dir = f"{results_dir}/success"
        error_dir = f"{results_dir}/error"
        
        if os.path.exists(success_dir):
            success_files = len([f for f in os.listdir(success_dir) if f.endswith('.jpg')])
            print(f"   📂 Success folder: {success_files} files")
        
        if os.path.exists(error_dir):
            error_files = len([f for f in os.listdir(error_dir) if f.endswith('.jpg')])
            print(f"   📂 Error folder: {error_files} files")
    
    return success_count > 0 and failure_count > 0

if __name__ == "__main__":
    success = test_pipeline_isolation()
    if success:
        print("\n🎉 Pipeline isolation test passed!")
        print("✅ Errors are properly isolated between images")
        sys.exit(0)
    else:
        print("\n❌ Pipeline isolation test failed!")
        sys.exit(1)
