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
        class_name = self.__class__.__name__
        filename = os.path.basename(image_path)
        
        print(f"[{class_name}] ====== Starting Orientation Check Stage ======")
        print(f"[{class_name}] Processing image: {filename}")
        print(f"[{class_name}] Full image path: {image_path}")
        
        try:
            # Read image
            print(f"[{class_name}] Reading image from disk")
            image = cv2.imread(image_path)
            
            if image is None:
                print(f"[{class_name}] ❌ ERROR: Could not read image from path")
                print(f"[{class_name}] Returning failure result")
                return self.create_stage_result(
                    success=False,
                    error="Could not read image",
                    rotated_image_path=None
                )
            
            print(f"[{class_name}] Image loaded successfully - Shape: {image.shape}")
            
            # Convert to grayscale
            print(f"[{class_name}] Converting image to grayscale for marker detection")
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            print(f"[{class_name}] Grayscale conversion complete")
            
            # Detect ArUco markers to determine orientation
            print(f"[{class_name}] Detecting ArUco markers for orientation analysis")
            print(f"[{class_name}] Using {'new' if self.processor.use_new_api else 'old'} OpenCV API")
            
            if self.processor.use_new_api:
                corners, ids, rejected = self.processor.aruco_detector.detectMarkers(gray)
            else:
                corners, ids, rejected = cv2.aruco.detectMarkers(
                    gray, self.processor.aruco_dict, parameters=self.processor.aruco_params
                )
            
            print(f"[{class_name}] Marker detection complete")
            print(f"[{class_name}] Markers found: {len(ids) if ids is not None else 0}")
            print(f"[{class_name}] Marker IDs: {ids.flatten().tolist() if ids is not None else []}")
            
            if ids is None or len(ids) == 0:
                print(f"[{class_name}] ❌ FAILURE: No ArUco markers found for orientation detection")
                print(f"[{class_name}] Cannot determine orientation without markers")
                print(f"[{class_name}] Returning failure result")
                return self.create_stage_result(
                    success=False,
                    error="No ArUco markers found for orientation detection",
                    rotated_image_path=None
                )
            
            # Use marker positions to determine if rotation is needed
            print(f"[{class_name}] Analyzing marker positions to determine rotation")
            rotation_needed = self._determine_rotation_needed(corners, ids)
            print(f"[{class_name}] Rotation analysis complete - Rotation needed: {rotation_needed}°")
            
            if rotation_needed != 0:
                print(f"[{class_name}] Image requires rotation: {rotation_needed}°")
                
                # Rotate image
                height, width = image.shape[:2]
                center = (width // 2, height // 2)
                print(f"[{class_name}] Image dimensions: {width}x{height}")
                print(f"[{class_name}] Rotation center: {center}")
                print(f"[{class_name}] Creating rotation matrix")
                
                rotation_matrix = cv2.getRotationMatrix2D(center, rotation_needed, 1.0)
                print(f"[{class_name}] Applying rotation transformation")
                rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
                print(f"[{class_name}] Rotation applied successfully")
                
                # Save rotated image
                rotated_path = os.path.splitext(image_path)[0] + "_rotated.jpg"
                print(f"[{class_name}] Saving rotated image to: {rotated_path}")
                cv2.imwrite(rotated_path, rotated_image)
                print(f"[{class_name}] Rotated image saved successfully")
                
                print(f"[{class_name}] ✅ SUCCESS: Image rotated and saved")
                print(f"[{class_name}] Returning success result with rotated image path")
                return self.create_stage_result(
                    success=True,
                    rotation_applied=rotation_needed,
                    rotated_image_path=rotated_path
                )
            else:
                print(f"[{class_name}] No rotation needed - Image orientation is correct")
                print(f"[{class_name}] ✅ SUCCESS: Using original image path")
                print(f"[{class_name}] Returning success result")
                return self.create_stage_result(
                    success=True,
                    rotation_applied=0,
                    rotated_image_path=image_path
                )
                
        except Exception as e:
            error_msg = f"Orientation check failed: {str(e)}"
            print(f"[{class_name}] ❌ EXCEPTION: {error_msg}")
            print(f"[{class_name}] Exception type: {type(e).__name__}")
            print(f"[{class_name}] Returning failure result")
            return self.create_stage_result(
                success=False,
                error=error_msg,
                rotated_image_path=None
            )
        finally:
            print(f"[{class_name}] ====== Orientation Check Stage Complete ======\n")
    
    def _determine_rotation_needed(self, corners, ids) -> int:
        """
        Determine if image needs rotation based on ArUco marker positions.
        This is a placeholder implementation - you can improve this logic.
        """
        class_name = self.__class__.__name__
        print(f"[{class_name}] _determine_rotation_needed() called")
        print(f"[{class_name}] Number of corners: {len(corners)}")
        print(f"[{class_name}] Number of IDs: {len(ids)}")
        
        # Simple heuristic: check if markers are in expected positions
        # For now, return 0 (no rotation needed)
        # You can implement more sophisticated logic here
        print(f"[{class_name}] Using default logic - returning 0° (no rotation)")
        return 0
