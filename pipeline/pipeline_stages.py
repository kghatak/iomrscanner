#!/usr/bin/env python3
"""
Pipeline Stages Module

This module provides a modular, class-based approach to the image processing pipeline.
Each stage inherits from a base class and can be easily added, removed, or modified.
"""

import os
import cv2
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple, List
import re
import shutil

# Import base class
from .base_stage import PipelineStage

# Import stage implementations
from .aruco_check_stage import ArUcoCheckStage
from .orientation_check_stage import OrientationCheckStage
from .roll_number_extraction_stage import RollNumberExtractionStage
from .omr_processing_stage import OMRProcessingStage
from .api_upload_stage import APIUploadStage


class PipelineManager:
    """
    Manages the pipeline stages and orchestrates the processing flow.
    """
    
    def __init__(self, processor_instance):
        """
        Initialize the pipeline manager.
        
        Args:
            processor_instance: Reference to the ImageProcessor instance
        """
        self.processor = processor_instance
        self.stages = []
        self._initialize_default_stages()
    
    def _initialize_default_stages(self):
        """Initialize the default pipeline stages."""
        self.stages = [
            ArUcoCheckStage(self.processor),
            OrientationCheckStage(self.processor),
            RollNumberExtractionStage(self.processor),
            OMRProcessingStage(self.processor),
            APIUploadStage(self.processor)
        ]
    
    def add_stage(self, stage: PipelineStage, position: Optional[int] = None):
        """
        Add a new stage to the pipeline.
        
        Args:
            stage: PipelineStage instance to add
            position: Position to insert the stage (None for end)
        """
        if position is None:
            self.stages.append(stage)
        else:
            self.stages.insert(position, stage)
    
    def remove_stage(self, stage_name: str) -> bool:
        """
        Remove a stage from the pipeline.
        
        Args:
            stage_name: Name of the stage to remove
            
        Returns:
            True if stage was removed, False if not found
        """
        for i, stage in enumerate(self.stages):
            if stage.get_stage_name() == stage_name:
                del self.stages[i]
                return True
        return False
    
    def get_stage(self, stage_name: str) -> Optional[PipelineStage]:
        """
        Get a stage by name.
        
        Args:
            stage_name: Name of the stage to retrieve
            
        Returns:
            PipelineStage instance or None if not found
        """
        for stage in self.stages:
            if stage.get_stage_name() == stage_name:
                return stage
        return None
    
    def get_stages_info(self) -> List[Dict[str, str]]:
        """
        Get information about all stages.
        
        Returns:
            List of dictionaries with stage information
        """
        return [
            {
                "name": stage.get_stage_name(),
                "description": stage.get_stage_description()
            }
            for stage in self.stages
        ]
    
    def process_image(self, image_path: str, output_folder: str) -> Dict[str, Any]:
        """
        Process an image through all pipeline stages.
        
        Args:
            image_path: Path to the image to process
            output_folder: Base output folder for results
            
        Returns:
            Dictionary with processing results and stage information
        """
        filename = os.path.basename(image_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        print(f"[PIPELINE] Starting processing for: {filename}")
        
        # Initialize pipeline result
        pipeline_result = {
            "filename": filename,
            "success": False,
            "stages": {},
            "error_stage": None,
            "error_message": None,
            "output_path": None,
            "api_upload_success": False
        }
        
        # Context to pass between stages
        context = {
            "original_image_path": image_path,
            "current_image_path": image_path
        }
        
        try:
            # Process through each stage
            for stage in self.stages:
                stage_name = stage.get_stage_name()
                print(f"[PIPELINE] {stage_name}: {stage.get_stage_description()} for {filename}")
                
                # Process the stage
                stage_result = stage.process(context["current_image_path"], context)
                pipeline_result["stages"][stage_name] = stage_result
                
                # Check if stage failed
                if not stage_result["success"]:
                    pipeline_result["error_stage"] = stage_name
                    pipeline_result["error_message"] = stage_result.get("error", "Unknown error")
                    return stage.handle_pipeline_error(image_path, output_folder, pipeline_result)
                
                # Update context with stage results
                context.update(stage_result)
                
                # Update current image path if stage produced a new image
                if "rotated_image_path" in stage_result:
                    context["current_image_path"] = stage_result["rotated_image_path"]
            
            # All stages successful
            pipeline_result["success"] = True
            pipeline_result["output_path"] = context["current_image_path"]
            pipeline_result["api_upload_success"] = True
            
            # Move to success folder
            success_folder = os.path.join(output_folder, "success")
            os.makedirs(success_folder, exist_ok=True)
            
            final_output_path = os.path.join(success_folder, f"{name_without_ext}_processed.jpg")
            shutil.copy2(context["current_image_path"], final_output_path)
            pipeline_result["output_path"] = final_output_path
            
            print(f"[PIPELINE] ✅ All stages completed successfully for {filename}")
            return pipeline_result
            
        except Exception as e:
            pipeline_result["error_stage"] = "pipeline_exception"
            pipeline_result["error_message"] = f"Unexpected error: {str(e)}"
            # Use the first stage for error handling (they all have the same error handling methods)
            if self.stages:
                return self.stages[0].handle_pipeline_error(image_path, output_folder, pipeline_result)
            else:
                return pipeline_result
