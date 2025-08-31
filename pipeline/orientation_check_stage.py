#!/usr/bin/env python3
"""
Orientation Check Stage Implementation

This stage checks image orientation and rotates if needed.
"""

import os
import cv2
from .base_stage import PipelineStage
from typing import Dict, Any


class OrientationCheckStage(PipelineStage):
    """Stage 2: Check image orientation and rotate if needed"""
    
    def get_stage_name(self) -> str:
        return "orientation_check"
    
    def get_stage_description(self) -> str:
        return "Check and rotate tilted images"
    
    def process(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return self.create_stage_result(
                    success=False,
                    error="Could not read image",
                    rotated_image_path=None
                )
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect ArUco markers to determine orientation
            if self.processor.use_new_api:
                corners, ids, rejected = self.processor.aruco_detector.detectMarkers(gray)
            else:
                corners, ids, rejected = cv2.aruco.detectMarkers(
                    gray, self.processor.aruco_dict, parameters=self.processor.aruco_params
                )
            
            if ids is None or len(ids) == 0:
                return self.create_stage_result(
                    success=False,
                    error="No ArUco markers found for orientation detection",
                    rotated_image_path=None
                )
            
            # Use marker positions to determine if rotation is needed
            rotation_needed = self._determine_rotation_needed(corners, ids)
            
            if rotation_needed != 0:
                # Rotate image
                height, width = image.shape[:2]
                center = (width // 2, height // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, rotation_needed, 1.0)
                rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
                
                # Save rotated image
                rotated_path = os.path.splitext(image_path)[0] + "_rotated.jpg"
                cv2.imwrite(rotated_path, rotated_image)
                
                return self.create_stage_result(
                    success=True,
                    rotation_applied=rotation_needed,
                    rotated_image_path=rotated_path
                )
            else:
                return self.create_stage_result(
                    success=True,
                    rotation_applied=0,
                    rotated_image_path=image_path
                )
                
        except Exception as e:
            return self.create_stage_result(
                success=False,
                error=f"Orientation check failed: {str(e)}",
                rotated_image_path=None
            )
    
    def _determine_rotation_needed(self, corners, ids) -> int:
        """
        Determine if image needs rotation based on ArUco marker positions.
        This is a placeholder implementation - you can improve this logic.
        """
        # Simple heuristic: check if markers are in expected positions
        # For now, return 0 (no rotation needed)
        # You can implement more sophisticated logic here
        return 0
