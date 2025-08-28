#!/usr/bin/env python3
"""
Image processing module for ArUco marker detection and OCR
"""

# Handle imports with better error handling
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError as e:
    print(f"Warning: OpenCV not available - {e}")
    OPENCV_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: NumPy not available - {e}")
    NUMPY_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: pytesseract not available - {e}")
    PYTESSERACT_AVAILABLE = False
except ValueError as e:
    print(f"Warning: pytesseract dependency issue - {e}")
    print("This might be due to numpy/pandas version incompatibility")
    PYTESSERACT_AVAILABLE = False

import os
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# Check if all required dependencies are available
ALL_DEPENDENCIES_AVAILABLE = OPENCV_AVAILABLE and NUMPY_AVAILABLE and PYTESSERACT_AVAILABLE

# Check if core dependencies for ArUco processing are available
ARUCO_DEPENDENCIES_AVAILABLE = OPENCV_AVAILABLE and NUMPY_AVAILABLE


class ImageProcessor:
    """Handles image processing with OpenCV and ArUco marker detection"""
    
    def __init__(self):
        # Initialize as False by default
        self.opencv_initialized = False
        
        print(f"[DEBUG] Initializing ImageProcessor...")
        print(f"[DEBUG] ALL_DEPENDENCIES_AVAILABLE: {ALL_DEPENDENCIES_AVAILABLE}")
        print(f"[DEBUG] OPENCV_AVAILABLE: {OPENCV_AVAILABLE}")
        print(f"[DEBUG] NUMPY_AVAILABLE: {NUMPY_AVAILABLE}")
        print(f"[DEBUG] PYTESSERACT_AVAILABLE: {PYTESSERACT_AVAILABLE}")
        
        if not ARUCO_DEPENDENCIES_AVAILABLE:
            print("Warning: Core dependencies (OpenCV/NumPy) not available for image processing")
            return
            
        if ARUCO_DEPENDENCIES_AVAILABLE:
            try:
                print("[DEBUG] Attempting to initialize OpenCV ArUco detector...")
                print(f"[DEBUG] OpenCV version: {cv2.__version__}")
                
                # Initialize ArUco detector for DICT_4X4_50 (valid IDs: 0-49)
                # Handle both old and new OpenCV API versions
                try:
                    # Try new style first (OpenCV >= 4.7)
                    print("[DEBUG] Trying new OpenCV ArUco API...")
                    self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
                    self.aruco_params = cv2.aruco.DetectorParameters()
                    self.aruco_detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
                    self.use_new_api = True
                    print("[DEBUG] Using new OpenCV ArUco API")
                except AttributeError:
                    # Fall back to old style (OpenCV < 4.7)
                    print("[DEBUG] Trying old OpenCV ArUco API...")
                    self.aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
                    self.aruco_params = cv2.aruco.DetectorParameters_create()
                    self.aruco_detector = None
                    self.use_new_api = False
                    print("[DEBUG] Using old OpenCV ArUco API")
                
                self.opencv_initialized = True
                print("[DEBUG] OpenCV ArUco detector initialized successfully")
            except Exception as e:
                print(f"[ERROR] Failed to initialize OpenCV ArUco detector: {e}")
                self.opencv_initialized = False
        else:
            print("[ERROR] OpenCV or NumPy not available for initialization")
            self.opencv_initialized = False
        
        # Expected ArUco marker IDs (valid range: 0-49 for DICT_4X4_50)
        # Default to IDs 1-20 for OMR/ArUco workflows
        self.expected_markers = list(range(1, 21))  # Expecting 20 markers with IDs 1-20
        
    def detect_aruco_markers(self, image_path: str) -> Tuple[List[int], Dict]:
        """
        Detect ArUco markers in an image and extract their midpoints

        Args:
            image_path: Path to the image file

        Returns:
            Tuple of (detected_marker_ids, detection_info)
        """
        if not self.opencv_initialized:
            return [], {"error": "OpenCV not properly initialized"}
            
        try:
            print(f"[DEBUG] Reading image: {os.path.basename(image_path)}")
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                print(f"[ERROR] Could not read image: {image_path}")
                return [], {"error": "Could not read image"}
            
            print(f"[DEBUG] Image dimensions: {image.shape}")
            
            # Convert to grayscale for better detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            print(f"[DEBUG] Converted to grayscale for ArUco detection")
            
            # Detect ArUco markers
            print(f"[DEBUG] Starting ArUco marker detection...")
            
            if self.use_new_api:
                # Use new API (OpenCV >= 4.7)
                corners, ids, rejected = self.aruco_detector.detectMarkers(gray)
            else:
                # Use old API (OpenCV < 4.7)
                corners, ids, rejected = cv2.aruco.detectMarkers(
                    gray, self.aruco_dict, parameters=self.aruco_params
                )
            
            detected_ids = []
            midpoints = []
            if ids is not None:
                detected_ids = ids.flatten().tolist()
                print(f"[DEBUG] ArUco detection found {len(detected_ids)} markers: {detected_ids}")

                # Calculate midpoints for each detected marker
                for marker_corners in corners:
                    # marker_corners is a 4x2 array (4 corners with x, y coordinates)
                    midpoint = tuple(np.mean(marker_corners[0], axis=0).astype(int))
                    midpoints.append(midpoint)
                    print(f"[DEBUG] Marker midpoint: {midpoint}")
            else:
                print(f"[DEBUG] No ArUco markers detected")
            
            if len(rejected) > 0:
                print(f"[DEBUG] {len(rejected)} potential markers were rejected")
            
            detection_info = {
                "total_detected": len(detected_ids),
                "detected_ids": detected_ids,
                "expected_ids": self.expected_markers,
                "missing_ids": [mid for mid in self.expected_markers if mid not in detected_ids],
                "image_shape": image.shape,
                "corners_count": len(corners) if corners else 0,
                "marker_midpoints": []  # Add midpoints to detection info
            }

            if corners:
                for corner_set in corners:
                    # Calculate midpoint for each marker
                    midpoint = tuple(np.mean(corner_set[0], axis=0).astype(int))
                    detection_info["marker_midpoints"].append(midpoint)

            return detected_ids, detection_info
            
        except Exception as e:
            error_msg = f"Exception in ArUco detection: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return [], {"error": error_msg}
    
    def check_aruco_completeness(self, image_path: str) -> Tuple[bool, Dict]:
        """
        Check if all expected ArUco markers are present
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (all_markers_present, detection_details)
        """
        detected_ids, detection_info = self.detect_aruco_markers(image_path)
        
        if "error" in detection_info:
            return False, detection_info
        
        missing_markers = detection_info["missing_ids"]
        all_present = len(missing_markers) == 0
        
        detection_info.update({
            "all_markers_present": all_present,
            "missing_count": len(missing_markers),
            "success": all_present
        })
        
        return all_present, detection_info
    
    def extract_text_with_ocr(self, image_path: str) -> str:
        """
        Extract text from image using Tesseract OCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text string
        """
        if not PYTESSERACT_AVAILABLE:
            return "OCR Error: pytesseract not available or has dependency issues"
            
        try:
            # Read image with PIL for OCR
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using pytesseract
            extracted_text = pytesseract.image_to_string(image)
            
            return extracted_text.strip()
            
        except Exception as e:
            return f"OCR Error: {str(e)}"
    
    def create_annotated_image(self, image_path: str, output_path: str, 
                             detection_info: Dict, extracted_text: str = "") -> bool:
        """
        Create an annotated image with ArUco detection results and text overlay
        
        Args:
            image_path: Original image path
            output_path: Where to save the annotated image
            detection_info: Detection results from check_aruco_completeness
            extracted_text: OCR extracted text to overlay
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read original image
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            # Convert BGR to RGB for PIL
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image_rgb)
            
            # Create drawing context
            draw = ImageDraw.Draw(pil_image)
            
            # Try to load a font (fallback to default if not available)
            try:
                font_large = ImageFont.truetype("arial.ttf", 40)
                font_small = ImageFont.truetype("arial.ttf", 20)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Get image dimensions
            width, height = pil_image.size
            
            # Create status text
            status = "✓ ALL MARKERS FOUND" if detection_info.get("all_markers_present", False) else "✗ MISSING MARKERS"
            status_color = (0, 255, 0) if detection_info.get("all_markers_present", False) else (255, 0, 0)
            
            # Draw status banner
            banner_height = 80
            draw.rectangle([0, 0, width, banner_height], fill=(0, 0, 0, 180))
            draw.text((10, 10), status, fill=status_color, font=font_large)
            
            # Add detection details
            y_offset = banner_height + 10
            details = [
                f"Detected: {detection_info.get('detected_ids', [])}",
                f"Missing: {detection_info.get('missing_ids', [])}",
                f"Expected: {detection_info.get('expected_ids', [])}"
            ]
            
            for detail in details:
                draw.text((10, y_offset), detail, fill=(255, 255, 255), font=font_small)
                y_offset += 25
            
            # Add OCR text if provided
            if extracted_text:
                # Limit text length for display
                display_text = extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
                text_lines = display_text.split('\n')[:5]  # Max 5 lines
                
                y_offset += 20
                draw.text((10, y_offset), "Extracted Text:", fill=(255, 255, 0), font=font_small)
                y_offset += 25
                
                for line in text_lines:
                    if line.strip():
                        draw.text((10, y_offset), line.strip(), fill=(255, 255, 255), font=font_small)
                        y_offset += 20
            
            # Save annotated image
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            pil_image.save(output_path, quality=95)
            
            return True
            
        except Exception as e:
            print(f"Error creating annotated image: {e}")
            return False
    
    def process_image(self, image_path: str, output_folder: str) -> Dict:
        """
        Process a single image: detect ArUco markers, extract text, and categorize
        
        Args:
            image_path: Path to the image to process
            output_folder: Base output folder for results
            
        Returns:
            Dictionary with processing results
        """
        filename = os.path.basename(image_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        print(f"[DEBUG] Starting processing for: {filename}")
        
        # Check ArUco markers
        print(f"[DEBUG] Detecting ArUco markers in: {filename}")
        all_markers_present, detection_info = self.check_aruco_completeness(image_path)
        
        if "error" in detection_info:
            print(f"[ERROR] ArUco detection failed for {filename}: {detection_info['error']}")
        else:
            detected_ids = detection_info.get('detected_ids', [])
            missing_ids = detection_info.get('missing_ids', [])
            print(f"[DEBUG] {filename} - Detected markers: {detected_ids}")
            if missing_ids:
                print(f"[DEBUG] {filename} - Missing markers: {missing_ids}")
        
        # Extract text with OCR
        print(f"[DEBUG] Extracting text via OCR from: {filename}")
        extracted_text = self.extract_text_with_ocr(image_path)
        
        if extracted_text.startswith("OCR Error:"):
            print(f"[ERROR] OCR failed for {filename}: {extracted_text}")
        elif extracted_text.strip():
            text_preview = extracted_text[:100] + "..." if len(extracted_text) > 100 else extracted_text
            print(f"[DEBUG] {filename} - OCR text preview: {text_preview}")
        else:
            print(f"[DEBUG] {filename} - No text extracted")
        
        # Determine output subfolder
        subfolder = "success" if all_markers_present else "failure"
        output_subdir = os.path.join(output_folder, subfolder)
        print(f"[DEBUG] {filename} categorized as: {subfolder}")
        
        # Create output filename with annotation
        annotated_filename = f"{name_without_ext}_processed.jpg"
        output_path = os.path.join(output_subdir, annotated_filename)
        
        # Create annotated image
        print(f"[DEBUG] Creating annotated image for: {filename}")
        annotation_success = self.create_annotated_image(
            image_path, output_path, detection_info, extracted_text
        )
        
        if annotation_success:
            print(f"[DEBUG] Annotated image created: {annotated_filename}")
        else:
            print(f"[ERROR] Failed to create annotated image for: {filename}")
        
        # Also save original if needed
        original_output_path = os.path.join(output_subdir, filename)
        try:
            import shutil
            shutil.copy2(image_path, original_output_path)
            print(f"[DEBUG] Original image copied to: {original_output_path}")
        except Exception as e:
            print(f"[WARNING] Could not copy original file {filename}: {e}")
        
        # Save processing report
        report_path = os.path.join(output_subdir, f"{name_without_ext}_report.txt")
        print(f"[DEBUG] Saving processing report for: {filename}")
        self.save_processing_report(report_path, filename, detection_info, extracted_text)
        
        result = {
            "filename": filename,
            "success": all_markers_present,
            "detection_info": detection_info,
            "extracted_text": extracted_text,
            "output_path": output_path,
            "original_output_path": original_output_path,
            "report_path": report_path,
            "annotation_created": annotation_success
        }
        
        print(f"[DEBUG] Processing completed for: {filename} - Success: {all_markers_present}")
        return result
    
    def save_processing_report(self, report_path: str, filename: str, 
                             detection_info: Dict, extracted_text: str):
        """Save a detailed processing report for the image"""
        try:
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"Image Processing Report\n")
                f.write(f"=" * 50 + "\n\n")
                f.write(f"File: {filename}\n")
                f.write(f"Status: {'SUCCESS' if detection_info.get('all_markers_present', False) else 'FAILURE'}\n\n")
                
                f.write("ArUco Marker Detection:\n")
                f.write(f"  Expected IDs: {detection_info.get('expected_ids', [])}\n")
                f.write(f"  Detected IDs: {detection_info.get('detected_ids', [])}\n")
                f.write(f"  Missing IDs: {detection_info.get('missing_ids', [])}\n")
                f.write(f"  Total Detected: {detection_info.get('total_detected', 0)}\n\n")
                
                f.write("OCR Extracted Text:\n")
                f.write("-" * 20 + "\n")
                f.write(extracted_text if extracted_text else "No text extracted")
                f.write("\n" + "-" * 20 + "\n")
                
        except Exception as e:
            print(f"Error saving report: {e}")
    
    def set_expected_markers(self, marker_ids: List[int]):
        """Set the list of expected ArUco marker IDs"""
        self.expected_markers = marker_ids
    
    def get_expected_markers(self) -> List[int]:
        """Get the current list of expected ArUco marker IDs"""
        return self.expected_markers.copy()

    def process_image_pipeline(self, image_path: str, output_folder: str) -> Dict:
        """
        Comprehensive pipeline for processing OMR images:
        1. Check basic ArUco markers are present
        2. Check and rotate tilted images
        3. Extract exam roll number from image
        4. Process the OMR sheet
        5. Upload to API
        
        Args:
            image_path: Path to the image to process
            output_folder: Base output folder for results
            
        Returns:
            Dictionary with processing results and stage information
        """
        filename = os.path.basename(image_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        print(f"[PIPELINE] Starting processing for: {filename}")
        
        # Initialize pipeline result
        pipeline_result = {
            "filename": filename,
            "success": False,
            "stages": {},
            "error_stage": None,
            "error_message": None,
            "output_path": None,
            "api_upload_success": False
        }
        
        try:
            # Stage 1: Check basic ArUco markers are present
            print(f"[PIPELINE] Stage 1: Checking ArUco markers for {filename}")
            stage1_result = self._stage1_check_aruco_markers(image_path)
            pipeline_result["stages"]["aruco_check"] = stage1_result
            
            if not stage1_result["success"]:
                pipeline_result["error_stage"] = "aruco_check"
                pipeline_result["error_message"] = stage1_result["error"]
                return self._handle_pipeline_error(image_path, output_folder, pipeline_result)
            
            # Stage 2: Check and rotate tilted images
            print(f"[PIPELINE] Stage 2: Checking image orientation for {filename}")
            stage2_result = self._stage2_check_and_rotate_image(image_path)
            pipeline_result["stages"]["orientation_check"] = stage2_result
            
            if not stage2_result["success"]:
                pipeline_result["error_stage"] = "orientation_check"
                pipeline_result["error_message"] = stage2_result["error"]
                return self._handle_pipeline_error(image_path, output_folder, pipeline_result)
            
            # Stage 3: Extract exam roll number
            print(f"[PIPELINE] Stage 3: Extracting roll number for {filename}")
            stage3_result = self._stage3_extract_roll_number(stage2_result["rotated_image_path"])
            pipeline_result["stages"]["roll_number_extraction"] = stage3_result
            
            if not stage3_result["success"]:
                pipeline_result["error_stage"] = "roll_number_extraction"
                pipeline_result["error_message"] = stage3_result["error"]
                return self._handle_pipeline_error(stage2_result["rotated_image_path"], output_folder, pipeline_result)
            
            # Stage 4: Process OMR sheet
            print(f"[PIPELINE] Stage 4: Processing OMR sheet for {filename}")
            stage4_result = self._stage4_process_omr_sheet(stage2_result["rotated_image_path"], stage3_result["roll_number"])
            pipeline_result["stages"]["omr_processing"] = stage4_result
            
            if not stage4_result["success"]:
                pipeline_result["error_stage"] = "omr_processing"
                pipeline_result["error_message"] = stage4_result["error"]
                return self._handle_pipeline_error(stage2_result["rotated_image_path"], output_folder, pipeline_result)
            
            # Stage 5: Upload to API
            print(f"[PIPELINE] Stage 5: Uploading to API for {filename}")
            stage5_result = self._stage5_upload_to_api(stage4_result["omr_data"], stage3_result["roll_number"])
            pipeline_result["stages"]["api_upload"] = stage5_result
            
            if not stage5_result["success"]:
                pipeline_result["error_stage"] = "api_upload"
                pipeline_result["error_message"] = stage5_result["error"]
                return self._handle_pipeline_error(stage2_result["rotated_image_path"], output_folder, pipeline_result)
            
            # All stages successful
            pipeline_result["success"] = True
            pipeline_result["output_path"] = stage2_result["rotated_image_path"]
            pipeline_result["api_upload_success"] = True
            
            # Move to success folder
            success_folder = os.path.join(output_folder, "success")
            os.makedirs(success_folder, exist_ok=True)
            
            final_output_path = os.path.join(success_folder, f"{name_without_ext}_processed.jpg")
            import shutil
            shutil.copy2(stage2_result["rotated_image_path"], final_output_path)
            pipeline_result["output_path"] = final_output_path
            
            print(f"[PIPELINE] ✅ All stages completed successfully for {filename}")
            return pipeline_result
            
        except Exception as e:
            pipeline_result["error_stage"] = "pipeline_exception"
            pipeline_result["error_message"] = f"Unexpected error: {str(e)}"
            return self._handle_pipeline_error(image_path, output_folder, pipeline_result)
    
    def _stage1_check_aruco_markers(self, image_path: str) -> Dict:
        """Stage 1: Check if basic ArUco markers are present"""
        try:
            detected_ids, detection_info = self.detect_aruco_markers(image_path)
            
            if "error" in detection_info:
                return {
                    "success": False,
                    "error": detection_info["error"],
                    "detected_markers": []
                }
            
            # Check if we have at least some markers (adjust threshold as needed)
            min_required_markers = 5  # Minimum markers required
            if len(detected_ids) < min_required_markers:
                return {
                    "success": False,
                    "error": f"Insufficient ArUco markers found. Expected at least {min_required_markers}, found {len(detected_ids)}",
                    "detected_markers": detected_ids
                }
            
            return {
                "success": True,
                "detected_markers": detected_ids,
                "detection_info": detection_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"ArUco detection failed: {str(e)}",
                "detected_markers": []
            }
    
    def _stage2_check_and_rotate_image(self, image_path: str) -> Dict:
        """Stage 2: Check image orientation and rotate if needed"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return {
                    "success": False,
                    "error": "Could not read image",
                    "rotated_image_path": None
                }
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect ArUco markers to determine orientation
            if self.use_new_api:
                corners, ids, rejected = self.aruco_detector.detectMarkers(gray)
            else:
                corners, ids, rejected = cv2.aruco.detectMarkers(
                    gray, self.aruco_dict, parameters=self.aruco_params
                )
            
            if ids is None or len(ids) == 0:
                return {
                    "success": False,
                    "error": "No ArUco markers found for orientation detection",
                    "rotated_image_path": None
                }
            
            # Use marker positions to determine if rotation is needed
            # This is a simple heuristic - you might want to improve this
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
                
                return {
                    "success": True,
                    "rotation_applied": rotation_needed,
                    "rotated_image_path": rotated_path
                }
            else:
                return {
                    "success": True,
                    "rotation_applied": 0,
                    "rotated_image_path": image_path
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Orientation check failed: {str(e)}",
                "rotated_image_path": None
            }
    
    def _stage3_extract_roll_number(self, image_path: str) -> Dict:
        """Stage 3: Extract exam roll number from image"""
        try:
            # Check if OCR is available
            if not PYTESSERACT_AVAILABLE:
                return {
                    "success": False,
                    "error": "OCR not available - pytesseract dependency issue",
                    "roll_number": None
                }
            
            # Extract text using OCR
            extracted_text = self.extract_text_with_ocr(image_path)
            
            if extracted_text.startswith("OCR Error:"):
                return {
                    "success": False,
                    "error": extracted_text,
                    "roll_number": None
                }
            
            # Parse roll number from extracted text
            roll_number = self._parse_roll_number(extracted_text)
            
            if roll_number is None:
                return {
                    "success": False,
                    "error": "Could not extract roll number from image",
                    "extracted_text": extracted_text,
                    "roll_number": None
                }
            
            return {
                "success": True,
                "roll_number": roll_number,
                "extracted_text": extracted_text
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Roll number extraction failed: {str(e)}",
                "roll_number": None
            }
    
    def _stage4_process_omr_sheet(self, image_path: str, roll_number: str) -> Dict:
        """Stage 4: Process OMR sheet and extract answers"""
        try:
            # This is where you'd implement OMR-specific processing
            # For now, we'll do basic ArUco detection and return structure
            
            detected_ids, detection_info = self.detect_aruco_markers(image_path)
            
            if "error" in detection_info:
                return {
                    "success": False,
                    "error": detection_info["error"],
                    "omr_data": None
                }
            
            # Create OMR data structure
            omr_data = {
                "roll_number": roll_number,
                "detected_markers": detected_ids,
                "marker_positions": detection_info.get("marker_midpoints", []),
                "processing_timestamp": str(datetime.now()),
                "image_path": image_path
            }
            
            return {
                "success": True,
                "omr_data": omr_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"OMR processing failed: {str(e)}",
                "omr_data": None
            }
    
    def _stage5_upload_to_api(self, omr_data: Dict, roll_number: str) -> Dict:
        """Stage 5: Upload processed data to API"""
        try:
            # This is where you'd implement API upload
            # For now, we'll simulate a successful upload
            
            # Simulate API call
            api_response = self._simulate_api_upload(omr_data)
            
            if api_response["success"]:
                return {
                    "success": True,
                    "api_response": api_response,
                    "upload_id": api_response.get("upload_id")
                }
            else:
                return {
                    "success": False,
                    "error": api_response.get("error", "API upload failed"),
                    "api_response": api_response
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"API upload failed: {str(e)}",
                "api_response": None
            }
    
    def _handle_pipeline_error(self, image_path: str, output_folder: str, pipeline_result: Dict) -> Dict:
        """Handle pipeline errors by marking image and moving to error folder"""
        try:
            # Create error folder
            error_folder = os.path.join(output_folder, "error")
            os.makedirs(error_folder, exist_ok=True)
            
            # Add red line to image to mark as error
            error_image_path = self._mark_image_as_error(image_path, error_folder, pipeline_result)
            
            # Update pipeline result
            pipeline_result["output_path"] = error_image_path
            pipeline_result["error_image_path"] = error_image_path
            
            print(f"[PIPELINE] ❌ Error at stage '{pipeline_result['error_stage']}' for {pipeline_result['filename']}")
            print(f"[PIPELINE] Error message: {pipeline_result['error_message']}")
            
            return pipeline_result
            
        except Exception as e:
            print(f"[PIPELINE] Failed to handle error: {str(e)}")
            return pipeline_result
    
    def _mark_image_as_error(self, image_path: str, error_folder: str, pipeline_result: Dict) -> str:
        """Add red line to image and save to error folder"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return image_path
            
            # Add red line across the image
            height, width = image.shape[:2]
            cv2.line(image, (0, height//2), (width, height//2), (0, 0, 255), 5)  # Red line
            
            # Add error text
            error_text = f"ERROR: {pipeline_result['error_stage']}"
            cv2.putText(image, error_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Save to error folder
            filename = os.path.basename(image_path)
            name_without_ext = os.path.splitext(filename)[0]
            error_image_path = os.path.join(error_folder, f"{name_without_ext}_ERROR.jpg")
            cv2.imwrite(error_image_path, image)
            
            return error_image_path
            
        except Exception as e:
            print(f"Failed to mark image as error: {str(e)}")
            return image_path
    
    def _determine_rotation_needed(self, corners, ids) -> int:
        """Determine if image needs rotation based on ArUco marker positions"""
        # This is a simple heuristic - you might want to improve this
        # For now, we'll assume no rotation is needed
        return 0
    
    def _parse_roll_number(self, text: str) -> str:
        """Parse roll number from OCR text"""
        # This is a simple parser - you might want to improve this
        # Look for patterns like "Roll No:", "Roll Number:", etc.
        import re
        
        # Common patterns for roll numbers
        patterns = [
            r'Roll\s*[Nn]o[.:]\s*(\d+)',
            r'Roll\s*[Nn]umber[.:]\s*(\d+)',
            r'(\d{6,10})',  # 6-10 digit number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def _simulate_api_upload(self, omr_data: Dict) -> Dict:
        """Simulate API upload - replace with actual API call"""
        # Simulate network delay
        import time
        time.sleep(0.1)
        
        # Simulate successful upload
        return {
            "success": True,
            "upload_id": f"upload_{int(time.time())}",
            "message": "Data uploaded successfully"
        }


def test_image_processor():
    """Test function for the ImageProcessor class"""
    processor = ImageProcessor()
    
    # Test with a sample image (replace with actual image path)
    test_image = "test_image.jpg"
    output_folder = "test_output"
    
    if os.path.exists(test_image):
        result = processor.process_image(test_image, output_folder)
        print("Processing Result:", result)
    else:
        print(f"Test image {test_image} not found")


if __name__ == "__main__":
    test_image_processor()
