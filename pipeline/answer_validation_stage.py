#!/usr/bin/env python3
"""
Answer Validation and Detection Stage

This stage validates the processing results and detects marked circles
to create the final answer structure.
"""

import os
import cv2
import numpy as np
from .base_stage import PipelineStage
from typing import Dict, Any, List, Optional


class AnswerValidationStage(PipelineStage):
    """Stage: Validate results and detect marked circles for final answers"""
    
    def get_stage_name(self) -> str:
        return "answer_validation"
    
    def get_stage_description(self) -> str:
        return "Validate results and detect marked circles"
    
    def process(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        class_name = self.__class__.__name__
        filename = os.path.basename(image_path)
        
        print(f"[{class_name}] ====== Starting Answer Validation Stage ======")
        print(f"[{class_name}] Processing image: {filename}")
        
        try:
            # Validation Step 1: Check roll number
            print(f"[{class_name}] ========================================")
            print(f"[{class_name}] Validation Step 1: Check Roll Number")
            
            roll_number = context.get('roll_number')
            if not roll_number or roll_number == 'Unknown':
                error_msg = "Roll number not properly extracted"
                print(f"[{class_name}] ❌ VALIDATION FAILED: {error_msg}")
                return self.create_stage_result(
                    success=False,
                    error=error_msg,
                    validation_failed="roll_number_missing"
                )
            
            print(f"[{class_name}] ✅ Roll number found: {roll_number}")
            
            # Validation Step 2: Check 100 grid circles per column (400 total)
            print(f"[{class_name}] ========================================")
            print(f"[{class_name}] Validation Step 2: Check Grid Circles")
            
            total_grid_circles = 0
            column_circle_counts = {}
            
            for col_idx in range(1, 5):
                grid_key = f"col{col_idx}_grid"
                grid_data = context.get(grid_key)
                
                if not grid_data:
                    error_msg = f"Grid data missing for column {col_idx}"
                    print(f"[{class_name}] ❌ VALIDATION FAILED: {error_msg}")
                    return self.create_stage_result(
                        success=False,
                        error=error_msg,
                        validation_failed=f"col{col_idx}_grid_missing"
                    )
                
                grid_circles = grid_data.get('grid_circles', [])
                column_circle_counts[col_idx] = len(grid_circles)
                total_grid_circles += len(grid_circles)
                
                print(f"[{class_name}]   Column {col_idx}: {len(grid_circles)} grid circles")
                
                if len(grid_circles) != 100:
                    error_msg = f"Column {col_idx} has {len(grid_circles)} circles, expected 100"
                    print(f"[{class_name}] ❌ VALIDATION FAILED: {error_msg}")
                    return self.create_stage_result(
                        success=False,
                        error=error_msg,
                        validation_failed=f"col{col_idx}_circle_count"
                    )
            
            if total_grid_circles != 400:
                error_msg = f"Total grid circles: {total_grid_circles}, expected 400"
                print(f"[{class_name}] ❌ VALIDATION FAILED: {error_msg}")
                return self.create_stage_result(
                    success=False,
                    error=error_msg,
                    validation_failed="total_circle_count"
                )
            
            print(f"[{class_name}] ✅ Total grid circles: {total_grid_circles}")
            print(f"[{class_name}] ✅ All validations passed!")
            
            # Step 3: Detect marked circles and create final_answer structure
            print(f"[{class_name}] ========================================")
            print(f"[{class_name}] Step 3: Detect Marked Circles")
            
            # Read original image for circle analysis
            image_to_process = context.get('current_image_path', image_path)
            image = cv2.imread(image_to_process)
            
            if image is None:
                error_msg = "Could not read image for circle detection"
                print(f"[{class_name}] ❌ ERROR: {error_msg}")
                return self.create_stage_result(success=False, error=error_msg)
            
            print(f"[{class_name}] Image loaded for analysis")
            
            # Load visualization image for marking
            viz_image_path = context.get('visualization_image_path')
            if viz_image_path and os.path.exists(viz_image_path):
                viz_image = cv2.imread(viz_image_path)
                print(f"[{class_name}] Loaded visualization image: {os.path.basename(viz_image_path)}")
            else:
                print(f"[{class_name}] ⚠️ Visualization image not found, using original")
                viz_image = image.copy()
            
            # Create final_answer array (100 questions)
            final_answer = []
            marked_circles = []  # For highlighting
            
            # Process each column
            for col_idx in range(1, 5):
                print(f"[{class_name}] Processing Column {col_idx}...")
                
                grid_key = f"col{col_idx}_grid"
                r_mean_key = f"r_mean_col_{col_idx}"
                
                grid_data = context.get(grid_key)
                r_mean = context.get(r_mean_key, 16)
                
                grid_circles = grid_data.get('grid_circles', [])
                
                # Each column has 100 circles: 25 questions × 4 options
                for question_idx in range(25):
                    # Get 4 circles for this question (a, b, c, d)
                    start_idx = question_idx * 4
                    end_idx = start_idx + 4
                    question_circles = grid_circles[start_idx:end_idx]
                    
                    if len(question_circles) != 4:
                        print(f"[{class_name}] ⚠️ Question {question_idx+1} has {len(question_circles)} circles, expected 4")
                        final_answer.append(-1)
                        continue
                    
                    # Detect which circle is marked (if any)
                    marked_option = self._detect_marked_circle(
                        image, question_circles, r_mean
                    )
                    
                    final_answer.append(marked_option)
                    
                    # Store marked circle for highlighting
                    if marked_option >= 0 and marked_option < 4:
                        marked_circle = question_circles[marked_option]
                        marked_circles.append((marked_circle, r_mean))
                
                print(f"[{class_name}] Column {col_idx}: Processed 25 questions")
            
            # Highlight marked circles on visualization image
            print(f"[{class_name}] ========================================")
            print(f"[{class_name}] Highlighting {len(marked_circles)} marked circles in GREEN")
            
            for (x, y), r_mean in marked_circles:
                r_mean_int = int(round(r_mean))
                # Draw green circle with 2 pixel width
                cv2.circle(viz_image, (x, y), r_mean_int, (0, 255, 0), 2)
            
            # Save updated visualization image
            print(f"[{class_name}] Saving updated visualization with marked circles...")
            cv2.imwrite(viz_image_path, viz_image)
            print(f"[{class_name}] Visualization image updated")
            
            # Calculate statistics
            marked_count = sum(1 for ans in final_answer if ans >= 0)
            skipped_count = sum(1 for ans in final_answer if ans == -1)
            
            print(f"[{class_name}] ========================================")
            print(f"[{class_name}] Final Answer Summary:")
            print(f"[{class_name}]   Total questions: {len(final_answer)}")
            print(f"[{class_name}]   Marked: {marked_count}")
            print(f"[{class_name}]   Skipped: {skipped_count}")
            print(f"[{class_name}]   First 10 answers: {final_answer[:10]}")
            
            # Create result
            result = self.create_stage_result(
                success=True,
                roll_number=roll_number,
                total_questions=len(final_answer),
                marked_count=marked_count,
                skipped_count=skipped_count,
                final_answer=final_answer,
                marked_circles_highlighted=len(marked_circles)
            )
            
            print(f"[{class_name}] ✅ SUCCESS: Answer validation complete")
            return result
            
        except Exception as e:
            error_msg = f"Answer validation failed: {str(e)}"
            print(f"[{class_name}] ❌ EXCEPTION: {error_msg}")
            import traceback
            print(f"[{class_name}] Traceback: {traceback.format_exc()}")
            return self.create_stage_result(
                success=False,
                error=error_msg
            )
        finally:
            print(f"[{class_name}] ====== Answer Validation Stage Complete ======\n")
    
    def _detect_marked_circle(self, image: np.ndarray, circles: List, r_mean: float) -> int:
        """
        Detect which circle in a row is marked (if any).
        
        Args:
            image: Source image
            circles: List of 4 (x, y) tuples for options a, b, c, d
            r_mean: Mean radius
            
        Returns:
            Index of marked circle (0-3) or -1 if none/multiple marked
        """
        class_name = self.__class__.__name__
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        fill_ratios = []
        
        for x, y in circles:
            # Create circular mask
            mask = np.zeros(gray.shape, dtype=np.uint8)
            inner_radius = int(r_mean * 0.85)
            cv2.circle(mask, (x, y), inner_radius, 255, -1)
            
            # Get pixels inside the circle
            circle_pixels = gray[mask == 255]
            
            if len(circle_pixels) == 0:
                fill_ratios.append(0.0)
                continue
            
            # Calculate fill ratio (percentage of dark pixels)
            threshold = 180
            dark_pixels = np.sum(circle_pixels < threshold)
            fill_ratio = dark_pixels / len(circle_pixels)
            fill_ratios.append(fill_ratio)
        
        # Determine which circle is marked
        # A circle is "marked" if fill_ratio > 0.35
        marked_threshold = 0.35
        marked_indices = [i for i, ratio in enumerate(fill_ratios) if ratio > marked_threshold]
        
        if len(marked_indices) == 0:
            # No circle marked (skipped question)
            return -1
        elif len(marked_indices) == 1:
            # Exactly one circle marked (correct)
            return marked_indices[0]
        else:
            # Multiple circles marked (ambiguous)
            # Return the one with highest fill ratio
            max_idx = marked_indices[0]
            max_ratio = fill_ratios[max_idx]
            for idx in marked_indices[1:]:
                if fill_ratios[idx] > max_ratio:
                    max_ratio = fill_ratios[idx]
                    max_idx = idx
            return max_idx

