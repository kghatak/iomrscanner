#!/usr/bin/env python3
"""
Single Stage Testing Framework

This script allows you to test individual pipeline stages independently.
Useful for development, debugging, and understanding each stage's behavior.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from image_processor import ImageProcessor
from pipeline.base_stage import PipelineStage
from pipeline.aruco_check_stage import ArUcoCheckStage
from pipeline.orientation_check_stage import OrientationCheckStage
from pipeline.roll_number_extraction_stage import RollNumberExtractionStage
from pipeline.omr_processing_stage import OMRProcessingStage
from pipeline.api_upload_stage import APIUploadStage


class SingleStageTester:
    """Test individual pipeline stages independently."""
    
    def __init__(self):
        """Initialize the tester with an ImageProcessor instance."""
        self.processor = ImageProcessor()
        self.stages = {
            'aruco_check': ArUcoCheckStage(self.processor),
            'orientation_check': OrientationCheckStage(self.processor),
            'roll_number_extraction': RollNumberExtractionStage(self.processor),
            'omr_processing': OMRProcessingStage(self.processor),
            'api_upload': APIUploadStage(self.processor)
        }
    
    def get_available_stages(self):
        """Get list of available stages."""
        return list(self.stages.keys())
    
    def test_stage(self, stage_name: str, image_path: str, context: dict = None, output_folder: str = None):
        """
        Test a single stage with the given image and context.
        
        Args:
            stage_name: Name of the stage to test
            image_path: Path to the image to process
            context: Context dictionary (optional)
            output_folder: Output folder for results (optional)
            
        Returns:
            Stage result dictionary
        """
        if stage_name not in self.stages:
            raise ValueError(f"Unknown stage: {stage_name}. Available stages: {self.get_available_stages()}")
        
        stage = self.stages[stage_name]
        
        # Create default context if not provided
        if context is None:
            context = {
                "original_image_path": image_path,
                "current_image_path": image_path
            }
        
        print(f"🧪 Testing stage: {stage_name}")
        print(f"📁 Image: {image_path}")
        print(f"📋 Context: {context}")
        print(f"📝 Description: {stage.get_stage_description()}")
        print("-" * 60)
        
        try:
            # Process the stage
            result = stage.process(image_path, context)
            
            # Display results
            print(f"✅ Stage completed successfully: {result['success']}")
            if result['success']:
                print("📊 Results:")
                for key, value in result.items():
                    if key not in ['success', 'stage_name', 'stage_description']:
                        print(f"  {key}: {value}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
            # Handle error marking if output folder provided
            if output_folder and not result['success']:
                os.makedirs(output_folder, exist_ok=True)
                error_result = {
                    "filename": os.path.basename(image_path),
                    "error_stage": stage_name,
                    "error_message": result.get('error', 'Unknown error')
                }
                error_image_path = stage.handle_pipeline_error(image_path, output_folder, error_result)
                print(f"🖼️ Error image saved: {error_image_path}")
            
            return result
            
        except Exception as e:
            print(f"💥 Exception occurred: {str(e)}")
            return {
                "success": False,
                "error": f"Exception: {str(e)}",
                "stage_name": stage_name
            }
    
    def test_stage_with_mock_context(self, stage_name: str, image_path: str, mock_data: dict = None):
        """
        Test a stage with mock context data from previous stages.
        
        Args:
            stage_name: Name of the stage to test
            image_path: Path to the image to process
            mock_data: Mock data to simulate previous stages
            
        Returns:
            Stage result dictionary
        """
        # Create context with mock data
        context = {
            "original_image_path": image_path,
            "current_image_path": image_path
        }
        
        if mock_data:
            context.update(mock_data)
            print(f"🎭 Using mock context data: {mock_data}")
        
        return self.test_stage(stage_name, image_path, context)
    
    def test_stage_sequence(self, image_path: str, stages_to_test: list, output_folder: str = None):
        """
        Test a sequence of stages, passing results from one to the next.
        
        Args:
            image_path: Path to the image to process
            stages_to_test: List of stage names to test in sequence
            output_folder: Output folder for results
            
        Returns:
            Dictionary with results from all stages
        """
        context = {
            "original_image_path": image_path,
            "current_image_path": image_path
        }
        
        results = {}
        
        for stage_name in stages_to_test:
            print(f"\n🔄 Testing stage sequence: {stage_name}")
            result = self.test_stage(stage_name, image_path, context, output_folder)
            results[stage_name] = result
            
            if result['success']:
                # Update context with stage results
                context.update(result)
                print(f"✅ Context updated for next stage")
            else:
                print(f"❌ Stage failed, stopping sequence")
                break
        
        return results


def create_test_image_with_aruco():
    """Create a test image with ArUco markers for testing."""
    import cv2
    import numpy as np
    
    # Create a white image
    image = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Add some ArUco markers (you'll need to have ArUco markers available)
    # This is a placeholder - you can replace with actual ArUco marker images
    cv2.putText(image, "Test Image with ArUco Markers", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(image, "Roll No: 123456", (50, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Save test image
    test_image_path = "test_single_stage_image.jpg"
    cv2.imwrite(test_image_path, image)
    print(f"📸 Created test image: {test_image_path}")
    
    return test_image_path


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Test individual pipeline stages")
    parser.add_argument("stage", choices=["aruco_check", "orientation_check", "roll_number_extraction", 
                                         "omr_processing", "api_upload", "all"],
                       help="Stage to test")
    parser.add_argument("image_path", help="Path to the image to process")
    parser.add_argument("--output-folder", "-o", help="Output folder for results")
    parser.add_argument("--create-test-image", "-c", action="store_true", 
                       help="Create a test image with ArUco markers")
    parser.add_argument("--mock-context", "-m", help="Mock context data (JSON string)")
    
    args = parser.parse_args()
    
    # Create test image if requested
    if args.create_test_image:
        image_path = create_test_image_with_aruco()
    else:
        image_path = args.image_path
    
    # Initialize tester
    tester = SingleStageTester()
    
    # Parse mock context if provided
    mock_data = None
    if args.mock_context:
        import json
        try:
            mock_data = json.loads(args.mock_context)
        except json.JSONDecodeError:
            print("❌ Invalid JSON in mock context")
            return
    
    # Test the stage(s)
    if args.stage == "all":
        print("🧪 Testing all stages in sequence...")
        all_stages = tester.get_available_stages()
        results = tester.test_stage_sequence(image_path, all_stages, args.output_folder)
        
        print("\n📊 Summary of all stages:")
        for stage_name, result in results.items():
            status = "✅" if result['success'] else "❌"
            print(f"{status} {stage_name}: {result.get('error', 'Success')}")
    else:
        if mock_data:
            result = tester.test_stage_with_mock_context(args.stage, image_path, mock_data)
        else:
            result = tester.test_stage(args.stage, image_path, output_folder=args.output_folder)
        
        print(f"\n📊 Final result: {result}")


if __name__ == "__main__":
    main()
