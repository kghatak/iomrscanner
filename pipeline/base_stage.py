#!/usr/bin/env python3
"""
Pipeline Stage Base Class

This module contains the abstract base class for all pipeline stages.
"""

import os
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
        try:
            # Create error folder
            error_folder = os.path.join(output_folder, "error")
            os.makedirs(error_folder, exist_ok=True)
            
            # Add red line to image to mark as error
            error_image_path = self.mark_image_as_error(image_path, error_folder, pipeline_result)
            
            # Update pipeline result
            pipeline_result["output_path"] = error_image_path
            pipeline_result["error_image_path"] = error_image_path
            
            print(f"[PIPELINE] ❌ Error at stage '{pipeline_result['error_stage']}' for {pipeline_result['filename']}")
            print(f"[PIPELINE] Error message: {pipeline_result['error_message']}")
            
            return pipeline_result
            
        except Exception as e:
            print(f"[PIPELINE] Failed to handle error: {str(e)}")
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
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return image_path
            
            # Add red line across the image
            height, width = image.shape[:2]
            cv2.line(image, (0, height//2), (width, height//2), (0, 0, 255), 5)  # Red line
            
            # Add error text
            error_text = f"ERROR: {pipeline_result['error_stage']}"
            cv2.putText(image, error_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Save to error folder
            filename = os.path.basename(image_path)
            name_without_ext = os.path.splitext(filename)[0]
            error_image_path = os.path.join(error_folder, f"{name_without_ext}_ERROR.jpg")
            cv2.imwrite(error_image_path, image)
            
            return error_image_path
            
        except Exception as e:
            print(f"Failed to mark image as error: {str(e)}")
            return image_path
