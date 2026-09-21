#!/usr/bin/env python3
"""
Test script to run the full pipeline on a single PNG image without UI.

This script replicates exactly what the UI does when processing an image,
but runs from command line for quick iteration and testing.

Usage:
    python test_single_image_pipeline.py <image_path> [output_folder]

Examples:
    python test_single_image_pipeline.py test_input_pdf/OMR_300DPI_pages/page_1.png
    python test_single_image_pipeline.py path/to/image.png results/
    python test_single_image_pipeline.py image.png ./output
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from image_processor import ImageProcessor


def print_header(text: str, char: str = "="):
    """Print a formatted header."""
    print("\n" + char * 80)
    print(f"  {text}")
    print(char * 80 + "\n")


def print_stage_result(stage_name: str, stage_result: dict):
    """Print formatted stage result."""
    success = stage_result.get('success', False)
    status = "✅" if success else "❌"
    
    print(f"  {status} {stage_name}")
    
    if not success:
        error = stage_result.get('error', 'Unknown error')
        print(f"     Error: {error}")
    
    # Print stage-specific information
    if stage_name == 'aruco_check':
        detected = stage_result.get('detected_ids', [])
        missing = stage_result.get('missing_ids', [])
        if detected:
            print(f"     Detected markers: {detected}")
        if missing:
            print(f"     Missing markers: {missing}")
    
    elif stage_name == 'roll_number_extraction':
        roll_number = stage_result.get('roll_number')
        if roll_number:
            print(f"     🆔 Roll Number: {roll_number}")

    elif stage_name == 'qr_reading':
        qr_result = stage_result.get('qr_result')
        if qr_result:
            print(f"     QR status: {qr_result.status.value}")
            if qr_result.is_valid:
                print(f"     StudentCode: {qr_result.data.student_code}")
                print(f"     ExamCode: {qr_result.data.exam_code}")
                print(f"     ExamRoll: {qr_result.data.exam_roll}")
                print(f"     ExamRollNumber: {qr_result.data.exam_roll_number}")
    
    elif stage_name == 'fetch_student':
        student_data = stage_result.get('student_data', {})
        if student_data:
            print(f"     Student: {student_data.get('name', 'N/A')}")
            print(f"     Class: {student_data.get('class', 'N/A')}")
    
    elif stage_name == 'omr_answer_extraction':
        marked_count = stage_result.get('marked_count', 0)
        print(f"     Marked answers: {marked_count}")
    
    elif stage_name == 'api_upload':
        upload_id = stage_result.get('upload_id')
        if upload_id:
            print(f"     📤 Upload ID: {upload_id}")


def main():
    """Main function to run pipeline on a single image."""
    parser = argparse.ArgumentParser(
        prog="test_single_image_pipeline.py",
        description="""
Run the full OMR (Optical Mark Recognition) pipeline on a single image without UI.

This script replicates exactly what the UI does when processing an image, but runs
from command line for quick iteration and internal testing. It processes the image
through all pipeline stages: ArUco check, orientation, roll number extraction,
student data fetch, OMR processing, answer extraction, validation, and API upload.

The script saves results to 'success/' or 'error/' folders, just like the UI.
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default settings
  python test_single_image_pipeline.py test_input_pdf/OMR_300DPI_pages/page_1.png
  
  # Specify custom output folder
  python test_single_image_pipeline.py image.png ./my_results
  
  # Use custom ArUco marker range
  python test_single_image_pipeline.py image.png --markers "1-20"
  
  # Use specific ArUco markers only
  python test_single_image_pipeline.py image.png --markers "1,2,3,4,5,10,15"
  
  # Full example with all options
  python test_single_image_pipeline.py path/to/image.png ./output --markers "1-20"

Supported Image Formats:
  PNG, JPG, JPEG, BMP, TIFF

Output Structure:
  <output_folder>/
    ├── success/          # Successfully processed images
    └── error/            # Failed images with error details

Exit Codes:
  0  - Pipeline completed successfully
  1  - Pipeline failed or error occurred
  130 - Interrupted by user (Ctrl+C)
        """
    )
    
    parser.add_argument(
        "image_path",
        type=str,
        help="Path to the image file to process (PNG, JPG, JPEG, BMP, or TIFF)"
    )
    
    parser.add_argument(
        "output_folder",
        nargs="?",
        default=None,
        type=str,
        help="""Output folder for results (optional).
        
If not specified, creates a timestamped folder like 'pipeline_results_20250115_143022'
in the current directory. The folder will contain 'success/' and 'error/' subfolders.
        """
    )
    
    parser.add_argument(
        "--markers",
        type=str,
        default="1-20",
        metavar="MARKERS",
        help="""Expected ArUco marker IDs to detect in the image.
        
Format options:
  Range:   "1-20"  (markers 1 through 20, inclusive)
  List:    "1,2,3,4,5"  (specific markers only)
  
Default: "1-20" (matches UI default)

