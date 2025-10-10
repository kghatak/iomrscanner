#!/usr/bin/env python3
"""
ArUco Check Stage Implementation

This stage checks if basic ArUco markers are present in the image.
"""

import os
from .base_stage import PipelineStage
from typing import Dict, Any


class ArUcoCheckStage(PipelineStage):
    """Stage 1: Check if basic ArUco markers are present"""
    
    def get_stage_name(self) -> str:
        return "aruco_check"
    
    def get_stage_description(self) -> str:
        return "Check basic ArUco markers are present"
    
    def process(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        class_name = self.__class__.__name__
        filename = os.path.basename(image_path)
        
        print(f"[{class_name}] ====== Starting ArUco Check Stage ======")
        print(f"[{class_name}] Processing image: {filename}")
        print(f"[{class_name}] Full image path: {image_path}")
        
        try:
            print(f"[{class_name}] Calling detect_aruco_markers() on processor")
            detected_ids, detection_info = self.processor.detect_aruco_markers(image_path)
            print(f"[{class_name}] ArUco detection completed")
            print(f"[{class_name}] Detected marker IDs: {detected_ids}")
            
            if "error" in detection_info:
                error_msg = detection_info["error"]
                print(f"[{class_name}] ❌ ERROR: Detection error occurred: {error_msg}")
                print(f"[{class_name}] Returning failure result")
                return self.create_stage_result(
                    success=False,
                    error=error_msg,
                    detected_markers=[]
                )
            
            # Check if we have at least some markers (adjust threshold as needed)
            min_required_markers = 5  # Minimum markers required
            print(f"[{class_name}] Minimum required markers: {min_required_markers}")
            print(f"[{class_name}] Number of markers detected: {len(detected_ids)}")
            
            if len(detected_ids) < min_required_markers:
                error_msg = f"Insufficient ArUco markers found. Expected at least {min_required_markers}, found {len(detected_ids)}"
                print(f"[{class_name}] ❌ FAILURE: {error_msg}")
                print(f"[{class_name}] Detected markers: {detected_ids}")
                print(f"[{class_name}] Returning failure result")
                return self.create_stage_result(
                    success=False,
                    error=error_msg,
                    detected_markers=detected_ids
                )
            
            print(f"[{class_name}] ✅ SUCCESS: Sufficient markers detected")
            print(f"[{class_name}] Detection info: {detection_info}")
            print(f"[{class_name}] Returning success result")
            return self.create_stage_result(
                success=True,
                detected_markers=detected_ids,
                detection_info=detection_info
            )
            
        except Exception as e:
            error_msg = f"ArUco detection failed: {str(e)}"
            print(f"[{class_name}] ❌ EXCEPTION: {error_msg}")
            print(f"[{class_name}] Exception type: {type(e).__name__}")
            print(f"[{class_name}] Returning failure result")
            return self.create_stage_result(
                success=False,
                error=error_msg,
                detected_markers=[]
            )
        finally:
            print(f"[{class_name}] ====== ArUco Check Stage Complete ======\n")
