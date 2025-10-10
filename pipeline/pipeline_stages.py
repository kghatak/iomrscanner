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
from .omr_answer_extraction_stage import OMRAnswerExtractionStage
from .answer_validation_stage import AnswerValidationStage
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
        class_name = self.__class__.__name__
        print(f"[{class_name}] Initializing PipelineManager")
        
        self.processor = processor_instance
        self.stages = []
        
        print(f"[{class_name}] Calling _initialize_default_stages()")
        self._initialize_default_stages()
        print(f"[{class_name}] PipelineManager initialized with {len(self.stages)} stages")
    
    def _initialize_default_stages(self):
        """Initialize the default pipeline stages."""
        class_name = self.__class__.__name__
        print(f"[{class_name}] Creating default pipeline stages")
        
        # Core stages (always included)
        self.stages = [
            ArUcoCheckStage(self.processor),
            OrientationCheckStage(self.processor),
            RollNumberExtractionStage(self.processor),
            OMRProcessingStage(self.processor),
            OMRAnswerExtractionStage(self.processor),
            AnswerValidationStage(self.processor),  # Validate and detect answers
            APIUploadStage(self.processor)
        ]
        
        # NOTE: ML Dataset Generator stage is DISABLED by default
        # To enable, manually add it: processor.pipeline_manager.add_stage(MLDatasetGeneratorStage(processor), position=6)
        
        print(f"[{class_name}] Default stages created:")
        for i, stage in enumerate(self.stages, 1):
            print(f"[{class_name}]   Stage {i}: {stage.get_stage_name()} - {stage.get_stage_description()}")
    
    def add_stage(self, stage: PipelineStage, position: Optional[int] = None):
        """
        Add a new stage to the pipeline.
        
        Args:
            stage: PipelineStage instance to add
            position: Position to insert the stage (None for end)
        """
        class_name = self.__class__.__name__
        print(f"[{class_name}] add_stage() called")
        print(f"[{class_name}] Adding stage: {stage.get_stage_name()}")
        print(f"[{class_name}] Position: {'end' if position is None else position}")
        
        if position is None:
            self.stages.append(stage)
            print(f"[{class_name}] Stage appended to end of pipeline")
        else:
            self.stages.insert(position, stage)
            print(f"[{class_name}] Stage inserted at position {position}")
        
        print(f"[{class_name}] Pipeline now has {len(self.stages)} stages")
    
    def remove_stage(self, stage_name: str) -> bool:
        """
        Remove a stage from the pipeline.
        
        Args:
            stage_name: Name of the stage to remove
            
        Returns:
            True if stage was removed, False if not found
        """
        class_name = self.__class__.__name__
        print(f"[{class_name}] remove_stage() called")
        print(f"[{class_name}] Looking for stage: {stage_name}")
        
        for i, stage in enumerate(self.stages):
            if stage.get_stage_name() == stage_name:
                print(f"[{class_name}] Stage found at position {i}")
                del self.stages[i]
                print(f"[{class_name}] Stage removed successfully")
                print(f"[{class_name}] Pipeline now has {len(self.stages)} stages")
                return True
        
        print(f"[{class_name}] Stage not found: {stage_name}")
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
        class_name = self.__class__.__name__
        filename = os.path.basename(image_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        print(f"[{class_name}] ========================================")
        print(f"[{class_name}] STARTING PIPELINE PROCESSING")
        print(f"[{class_name}] ========================================")
        print(f"[{class_name}] Image: {filename}")
        print(f"[{class_name}] Full path: {image_path}")
        print(f"[{class_name}] Output folder: {output_folder}")
        print(f"[{class_name}] Total pipeline stages: {len(self.stages)}")
        
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
        
        print(f"[{class_name}] Pipeline result initialized")
        
        # Context to pass between stages
        context = {
            "original_image_path": image_path,
            "current_image_path": image_path
        }
        
        print(f"[{class_name}] Context initialized: {context}")
        
        # Log initial context state
        if self.stages:
            self.stages[0].log_context(context, prefix=" [Initial Context]")
        
        print(f"[{class_name}] ========================================\n")
        
        try:
            # Process through each stage
            for stage_index, stage in enumerate(self.stages, 1):
                stage_name = stage.get_stage_name()
                stage_desc = stage.get_stage_description()
                
                print(f"[{class_name}] ========================================")
                print(f"[{class_name}] STAGE {stage_index}/{len(self.stages)}: {stage_name}")
                print(f"[{class_name}] Description: {stage_desc}")
                print(f"[{class_name}] Processing: {filename}")
                print(f"[{class_name}] Current image path: {context['current_image_path']}")
                print(f"[{class_name}] ========================================")
                
                # Process the stage
                print(f"[{class_name}] Calling stage.process()...")
                stage_result = stage.process(context["current_image_path"], context)
                print(f"[{class_name}] Stage process() returned")
                print(f"[{class_name}] Stage result success: {stage_result.get('success')}")
                
                pipeline_result["stages"][stage_name] = stage_result
                print(f"[{class_name}] Stage result stored in pipeline_result")
                
                # Check if stage failed
                if not stage_result["success"]:
                    error_msg = stage_result.get("error", "Unknown error")
                    print(f"[{class_name}] ❌ STAGE FAILED: {stage_name}")
                    print(f"[{class_name}] Error: {error_msg}")
                    print(f"[{class_name}] Stopping pipeline processing")
                    
                    pipeline_result["error_stage"] = stage_name
                    pipeline_result["error_message"] = error_msg
                    pipeline_result["context"] = context  # Add context for roll number access
                    
                    print(f"[{class_name}] Calling handle_pipeline_error()")
                    return stage.handle_pipeline_error(image_path, output_folder, pipeline_result)
                
                print(f"[{class_name}] ✅ Stage completed successfully")
                
                # Update context with stage results
                print(f"[{class_name}] Updating context with stage results")
                context.update(stage_result)
                print(f"[{class_name}] Context updated - Keys: {list(context.keys())}")
                
                # Update current image path if stage produced a new image
                if "rotated_image_path" in stage_result:
                    old_path = context["current_image_path"]
                    context["current_image_path"] = stage_result["rotated_image_path"]
                    print(f"[{class_name}] Current image path updated:")
                    print(f"[{class_name}]   Old: {os.path.basename(old_path)}")
                    print(f"[{class_name}]   New: {os.path.basename(context['current_image_path'])}")
                
                # Log complete context state after this stage
                stage.log_context(context, prefix=f" [After {stage_name}]")
                
                print(f"[{class_name}] Stage {stage_index}/{len(self.stages)} complete\n")
            
            # All stages successful
            print(f"[{class_name}] ========================================")
            print(f"[{class_name}] ALL STAGES COMPLETED SUCCESSFULLY")
            print(f"[{class_name}] ========================================")
            
            # Log final context state
            if self.stages:
                self.stages[0].log_context(context, prefix=" [Final Context]")
            
            pipeline_result["success"] = True
            pipeline_result["output_path"] = context["current_image_path"]
            pipeline_result["api_upload_success"] = True
            
            print(f"[{class_name}] Pipeline result marked as successful")
            
            # Move to success folder with roll number as filename
            success_folder = os.path.join(output_folder, "success")
            print(f"[{class_name}] Creating success folder: {success_folder}")
            os.makedirs(success_folder, exist_ok=True)
            print(f"[{class_name}] Success folder created/verified")
            
            # Get roll number for filename
            roll_number = context.get('roll_number', 'Unknown')
            # Sanitize roll number for filename
            safe_roll_number = "".join(c for c in roll_number if c.isalnum() or c in ('_', '-'))
            if not safe_roll_number or safe_roll_number == 'Unknown':
                safe_roll_number = name_without_ext
            
            # Use visualization image (with green marked circles) instead of original
            viz_image_path = context.get('visualization_image_path')
            if viz_image_path and os.path.exists(viz_image_path):
                print(f"[{class_name}] Using visualization image: {os.path.basename(viz_image_path)}")
                success_image = cv2.imread(viz_image_path)
            else:
                print(f"[{class_name}] Visualization not found, using current image")
                success_image = cv2.imread(context["current_image_path"])
            
            # Add big GREEN "SUCCESS" text at top with details
            if success_image is not None:
                height, width = success_image.shape[:2]
                
                # Get data for display
                marked_count = context.get('marked_count', 0)
                
                # Main SUCCESS text
                text = "SUCCESS"
                font_big = cv2.FONT_HERSHEY_DUPLEX
                font_small = cv2.FONT_HERSHEY_SIMPLEX
                font_scale_big = 3.0
                font_scale_small = 0.8
                thickness_big = 8
                thickness_small = 2
                
                # Get text size for centering
                (text_width, text_height), baseline = cv2.getTextSize(text, font_big, font_scale_big, thickness_big)
                text_x = (width - text_width) // 2
                text_y = 80  # 80 pixels from top
                
                # Draw SUCCESS text with black shadow
                cv2.putText(success_image, text, (text_x+3, text_y+3), font_big, font_scale_big, (0, 0, 0), thickness_big)
                cv2.putText(success_image, text, (text_x, text_y), font_big, font_scale_big, (0, 255, 0), thickness_big)
                
                # Add details below SUCCESS text
                details_y = text_y + text_height + 20
                line_height = 30
                details_x = 50  # Left margin
                
                # 1. Exam Roll Number
                detail_line = f"Exam Roll Number: {roll_number}"
                cv2.putText(success_image, detail_line, (details_x+2, details_y+2), 
                           font_small, font_scale_small, (0, 0, 0), thickness_small)
                cv2.putText(success_image, detail_line, (details_x, details_y), 
                           font_small, font_scale_small, (0, 255, 0), thickness_small)
                
                # 2. Number of answers Marked
                details_y += line_height
                detail_line = f"Number of answers Marked: {marked_count}"
                cv2.putText(success_image, detail_line, (details_x+2, details_y+2), 
                           font_small, font_scale_small, (0, 0, 0), thickness_small)
                cv2.putText(success_image, detail_line, (details_x, details_y), 
                           font_small, font_scale_small, (0, 255, 0), thickness_small)
                
                # 3. Number of Answers correct (blank for now)
                details_y += line_height
                detail_line = "Number of Answers correct: _____"
                cv2.putText(success_image, detail_line, (details_x+2, details_y+2), 
                           font_small, font_scale_small, (0, 0, 0), thickness_small)
                cv2.putText(success_image, detail_line, (details_x, details_y), 
                           font_small, font_scale_small, (255, 255, 255), thickness_small)  # White for blank
                
                # 4. Marks obtained (blank for now)
                details_y += line_height
                detail_line = "Marks obtained: _____"
                cv2.putText(success_image, detail_line, (details_x+2, details_y+2), 
                           font_small, font_scale_small, (0, 0, 0), thickness_small)
                cv2.putText(success_image, detail_line, (details_x, details_y), 
                           font_small, font_scale_small, (255, 255, 255), thickness_small)  # White for blank
                
                print(f"[{class_name}] Added GREEN 'SUCCESS' text with details to image")
                print(f"[{class_name}]   Roll Number: {roll_number}")
                print(f"[{class_name}]   Marked Answers: {marked_count}")
            
            final_output_path = os.path.join(success_folder, f"{safe_roll_number}.png")
            print(f"[{class_name}] Saving success image to: {final_output_path}")
            cv2.imwrite(final_output_path, success_image)
            print(f"[{class_name}] Success image saved")
            
            pipeline_result["output_path"] = final_output_path
            
            print(f"[{class_name}] ✅ PIPELINE COMPLETED SUCCESSFULLY for {filename}")
            print(f"[{class_name}] Final output: {final_output_path}")
            print(f"[{class_name}] ========================================\n")
            
            return pipeline_result
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"[{class_name}] ========================================")
            print(f"[{class_name}] ❌ PIPELINE EXCEPTION")
            print(f"[{class_name}] ========================================")
            print(f"[{class_name}] Exception: {error_msg}")
            print(f"[{class_name}] Exception type: {type(e).__name__}")
            print(f"[{class_name}] Image: {filename}")
            
            pipeline_result["error_stage"] = "pipeline_exception"
            pipeline_result["error_message"] = error_msg
            
            # Use the first stage for error handling (they all have the same error handling methods)
            if self.stages:
                print(f"[{class_name}] Calling handle_pipeline_error() on first stage")
                return self.stages[0].handle_pipeline_error(image_path, output_folder, pipeline_result)
            else:
                print(f"[{class_name}] No stages available for error handling")
                return pipeline_result
