#!/usr/bin/env python3
"""
Test script for the comprehensive image processing pipeline
"""

import sys
sys.path.append("..")  # Add parent directory to path

import os
import sys
from image_processor import ImageProcessor

def test_pipeline():
    """Test the comprehensive pipeline processing"""
    print("🚀 Testing Comprehensive Image Processing Pipeline")
    print("=" * 60)
    
    # Initialize processor
    processor = ImageProcessor()
    
    # Test folder setup
    test_folder = "test_pipeline"
    os.makedirs(test_folder, exist_ok=True)
    
    # Create some test images (you can replace these with actual images)
    test_images = [
        os.path.join("test_images", "complete_markers.jpg"),
        os.path.join("test_images", "missing_markers.jpg"),
        os.path.join("test_images", "partial_markers.jpg"),
        os.path.join("test_images", "no_markers.jpg")
    ]
    
    # Filter to only existing images
    existing_images = [img for img in test_images if os.path.exists(img)]
    
    if not existing_images:
        print("❌ No test images found. Please ensure test_images folder contains images.")
        return False
    
    print(f"📁 Found {len(existing_images)} test images")
    
    # Process each image through the pipeline
    results = []
    for i, image_path in enumerate(existing_images):
        print(f"\n📷 [{i+1}/{len(existing_images)}] Processing: {os.path.basename(image_path)}")
        print("-" * 40)
        
        # Run pipeline
        result = processor.process_image_pipeline(image_path, test_folder)
        results.append(result)
        
        # Display results
        if result['success']:
            print(f"✅ Pipeline completed successfully")
            stages = result.get('stages', {})
            for stage_name, stage_result in stages.items():
                status = "✅" if stage_result.get('success') else "❌"
                print(f"  {status} {stage_name}")
                
                # Show roll number if extracted
                if stage_name == 'roll_number_extraction' and stage_result.get('roll_number'):
                    print(f"    🆔 Roll Number: {stage_result['roll_number']}")
                
                # Show API upload if successful
                if stage_name == 'api_upload' and stage_result.get('upload_id'):
                    print(f"    📤 Upload ID: {stage_result['upload_id']}")
        else:
            print(f"❌ Pipeline failed at stage: {result.get('error_stage')}")
            print(f"   Error: {result.get('error_message')}")
    
    # Summary
    print(f"\n📊 Pipeline Test Summary")
    print("=" * 40)
    success_count = sum(1 for r in results if r['success'])
    failure_count = len(results) - success_count
    
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failure_count}")
    print(f"📈 Success Rate: {(success_count/len(results)*100):.1f}%")
    
    # Show output folders
    print(f"\n📁 Output folders created:")
    print(f"   📂 {test_folder}/pipeline_results/success/")
    print(f"   📂 {test_folder}/pipeline_results/error/")
    
    return success_count > 0

def test_individual_stages():
    """Test individual pipeline stages"""
    print("\n🔧 Testing Individual Pipeline Stages")
    print("=" * 50)
    
    processor = ImageProcessor()
    
    # Test with a sample image
    test_image = os.path.join("test_images", "complete_markers.jpg")
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        return False
    
    print(f"📷 Testing with: {os.path.basename(test_image)}")
    
    # Test Stage 1: ArUco Check
    print("\n1️⃣ Testing Stage 1: ArUco Marker Check")
    stage1_result = processor._stage1_check_aruco_markers(test_image)
    if stage1_result['success']:
        print(f"   ✅ Found {len(stage1_result['detected_markers'])} markers")
    else:
        print(f"   ❌ {stage1_result['error']}")
    
    # Test Stage 2: Orientation Check
    print("\n2️⃣ Testing Stage 2: Image Orientation Check")
    stage2_result = processor._stage2_check_and_rotate_image(test_image)
    if stage2_result['success']:
        rotation = stage2_result.get('rotation_applied', 0)
        print(f"   ✅ Orientation check passed (rotation: {rotation}°)")
    else:
        print(f"   ❌ {stage2_result['error']}")
    
    # Test Stage 3: Roll Number Extraction
    print("\n3️⃣ Testing Stage 3: Roll Number Extraction")
    image_path = stage2_result.get('rotated_image_path', test_image)
    stage3_result = processor._stage3_extract_roll_number(image_path)
    if stage3_result['success']:
        print(f"   ✅ Roll number extracted: {stage3_result['roll_number']}")
    else:
        print(f"   ❌ {stage3_result['error']}")
    
    # Test Stage 4: OMR Processing
    print("\n4️⃣ Testing Stage 4: OMR Sheet Processing")
    roll_number = stage3_result.get('roll_number', 'TEST123')
    stage4_result = processor._stage4_process_omr_sheet(image_path, roll_number)
    if stage4_result['success']:
        print(f"   ✅ OMR data processed successfully")
        omr_data = stage4_result['omr_data']
        print(f"   📊 Detected {len(omr_data.get('detected_markers', []))} markers")
    else:
        print(f"   ❌ {stage4_result['error']}")
    
    # Test Stage 5: API Upload
    print("\n5️⃣ Testing Stage 5: API Upload")
    omr_data = stage4_result.get('omr_data', {})
    stage5_result = processor._stage5_upload_to_api(omr_data, roll_number)
    if stage5_result['success']:
        print(f"   ✅ API upload successful")
        print(f"   📤 Upload ID: {stage5_result.get('upload_id')}")
    else:
        print(f"   ❌ {stage5_result['error']}")
    
    return True

if __name__ == "__main__":
    print("🧪 Pipeline Testing Suite")
    print("=" * 50)
    
    # Test individual stages
    test_individual_stages()
    
    # Test full pipeline
    print("\n" + "=" * 60)
    success = test_pipeline()
    
    if success:
        print("\n🎉 Pipeline testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Pipeline testing failed!")
        sys.exit(1)