Note: ArUco markers use DICT_4X4_50 format, valid IDs are 0-49.
        """
    )
    
    args = parser.parse_args()
    
    # Validate image path
    image_path = Path(args.image_path)
    if not image_path.exists():
        print(f"❌ ERROR: Image file not found: {image_path}")
        sys.exit(1)
    
    if not image_path.is_file():
        print(f"❌ ERROR: Path is not a file: {image_path}")
        sys.exit(1)
    
    # Validate image extension
    valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff'}
    if image_path.suffix.lower() not in valid_extensions:
        print(f"⚠️  WARNING: File extension '{image_path.suffix}' may not be supported")
        print(f"   Supported: {', '.join(valid_extensions)}")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Determine output folder
    if args.output_folder:
        output_folder = Path(args.output_folder)
    else:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = project_root / f"pipeline_results_{timestamp}"
    
    output_folder = output_folder.resolve()
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Parse expected markers
    expected_markers = []
    if '-' in args.markers:
        # Range format: "1-20"
        try:
            start, end = map(int, args.markers.split('-'))
            expected_markers = list(range(start, end + 1))
        except ValueError:
            print(f"❌ ERROR: Invalid marker range format: {args.markers}")
            print("   Use format: '1-20' or '1,2,3,4,5'")
            sys.exit(1)
    else:
        # Comma-separated format: "1,2,3,4,5"
        try:
            expected_markers = [int(x.strip()) for x in args.markers.split(',')]
        except ValueError:
            print(f"❌ ERROR: Invalid marker list format: {args.markers}")
            print("   Use format: '1-20' or '1,2,3,4,5'")
            sys.exit(1)
    
    # Print header
    print_header("OMR Pipeline - Single Image Test (No UI)")
    print(f"📷 Image: {image_path}")
    print(f"📂 Output: {output_folder}")
    print(f"🎯 Expected ArUco Markers: {expected_markers}")
    print()
    
    # Initialize processor
    print("🔧 Initializing ImageProcessor...")
    try:
        processor = ImageProcessor()
        
        if not processor.ALL_DEPENDENCIES_AVAILABLE:
            print("❌ ERROR: Required dependencies not available")
            print("   Please install: pip install opencv-python pytesseract numpy")
            sys.exit(1)
        
        # Set expected markers
        processor.set_expected_markers(expected_markers)
        print(f"✅ ImageProcessor initialized")
        print(f"   Expected markers: {processor.get_expected_markers()}")
        print()
        
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize ImageProcessor: {e}")
        sys.exit(1)
    
    # Run pipeline
    print_header("Running Pipeline", "-")
    
    try:
        result = processor.process_image_pipeline(str(image_path), str(output_folder))

        qr_result = result.get('qr_result')
        if qr_result:
            print(f"QR status: {qr_result.status.value}")
            if qr_result.is_valid:
                print(f"StudentCode: {qr_result.data.student_code}")
                print(f"ExamCode: {qr_result.data.exam_code}")
                print(f"ExamRoll: {qr_result.data.exam_roll}")
                print(f"ExamRollNumber: {qr_result.data.exam_roll_number}")
        
        # Print results
        print_header("Pipeline Results", "-")
        
        if result['success']:
            print("✅ Pipeline completed successfully!\n")
            
            print("📊 Stage Results:")
            stages = result.get('stages', {})
            for stage_name, stage_result in stages.items():
                print_stage_result(stage_name, stage_result)
            
            print()
            print(f"📁 Output image: {result.get('output_path', 'N/A')}")
            
            # Show roll number if extracted
            roll_number = None
            roll_stage = stages.get('roll_number_extraction', {})
            if roll_stage.get('success'):
                roll_number = roll_stage.get('roll_number')
            
            if roll_number:
                print(f"🆔 Roll Number: {roll_number}")
            
            # Show API upload status
            api_stage = stages.get('api_upload', {})
            if api_stage.get('success'):
                upload_id = api_stage.get('upload_id')
                print(f"📤 API Upload: Success (ID: {upload_id})")
            else:
                print(f"📤 API Upload: {'Skipped' if api_stage.get('skipped') else 'Failed'}")
            
            print()
            print_header("✅ SUCCESS - Pipeline completed", "=")
            print(f"📂 Check results in: {output_folder}")
            print(f"   - Success images: {output_folder / 'success'}")
            print(f"   - Error images: {output_folder / 'error'}")
            print()
            
            sys.exit(0)
            
        else:
            print("❌ Pipeline failed!\n")
            print(f"   Failed at stage: {result.get('error_stage', 'Unknown')}")
            print(f"   Error: {result.get('error_message', 'Unknown error')}")
            print()
            
            # Show which stages completed
            stages = result.get('stages', {})
            if stages:
                print("📊 Stage Results (up to failure):")
                for stage_name, stage_result in stages.items():
                    print_stage_result(stage_name, stage_result)
            
            print()
            print(f"📁 Error image: {result.get('error_image_path', result.get('output_path', 'N/A'))}")
            print()
            print_header("❌ FAILED - Pipeline stopped", "=")
            print(f"📂 Check error details in: {output_folder / 'error'}")
            print()
            
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {e}")
        print(f"   Exception type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

