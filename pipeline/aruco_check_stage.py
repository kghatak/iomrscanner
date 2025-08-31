#!/usr/bin/env python3
"""
ArUco Check Stage Implementation

This stage checks if basic ArUco markers are present in the image.
"""

from .base_stage import PipelineStage
from typing import Dict, Any


class ArUcoCheckStage(PipelineStage):
    """Stage 1: Check if basic ArUco markers are present"""
    
    def get_stage_name(self) -> str:
        return "aruco_check"
    
    def get_stage_description(self) -> str:
        return "Check basic ArUco markers are present"
    
    def process(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            detected_ids, detection_info = self.processor.detect_aruco_markers(image_path)
            
            if "error" in detection_info:
                return self.create_stage_result(
                    success=False,
                    error=detection_info["error"],
                    detected_markers=[]
                )
            
            # Check if we have at least some markers (adjust threshold as needed)
            min_required_markers = 5  # Minimum markers required
            if len(detected_ids) < min_required_markers:
                return self.create_stage_result(
                    success=False,
                    error=f"Insufficient ArUco markers found. Expected at least {min_required_markers}, found {len(detected_ids)}",
                    detected_markers=detected_ids
                )
            
            return self.create_stage_result(
                success=True,
                detected_markers=detected_ids,
                detection_info=detection_info
            )
            
        except Exception as e:
            return self.create_stage_result(
                success=False,
                error=f"ArUco detection failed: {str(e)}",
                detected_markers=[]
            )
