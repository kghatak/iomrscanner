#!/usr/bin/env python3
"""
Test script for the modular pipeline system
"""

import os
import sys
import sys
sys.path.append('..')  # Add parent directory to path

from image_processor import ImageProcessor
from pipeline.pipeline_stages import PipelineStage

class CustomValidationStage(PipelineStage):
    """Custom stage: Additional validation after ArUco detection"""
    
    def get_stage_name(self) -> str:
        return "custom_validation"
    
    def get_stage_description(self) -> str:
        return "Custom validation stage"
    
    def process(self, image_path: str, context: dict) -> dict:
        try:
            # Get detected markers from previous stage
            detected_markers = context.get('detected_markers', [])
            
            # Custom validation logic
            if len(detected_markers) >= 10:
                return self.create_stage_result(
                    success=True,
                    validation_passed=True,
                    marker_count=len(detected_markers)
                )
            else:
                return self.create_stage_result(
                    success=False,
                    error=f"Custom validation failed: Need at least 10 markers, found {len(detected_markers)}",
                    validation_passed=False,
                    marker_count=len(detected_markers)
                )
                
        except Exception as e:
            return self.create_stage_result(
                success=False,
                error=f"Custom validation failed: {str(e)}",
                validation_passed=False
            )


class ImageQualityCheckStage(PipelineStage):
    """Custom stage: Check image quality metrics"""
    
    def get_stage_name(self) -> str:
        return "image_quality_check"
    
    def get_stage_description(self) -> str:
        return "Check image quality metrics"
    
    def process(self, image_path: str, context: dict) -> dict:
        try:
            import cv2
            import numpy as np
            
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return self.create_stage_result(
                    success=False,
                    error="Could not read image for quality check"
                )
            
            # Calculate quality metrics
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 1. Sharpness (using Laplacian variance)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # 2. Brightness
            brightness = np.mean(gray)
            
            # 3. Contrast
            contrast = np.std(gray)
            
            # Quality thresholds
            min_sharpness = 100
            min_brightness = 50
            max_brightness = 200
            min_contrast = 30
            
            quality_issues = []
            
            if laplacian_var < min_sharpness:
                quality_issues.append(f"Image too blurry (sharpness: {laplacian_var:.1f})")
            
            if brightness < min_brightness:
                quality_issues.append(f"Image too dark (brightness: {brightness:.1f})")
            elif brightness > max_brightness:
                quality_issues.append(f"Image too bright (brightness: {brightness:.1f})")
            
            if contrast < min_contrast:
                quality_issues.append(f"Image has low contrast (contrast: {contrast:.1f})")
            
            if quality_issues:
                return self.create_stage_result(
                    success=False,
                    error=f"Image quality issues: {'; '.join(quality_issues)}",
                    quality_metrics={
                        'sharpness': laplacian_var,
                        'brightness': brightness,
                        'contrast': contrast
                    }
                )
            else:
                return self.create_stage_result(
                    success=True,
                    quality_metrics={
                        'sharpness': laplacian_var,
                        'brightness': brightness,
                        'contrast': contrast
                    }
                )
                
        except Exception as e:
            return self.create_stage_result(
                success=False,
                error=f"Quality check failed: {str(e)}"
            )


