#!/usr/bin/env python3
"""
Roll Number Extraction Stage Implementation

This stage extracts exam roll number from image using OCR.
"""

import os
import cv2
import re
from typing import Optional
from .base_stage import PipelineStage
from typing import Dict, Any


class RollNumberExtractionStage(PipelineStage):
    """Stage 3: Extract exam roll number from image using OCR"""
    
    def get_stage_name(self) -> str:
        return "roll_number_extraction"
    
    def get_stage_description(self) -> str:
        return "Extract exam roll number from image"
    
    def process(self, image_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        class_name = self.__class__.__name__
        filename = os.path.basename(image_path)
        
        print(f"[{class_name}] ====== Starting Roll Number Extraction Stage ======")
        print(f"[{class_name}] Processing image: {filename}")
        print(f"[{class_name}] Full image path: {image_path}")
        
        try:
            # Check if pytesseract is available
            print(f"[{class_name}] Checking pytesseract availability")
            pytesseract_available = hasattr(self.processor, 'PYTESSERACT_AVAILABLE') and self.processor.PYTESSERACT_AVAILABLE
            print(f"[{class_name}] Pytesseract available: {pytesseract_available}")
            
            if not pytesseract_available:
                print(f"[{class_name}] ❌ ERROR: pytesseract not available")
                print(f"[{class_name}] Returning failure result")
                return self.create_stage_result(
                    success=False,
                    error="OCR Error: pytesseract not available or has dependency issues",
                    roll_number=None
                )
            
            # Use the rotated image path from previous stage if available
            image_to_process = context.get('rotated_image_path', image_path)
            print(f"[{class_name}] Image to process: {os.path.basename(image_to_process)}")
            print(f"[{class_name}] Using {'rotated' if image_to_process != image_path else 'original'} image")
            
            # Read image
            print(f"[{class_name}] Reading image from disk")
            image = cv2.imread(image_to_process)
            
            if image is None:
                print(f"[{class_name}] ❌ ERROR: Could not read image from path")
                print(f"[{class_name}] Returning failure result")
                return self.create_stage_result(
                    success=False,
                    error="Could not read image for OCR",
                    roll_number=None
                )
            
            print(f"[{class_name}] Image loaded successfully - Shape: {image.shape}")
            
            # Get detection info from context (from ArUco stage)
            detection_info = context.get('detection_info', {})
            detected_markers = context.get('detected_markers', [])
            print(f"[{class_name}] Detected markers from context: {detected_markers}")
            
            # Create or get the visualization grayscale image
            print(f"[{class_name}] Creating visualization grayscale image")
            viz_image_path = context.get('visualization_image_path')
            
            if viz_image_path and os.path.exists(viz_image_path):
                print(f"[{class_name}] Loading existing visualization image: {os.path.basename(viz_image_path)}")
                viz_image = cv2.imread(viz_image_path)
            else:
                print(f"[{class_name}] Creating new grayscale visualization image")
                viz_image = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
                viz_image = cv2.cvtColor(viz_image, cv2.COLOR_GRAY2BGR)  # Convert back to 3-channel for color drawing
                
                # Create visualization subfolder
                image_dir = os.path.dirname(image_to_process)
                viz_folder = os.path.join(image_dir, "visualization")
                os.makedirs(viz_folder, exist_ok=True)
                
                # Save visualization image in visualization subfolder
                base_name = os.path.basename(os.path.splitext(image_to_process)[0])
                viz_image_path = os.path.join(viz_folder, f"{base_name}_visualization.png")
                print(f"[{class_name}] Visualization image path: {viz_image_path}")
            
            # Try to extract roll number using ArUco marker-based regions
            print(f"[{class_name}] Attempting ArUco marker-based roll number extraction")
            roll_number, extracted_text, roll_rect = self._extract_roll_number_with_markers(
                image, detection_info, detected_markers
            )
            
            if roll_number:
                print(f"[{class_name}] ✅ SUCCESS: Roll number extracted: {roll_number}")
                print(f"[{class_name}] Extracted string: '{extracted_text}'")
                
                # Validate and enforce expected prefix if provided
                roll_number = self._validate_and_enforce_prefix(roll_number, context, class_name)
                
                # Mark roll number rectangle on visualization image
                if roll_rect:
                    print(f"[{class_name}] Marking roll number rectangle on visualization image")
                    x_min, y_min, x_max, y_max = roll_rect
                    cv2.rectangle(viz_image, (x_min, y_min), (x_max, y_max), (255, 0, 0), 3)  # Blue rectangle
                    cv2.putText(viz_image, "Roll Number", (x_min, y_min - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    print(f"[{class_name}] Roll number rectangle marked at: ({x_min}, {y_min}) to ({x_max}, {y_max})")
                
                # Save visualization image
                print(f"[{class_name}] Saving visualization image to: {viz_image_path}")
                cv2.imwrite(viz_image_path, viz_image)
                print(f"[{class_name}] Visualization image saved")
                
                print(f"[{class_name}] Returning success result")
                return self.create_stage_result(
                    success=True,
                    roll_number=roll_number,
                    extracted_text=extracted_text,
                    roll_number_rect=roll_rect,
                    visualization_image_path=viz_image_path
                )
            else:
                print(f"[{class_name}] ❌ FAILURE: No valid roll number found")
                print(f"[{class_name}] Returning failure result")
                return self.create_stage_result(
                    success=False,
                    error="No valid roll number found using ArUco marker regions",
                    roll_number=None,
                    extracted_text=extracted_text if extracted_text else ""
                )
                
        except Exception as e:
            error_msg = f"OCR processing failed: {str(e)}"
            print(f"[{class_name}] ❌ EXCEPTION: {error_msg}")
            print(f"[{class_name}] Exception type: {type(e).__name__}")
            print(f"[{class_name}] Returning failure result")
            return self.create_stage_result(
                success=False,
                error=error_msg,
                roll_number=None
            )
        finally:
            print(f"[{class_name}] ====== Roll Number Extraction Stage Complete ======\n")
    
    def _extract_roll_number_with_markers(self, image, detection_info: Dict, detected_markers: list) -> tuple:
        """
        Extract roll number using ArUco markers to define the OCR region.
        
        Args:
            image: OpenCV image
            detection_info: Detection information from ArUco stage
            detected_markers: List of detected marker IDs
            
        Returns:
            Tuple of (roll_number, extracted_text, rectangle_coordinates)
            rectangle_coordinates: (x_min, y_min, x_max, y_max) or None
        """
        class_name = self.__class__.__name__
        import pytesseract
        
        print(f"[{class_name}] _extract_roll_number_with_markers() called")
        
        # Get marker midpoints from detection info
        marker_midpoints = detection_info.get('marker_midpoints', [])
        detected_ids = detection_info.get('detected_ids', [])
        
        print(f"[{class_name}] Available markers: {detected_ids}")
        print(f"[{class_name}] Total marker midpoints: {len(marker_midpoints)}")
        
        # Try primary markers: 17 and 18
        print(f"[{class_name}] Attempting extraction with markers 17 and 18...")
        roll_number, text, rect = self._try_marker_pair(image, detected_ids, marker_midpoints, 17, 18, pytesseract)
        
        if roll_number:
            print(f"[{class_name}] ✅ SUCCESS with markers 17 and 18")
            return roll_number, text, rect
        
        # Fallback: Try markers 19 and 20
        print(f"[{class_name}] Primary markers failed, trying fallback markers 19 and 20...")
        roll_number, text, rect = self._try_marker_pair(image, detected_ids, marker_midpoints, 19, 20, pytesseract)
        
        if roll_number:
            print(f"[{class_name}] ✅ SUCCESS with markers 19 and 20")
            return roll_number, text, rect
        
        print(f"[{class_name}] ❌ Both marker pairs failed")
        return None, text if text else "", None
    
    def _try_marker_pair(self, image, detected_ids: list, marker_midpoints: list, 
                         marker_id_1: int, marker_id_2: int, pytesseract) -> tuple:
        """
        Try to extract roll number using a specific pair of ArUco markers.
        
        Args:
            image: OpenCV image
            detected_ids: List of detected marker IDs
            marker_midpoints: List of marker midpoint coordinates
            marker_id_1: First marker ID (top-left)
            marker_id_2: Second marker ID (bottom-right)
            pytesseract: Pytesseract module
            
        Returns:
            Tuple of (roll_number, extracted_text, rectangle_coordinates)
            rectangle_coordinates: (x_min, y_min, x_max, y_max) or None
        """
        class_name = self.__class__.__name__
        
        print(f"[{class_name}] _try_marker_pair() called for markers {marker_id_1} and {marker_id_2}")
        
        # Check if both markers are detected
        if marker_id_1 not in detected_ids or marker_id_2 not in detected_ids:
            print(f"[{class_name}] ❌ Required markers not found")
            print(f"[{class_name}]   Marker {marker_id_1} present: {marker_id_1 in detected_ids}")
            print(f"[{class_name}]   Marker {marker_id_2} present: {marker_id_2 in detected_ids}")
            return None, "", None
        
        # Get indices of the markers
        idx_1 = detected_ids.index(marker_id_1)
        idx_2 = detected_ids.index(marker_id_2)
        
        print(f"[{class_name}] Marker {marker_id_1} index: {idx_1}")
        print(f"[{class_name}] Marker {marker_id_2} index: {idx_2}")
        
        # Get midpoint coordinates
        midpoint_1 = marker_midpoints[idx_1]
        midpoint_2 = marker_midpoints[idx_2]
        
        print(f"[{class_name}] Marker {marker_id_1} location: {midpoint_1}")
        print(f"[{class_name}] Marker {marker_id_2} location: {midpoint_2}")
        
        # Define bounding box using markers as top-left and bottom-right
        x1, y1 = int(midpoint_1[0]), int(midpoint_1[1])
        x2, y2 = int(midpoint_2[0]), int(midpoint_2[1])
        
        # Ensure correct ordering (top-left to bottom-right)
        x_min = min(x1, x2)
        y_min = min(y1, y2)
        x_max = max(x1, x2)
        y_max = max(y1, y2)
        
        print(f"[{class_name}] Bounding box: ({x_min}, {y_min}) to ({x_max}, {y_max})")
        print(f"[{class_name}] Box dimensions: {x_max - x_min}x{y_max - y_min} pixels")
        
        # Validate bounding box
        if x_max <= x_min or y_max <= y_min:
            print(f"[{class_name}] ❌ Invalid bounding box dimensions")
            return None, "", None
        
        # Store rectangle coordinates
        rect_coords = (x_min, y_min, x_max, y_max)
        
        # Crop the region
        print(f"[{class_name}] Cropping image region...")
        cropped_region = image[y_min:y_max, x_min:x_max]
        
        if cropped_region.size == 0:
            print(f"[{class_name}] ❌ Cropped region is empty")
            return None, "", None
        
        print(f"[{class_name}] Cropped region shape: {cropped_region.shape}")
        
        # Convert to grayscale
        print(f"[{class_name}] Converting cropped region to grayscale")
        gray = cv2.cvtColor(cropped_region, cv2.COLOR_BGR2GRAY)
        
        # Apply preprocessing
        print(f"[{class_name}] Applying Otsu's thresholding to cropped region")
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Perform OCR on the cropped region
        print(f"[{class_name}] Performing OCR on cropped region...")
        text = pytesseract.image_to_string(thresh, config='--psm 6')  # Assume uniform text block
        print(f"[{class_name}] OCR complete")
        print(f"[{class_name}] Extracted text length: {len(text)} characters")
        print(f"[{class_name}] Extracted text: '{text.strip()}'")
        
        # Parse roll number from extracted text
        print(f"[{class_name}] Parsing roll number from extracted text")
        roll_number = self._parse_roll_number(text)
        
        if roll_number:
            print(f"[{class_name}] ✅ Roll number found: {roll_number}")
        else:
            print(f"[{class_name}] ❌ No valid roll number found in text")
        
        return roll_number, text.strip(), rect_coords
    
    def _parse_roll_number(self, text: str) -> Optional[str]:
        """
        Parse roll number from OCR text using regex patterns.
        Handles alphanumeric roll numbers and cleans up extra characters.
        
        Args:
            text: Text extracted from image
            
        Returns:
            Extracted roll number or None if not found
        """
        class_name = self.__class__.__name__
        print(f"[{class_name}] _parse_roll_number() called")
        print(f"[{class_name}] Raw text: '{text}'")
        print(f"[{class_name}] Text length: {len(text)} characters")
        
        # Clean up the text first - remove common OCR artifacts
        print(f"[{class_name}] Cleaning text...")
        cleaned_text = text.strip()
        
        # Step 1: Normalize hyphens by removing spaces before and after them
        # This handles cases like "NAYA2508 - 0075" -> "NAYA2508-0075"
        print(f"[{class_name}] Normalizing hyphens (removing spaces around '-')...")
        cleaned_text = re.sub(r'\s*-\s*', '-', cleaned_text)  # " - " or " -" or "- " -> "-"
        print(f"[{class_name}] After hyphen normalization: '{cleaned_text}'")
        
        # Remove leading/trailing special characters but keep alphanumeric
        cleaned_text = re.sub(r'^[^A-Za-z0-9]+', '', cleaned_text)  # Remove leading non-alphanumeric
        cleaned_text = re.sub(r'[^A-Za-z0-9]+$', '', cleaned_text)  # Remove trailing non-alphanumeric
        
        print(f"[{class_name}] Cleaned text: '{cleaned_text}'")
        
        # Patterns for roll numbers (ordered by specificity)
        # Note: Patterns allow dashes, underscores, and slashes within roll numbers
        patterns = [
            # Priority pattern: Letters + digits + dash + exactly 4 digits (e.g., NAYA2508-0075)
            r'\b([A-Z]{2,6}[A-Z0-9]*-\d{4})\b',  # Letters + optional alphanumeric + dash + exactly 4 digits
            
            # Pattern: Letters + dash + exactly 4 digits (e.g., NAYA-0075)
            r'\b([A-Z]{2,6}-\d{4})\b',  # Letters + dash + exactly 4 digits
            
            # Alphanumeric patterns with separators (e.g., SURI-123123123, JAMB24090019)
            r'\b([A-Z]{2,6}[-_/]?\d{6,12})\b',  # Letters + optional separator + numbers
            r'\b([A-Z]{2,6}[-_/]?[A-Z0-9]{6,12})\b',  # Letters + optional separator + mixed
            r'\b([A-Z]{2,6}[A-Z0-9\-_/]{6,15})\b',  # Mixed with separators allowed throughout
            
            # Pure alphanumeric (no separators - backward compatibility)
            r'\b([A-Z]{2,6}\d{6,12})\b',  # Letters followed by numbers (JAMB24090019)
            r'\b([A-Z]{2,6}[A-Z0-9]{6,12})\b',  # Mixed alphanumeric
            
            # Patterns with labels
            r'Roll\s*No[:\s]*([A-Z0-9\-_/]{6,15})',
            r'Roll\s*Number[:\s]*([A-Z0-9\-_/]{6,15})',
            r'Student\s*ID[:\s]*([A-Z0-9\-_/]{6,15})',
            r'ID[:\s]*([A-Z0-9\-_/]{6,15})',
            r'Exam\s*No[:\s]*([A-Z0-9\-_/]{6,15})',
            
            # Pure numeric patterns (last resort)
            r'\b(\d{8,12})\b',  # 8-12 digit number
            r'\b(\d{6,10})\b',  # 6-10 digit number
        ]
        
        print(f"[{class_name}] Trying {len(patterns)} regex patterns")
        print(f"[{class_name}] Text to search: '{cleaned_text}'")
        
        # Check if text contains a dash - if so, we should prioritize dash patterns
        has_dash_in_text = '-' in cleaned_text
        print(f"[{class_name}] Text contains dash: {has_dash_in_text}")
        if has_dash_in_text:
            print(f"[{class_name}] → Will require dash + exactly 4 digits format")
        
        # Try patterns on cleaned text first
        for i, pattern in enumerate(patterns, 1):
            print(f"[{class_name}] ========================================")
            print(f"[{class_name}] Pattern {i}/{len(patterns)}: {pattern}")
            match = re.search(pattern, cleaned_text, re.IGNORECASE)
            if match:
                roll_number = match.group(1).upper()  # Convert to uppercase for consistency
                print(f"[{class_name}]   → Match found: '{match.group(1)}'")
                print(f"[{class_name}]   → After upper(): '{roll_number}'")
                print(f"[{class_name}]   → Length: {len(roll_number)} characters")
                
                # Additional validation - ensure it's not too short
                if len(roll_number) >= 6:
                    # If text contains a dash, roll number MUST have dash + exactly 4 digits
                    if has_dash_in_text:
                        if '-' not in roll_number:
                            print(f"[{class_name}]   ⚠️ REJECTED: Text contains dash, but roll number doesn't")
                            print(f"[{class_name}]   → Trying next pattern...")
                            continue
                    
                    # If roll number contains a dash, validate that exactly 4 digits follow it
                    if '-' in roll_number:
                        parts = roll_number.split('-', 1)  # Split only on first dash
                        if len(parts) == 2:
                            before_dash = parts[0]
                            after_dash = parts[1]
                            print(f"[{class_name}]   → Contains dash: '{before_dash}' - '{after_dash}'")
                            if not (after_dash.isdigit() and len(after_dash) == 4):
                                print(f"[{class_name}]   ⚠️ REJECTED: Dash must be followed by exactly 4 digits")
                                print(f"[{class_name}]   → Found: '{after_dash}' (length: {len(after_dash)}, isdigit: {after_dash.isdigit()})")
                                print(f"[{class_name}]   → Trying next pattern...")
                                continue  # Skip this match, try next pattern
                            else:
                                print(f"[{class_name}]   ✅ VALID: Dash followed by exactly 4 digits")
                    else:
                        if has_dash_in_text:
                            print(f"[{class_name}]   ⚠️ REJECTED: Text has dash but roll number doesn't")
                            print(f"[{class_name}]   → Trying next pattern...")
                            continue
                        else:
                            print(f"[{class_name}]   → No dash in roll number (acceptable for non-dash patterns)")
                    
                    print(f"[{class_name}] ========================================")
                    print(f"[{class_name}] ✅ SUCCESS! Final roll number: {roll_number}")
                    print(f"[{class_name}] Matched pattern: {pattern}")
                    return roll_number
                else:
                    print(f"[{class_name}]   ⚠️ REJECTED: Match too short ({len(roll_number)} chars, minimum 6)")
                    print(f"[{class_name}]   → Trying next pattern...")
            else:
                print(f"[{class_name}]   → No match")
        
        print(f"[{class_name}] ========================================")
        
        # If no match on cleaned text, try on original text as fallback (with hyphen normalization)
        print(f"[{class_name}] ========================================")
        print(f"[{class_name}] No match on cleaned text, trying original text as fallback...")
        # Normalize hyphens in original text too
        normalized_original = re.sub(r'\s*-\s*', '-', text.strip())
        print(f"[{class_name}] Normalized original text: '{normalized_original}'")
        
        # Check if normalized original text contains a dash
        has_dash_in_original = '-' in normalized_original
        print(f"[{class_name}] Normalized text contains dash: {has_dash_in_original}")
        if has_dash_in_original:
            print(f"[{class_name}] → Will require dash + exactly 4 digits format")
        
        for i, pattern in enumerate(patterns, 1):
            print(f"[{class_name}] ========================================")
            print(f"[{class_name}] Pattern {i}/{len(patterns)}: {pattern}")
            match = re.search(pattern, normalized_original, re.IGNORECASE)
            if match:
                roll_number = match.group(1).upper()
                print(f"[{class_name}]   → Match found: '{match.group(1)}'")
                print(f"[{class_name}]   → After upper(): '{roll_number}'")
                print(f"[{class_name}]   → Length: {len(roll_number)} characters")
                
                if len(roll_number) >= 6:
                    # If text contains a dash, roll number MUST have dash + exactly 4 digits
                    if has_dash_in_original:
                        if '-' not in roll_number:
                            print(f"[{class_name}]   ⚠️ REJECTED: Text contains dash, but roll number doesn't")
                            print(f"[{class_name}]   → Trying next pattern...")
                            continue
                    
                    # If roll number contains a dash, validate that exactly 4 digits follow it
                    if '-' in roll_number:
                        parts = roll_number.split('-', 1)  # Split only on first dash
                        if len(parts) == 2:
                            before_dash = parts[0]
                            after_dash = parts[1]
                            print(f"[{class_name}]   → Contains dash: '{before_dash}' - '{after_dash}'")
                            if not (after_dash.isdigit() and len(after_dash) == 4):
                                print(f"[{class_name}]   ⚠️ REJECTED: Dash must be followed by exactly 4 digits")
                                print(f"[{class_name}]   → Found: '{after_dash}' (length: {len(after_dash)}, isdigit: {after_dash.isdigit()})")
                                print(f"[{class_name}]   → Trying next pattern...")
                                continue  # Skip this match, try next pattern
                            else:
                                print(f"[{class_name}]   ✅ VALID: Dash followed by exactly 4 digits")
                    else:
                        if has_dash_in_original:
                            print(f"[{class_name}]   ⚠️ REJECTED: Text has dash but roll number doesn't")
                            print(f"[{class_name}]   → Trying next pattern...")
                            continue
                        else:
                            print(f"[{class_name}]   → No dash in roll number (acceptable for non-dash patterns)")
                    
                    print(f"[{class_name}] ========================================")
                    print(f"[{class_name}] ✅ SUCCESS! Final roll number: {roll_number}")
                    print(f"[{class_name}] Matched pattern: {pattern}")
                    return roll_number
                else:
                    print(f"[{class_name}]   ⚠️ REJECTED: Match too short ({len(roll_number)} chars, minimum 6)")
                    print(f"[{class_name}]   → Trying next pattern...")
            else:
                print(f"[{class_name}]   → No match")
        
        print(f"[{class_name}] ========================================")
        
        print(f"[{class_name}] ❌ No roll number found with any pattern")
        return None
    
    def _validate_and_enforce_prefix(self, roll_number: str, context: Dict[str, Any], class_name: str) -> str:
        """
        Validate extracted roll number prefix against expected prefix from context.
        If they don't match, enforce the expected prefix.
        
        Args:
            roll_number: The extracted roll number
            context: Pipeline context containing expected_roll_number_prefix
            class_name: Class name for logging
            
        Returns:
            The roll number with enforced prefix if needed
        """
        # Get expected prefix from context
        expected_prefix = context.get('expected_roll_number_prefix')
        
        if not expected_prefix:
            print(f"[{class_name}] ⚠️ No expected_roll_number_prefix found in context, skipping prefix validation")
            return roll_number
        
        print(f"[{class_name}] ====== Prefix Validation ======")
        print(f"[{class_name}] Expected prefix: '{expected_prefix}'")
        print(f"[{class_name}] Extracted roll number: '{roll_number}'")
        
        # Determine the actual prefix from extracted roll number
        # Prefix format is: <zone><year two digit><class two digit>
        # We need to extract the prefix part (everything before the dash if there's a dash, or a certain length)
        actual_prefix = None
        
        # If roll number contains a dash, prefix is everything before the dash
        if '-' in roll_number:
            parts = roll_number.split('-', 1)
            actual_prefix = parts[0]
            suffix = parts[1] if len(parts) > 1 else ""
            print(f"[{class_name}] Roll number contains dash: '{actual_prefix}' - '{suffix}'")
        else:
            # No dash - prefix length should match expected prefix length
            expected_prefix_len = len(expected_prefix)
            if len(roll_number) >= expected_prefix_len:
                actual_prefix = roll_number[:expected_prefix_len]
                suffix = roll_number[expected_prefix_len:]
                print(f"[{class_name}] No dash found, using first {expected_prefix_len} chars as prefix: '{actual_prefix}'")
                print(f"[{class_name}] Remaining suffix: '{suffix}'")
            else:
                print(f"[{class_name}] ⚠️ Roll number shorter than expected prefix, cannot validate")
                return roll_number
        
        # Compare prefixes (case-insensitive)
        if actual_prefix.upper() == expected_prefix.upper():
            print(f"[{class_name}] ✅ Prefix matches expected prefix exactly")
            print(f"[{class_name}] ================================")
            return roll_number
        else:
            print(f"[{class_name}] ⚠️ Prefix mismatch detected!")
            print(f"[{class_name}]   Expected: '{expected_prefix}'")
            print(f"[{class_name}]   Actual:   '{actual_prefix}'")
            print(f"[{class_name}] 🔧 Enforcing expected prefix...")
            
            # Enforce the expected prefix
            if '-' in roll_number:
                # Reconstruct with expected prefix and original suffix
                enforced_roll_number = f"{expected_prefix}-{suffix}"
            else:
                # Replace prefix and keep the rest
                enforced_roll_number = expected_prefix + suffix
            
            print(f"[{class_name}]   Original:  '{roll_number}'")
            print(f"[{class_name}]   Enforced:  '{enforced_roll_number}'")
            print(f"[{class_name}] ================================")
            return enforced_roll_number
