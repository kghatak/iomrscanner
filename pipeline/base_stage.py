#!/usr/bin/env python3
"""
Pipeline Stage Base Class

This module contains the abstract base class for all pipeline stages.
"""

import os
import time
import cv2
from abc import ABC, abstractmethod
from typing import Dict, Any


class PipelineStage(ABC):
    """
    Abstract base class for all pipeline stages.
    
    Each stage must implement:
    - process(): Main processing logic
    - get_stage_name(): Return stage identifier
    - get_stage_description(): Return human-readable description
    """
    
    def __init__(self, processor_instance):
        """
        Initialize the stage with a reference to the main processor.
        
        Args:
            processor_instance: Reference to the ImageProcessor instance
        """
        self.processor = processor_instance
        self.stage_name = self.get_stage_name()
        self.stage_description = self.get_stage_description()
    
    @abstractmethod
    def process(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the image for this stage.
        
        Args:
            image_path: Path to the image to process
            context: Dictionary containing context from previous stages
            
        Returns:
            Dictionary with stage results
        """
        pass
    
    @abstractmethod
    def get_stage_name(self) -> str:
        """Return the stage identifier."""
        pass
    
    @abstractmethod
    def get_stage_description(self) -> str:
        """Return human-readable description of the stage."""
        pass
    
    def create_stage_result(self, success: bool, **kwargs) -> Dict[str, Any]:
        """
        Create a standardized stage result dictionary.
        
        Args:
            success: Whether the stage was successful
            **kwargs: Additional result data
            
        Returns:
            Standardized result dictionary
        """
        result = {
            "success": success,
            "stage_name": self.stage_name,
            "stage_description": self.stage_description
        }
        result.update(kwargs)
        return result

    def run_with_timing(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the stage while measuring elapsed time.

        Adds:
            - elapsed_seconds: float seconds spent in this stage
            - context['stage_times'][stage_name]: elapsed_seconds
        """
        start_time = time.time()
        result = self.process(image_path, context)
        elapsed = time.time() - start_time

        # Attach timing to result
        result["elapsed_seconds"] = elapsed

        # Store timing in context aggregate
        stage_times = context.setdefault("stage_times", {})
        stage_times[self.stage_name] = elapsed

        return result
    
    def log_context(self, context: Dict[str, Any], prefix: str = ""):
        """
        Log the current context dictionary with detailed information.
        
        Args:
            context: Context dictionary to log
            prefix: Optional prefix for log messages
        """
        class_name = self.__class__.__name__
        log_prefix = f"[{class_name}]{prefix}"
        
        print(f"{log_prefix} ========== CONTEXT STATE ==========")
        print(f"{log_prefix} Total context keys: {len(context)}")
        
        # Log each context item with appropriate formatting
        for key, value in context.items():
            if key == "qr_result":
                print(f"{log_prefix}   qr_result: status={value.status.value}")
            elif key in {"qr_identity", "qr_studentID", "qr_exam_roll_number"}:
                print(f"{log_prefix}   {key}: [validated identifier]")
            elif isinstance(value, str) and os.path.exists(value):
                # It's a file path - add descriptive labels
                file_type = ""
                if "visualization_circle" in key:
                    file_type = " (visualization: rectangles + circles)"
                elif "visualization" in key:
                    file_type = " (visualization: rectangles only)"
                else:
                    file_type = " (file)"
                print(f"{log_prefix}   {key}: {os.path.basename(value)}{file_type}")
            elif isinstance(value, (list, tuple)) and len(value) == 4 and all(isinstance(x, (int, float)) for x in value):
                # It's likely rectangle coordinates
                print(f"{log_prefix}   {key}: {value} (rectangle)")
            elif isinstance(value, list):
                # It's a list - check if it contains circle data
                if key.endswith('_circles') and len(value) > 0 and isinstance(value[0], tuple) and len(value[0]) == 3:
                    # It's circle data
                    print(f"{log_prefix}   {key}: [{len(value)} circles]")
                elif len(value) > 10:
                    print(f"{log_prefix}   {key}: [{len(value)} items]")
                else:
                    print(f"{log_prefix}   {key}: {value}")
            elif isinstance(value, dict):
                # It's a nested dictionary
                print(f"{log_prefix}   {key}: {{{len(value)} keys}}")
            elif isinstance(value, (int, float)):
                # Numeric value - check if it's a mean radius
                if key.startswith('r_mean_col_'):
                    print(f"{log_prefix}   {key}: {value:.2f} pixels (mean radius)")
                else:
                    print(f"{log_prefix}   {key}: {value}")
            else:
                # Other types
                value_str = str(value)
                if len(value_str) > 100:
                    print(f"{log_prefix}   {key}: {value_str[:97]}...")
                else:
                    print(f"{log_prefix}   {key}: {value}")
        
        print(f"{log_prefix} ====================================\n")
    
    def handle_pipeline_error(self, image_path: str, output_folder: str, pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle pipeline errors by marking image and moving to error folder.
        
        Args:
            image_path: Path to the original image
            output_folder: Base output folder
            pipeline_result: Current pipeline result dictionary
            
        Returns:
            Updated pipeline result with error information
        """
        class_name = self.__class__.__name__
        filename = os.path.basename(image_path)
        
        print(f"[{class_name}] handle_pipeline_error() called")
        print(f"[{class_name}] Image: {filename}")
        print(f"[{class_name}] Error stage: {pipeline_result.get('error_stage')}")
        print(f"[{class_name}] Error message: {pipeline_result.get('error_message')}")
        
        try:
            # Create error folder
            error_folder = os.path.join(output_folder, "error")
            print(f"[{class_name}] Creating error folder: {error_folder}")
            os.makedirs(error_folder, exist_ok=True)
            print(f"[{class_name}] Error folder created/verified")
            
            # Add red line to image to mark as error
            print(f"[{class_name}] Marking image with error visualization")
            error_image_path = self.mark_image_as_error(image_path, error_folder, pipeline_result)
            print(f"[{class_name}] Error image created: {os.path.basename(error_image_path)}")
            
            # Update pipeline result
            pipeline_result["output_path"] = error_image_path
            pipeline_result["error_image_path"] = error_image_path
            
            print(f"[{class_name}] ❌ Pipeline error handled for {pipeline_result['filename']}")
            print(f"[{class_name}] Failed at stage: '{pipeline_result['error_stage']}'")
            print(f"[{class_name}] Error: {pipeline_result['error_message']}")
            
            return pipeline_result
            
        except Exception as e:
            print(f"[{class_name}] ❌ EXCEPTION in error handler: {str(e)}")
            print(f"[{class_name}] Exception type: {type(e).__name__}")
            return pipeline_result
    
    def mark_image_as_error(self, image_path: str, error_folder: str, pipeline_result: Dict[str, Any]) -> str:
        """
        Add red line to image and save to error folder.
        
        Args:
            image_path: Path to the original image
            error_folder: Error folder path
            pipeline_result: Pipeline result dictionary
            
        Returns:
            Path to the error-marked image
        """
        class_name = self.__class__.__name__
        filename = os.path.basename(image_path)
        
        print(f"[{class_name}] mark_image_as_error() called")
        print(f"[{class_name}] Image: {filename}")
        print(f"[{class_name}] Error folder: {error_folder}")
        
        try:
            # Read image
            print(f"[{class_name}] Reading image from disk")
            image = cv2.imread(image_path)
            
            if image is None:
                print(f"[{class_name}] WARNING: Could not read image, returning original path")
                return image_path
            
            print(f"[{class_name}] Image loaded - Shape: {image.shape}")
            
            # Get error information
            error_stage = pipeline_result.get('error_stage', 'Unknown')
            error_message = pipeline_result.get('error_message', 'Unknown error')
            
            # Add big RED "ERROR" text at top
            text_error = "ERROR"
            text_details = error_stage.replace('_', ' ').title()
            
            font = cv2.FONT_HERSHEY_DUPLEX  # Use DUPLEX for bold-like appearance
            font_scale_big = 3.0
            font_scale_small = 1.2
            thickness_big = 8
            thickness_small = 4
            
            # Get text size for centering
            (text_width, text_height), _ = cv2.getTextSize(text_error, font, font_scale_big, thickness_big)
            (detail_width, detail_height), _ = cv2.getTextSize(text_details, font, font_scale_small, thickness_small)
            
            text_x = (image.shape[1] - text_width) // 2
            text_y = 80
            detail_x = (image.shape[1] - detail_width) // 2
            detail_y = text_y + text_height + 30
            
            # Draw ERROR text with black shadow for visibility
            cv2.putText(image, text_error, (text_x+3, text_y+3), font, font_scale_big, (0, 0, 0), thickness_big)
            cv2.putText(image, text_error, (text_x, text_y), font, font_scale_big, (0, 0, 255), thickness_big)
            
            # Draw error details
            cv2.putText(image, text_details, (detail_x+2, detail_y+2), font, font_scale_small, (0, 0, 0), thickness_small)
            cv2.putText(image, text_details, (detail_x, detail_y), font, font_scale_small, (0, 0, 255), thickness_small)
            
            print(f"[{class_name}] Added BIG RED 'ERROR' text to image")
            print(f"[{class_name}] Error details shown: {text_details}")
            
            # Get roll number for filename (if available)
            context = pipeline_result.get('context', {})
            roll_number = context.get('roll_number', 'Unknown')
            if not roll_number or roll_number == 'Unknown':
                roll_number = os.path.splitext(filename)[0]
            
            # Sanitize roll number for filename
            safe_roll_number = "".join(c for c in roll_number if c.isalnum() or c in ('_', '-'))
            if not safe_roll_number:
                safe_roll_number = "error_unknown"
            
            # Save to error folder with roll number as filename
            error_image_path = os.path.join(error_folder, f"{safe_roll_number}.png")
            print(f"[{class_name}] Saving error-marked image to: {error_image_path}")
            cv2.imwrite(error_image_path, image)
            print(f"[{class_name}] Error-marked image saved successfully")
            
            return error_image_path
            
        except Exception as e:
            print(f"[{class_name}] ❌ EXCEPTION in mark_image_as_error: {str(e)}")
            print(f"[{class_name}] Exception type: {type(e).__name__}")
            print(f"[{class_name}] Returning original image path")
            return image_path
