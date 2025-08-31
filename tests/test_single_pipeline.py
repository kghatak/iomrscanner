#!/usr/bin/env python3
"""
Test the pipeline with a single image that has a roll number
"""

import sys
sys.path.append("..")  # Add parent directory to path

import os
from image_processor import ImageProcessor

def test_single_pipeline():
    """Test pipeline with a single image"""
    
    # Initialize processor
    processor = ImageProcessor()
    
    # Test image with roll number
    test_image = "test_images/complete_markers_with_roll.jpg"
    
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        return False
    
    print(f"🧪 Testing Pipeline with: {os.path.basename(test_image)}")
    print("=" * 60)
    
    # Run pipeline
    result = processor.process_image_pipeline(test_image, "test_single_pipeline")
    
    # Display results
    if result['success']:
        print("✅ Pipeline completed successfully!")
        print("\n📊 Stage Results:")
        
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
        
        print(f"\n📁 Output: {result['output_path']}")
        return True
    else:
        print(f"❌ Pipeline failed at stage: {result.get('error_stage')}")
        print(f"   Error: {result.get('error_message')}")
        print(f"📁 Error image: {result.get('error_image_path')}")
        return False

if __name__ == "__main__":
    success = test_single_pipeline()
    if success:
        print("\n🎉 Pipeline test completed successfully!")
    else:
        print("\n❌ Pipeline test failed!")
