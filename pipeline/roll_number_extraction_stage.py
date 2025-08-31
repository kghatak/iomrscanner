#!/usr/bin/env python3
"""
Roll Number Extraction Stage Implementation

This stage extracts exam roll number from image using OCR.
"""

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
        try:
            # Check if pytesseract is available
            if not hasattr(self.processor, 'PYTESSERACT_AVAILABLE') or not self.processor.PYTESSERACT_AVAILABLE:
                return self.create_stage_result(
                    success=False,
                    error="OCR Error: pytesseract not available or has dependency issues",
                    roll_number=None
                )
            
            # Use the rotated image path from previous stage if available
            image_to_process = context.get('rotated_image_path', image_path)
            
            # Read image
            image = cv2.imread(image_to_process)
            if image is None:
                return self.create_stage_result(
                    success=False,
                    error="Could not read image for OCR",
                    roll_number=None
                )
            
            # Convert to grayscale for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply some preprocessing to improve OCR accuracy
            # 1. Resize image (optional)
            # 2. Apply thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Extract text using OCR
            import pytesseract
            text = pytesseract.image_to_string(thresh)
            
            # Parse roll number from text
            roll_number = self._parse_roll_number(text)
            
            if roll_number:
                return self.create_stage_result(
                    success=True,
                    roll_number=roll_number,
                    extracted_text=text
                )
            else:
                return self.create_stage_result(
                    success=False,
                    error="No valid roll number found in image",
                    roll_number=None,
                    extracted_text=text
                )
                
        except Exception as e:
            return self.create_stage_result(
                success=False,
                error=f"OCR processing failed: {str(e)}",
                roll_number=None
            )
    
    def _parse_roll_number(self, text: str) -> Optional[str]:
        """
        Parse roll number from OCR text using regex patterns.
        
        Args:
            text: Text extracted from image
            
        Returns:
            Extracted roll number or None if not found
        """
        # Common patterns for roll numbers
        patterns = [
            r'Roll\s*No[:\s]*(\d+)',
            r'Roll\s*Number[:\s]*(\d+)',
            r'Student\s*ID[:\s]*(\d+)',
            r'ID[:\s]*(\d+)',
            r'(\d{6,10})',  # Generic 6-10 digit number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