def test_modular_pipeline():
    """Test the modular pipeline system"""
    print("🧪 Testing Modular Pipeline System")
    print("=" * 50)
    
    # Initialize processor
    processor = ImageProcessor()
    
    # Check if pipeline manager is available
    if processor.pipeline_manager is None:
        print("❌ Pipeline manager not available")
        return False
    
    print("✅ Pipeline manager initialized successfully")
    
    # Show current stages
    print("\n📋 Current Pipeline Stages:")
    stages_info = processor.get_pipeline_stages_info()
    for i, stage_info in enumerate(stages_info):
        print(f"   {i+1}. {stage_info['name']}: {stage_info['description']}")
    
    # Test adding a custom stage
    print("\n🔧 Adding Custom Validation Stage...")
    custom_stage = CustomValidationStage(processor)
    success = processor.add_pipeline_stage(custom_stage, position=1)  # Add after ArUco check
    if success:
        print("✅ Custom validation stage added successfully")
    else:
        print("❌ Failed to add custom validation stage")
    
    # Test adding another custom stage
    print("\n🔧 Adding Image Quality Check Stage...")
    quality_stage = ImageQualityCheckStage(processor)
    success = processor.add_pipeline_stage(quality_stage, position=2)  # Add after orientation check
    if success:
        print("✅ Image quality check stage added successfully")
    else:
        print("❌ Failed to add image quality check stage")
    
    # Show updated stages
    print("\n📋 Updated Pipeline Stages:")
    stages_info = processor.get_pipeline_stages_info()
    for i, stage_info in enumerate(stages_info):
        print(f"   {i+1}. {stage_info['name']}: {stage_info['description']}")
    
    # Test removing a stage
    print("\n🗑️ Removing API Upload Stage...")
    success = processor.remove_pipeline_stage("api_upload")
    if success:
        print("✅ API upload stage removed successfully")
    else:
        print("❌ Failed to remove API upload stage")
    
    # Show final stages
    print("\n📋 Final Pipeline Stages:")
    stages_info = processor.get_pipeline_stages_info()
    for i, stage_info in enumerate(stages_info):
        print(f"   {i+1}. {stage_info['name']}: {stage_info['description']}")
    
    # Test pipeline with a sample image
    print("\n🚀 Testing Pipeline with Sample Image...")
    
    # Create a test image
    import cv2
    import numpy as np
    
    test_dir = "test_modular_pipeline"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a test image with text
    image = np.ones((800, 1200, 3), dtype=np.uint8) * 255
    cv2.putText(image, "Roll No: 123456", (400, 400), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    test_image_path = f"{test_dir}/test_image.jpg"
    cv2.imwrite(test_image_path, image)
    
    print(f"📷 Created test image: {test_image_path}")
    
    # Process through pipeline
    result = processor.process_image_pipeline(test_image_path, test_dir)
    
    print(f"\n📊 Pipeline Result:")
    print(f"   Success: {result['success']}")
    print(f"   Error Stage: {result.get('error_stage', 'None')}")
    print(f"   Error Message: {result.get('error_message', 'None')}")
    
    if result['success']:
        print("✅ Pipeline completed successfully!")
        
        # Show stage results
        print("\n📋 Stage Results:")
        for stage_name, stage_result in result.get('stages', {}).items():
            status = "✅" if stage_result.get('success') else "❌"
            print(f"   {status} {stage_name}: {stage_result.get('stage_description', 'Unknown')}")
            
            # Show custom stage results
            if stage_name == 'custom_validation':
                marker_count = stage_result.get('marker_count', 0)
                print(f"      📊 Marker count: {marker_count}")
            
            elif stage_name == 'image_quality_check':
                metrics = stage_result.get('quality_metrics', {})
                print(f"      📊 Quality metrics: Sharpness={metrics.get('sharpness', 0):.1f}, "
                      f"Brightness={metrics.get('brightness', 0):.1f}, "
                      f"Contrast={metrics.get('contrast', 0):.1f}")
    else:
        print("❌ Pipeline failed!")
    
    return result['success']


def test_pipeline_flexibility():
    """Test pipeline flexibility by creating different configurations"""
    print("\n🔧 Testing Pipeline Flexibility")
    print("=" * 50)
    
    # Create a new processor for testing
    processor = ImageProcessor()
    
    if processor.pipeline_manager is None:
        print("❌ Pipeline manager not available")
        return False
    
    # Remove all stages
    print("🗑️ Removing all stages...")
    stage_names = [stage.get_stage_name() for stage in processor.pipeline_manager.stages]
    for stage_name in stage_names:
        processor.remove_pipeline_stage(stage_name)
    
    print(f"✅ Removed {len(stage_names)} stages")
    
    # Add only ArUco check and quality check
    print("\n🔧 Creating minimal pipeline (ArUco + Quality)...")
    from pipeline.pipeline_stages import ArUcoCheckStage
    quality_stage = ImageQualityCheckStage(processor)
    
    processor.add_pipeline_stage(ArUcoCheckStage(processor))
    processor.add_pipeline_stage(quality_stage)
    
    print("✅ Minimal pipeline created")
    
    # Show stages
    stages_info = processor.get_pipeline_stages_info()
    print(f"📋 Pipeline now has {len(stages_info)} stages:")
    for i, stage_info in enumerate(stages_info):
        print(f"   {i+1}. {stage_info['name']}: {stage_info['description']}")
    
    return True


if __name__ == "__main__":
    print("🧪 Modular Pipeline System Test")
    print("=" * 60)
    
    # Test basic functionality
    success1 = test_modular_pipeline()
    
    # Test flexibility
    success2 = test_pipeline_flexibility()
    
    if success1 and success2:
        print("\n🎉 All tests passed!")
        print("✅ Modular pipeline system is working correctly")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
