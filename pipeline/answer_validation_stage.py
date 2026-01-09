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
            
            # Step 4: Validate answers with uploaded answer key if available
            answer_validation_result = None
            uploaded_answer_key = context.get('uploaded_answer_key')
            if uploaded_answer_key:
                print(f"[{class_name}] ========================================")
                print(f"[{class_name}] Step 4: Validate Answers with Answer Key")
                answer_validation_result = self._validate_answers_with_answer_key(
                    final_answer, uploaded_answer_key, roll_number, context
                )
                if answer_validation_result:
                    print(f"[{class_name}] ✅ Answer validation completed")
                    print(f"[{class_name}] Validation result: {answer_validation_result}")
                else:
                    print(f"[{class_name}] ⚠️  Answer validation completed but no result generated")
            else:
                print(f"[{class_name}] ℹ️  No uploaded answer key found. Skipping answer validation.")
            
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
            
            # Add answer validation result to context if available
            if answer_validation_result:
                result['answer_validation_result'] = answer_validation_result
            
            # Step 5: Mark correct/wrong answers with ticks and crosses on visualization images
            # (Can be commented out if marking is not needed)
            if uploaded_answer_key and answer_validation_result:
                self._mark_answer_correctness_on_images(
                    final_answer, uploaded_answer_key, context, image
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
    
    def _validate_answers_with_answer_key(self, final_answer: List[int], uploaded_answer_key: List[Dict], 
                                          roll_number: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate marked answers against uploaded answer key and calculate marks by category.
        
        Args:
            final_answer: List of marked answers (indices 0-3 or -1 for skipped)
            uploaded_answer_key: List of answer key entries with correctchoice, questioncategory, marks, wrongquestion
            roll_number: Roll number of the student
            context: Pipeline context to get tenant
            
        Returns:
            Dictionary with {roll_number, tenant, questionCategory1: marks, questionCategory2: marks, ...}
            or None if validation fails
        """
        class_name = self.__class__.__name__
        
        print(f"[{class_name}] _validate_answers_with_answer_key() called")
        print(f"[{class_name}] Final answer count: {len(final_answer)}")
        print(f"[{class_name}] Answer key count: {len(uploaded_answer_key)}")
        
        # Get tenant from context
        tenant = context.get('tenant', '')
        
        # Initialize marks by category
        marks_by_category = {}
        
        # Track statistics
        correct_answers = 0
        incorrect_answers = 0
        skipped_answers = 0
        wrong_questions_count = 0
        
        # Process each question
        for question_idx in range(len(final_answer)):
            marked_answer = final_answer[question_idx]
            
            # Skip if question not marked (marked_answer == -1)
            if marked_answer == -1:
                skipped_answers += 1
                continue
            
            # Check if we have answer key for this question
            if question_idx >= len(uploaded_answer_key):
                print(f"[{class_name}] ⚠️  WARNING: No answer key entry for question {question_idx + 1}")
                continue
            
            answer_key_entry = uploaded_answer_key[question_idx]
            correctchoice = answer_key_entry.get('correctchoice', -1)
            questioncategory = answer_key_entry.get('questioncategory', '').strip()
            marks = answer_key_entry.get('marks', 0)
            wrongquestion = answer_key_entry.get('wrongquestion', False)
            
            # Convert wrongquestion to boolean if it's an integer
            if isinstance(wrongquestion, int):
                wrongquestion = bool(wrongquestion)
            
            # Initialize category if not exists
            if questioncategory:
                if questioncategory not in marks_by_category:
                    marks_by_category[questioncategory] = 0
            
            # Handle WrongQuestion == 1: If attempted, award full marks regardless of correctness
            if wrongquestion:
                if marked_answer != -1:
                    # Question was attempted - award full marks
                    wrong_questions_count += 1
                    if questioncategory:
                        marks_by_category[questioncategory] += marks
                        print(f"[{class_name}] ✅ Question {question_idx + 1}: Wrong question but attempted! "
                              f"Category: {questioncategory}, Full Marks: +{marks}")
                    else:
                        print(f"[{class_name}] ✅ Question {question_idx + 1}: Wrong question but attempted! "
                              f"(No category), Full Marks: +{marks}")
                    correct_answers += 1  # Count as correct for statistics
                else:
                    # Question was not attempted - skip
                    wrong_questions_count += 1
                    print(f"[{class_name}] ⚠️  Question {question_idx + 1} is marked as wrong question and not attempted. Skipping.")
                continue
            
            # Normal validation: Check if marked answer matches correct choice
            if marked_answer == correctchoice:
                # Correct answer - add marks to category
                correct_answers += 1
                if questioncategory:
                    marks_by_category[questioncategory] += marks
                    print(f"[{class_name}] ✅ Question {question_idx + 1}: Correct! "
                          f"Category: {questioncategory}, Marks: +{marks}")
                else:
                    print(f"[{class_name}] ✅ Question {question_idx + 1}: Correct! "
                          f"(No category), Marks: +{marks}")
            else:
                # Incorrect answer
                incorrect_answers += 1
                print(f"[{class_name}] ❌ Question {question_idx + 1}: Incorrect. "
                      f"Marked: {marked_answer}, Correct: {correctchoice}")
        
        # Prepare result JSON structure
        validation_result = {
            'roll_number': roll_number,
            'tenant': tenant
        }
        
        # Add marks for each category
        for category, total_marks in marks_by_category.items():
            validation_result[category] = total_marks
        
        # Log summary
        print(f"[{class_name}] ========================================")
        print(f"[{class_name}] Answer Validation Summary:")
        print(f"[{class_name}]   Correct answers: {correct_answers}")
        print(f"[{class_name}]   Incorrect answers: {incorrect_answers}")
        print(f"[{class_name}]   Skipped answers: {skipped_answers}")
        print(f"[{class_name}]   Wrong questions skipped: {wrong_questions_count}")
        print(f"[{class_name}]   Marks by category:")
        total_marks_obtained = 0
        for category, marks in marks_by_category.items():
            print(f"[{class_name}]     {category}: {marks} marks")
            total_marks_obtained += marks
        print(f"[{class_name}]   Total marks obtained: {total_marks_obtained}")
        print(f"[{class_name}] ========================================")
        
        # Add total marks to result
        validation_result['total_marks_obtained'] = total_marks_obtained
        validation_result['correct_answers'] = correct_answers
        validation_result['incorrect_answers'] = incorrect_answers
        validation_result['skipped_answers'] = skipped_answers
        
        # Store in context
        context['answer_validation_result'] = validation_result
        print(f"[{class_name}] ✅ Answer validation result added to context")
        
        return validation_result
    
    def _mark_answer_correctness_on_images(self, final_answer: List[int], uploaded_answer_key: List[Dict],
                                          context: Dict[str, Any], original_image: np.ndarray) -> None:
        """
        Mark correct answers with green ticks and wrong answers with red crosses on images.
        This method can be commented out if visual marking is not needed.
        
        Args:
            final_answer: List of marked answers (indices 0-3 or -1 for skipped)
            uploaded_answer_key: List of answer key entries
            context: Pipeline context containing grid data and image paths
            original_image: Original image (for fallback if needed)
        """
        class_name = self.__class__.__name__
        
        print(f"[{class_name}] ========================================")
        print(f"[{class_name}] Marking Answer Correctness on Images")
        print(f"[{class_name}] ========================================")
        
        # Load visualization image
        viz_image_path = context.get('visualization_image_path')
        if not viz_image_path or not os.path.exists(viz_image_path):
            print(f"[{class_name}] ⚠️  Visualization image not found. Skipping marking.")
            return
        
        viz_image = cv2.imread(viz_image_path)
        if viz_image is None:
            print(f"[{class_name}] ⚠️  Could not load visualization image. Skipping marking.")
            return
        
        print(f"[{class_name}] Loaded visualization image: {os.path.basename(viz_image_path)}")
        
        # Reconstruct question-to-circle mapping from grid data
        question_circle_map = {}  # question_index -> (x, y, r_mean)
        
        question_idx = 0
        for col_idx in range(1, 5):
            grid_key = f"col{col_idx}_grid"
            r_mean_key = f"r_mean_col_{col_idx}"
            
            grid_data = context.get(grid_key)
            if not grid_data:
                continue
            
            r_mean = context.get(r_mean_key, 16)
            grid_circles = grid_data.get('grid_circles', [])
            
            # Each column has 25 questions, each with 4 circles
            for q_in_col in range(25):
                if question_idx >= len(final_answer):
                    break
                
                # Get the marked answer for this question
                marked_answer = final_answer[question_idx]
                
                # If question was marked, find the circle position
                if marked_answer >= 0 and marked_answer < 4:
                    start_idx = q_in_col * 4
                    if start_idx + marked_answer < len(grid_circles):
                        marked_circle = grid_circles[start_idx + marked_answer]
                        question_circle_map[question_idx] = (marked_circle[0], marked_circle[1], r_mean)
                
                question_idx += 1
        
        print(f"[{class_name}] Mapped {len(question_circle_map)} marked questions to circle positions")
        
        # Mark correct and wrong answers
        correct_count = 0
        wrong_count = 0
        
        for question_idx in range(len(final_answer)):
            marked_answer = final_answer[question_idx]
            
            # Skip if question not marked or no circle position found
            if marked_answer == -1 or question_idx not in question_circle_map:
                continue
            
            # Check if we have answer key for this question
            if question_idx >= len(uploaded_answer_key):
                continue
            
            answer_key_entry = uploaded_answer_key[question_idx]
            correctchoice = answer_key_entry.get('correctchoice', -1)
            wrongquestion = answer_key_entry.get('wrongquestion', False)
            
            # Convert wrongquestion to boolean if needed
            if isinstance(wrongquestion, int):
                wrongquestion = bool(wrongquestion)
            
            x, y, r_mean = question_circle_map[question_idx]
            r_mean_int = int(round(r_mean))
            
            # Determine if answer is correct
            is_correct = False
            if wrongquestion:
                # Wrong question: any attempt is considered correct
                is_correct = True
            elif marked_answer == correctchoice:
                # Normal question: matches correct choice
                is_correct = True
            
            # Draw tick or cross
            if is_correct:
                # Draw green tick (checkmark)
                self._draw_tick(viz_image, x, y, r_mean_int, color=(0, 255, 0))
                correct_count += 1
            else:
                # Draw red cross
                self._draw_cross(viz_image, x, y, r_mean_int, color=(0, 0, 255))
                wrong_count += 1
        
        # Save marked visualization image
        print(f"[{class_name}] Saving visualization image with correctness marks...")
        cv2.imwrite(viz_image_path, viz_image)
        print(f"[{class_name}] ✅ Visualization image saved with {correct_count} ticks and {wrong_count} crosses")
        
        # Also mark the success image if it exists (it will be created later, but we can update the path)
        # The success image is created from visualization image, so marks will already be there
        # But let's also check if there's a success image path we should update
        print(f"[{class_name}] Note: Success image will be created from marked visualization image")
        print(f"[{class_name}] ========================================")
    
    def _draw_tick(self, image: np.ndarray, center_x: int, center_y: int, radius: int, color: tuple = (0, 255, 0), thickness: int = 3) -> None:
        """
        Draw a green tick (checkmark) at the specified position.
        
        Args:
            image: Image to draw on
            center_x: X coordinate of circle center
            center_y: Y coordinate of circle center
            radius: Radius of the circle (used to scale tick size)
            color: Color in BGR format (default: green)
            thickness: Line thickness
        """
        # Scale tick size based on circle radius
        tick_size = max(8, int(radius * 0.6))
        
        # Draw checkmark: two lines forming a tick
        # Start point (bottom-left of tick)
        start_x = center_x - tick_size // 2
        start_y = center_y + tick_size // 4
        
        # Middle point (middle-left)
        mid_x = center_x - tick_size // 6
        mid_y = center_y
        
        # End point (top-right of tick)
        end_x = center_x + tick_size // 2
        end_y = center_y - tick_size // 2
        
        # Draw the tick: two lines
        cv2.line(image, (start_x, start_y), (mid_x, mid_y), color, thickness)
        cv2.line(image, (mid_x, mid_y), (end_x, end_y), color, thickness)
    
    def _draw_cross(self, image: np.ndarray, center_x: int, center_y: int, radius: int, color: tuple = (0, 0, 255), thickness: int = 3) -> None:
        """
        Draw a red cross (X) at the specified position.
        
        Args:
            image: Image to draw on
            center_x: X coordinate of circle center
            center_y: Y coordinate of circle center
            radius: Radius of the circle (used to scale cross size)
            color: Color in BGR format (default: red)
            thickness: Line thickness
        """
        # Scale cross size based on circle radius
        cross_size = max(8, int(radius * 0.6))
        offset = cross_size // 2
        
        # Draw X: two diagonal lines
        # Top-left to bottom-right
        cv2.line(image, 
                (center_x - offset, center_y - offset), 
                (center_x + offset, center_y + offset), 
                color, thickness)
        # Top-right to bottom-left
        cv2.line(image, 
                (center_x + offset, center_y - offset), 
                (center_x - offset, center_y + offset), 
                color, thickness)

