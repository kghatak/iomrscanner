#!/usr/bin/env python3
"""
OMR Processing Second Stage (Pass 2) Implementation

This stage performs a second pass to estimate missing column rectangles
if the first pass (OMRProcessingStage) failed to detect all columns or
if roll number extraction failed.
"""

import os
import cv2
import numpy as np
from .base_stage import PipelineStage
from .omr_column_estimation import estimated_column_rectangle
from typing import Dict, Any, Optional, Tuple


class OMRProcessingSecondStage(PipelineStage):
    """Stage: Second pass for OMR column rectangle detection (Pass 2)"""
    
    def get_stage_name(self) -> str:
        return "omr_processing_second"
    
    def get_stage_description(self) -> str:
        return "Second pass for estimating missing column rectangles"
    
    def process(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        class_name = self.__class__.__name__
        filename = os.path.basename(image_path)
        
        print(f"[{class_name}] ====== Starting OMR Processing Second Stage (Pass 2) ======")
        print(f"[{class_name}] Processing image: {filename}")
        print(f"[{class_name}] Full image path: {image_path}")
        
        try:
            # Check condition 1: Roll number extracted properly
            roll_number = context.get('roll_number')
            roll_number_extracted = roll_number is not None and roll_number != "" and roll_number != "Unknown"
            
            print(f"[{class_name}] Condition 1 - Roll number extracted: {roll_number_extracted}")
            if roll_number_extracted:
                print(f"[{class_name}]   Roll number: {roll_number}")
            else:
                print(f"[{class_name}]   Roll number: {roll_number} (not properly extracted)")
            
            # Check condition 2: All four column rectangles detected
            column_rectangles = {
                'col1_rect': context.get('col1_rect'),
                'col2_rect': context.get('col2_rect'),
                'col3_rect': context.get('col3_rect'),
                'col4_rect': context.get('col4_rect')
            }
            
            all_columns_detected = all(rect is not None for rect in column_rectangles.values())
            detected_columns = [col for col, rect in column_rectangles.items() if rect is not None]
            missing_columns = [col for col, rect in column_rectangles.items() if rect is None]
            
            print(f"[{class_name}] Condition 2 - All columns detected: {all_columns_detected}")
            print(f"[{class_name}]   Detected columns: {detected_columns}")
            if missing_columns:
                print(f"[{class_name}]   Missing columns: {missing_columns}")
            
            # Decision: Skip if both conditions are satisfied
            if roll_number_extracted and all_columns_detected:
                print(f"[{class_name}] ✅ Both conditions satisfied:")
                print(f"[{class_name}]   - Roll number extracted: ✅")
                print(f"[{class_name}]   - All 4 columns detected: ✅")
                print(f"[{class_name}] Skipping Pass 2 - no processing needed")
                print(f"[{class_name}] Returning success with no changes")
                
                return self.create_stage_result(
                    success=True,
                    skipped=True,
                    reason="Roll number extracted and all columns detected in Pass 1",
                    omr_data=context.get('omr_data', {}),
                    estimated_columns={}
                )
            
            # Pass 2 needed: At least one condition is not satisfied
            print(f"[{class_name}] ⚠️  Pass 2 needed:")
            if not roll_number_extracted:
                print(f"[{class_name}]   - Roll number NOT extracted: ❌")
            if not all_columns_detected:
                print(f"[{class_name}]   - Missing columns: {missing_columns}")
            
            # Get image and detection info for estimation
            image_to_process = context.get('rotated_image_path', image_path)
            detection_info = context.get('detection_info', {})
            detected_markers = context.get('detected_markers', [])
            
            print(f"[{class_name}] Starting Pass 2 column rectangle estimation...")
            print(f"[{class_name}] Detected markers: {detected_markers}")
            print(f"[{class_name}] Missing columns to estimate: {missing_columns}")
            
            # Read the image
            print(f"[{class_name}] Reading image from disk")
            image = cv2.imread(image_to_process)
            
            if image is None:
                error_msg = "Could not read image for Pass 2 processing"
                print(f"[{class_name}] ❌ ERROR: {error_msg}")
                return self.create_stage_result(
                    success=False,
                    error=error_msg,
                    omr_data={}
                )
            
            print(f"[{class_name}] Image loaded - Shape: {image.shape}")
            
            # Get or create visualization image
            viz_image_path = context.get('visualization_image_path')
            if viz_image_path and os.path.exists(viz_image_path):
                print(f"[{class_name}] Loading existing visualization image")
                viz_image = cv2.imread(viz_image_path)
            else:
                print(f"[{class_name}] Creating new visualization image")
                viz_image = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
                viz_image = cv2.cvtColor(viz_image, cv2.COLOR_GRAY2BGR)
            
            # Dictionary to store estimated column rectangles
            estimated_columns = {}
            
            # Define column configuration (same as in OMRProcessingStage)
            # Each column has 4 markers: [a, b, c, d]
            # a = top-left, b = bottom-left, c = top-right, d = bottom-right
            columns_config = [
                {"number": 1, "markers": [1, 2, 3, 4], "rect_id": "col1_rect"},    # Column 1: Markers 1-4
                {"number": 2, "markers": [5, 6, 7, 8], "rect_id": "col2_rect"},    # Column 2: Markers 5-8
                {"number": 3, "markers": [9, 10, 11, 12], "rect_id": "col3_rect"}, # Column 3: Markers 9-12
                {"number": 4, "markers": [13, 14, 15, 16], "rect_id": "col4_rect"} # Column 4: Markers 13-16
            ]
            
            print(f"[{class_name}] Attempting to estimate missing columns...")
            
            # Try to estimate each missing column
            for missing_col in missing_columns:
                col_num = int(missing_col.replace('col', '').replace('_rect', ''))
                print(f"[{class_name}] ----------------------------------------")
                print(f"[{class_name}] Attempting to estimate Column {col_num} ({missing_col})...")
                
                # Find the column config for this missing column
                col_config = None
                for config in columns_config:
                    if config["number"] == col_num:
                        col_config = config
                        break
                
                if not col_config:
                    print(f"[{class_name}] ❌ ERROR: Could not find config for column {col_num}")
                    continue
                
                marker_ids = col_config["markers"]
                print(f"[{class_name}] Column {col_num} marker IDs: {marker_ids}")
                
                # Check how many markers are present for this column
                column_detected_markers = [m for m in marker_ids if m in detected_markers]
                column_missing_markers = [m for m in marker_ids if m not in detected_markers]
                
                print(f"[{class_name}] Detected markers for column {col_num}: {column_detected_markers}")
                print(f"[{class_name}] Missing markers for column {col_num}: {column_missing_markers}")
                
                # Use the helper function to estimate the rectangle
                estimated_rect = estimated_column_rectangle(
                    rectangle_id=missing_col,
                    detected_markers=detected_markers,
                    detected_rectangles=column_rectangles,  # Already detected rectangles
                    detection_info=detection_info,
                    marker_ids=marker_ids
                )
                
                if estimated_rect:
                    estimated_columns[missing_col] = estimated_rect
                    print(f"[{class_name}] ✅ Successfully estimated {missing_col}: {estimated_rect}")
                    
                    # Mark estimated rectangle on visualization image
                    x_min, y_min, x_max, y_max = estimated_rect
                    cv2.rectangle(viz_image, (x_min, y_min), (x_max, y_max), (0, 255, 255), 3)  # Yellow rectangle for estimated
                    cv2.putText(viz_image, f"Column {col_num} (Est.)", (x_min, y_min - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    print(f"[{class_name}] Estimated rectangle marked on visualization image (yellow)")
                else:
                    print(f"[{class_name}] ❌ Failed to estimate {missing_col}")
                    print(f"[{class_name}]   Missing markers: {column_missing_markers}")
                    print(f"[{class_name}]   Estimation logic may not support this case yet")
            
            print(f"[{class_name}] ----------------------------------------")
            print(f"[{class_name}] Estimation summary:")
            print(f"[{class_name}]   Successfully estimated: {list(estimated_columns.keys())}")
            remaining_missing = [col for col in missing_columns if col not in estimated_columns]
            if remaining_missing:
                print(f"[{class_name}]   Still missing: {remaining_missing}")
            
            # Save visualization image if any changes were made
            if viz_image_path:
                cv2.imwrite(viz_image_path, viz_image)
                print(f"[{class_name}] Visualization image updated")
            
            # Get existing OMR data or create new
            omr_data = context.get('omr_data', {})
            if not omr_data:
                omr_data = {
                    "roll_number": roll_number,
                    "detected_markers": detected_markers,
                    "processing_timestamp": str(np.datetime64('now')),
                    "image_path": image_to_process,
                }
            
            # Update OMR data with estimated columns
            omr_data.update(estimated_columns)
            
            # Update context with estimated columns
            for col_key, rect in estimated_columns.items():
                context[col_key] = rect
                print(f"[{class_name}] Updated context with {col_key}: {rect}")
            
            print(f"[{class_name}] ✅ Pass 2 processing complete")
            print(f"[{class_name}] Estimated columns: {list(estimated_columns.keys())}")
            
            return self.create_stage_result(
                success=True,
                skipped=False,
                omr_data=omr_data,
                estimated_columns=estimated_columns,
                missing_columns=missing_columns,
                visualization_image_path=viz_image_path
            )
            
        except Exception as e:
            error_msg = f"Pass 2 processing failed: {str(e)}"
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
            print(f"[{class_name}] ====== OMR Processing Second Stage Complete ======\n")

