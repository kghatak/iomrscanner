#!/usr/bin/env python3
"""
Interactive Stage Development Helper

This script provides an interactive environment for developing and testing
individual pipeline stages. Perfect for iterative development and debugging.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from image_processor import ImageProcessor
from pipeline.aruco_check_stage import ArUcoCheckStage
from pipeline.orientation_check_stage import OrientationCheckStage
from pipeline.roll_number_extraction_stage import RollNumberExtractionStage
from pipeline.omr_processing_stage import OMRProcessingStage
from pipeline.api_upload_stage import APIUploadStage


class StageDeveloper:
    """Interactive development environment for pipeline stages."""
    
    def __init__(self):
        """Initialize the development environment."""
        self.processor = ImageProcessor()
        self.stages = {
            'aruco_check': ArUcoCheckStage(self.processor),
            'orientation_check': OrientationCheckStage(self.processor),
            'roll_number_extraction': RollNumberExtractionStage(self.processor),
            'omr_processing': OMRProcessingStage(self.processor),
            'api_upload': APIUploadStage(self.processor)
        }
        self.context = {}
        self.current_image = None
    
    def show_menu(self):
        """Display the main menu."""
        print("\n" + "="*60)
        print("🔧 PIPELINE STAGE DEVELOPMENT ENVIRONMENT")
        print("="*60)
        print("1. Load image")
        print("2. Test single stage")
        print("3. Test stage with mock context")
        print("4. Test stage sequence")
        print("5. Show current context")
        print("6. Clear context")
        print("7. Create test image")
        print("8. List available stages")
        print("9. Exit")
        print("="*60)
    
    def load_image(self):
        """Load an image for testing."""
        image_path = input("Enter image path: ").strip()
        if os.path.exists(image_path):
            self.current_image = image_path
            self.context = {
                "original_image_path": image_path,
                "current_image_path": image_path
            }
            print(f"✅ Image loaded: {image_path}")
        else:
            print(f"❌ Image not found: {image_path}")
    
    def test_single_stage(self):
        """Test a single stage."""
        if not self.current_image:
            print("❌ No image loaded. Please load an image first.")
            return
        
        print("\nAvailable stages:")
        for i, stage_name in enumerate(self.stages.keys(), 1):
            stage = self.stages[stage_name]
            print(f"{i}. {stage_name} - {stage.get_stage_description()}")
        
        try:
            choice = int(input("\nSelect stage (number): ")) - 1
            stage_names = list(self.stages.keys())
            if 0 <= choice < len(stage_names):
                stage_name = stage_names[choice]
                self._run_stage(stage_name)
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def test_with_mock_context(self):
        """Test a stage with mock context data."""
        if not self.current_image:
            print("❌ No image loaded. Please load an image first.")
            return
        
        print("\nAvailable stages:")
        for i, stage_name in enumerate(self.stages.keys(), 1):
            stage = self.stages[stage_name]
            print(f"{i}. {stage_name} - {stage.get_stage_description()}")
        
        try:
            choice = int(input("\nSelect stage (number): ")) - 1
            stage_names = list(self.stages.keys())
            if 0 <= choice < len(stage_names):
                stage_name = stage_names[choice]
                
                print("\nEnter mock context data (JSON format):")
                print("Example: {\"detected_markers\": [1,2,3], \"roll_number\": \"123456\"}")
                mock_json = input("Mock context: ").strip()
                
                if mock_json:
                    try:
                        mock_data = json.loads(mock_json)
                        self._run_stage_with_mock(stage_name, mock_data)
                    except json.JSONDecodeError:
                        print("❌ Invalid JSON format")
                else:
                    self._run_stage(stage_name)
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def test_sequence(self):
        """Test a sequence of stages."""
        if not self.current_image:
            print("❌ No image loaded. Please load an image first.")
            return
        
        print("\nAvailable stages:")
        for i, stage_name in enumerate(self.stages.keys(), 1):
            stage = self.stages[stage_name]
            print(f"{i}. {stage_name} - {stage.get_stage_description()}")
        
        print("\nEnter stage numbers to test in sequence (comma-separated):")
        print("Example: 1,2,3 or 1,3,5")
        
        try:
            choices = input("Stages: ").strip().split(',')
            stage_names = list(self.stages.keys())
            selected_stages = []
            
            for choice in choices:
                stage_idx = int(choice.strip()) - 1
                if 0 <= stage_idx < len(stage_names):
                    selected_stages.append(stage_names[stage_idx])
                else:
                    print(f"❌ Invalid stage number: {choice}")
                    return
            
            self._run_stage_sequence(selected_stages)
            
        except ValueError:
            print("❌ Please enter valid numbers")
    
    def show_context(self):
        """Show current context."""
        print("\n📋 Current Context:")
        if self.context:
            for key, value in self.context.items():
                print(f"  {key}: {value}")
        else:
            print("  (empty)")
        
        if self.current_image:
            print(f"\n📁 Current Image: {self.current_image}")
        else:
            print("\n📁 Current Image: (none)")
    
    def clear_context(self):
        """Clear the current context."""
        self.context = {}
        if self.current_image:
            self.context = {
                "original_image_path": self.current_image,
                "current_image_path": self.current_image
            }
        print("✅ Context cleared")
    
    def create_test_image(self):
        """Create a test image."""
        try:
            import cv2
            import numpy as np
            
            # Create a white image
            image = np.ones((600, 800, 3), dtype=np.uint8) * 255
            
            # Add text
            cv2.putText(image, "Test Image for Stage Development", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.putText(image, "Roll No: 123456", (50, 100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.putText(image, "Question 1: A", (50, 150), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            cv2.putText(image, "Question 2: B", (50, 200), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            
            # Save test image
            test_image_path = "test_development_image.jpg"
            cv2.imwrite(test_image_path, image)
            
            self.current_image = test_image_path
            self.context = {
                "original_image_path": test_image_path,
                "current_image_path": test_image_path
            }
            
            print(f"✅ Created test image: {test_image_path}")
            
        except ImportError:
            print("❌ OpenCV not available. Cannot create test image.")
    
    def list_stages(self):
        """List all available stages."""
        print("\n📋 Available Stages:")
        for i, (stage_name, stage) in enumerate(self.stages.items(), 1):
            print(f"{i}. {stage_name}")
            print(f"   Description: {stage.get_stage_description()}")
            print()
    
    def _run_stage(self, stage_name):
        """Run a single stage."""
        stage = self.stages[stage_name]
        
        print(f"\n🧪 Testing stage: {stage_name}")
        print(f"📝 Description: {stage.get_stage_description()}")
        print("-" * 50)
        
        try:
            result = stage.process(self.current_image, self.context)
            
            print(f"✅ Success: {result['success']}")
            if result['success']:
                print("📊 Results:")
                for key, value in result.items():
                    if key not in ['success', 'stage_name', 'stage_description']:
                        print(f"  {key}: {value}")
                
                # Update context with results
                self.context.update(result)
                print("✅ Context updated with stage results")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            print(f"💥 Exception: {str(e)}")
            return None
    
    def _run_stage_with_mock(self, stage_name, mock_data):
        """Run a stage with mock context data."""
        # Create context with mock data
        context = {
            "original_image_path": self.current_image,
            "current_image_path": self.current_image
        }
        context.update(mock_data)
        
        stage = self.stages[stage_name]
        
        print(f"\n🧪 Testing stage: {stage_name} with mock context")
        print(f"📝 Description: {stage.get_stage_description()}")
        print(f"🎭 Mock data: {mock_data}")
        print("-" * 50)
        
        try:
            result = stage.process(self.current_image, context)
            
            print(f"✅ Success: {result['success']}")
            if result['success']:
                print("📊 Results:")
                for key, value in result.items():
                    if key not in ['success', 'stage_name', 'stage_description']:
                        print(f"  {key}: {value}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            print(f"💥 Exception: {str(e)}")
            return None
    
    def _run_stage_sequence(self, stage_names):
        """Run a sequence of stages."""
        print(f"\n🔄 Testing sequence: {' -> '.join(stage_names)}")
        print("-" * 50)
        
        results = {}
        
        for stage_name in stage_names:
            print(f"\n📋 Stage: {stage_name}")
            result = self._run_stage(stage_name)
            results[stage_name] = result
            
            if not result or not result['success']:
                print(f"❌ Sequence stopped at {stage_name}")
                break
        
        print(f"\n📊 Sequence Summary:")
        for stage_name, result in results.items():
            status = "✅" if result and result['success'] else "❌"
            error = result.get('error', 'Success') if result else 'Not run'
            print(f"{status} {stage_name}: {error}")
    
    def run(self):
        """Run the interactive development environment."""
        print("🚀 Starting Pipeline Stage Development Environment")
        print("This tool helps you test and develop individual pipeline stages.")
        
        while True:
            self.show_menu()
            choice = input("Enter your choice (1-9): ").strip()
            
            if choice == '1':
                self.load_image()
            elif choice == '2':
                self.test_single_stage()
            elif choice == '3':
                self.test_with_mock_context()
            elif choice == '4':
                self.test_sequence()
            elif choice == '5':
                self.show_context()
            elif choice == '6':
                self.clear_context()
            elif choice == '7':
                self.create_test_image()
            elif choice == '8':
                self.list_stages()
            elif choice == '9':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-9.")
            
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    developer = StageDeveloper()
    developer.run()
