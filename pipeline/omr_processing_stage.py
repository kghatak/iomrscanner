#!/usr/bin/env python3
"""
OMR Processing Stage Implementation

This stage processes the OMR sheet and extracts answers.
"""

import os
import cv2
import numpy as np
from .base_stage import PipelineStage
from typing import Dict, Any, Tuple, Optional


class OMRProcessingStage(PipelineStage):
    """Stage 4: Process the OMR sheet"""
    
    def get_stage_name(self) -> str:
        return "omr_processing"
    
    def get_stage_description(self) -> str:
        return "Process the OMR sheet"
    
    def process(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        class_name = self.__class__.__name__
        filename = os.path.basename(image_path)
        
        print(f"[{class_name}] ====== Starting OMR Processing Stage ======")
        print(f"[{class_name}] Processing image: {filename}")
        print(f"[{class_name}] Full image path: {image_path}")
        
        try:
            # Use the rotated image path from previous stage if available
            image_to_process = context.get('rotated_image_path', image_path)
            roll_number = context.get('roll_number', 'Unknown')
            
            print(f"[{class_name}] Image to process: {os.path.basename(image_to_process)}")
            print(f"[{class_name}] Using {'rotated' if image_to_process != image_path else 'original'} image")
            print(f"[{class_name}] Roll number from context: {roll_number}")
            
            # Get detection info from context
            detection_info = context.get('detection_info', {})
            detected_markers = context.get('detected_markers', [])
            
            print(f"[{class_name}] Detected markers from context: {detected_markers}")
            print(f"[{class_name}] Total markers detected: {len(detected_markers)}")
            
            # If in the context Roll number is already detected, then skip the markers 17,
            # 18, 19, 20, else expect all the 20 markers. check if roll_number is not None or empty string.
            if roll_number is not None and roll_number != "":
                expected_markers = list(range(1, 17))  # Markers 1-16
            else:
                expected_markers = list(range(1, 21))  # Markers 1-20

            # Check if all ArUco markers are detected as expected_markers.length    
            print(f"[{class_name}] Checking for all {len(expected_markers)} ArUco markers...")
            print(f"[{class_name}] Expected markers: {expected_markers}")
            
            missing_markers = [m for m in expected_markers if m not in detected_markers]
            
            # if missing marker count is more than 8, fail, otherwise there is a chance to recover.
            if len(missing_markers) > 8:
                error_msg = f"Not all {len(expected_markers)} markers detected. Missing markers: {missing_markers}"
                print(f"[{class_name}] ❌ ERROR: {error_msg}")
                print(f"[{class_name}] Found {len(detected_markers)} markers, need AT LEAST  {round(len(expected_markers)/2)} markers")
                print(f"[{class_name}] Returning failure result")
                return self.create_stage_result(
                    success=False,
                    error=error_msg,
                    omr_data={}
                )
            
            print(f"[{class_name}] ✅ Minumum number of {len(expected_markers)} ArUco markers detected!")
            
            # Read the image
            print(f"[{class_name}] Reading image from disk")
            image = cv2.imread(image_to_process)
            
            if image is None:
                error_msg = "Could not read image for OMR processing"
                print(f"[{class_name}] ❌ ERROR: {error_msg}")
                return self.create_stage_result(
                    success=False,
                    error=error_msg,
                    omr_data={}
                )
            
            print(f"[{class_name}] Image loaded - Shape: {image.shape}")
            
            # Get or create visualization image from context
            print(f"[{class_name}] Getting visualization image from context")
            viz_image_path = context.get('visualization_image_path')
            
            if viz_image_path and os.path.exists(viz_image_path):
                print(f"[{class_name}] Loading existing visualization image: {os.path.basename(viz_image_path)}")
                viz_image = cv2.imread(viz_image_path)
            else:
                print(f"[{class_name}] No visualization image in context, creating new grayscale image")
                viz_image = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
                viz_image = cv2.cvtColor(viz_image, cv2.COLOR_GRAY2BGR)  # Convert to 3-channel for color drawing
                
                # Create visualization subfolder
                image_dir = os.path.dirname(image_to_process)
                viz_folder = os.path.join(image_dir, "visualization")
                os.makedirs(viz_folder, exist_ok=True)
                
                # Save visualization image in visualization subfolder
                base_name = os.path.basename(os.path.splitext(image_to_process)[0])
                viz_image_path = os.path.join(viz_folder, f"{base_name}_visualization.png")
                print(f"[{class_name}] New visualization image path: {viz_image_path}")
            
            print(f"[{class_name}] Visualization image shape: {viz_image.shape}")
            
            # Mark all detected markers with their IDs on the visualization image
            print(f"[{class_name}] Marking detected markers on visualization image...")
            marker_midpoints = detection_info.get('marker_midpoints', [])
            detected_ids = detection_info.get('detected_ids', [])
            
            # Draw detected markers with their IDs
            for i, marker_id in enumerate(detected_ids):
                if i < len(marker_midpoints):
                    midpoint = marker_midpoints[i]
                    x, y = int(midpoint[0]), int(midpoint[1])
                    # Draw a small circle at marker position
                    cv2.circle(viz_image, (x, y), 10, (0, 255, 255), 2)  # Yellow circle
                    # Draw marker ID text
                    marker_text = f"ID:{marker_id}"
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.5
                    thickness = 1
                    (text_width, text_height), baseline = cv2.getTextSize(marker_text, font, font_scale, thickness)
                    # Position text above the marker
                    text_x = x - text_width // 2
                    text_y = y - 15
                    # Draw background rectangle for text
                    cv2.rectangle(viz_image, 
                                (text_x - 2, text_y - text_height - 2),
                                (text_x + text_width + 2, text_y + baseline + 2),
                                (0, 0, 0), -1)  # Black background
                    # Draw text in white
                    cv2.putText(viz_image, marker_text, (text_x, text_y),
                               font, font_scale, (255, 255, 255), thickness)
                    print(f"[{class_name}]   Marked marker {marker_id} at ({x}, {y})")
            
            # Display missing markers at the top of the visualization image
            if missing_markers:
                print(f"[{class_name}] Adding missing markers text at top of image...")
                missing_text = f"Missing Markers: {', '.join(map(str, missing_markers))}"
                font = cv2.FONT_HERSHEY_DUPLEX
                font_scale = 0.8
                thickness = 2
                text_color = (0, 0, 255)  # Red color for missing markers
                bg_color = (255, 255, 255)  # White background
                
                # Get text size
                (text_width, text_height), baseline = cv2.getTextSize(missing_text, font, font_scale, thickness)
                img_height, img_width = viz_image.shape[:2]
                
                # Position text at top center
                text_x = (img_width - text_width) // 2
                text_y = 40
                
                # Draw background rectangle for better visibility
                padding = 10
                cv2.rectangle(viz_image,
                            (text_x - padding, text_y - text_height - padding),
                            (text_x + text_width + padding, text_y + baseline + padding),
                            bg_color, -1)  # White background
                
                # Draw border around background
                cv2.rectangle(viz_image,
                            (text_x - padding, text_y - text_height - padding),
                            (text_x + text_width + padding, text_y + baseline + padding),
                            text_color, 2)  # Red border
                
                # Draw text
                cv2.putText(viz_image, missing_text, (text_x, text_y),
                           font, font_scale, text_color, thickness)
                print(f"[{class_name}]   Missing markers displayed: {missing_markers}")
            else:
                print(f"[{class_name}]   No missing markers - all expected markers detected!")
            
            # Define all 4 columns with their marker IDs
            columns_config = [
                {"number": 1, "markers": [1, 2, 3, 4]},    # Column 1: Markers 1-4
                {"number": 2, "markers": [5, 6, 7, 8]},    # Column 2: Markers 5-8
                {"number": 3, "markers": [9, 10, 11, 12]}, # Column 3: Markers 9-12
                {"number": 4, "markers": [13, 14, 15, 16]} # Column 4: Markers 13-16
            ]
            
            print(f"[{class_name}] Processing all 4 OMR columns...")
            print(f"[{class_name}] Column configuration:")
            for col_config in columns_config:
                print(f"[{class_name}]   Column {col_config['number']}: Markers {col_config['markers']}")
            
            # Extract rectangle coordinates for all columns
            column_rectangles = {}
            extraction_success = True
            
            for col_config in columns_config:
                col_num = col_config['number']
                markers = col_config['markers']
                
                print(f"[{class_name}] ----------------------------------------")
                print(f"[{class_name}] Processing Column {col_num} (Markers {markers})...")
                
                rect_coords = self._get_column_rectangle(
                    detection_info, detected_markers, marker_ids=markers, column_number=col_num
                )
                
                if rect_coords:
                    column_rectangles[f"col{col_num}_rect"] = rect_coords
                    print(f"[{class_name}] ✅ Column {col_num} rectangle: {rect_coords}")
                    
                    # Mark rectangle on visualization image
                    x_min, y_min, x_max, y_max = rect_coords
                    cv2.rectangle(viz_image, (x_min, y_min), (x_max, y_max), (255, 0, 0), 3)  # Blue rectangle
                    cv2.putText(viz_image, f"Column {col_num}", (x_min, y_min - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    print(f"[{class_name}] Rectangle marked on visualization image")
                else:
                    print(f"[{class_name}] ⚠️ Column {col_num} rectangle extraction failed")
                    extraction_success = False
            
            print(f"[{class_name}] ----------------------------------------")
            print(f"[{class_name}] Column extraction summary:")
            print(f"[{class_name}]   Column 1: {'✅' if 'col1_rect' in column_rectangles else '❌'}")
            print(f"[{class_name}]   Column 2: {'✅' if 'col2_rect' in column_rectangles else '❌'}")
            print(f"[{class_name}]   Column 3: {'✅' if 'col3_rect' in column_rectangles else '❌'}")
            print(f"[{class_name}]   Column 4: {'✅' if 'col4_rect' in column_rectangles else '❌'}")
            
            # Save final visualization image with all rectangles marked
            print(f"[{class_name}] Saving final visualization image to: {viz_image_path}")
            cv2.imwrite(viz_image_path, viz_image)
            print(f"[{class_name}] Visualization image saved with all rectangles marked")
            
            # Create OMR data structure
            omr_data = {
                "roll_number": roll_number,
                "detected_markers": detected_markers,
                "all_markers_present": True,
                "processing_timestamp": str(np.datetime64('now')),
                "image_path": image_to_process,
                "columns_detected": len(column_rectangles),
                "omr_answers": {}  # Will be filled later when analyzing columns
            }
            
            # Add column rectangles to omr_data
            omr_data.update(column_rectangles)
            
            print(f"[{class_name}] OMR data created successfully")
            print(f"[{class_name}] Total columns detected: {len(column_rectangles)}/4")
            print(f"[{class_name}] ✅ SUCCESS: OMR processing complete")
            print(f"[{class_name}] Returning success result")
            
            # Return with all column rectangles in the result
            result = self.create_stage_result(
                success=True,
                omr_data=omr_data,
                visualization_image_path=viz_image_path
            )
            
            # Add column rectangles to the result for context update
            result.update(column_rectangles)
            
            print(f"[{class_name}] Context will be updated with column rectangles:")
            for key, rect in column_rectangles.items():
                print(f"[{class_name}]   {key}: {rect}")
            
            return result
            
        except Exception as e:
            error_msg = f"OMR processing failed: {str(e)}"
            print(f"[{class_name}] ❌ EXCEPTION: {error_msg}")
            print(f"[{class_name}] Exception type: {type(e).__name__}")
            import traceback
            print(f"[{class_name}] Traceback: {traceback.format_exc()}")
            print(f"[{class_name}] Returning failure result")
            return self.create_stage_result(
                success=False,
                error=error_msg,
                omr_data={}
            )
        finally:
            print(f"[{class_name}] ====== OMR Processing Stage Complete ======\n")
    
    def _get_column_rectangle(self, detection_info: Dict, detected_markers: list, 
                              marker_ids: list, column_number: int) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the bounding rectangle for a column based on ArUco markers.
        
        Args:
            detection_info: Detection information from ArUco stage
            detected_markers: List of detected marker IDs
            marker_ids: List of 4 marker IDs defining the column [top-left, bottom-left, top-right, bottom-right]
            column_number: Column number (1-4)
            
        Returns:
            Tuple of (x_min, y_min, x_max, y_max) or None if failed
        """
        class_name = self.__class__.__name__
        
        print(f"[{class_name}] _get_column_rectangle() called for column {column_number}")
        print(f"[{class_name}] Marker IDs: {marker_ids}")
        
        # Validate marker_ids length
        if len(marker_ids) != 4:
            print(f"[{class_name}] ❌ ERROR: Expected 4 marker IDs, got {len(marker_ids)}")
            return None
        
        # Check if all required markers are present
        for marker_id in marker_ids:
            if marker_id not in detected_markers:
                print(f"[{class_name}] ❌ ERROR: Required marker {marker_id} not found")
                return None
        
        print(f"[{class_name}] ✅ All required markers present")
        
        # Get marker midpoints
        marker_midpoints = detection_info.get('marker_midpoints', [])
        detected_ids = detection_info.get('detected_ids', [])
        
        print(f"[{class_name}] Getting coordinates for markers {marker_ids}")
        
        # Get coordinates for the 4 corners
        coords = []
        for marker_id in marker_ids:
            idx = detected_ids.index(marker_id)
            midpoint = marker_midpoints[idx]
            coords.append((int(midpoint[0]), int(midpoint[1])))
            print(f"[{class_name}]   Marker {marker_id}: {coords[-1]}")
        
        # Define the four corners: [top-left, bottom-left, top-right, bottom-right]
        top_left, bottom_left, top_right, bottom_right = coords
        
        # Calculate bounding box
        x_min = min(top_left[0], bottom_left[0])
        x_max = max(top_right[0], bottom_right[0])
        y_min = min(top_left[1], top_right[1])
        y_max = max(bottom_left[1], bottom_right[1])
        
        print(f"[{class_name}] Bounding box: ({x_min}, {y_min}) to ({x_max}, {y_max})")
        print(f"[{class_name}] Column dimensions: {x_max - x_min}x{y_max - y_min} pixels")
        
        # Validate bounding box
        if x_max <= x_min or y_max <= y_min:
            print(f"[{class_name}] ❌ ERROR: Invalid bounding box dimensions")
            return None
        
        print(f"[{class_name}] ✅ Rectangle coordinates calculated successfully")
        
        return (x_min, y_min, x_max, y_max)
