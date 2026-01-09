#!/usr/bin/env python3
"""
Test OMR Sheet Generator and Bug Detection Script

This script:
1. Generates test OMR sheets with ArUco markers, roll numbers, and OMR bubbles
2. Runs each sheet through the pipeline 10 times
3. Collects all errors and bugs
4. Reports findings
"""

import os
import sys
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import traceback
import json
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from image_processor import ImageProcessor


class OMRTestGenerator:
    """Generate test OMR sheets for bug detection"""
    
    def __init__(self):
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.aruco_params = cv2.aruco.DetectorParameters()
        try:
            self.aruco_detector = cv2.aruco.ArucoDetector(self.aruco_dict, self.aruco_params)
            self.use_new_api = True
        except AttributeError:
            self.aruco_detector = None
            self.use_new_api = False
    
    def generate_aruco_marker(self, marker_id: int, size: int) -> np.ndarray:
        """Generate an ArUco marker image"""
        try:
            if self.use_new_api:
                return cv2.aruco.generateImageMarker(self.aruco_dict, marker_id, size)
            else:
                return cv2.aruco.drawMarker(self.aruco_dict, marker_id, size)
        except Exception as e:
            print(f"Error generating marker {marker_id}: {e}")
            return np.zeros((size, size), dtype=np.uint8)
    
    def generate_omr_sheet(self, roll_number: str, test_id: int, 
                           width: int = 2480, height: int = 3508) -> np.ndarray:
        """
        Generate a test OMR sheet with:
        - ArUco markers (IDs 1-20)
        - Roll number text
        - OMR bubbles for answers
        """
        # Create white background (A4 at 300 DPI: 2480x3508)
        image = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # Generate and place ArUco markers (IDs 1-20)
        marker_size = 80
        margin = 50
        
        # Place markers in a grid pattern
        # Top row: markers 1-10
        top_y = margin
        bottom_y = height - margin - marker_size
        
        # Calculate spacing for top row (10 markers)
        available_width = width - 2 * margin
        spacing_x = (available_width - 10 * marker_size) // 9
        
        # Place top row markers (1-10)
        for i in range(10):
            marker_id = i + 1
            x = margin + i * (marker_size + spacing_x)
            marker_img = self.generate_aruco_marker(marker_id, marker_size)
            marker_img_3ch = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)
            image[top_y:top_y+marker_size, x:x+marker_size] = marker_img_3ch
        
        # Place bottom row markers (11-20)
        for i in range(10):
            marker_id = i + 11
            x = margin + i * (marker_size + spacing_x)
            marker_img = self.generate_aruco_marker(marker_id, marker_size)
            marker_img_3ch = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)
            image[bottom_y:bottom_y+marker_size, x:x+marker_size] = marker_img_3ch
        
        # Add roll number text (positioned where OCR expects it)
        # Place it in the upper-middle area
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.5
        thickness = 4
        color = (0, 0, 0)  # Black text
        
        roll_text = f"Roll No: {roll_number}"
        (text_width, text_height), baseline = cv2.getTextSize(roll_text, font, font_scale, thickness)
        
        # Position roll number in upper-middle
        text_x = (width - text_width) // 2
        text_y = top_y + marker_size + 100
        
        # Draw text with shadow for better visibility
        cv2.putText(image, roll_text, (text_x + 2, text_y + 2), font, font_scale, (128, 128, 128), thickness)
        cv2.putText(image, roll_text, (text_x, text_y), font, font_scale, color, thickness)
        
        # Add OMR bubbles (simulate 50 questions with 4 options each)
        bubble_radius = 12
        bubble_thickness = 2
        start_y = text_y + 100
        question_spacing = 50
        option_spacing = 80
        
        for q in range(50):
            y = start_y + q * question_spacing
            if y + bubble_radius > bottom_y - 50:
                break
            
            # Question number
            q_text = f"Q{q+1:02d}"
            cv2.putText(image, q_text, (margin, y + bubble_radius), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
            
            # Draw 4 option bubbles (A, B, C, D)
            for opt_idx, opt_label in enumerate(['A', 'B', 'C', 'D']):
                x = margin + 100 + opt_idx * option_spacing
                center = (x, y)
                
                # Draw circle
                cv2.circle(image, center, bubble_radius, color, bubble_thickness)
                
                # Option label
                cv2.putText(image, opt_label, (x + bubble_radius + 5, y + 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        return image


class BugDetector:
    """Run tests and detect bugs"""
    
    def __init__(self):
        self.bugs = []
        self.test_results = []
        self.processor = None
    
    def initialize_processor(self):
        """Initialize the image processor"""
        try:
            self.processor = ImageProcessor()
            if not self.processor.ALL_DEPENDENCIES_AVAILABLE:
                raise Exception("Required dependencies not available")
            self.processor.set_expected_markers(list(range(1, 21)))
            return True
        except Exception as e:
            self.record_bug("INITIALIZATION", f"Failed to initialize ImageProcessor: {e}", traceback.format_exc())
            return False
    
    def record_bug(self, category: str, description: str, details: str = ""):
        """Record a bug"""
        bug = {
            "category": category,
            "description": description,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.bugs.append(bug)
        print(f"\n🐛 BUG DETECTED [{category}]: {description}")
        if details:
            print(f"   Details: {details[:200]}...")
    
    def run_single_test(self, image_path: str, test_iteration: int, test_id: int) -> Dict[str, Any]:
        """Run a single test iteration"""
        result = {
            "test_id": test_id,
            "iteration": test_iteration,
            "image_path": str(image_path),
            "success": False,
            "errors": [],
            "warnings": [],
            "stage_results": {}
        }
        
        try:
            # Create output folder for this test
            output_folder = project_root / f"test_bug_detection_results" / f"test_{test_id}" / f"run_{test_iteration}"
            output_folder.mkdir(parents=True, exist_ok=True)
            
            # Run pipeline
            pipeline_result = self.processor.process_image_pipeline(str(image_path), str(output_folder))
            
            result["success"] = pipeline_result.get("success", False)
            result["stage_results"] = pipeline_result.get("stages", {})
            
            # Check for errors in each stage
            for stage_name, stage_result in result["stage_results"].items():
                if not stage_result.get("success", False):
                    error_msg = stage_result.get("error", "Unknown error")
                    result["errors"].append(f"{stage_name}: {error_msg}")
                    
                    # Record bug
                    self.record_bug(
                        f"STAGE_FAILURE_{stage_name.upper()}",
                        f"Stage '{stage_name}' failed: {error_msg}",
                        json.dumps(stage_result, indent=2)
                    )
            
            # Check for warnings or unexpected behavior
            if result["success"]:
                # Check if roll number was extracted
                roll_stage = result["stage_results"].get("roll_number_extraction", {})
                if roll_stage.get("success"):
                    roll_number = roll_stage.get("roll_number")
                    if not roll_number:
                        result["warnings"].append("Roll number extraction succeeded but no roll number found")
                        self.record_bug(
                            "ROLL_NUMBER_EXTRACTION",
                            "Roll number extraction succeeded but returned empty roll number",
                            json.dumps(roll_stage, indent=2)
                        )
            
        except Exception as e:
            error_msg = str(e)
            result["errors"].append(f"EXCEPTION: {error_msg}")
            result["success"] = False
            
            self.record_bug(
                "EXCEPTION",
                f"Unexpected exception during test: {error_msg}",
                traceback.format_exc()
            )
        
        return result
    
    def run_test_suite(self, num_tests: int = 10, iterations_per_test: int = 10):
        """Run the full test suite"""
        print("=" * 80)
        print("OMR BUG DETECTION TEST SUITE")
        print("=" * 80)
        print(f"Generating {num_tests} test OMR sheets")
        print(f"Running each sheet {iterations_per_test} times through the pipeline")
        print("=" * 80)
        
        # Initialize processor
        print("\n[1/4] Initializing ImageProcessor...")
        if not self.initialize_processor():
            print("❌ Failed to initialize processor. Cannot continue.")
            return
        print("✅ Processor initialized")
        
        # Generate test OMR sheets
        print(f"\n[2/4] Generating {num_tests} test OMR sheets...")
        generator = OMRTestGenerator()
        test_images_dir = project_root / "test_bug_detection_images"
        test_images_dir.mkdir(exist_ok=True)
        
        test_images = []
        roll_numbers = [
            "JAMB24090019",
            "NAYA2508-0068",
            "NAYA2508-0069",
            "TEST001",
            "ABC123456",
            "XYZ-7890",
            "DEF123",
            "GHI456789",
            "JKL-0123",
            "MNO456"
        ]
        
        for i in range(num_tests):
            roll_number = roll_numbers[i % len(roll_numbers)]
            image = generator.generate_omr_sheet(roll_number, i)
            image_path = test_images_dir / f"test_omr_{i+1:02d}_{roll_number}.png"
            cv2.imwrite(str(image_path), image)
            test_images.append(image_path)
            print(f"  ✅ Generated: {image_path.name}")
        
        print(f"✅ Generated {len(test_images)} test images")
        
        # Run tests
        print(f"\n[3/4] Running tests ({iterations_per_test} iterations per image)...")
        total_tests = len(test_images) * iterations_per_test
        current_test = 0
        
        for test_id, image_path in enumerate(test_images, 1):
            print(f"\n--- Test Image {test_id}/{len(test_images)}: {image_path.name} ---")
            
            for iteration in range(1, iterations_per_test + 1):
                current_test += 1
                print(f"  [{current_test}/{total_tests}] Iteration {iteration}/{iterations_per_test}...", end=" ")
                
                result = self.run_single_test(image_path, iteration, test_id)
                self.test_results.append(result)
                
                if result["success"]:
                    print("✅")
                else:
                    print(f"❌ ({len(result['errors'])} errors)")
        
        # Analyze results
        print(f"\n[4/4] Analyzing results...")
        self.analyze_results()
        
        # Generate report
        self.generate_report()
    
    def analyze_results(self):
        """Analyze test results for patterns"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"\n📊 Test Results Summary:")
        print(f"   Total tests: {total_tests}")
        print(f"   Successful: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
        print(f"   Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        
        # Count errors by stage
        stage_failures = {}
        for result in self.test_results:
            for error in result["errors"]:
                stage_name = error.split(":")[0] if ":" in error else "UNKNOWN"
                stage_failures[stage_name] = stage_failures.get(stage_name, 0) + 1
        
        if stage_failures:
            print(f"\n📊 Failures by Stage:")
            for stage, count in sorted(stage_failures.items(), key=lambda x: x[1], reverse=True):
                print(f"   {stage}: {count} failures")
        
        # Check for consistency issues (same image, different results)
        print(f"\n📊 Checking for consistency issues...")
        image_results = {}
        for result in self.test_results:
            img_path = result["image_path"]
            if img_path not in image_results:
                image_results[img_path] = []
            image_results[img_path].append(result["success"])
        
        inconsistent_images = []
        for img_path, results in image_results.items():
            if len(set(results)) > 1:  # Different results for same image
                inconsistent_images.append((img_path, results))
                self.record_bug(
                    "CONSISTENCY",
                    f"Image {Path(img_path).name} produced inconsistent results across iterations",
                    f"Results: {results}"
                )
        
        if inconsistent_images:
            print(f"   ⚠️  Found {len(inconsistent_images)} images with inconsistent results")
        else:
            print(f"   ✅ All images produced consistent results")
    
    def generate_report(self):
        """Generate bug report"""
        report_dir = project_root / "test_bug_detection_results"
        report_dir.mkdir(exist_ok=True)
        
        report_path = report_dir / f"bug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("OMR PIPELINE BUG DETECTION REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Total bugs found: {len(self.bugs)}\n")
            f.write(f"Total tests run: {len(self.test_results)}\n")
            f.write(f"Successful tests: {sum(1 for r in self.test_results if r['success'])}\n")
            f.write(f"Failed tests: {sum(1 for r in self.test_results if not r['success'])}\n\n")
            
            # Group bugs by category
            bugs_by_category = {}
            for bug in self.bugs:
                category = bug["category"]
                if category not in bugs_by_category:
                    bugs_by_category[category] = []
                bugs_by_category[category].append(bug)
            
            f.write("=" * 80 + "\n")
            f.write("BUGS BY CATEGORY\n")
            f.write("=" * 80 + "\n\n")
            
            for category, bugs in sorted(bugs_by_category.items()):
                f.write(f"\n[{category}] - {len(bugs)} bug(s)\n")
                f.write("-" * 80 + "\n")
                for i, bug in enumerate(bugs, 1):
                    f.write(f"\n  Bug #{i}:\n")
                    f.write(f"    Description: {bug['description']}\n")
                    f.write(f"    Timestamp: {bug['timestamp']}\n")
                    if bug['details']:
                        f.write(f"    Details:\n{bug['details']}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("DETAILED TEST RESULTS\n")
            f.write("=" * 80 + "\n\n")
            
            for result in self.test_results:
                f.write(f"Test ID: {result['test_id']}, Iteration: {result['iteration']}\n")
                f.write(f"  Image: {Path(result['image_path']).name}\n")
                f.write(f"  Success: {result['success']}\n")
                if result['errors']:
                    f.write(f"  Errors: {len(result['errors'])}\n")
                    for error in result['errors']:
                        f.write(f"    - {error}\n")
                if result['warnings']:
                    f.write(f"  Warnings: {len(result['warnings'])}\n")
                    for warning in result['warnings']:
                        f.write(f"    - {warning}\n")
                f.write("\n")
        
        print(f"\n✅ Bug report saved to: {report_path}")
        
        # Print summary
        print("\n" + "=" * 80)
        print("BUG DETECTION SUMMARY")
        print("=" * 80)
        print(f"Total bugs found: {len(self.bugs)}")
        
        if self.bugs:
            bugs_by_category = {}
            for bug in self.bugs:
                category = bug["category"]
                bugs_by_category[category] = bugs_by_category.get(category, 0) + 1
            
            print("\nBugs by category:")
            for category, count in sorted(bugs_by_category.items(), key=lambda x: x[1], reverse=True):
                print(f"  {category}: {count}")
            
            print("\nTop bugs:")
            for i, bug in enumerate(self.bugs[:10], 1):
                print(f"  {i}. [{bug['category']}] {bug['description']}")
        else:
            print("✅ No bugs detected!")


def main():
    """Main entry point"""
    detector = BugDetector()
    detector.run_test_suite(num_tests=10, iterations_per_test=10)


if __name__ == "__main__":
    main()



