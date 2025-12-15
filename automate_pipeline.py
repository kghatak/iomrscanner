#!/usr/bin/env python3
"""
Automated Pipeline Processing Script

This script automates the entire OMR processing pipeline:
1. Takes a PDF file path as input
2. Extracts images from PDF
3. Runs all pipeline stages automatically
4. Generates results in organized folders

Usage:
    python automate_pipeline.py <pdf_path> [output_folder]

Example:
    python automate_pipeline.py /path/to/omr_sheet.pdf /path/to/output
"""

import os
import sys
import argparse
import time
from datetime import datetime
from typing import List, Dict, Any
import json

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import required modules
from pdf_utils import convert_pdf_with_poppler
from pipeline.pipeline_stages import PipelineManager
from image_processor import ImageProcessor


class AutomatedPipelineProcessor:
    """
    Automated processor that handles the entire pipeline workflow.
    """
    
    def __init__(self, output_folder: str = None):
        """
        Initialize the automated processor.
        
        Args:
            output_folder: Base output folder for results
        """
        self.class_name = self.__class__.__name__
        
        # Set default output folder if not provided
        if output_folder is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_folder = f"pipeline_results_{timestamp}"
        
        self.output_folder = os.path.abspath(output_folder)
        self.temp_folder = os.path.join(self.output_folder, "temp_images")
        
        print(f"[{self.class_name}] ========================================")
        print(f"[{self.class_name}] AUTOMATED PIPELINE PROCESSOR INITIALIZED")
        print(f"[{self.class_name}] ========================================")
        print(f"[{self.class_name}] Output folder: {self.output_folder}")
        print(f"[{self.class_name}] Temp folder: {self.temp_folder}")
        
        # Create output directories
        self._create_output_directories()
        
        # Initialize the image processor and pipeline manager
        self.image_processor = ImageProcessor()
        self.image_processor.output_folder = self.output_folder
        self.pipeline_manager = PipelineManager(self.image_processor)
        
        print(f"[{self.class_name}] Pipeline manager initialized with {len(self.pipeline_manager.stages)} stages")
        
    def _create_output_directories(self):
        """Create necessary output directories."""
        directories = [
            self.output_folder,
            self.temp_folder,
            os.path.join(self.output_folder, "success"),
            os.path.join(self.output_folder, "error"),
            os.path.join(self.output_folder, "logs")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"[{self.class_name}] Created/verified directory: {directory}")
    
    def extract_images_from_pdf(self, pdf_path: str) -> List[str]:
        """
        Extract images from PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of extracted image file paths
        """
        print(f"[{self.class_name}] ========================================")
        print(f"[{self.class_name}] EXTRACTING IMAGES FROM PDF")
        print(f"[{self.class_name}] ========================================")
        print(f"[{self.class_name}] PDF path: {pdf_path}")
        print(f"[{self.class_name}] Temp folder: {self.temp_folder}")
        
        try:
            # Extract images from PDF (returns PIL Image objects)
            print(f"[{self.class_name}] Starting PDF to image conversion...")
            pil_images = convert_pdf_with_poppler(pdf_path)
            
            if not pil_images:
                raise Exception("No images extracted from PDF")
            
            print(f"[{self.class_name}] ✅ Successfully extracted {len(pil_images)} PIL images from PDF")
            
            # Save PIL images to files
            image_paths = []
            for i, pil_image in enumerate(pil_images, 1):
                # Create filename for this page
                filename = f"page_{i:03d}.png"
                image_path = os.path.join(self.temp_folder, filename)
                
                # Save PIL image to file
                pil_image.save(image_path, "PNG")
                image_paths.append(image_path)
                
                print(f"[{self.class_name}]   Saved image {i}: {filename}")
            
            print(f"[{self.class_name}] ✅ Successfully saved {len(image_paths)} images to temp folder")
            
            return image_paths
            
        except Exception as e:
            print(f"[{self.class_name}] ❌ ERROR extracting images from PDF: {str(e)}")
            raise
    
    def process_images(self, image_paths: List[str]) -> Dict[str, Any]:
        """
        Process all extracted images through the pipeline.
        
        Args:
            image_paths: List of image file paths to process
            
        Returns:
            Dictionary with processing results
        """
        print(f"[{self.class_name}] ========================================")
        print(f"[{self.class_name}] PROCESSING IMAGES THROUGH PIPELINE")
        print(f"[{self.class_name}] ========================================")
        print(f"[{self.class_name}] Total images to process: {len(image_paths)}")
        
        results = {
            "total_images": len(image_paths),
            "successful": 0,
            "failed": 0,
            "results": [],
            "start_time": datetime.now().isoformat(),
            "end_time": None
        }
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"[{self.class_name}] ========================================")
            print(f"[{self.class_name}] PROCESSING IMAGE {i}/{len(image_paths)}")
            print(f"[{self.class_name}] ========================================")
            print(f"[{self.class_name}] Image: {os.path.basename(image_path)}")
            
            try:
                # Process image through pipeline
                result = self.pipeline_manager.process_image(image_path, self.output_folder)
                
                # Store result
                results["results"].append({
                    "image_path": image_path,
                    "filename": os.path.basename(image_path),
                    "success": result["success"],
                    "error_stage": result.get("error_stage"),
                    "error_message": result.get("error_message"),
                    "output_path": result.get("output_path"),
                    "roll_number": result.get("context", {}).get("roll_number", "Unknown")
                })
                
                if result["success"]:
                    results["successful"] += 1
                    print(f"[{self.class_name}] ✅ Image {i} processed successfully")
                else:
                    results["failed"] += 1
                    print(f"[{self.class_name}] ❌ Image {i} failed at stage: {result.get('error_stage')}")
                    print(f"[{self.class_name}] Error: {result.get('error_message')}")
                
            except Exception as e:
                results["failed"] += 1
                error_result = {
                    "image_path": image_path,
                    "filename": os.path.basename(image_path),
                    "success": False,
                    "error_stage": "exception",
                    "error_message": str(e),
                    "output_path": None,
                    "roll_number": "Unknown"
                }
                results["results"].append(error_result)
                print(f"[{self.class_name}] ❌ EXCEPTION processing image {i}: {str(e)}")
        
        results["end_time"] = datetime.now().isoformat()
        
        print(f"[{self.class_name}] ========================================")
        print(f"[{self.class_name}] PIPELINE PROCESSING COMPLETE")
        print(f"[{self.class_name}] ========================================")
        print(f"[{self.class_name}] Total images: {results['total_images']}")
        print(f"[{self.class_name}] Successful: {results['successful']}")
        print(f"[{self.class_name}] Failed: {results['failed']}")
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        Generate a detailed processing report.
        
        Args:
            results: Processing results dictionary
            
        Returns:
            Path to the generated report file
        """
        print(f"[{self.class_name}] ========================================")
        print(f"[{self.class_name}] GENERATING PROCESSING REPORT")
        print(f"[{self.class_name}] ========================================")
        
        # Create report content
        report_content = {
            "pipeline_summary": {
                "total_images": results["total_images"],
                "successful": results["successful"],
                "failed": results["failed"],
                "success_rate": f"{(results['successful'] / results['total_images'] * 100):.1f}%" if results["total_images"] > 0 else "0%",
                "start_time": results["start_time"],
                "end_time": results["end_time"]
            },
            "detailed_results": results["results"],
            "pipeline_stages": [
                {
                    "name": stage.get_stage_name(),
                    "description": stage.get_stage_description()
                }
                for stage in self.pipeline_manager.stages
            ]
        }
        
        # Save JSON report
        report_path = os.path.join(self.output_folder, "logs", "processing_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_content, f, indent=2, ensure_ascii=False)
        
        # Create human-readable summary
        summary_path = os.path.join(self.output_folder, "logs", "processing_summary.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("OMR PIPELINE PROCESSING REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Processing Date: {results['start_time']}\n")
            f.write(f"Total Images: {results['total_images']}\n")
            f.write(f"Successful: {results['successful']}\n")
            f.write(f"Failed: {results['failed']}\n")
            f.write(f"Success Rate: {report_content['pipeline_summary']['success_rate']}\n\n")
            
            f.write("PIPELINE STAGES:\n")
            f.write("-" * 20 + "\n")
            for i, stage in enumerate(report_content['pipeline_stages'], 1):
                f.write(f"{i}. {stage['name']}: {stage['description']}\n")
            
            f.write("\nDETAILED RESULTS:\n")
            f.write("-" * 20 + "\n")
            for result in results["results"]:
                status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
                f.write(f"{result['filename']}: {status}\n")
                if not result["success"]:
                    f.write(f"  Error Stage: {result['error_stage']}\n")
                    f.write(f"  Error Message: {result['error_message']}\n")
                else:
                    f.write(f"  Roll Number: {result['roll_number']}\n")
                f.write("\n")
        
        print(f"[{self.class_name}] ✅ Report generated: {report_path}")
        print(f"[{self.class_name}] ✅ Summary generated: {summary_path}")
        
        return report_path
    
    def cleanup_temp_files(self):
        """Clean up temporary files."""
        print(f"[{self.class_name}] ========================================")
        print(f"[{self.class_name}] CLEANING UP TEMPORARY FILES")
        print(f"[{self.class_name}] ========================================")
        
        try:
            if os.path.exists(self.temp_folder):
                import shutil
                shutil.rmtree(self.temp_folder)
                print(f"[{self.class_name}] ✅ Temporary folder removed: {self.temp_folder}")
            else:
                print(f"[{self.class_name}] No temporary folder to clean up")
        except Exception as e:
            print(f"[{self.class_name}] ⚠️  WARNING: Could not clean up temp folder: {str(e)}")
    
    def run_full_pipeline(self, pdf_path: str) -> Dict[str, Any]:
        """
        Run the complete pipeline from PDF to results.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with complete processing results
        """
        start_time = time.time()
        
        print(f"[{self.class_name}] ========================================")
        print(f"[{self.class_name}] STARTING FULL PIPELINE PROCESSING")
        print(f"[{self.class_name}] ========================================")
        print(f"[{self.class_name}] PDF: {pdf_path}")
        print(f"[{self.class_name}] Output: {self.output_folder}")
        
        try:
            # Step 1: Extract images from PDF
            image_paths = self.extract_images_from_pdf(pdf_path)
            
            # Step 2: Process images through pipeline
            results = self.process_images(image_paths)
            
            # Step 3: Generate report
            report_path = self.generate_report(results)
            
            # Step 4: Clean up temporary files
            self.cleanup_temp_files()
            
            # Calculate total processing time
            total_time = time.time() - start_time
            results["total_processing_time_seconds"] = total_time
            
            print(f"[{self.class_name}] ========================================")
            print(f"[{self.class_name}] PIPELINE COMPLETED SUCCESSFULLY")
            print(f"[{self.class_name}] ========================================")
            print(f"[{self.class_name}] Total processing time: {total_time:.2f} seconds")
            print(f"[{self.class_name}] Results saved to: {self.output_folder}")
            print(f"[{self.class_name}] Report: {report_path}")
            
            return results
            
        except Exception as e:
            print(f"[{self.class_name}] ❌ PIPELINE FAILED: {str(e)}")
            print(f"[{self.class_name}] Exception type: {type(e).__name__}")
            raise


def main():
    """Main function to run the automated pipeline."""
    parser = argparse.ArgumentParser(
        description="Automated OMR Pipeline Processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python automate_pipeline.py /path/to/omr_sheet.pdf
  python automate_pipeline.py /path/to/omr_sheet.pdf /path/to/output
  python automate_pipeline.py test_input_pdf/OMR_300DPI.pdf results/
        """
    )
    
    parser.add_argument(
        "pdf_path",
        help="Path to the PDF file containing OMR sheets"
    )
    
    parser.add_argument(
        "output_folder",
        nargs="?",
        help="Output folder for results (optional, defaults to timestamped folder)"
    )
    
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temporary extracted images (default: cleanup after processing)"
    )
    
    args = parser.parse_args()
    
    # Validate PDF path
    if not os.path.exists(args.pdf_path):
        print(f"❌ ERROR: PDF file not found: {args.pdf_path}")
        sys.exit(1)
    
    if not args.pdf_path.lower().endswith('.pdf'):
        print(f"❌ ERROR: File is not a PDF: {args.pdf_path}")
        sys.exit(1)
    
    try:
        # Initialize processor
        processor = AutomatedPipelineProcessor(args.output_folder)
        
        # Run full pipeline
        results = processor.run_full_pipeline(args.pdf_path)
        
        # Print final summary
        print("\n" + "=" * 60)
        print("FINAL SUMMARY")
        print("=" * 60)
        print(f"Total Images Processed: {results['total_images']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")
        print(f"Success Rate: {(results['successful'] / results['total_images'] * 100):.1f}%")
        print(f"Processing Time: {results['total_processing_time_seconds']:.2f} seconds")
        print(f"Results Location: {processor.output_folder}")
        print("=" * 60)
        
        # Exit with appropriate code
        if results['failed'] == 0:
            print("🎉 All images processed successfully!")
            sys.exit(0)
        else:
            print(f"⚠️  {results['failed']} images failed processing. Check logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        sys.exit(1)


if __name__ == "__main__":
    main()
