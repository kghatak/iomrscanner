#!/usr/bin/env python3
"""
Test script for the automated pipeline.

This script demonstrates how to use the automated pipeline processor
programmatically without command-line arguments.
"""

import os
import sys
from automate_pipeline import AutomatedPipelineProcessor


def test_automation():
    """Test the automated pipeline with a sample PDF."""
    
    # Check if test PDF exists
    test_pdf_path = "test_input_pdf/OMR_300DPI.pdf"
    
    if not os.path.exists(test_pdf_path):
        print(f"❌ Test PDF not found: {test_pdf_path}")
        print("Please ensure you have a PDF file in the test_input_pdf folder")
        return False
    
    print("🚀 Starting automated pipeline test...")
    print(f"📄 Test PDF: {test_pdf_path}")
    
    try:
        # Initialize the processor
        processor = AutomatedPipelineProcessor("test_results")
        
        # Run the full pipeline
        results = processor.run_full_pipeline(test_pdf_path)
        
        # Print results
        print("\n" + "=" * 50)
        print("TEST RESULTS")
        print("=" * 50)
        print(f"Total Images: {results['total_images']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")
        print(f"Processing Time: {results['total_processing_time_seconds']:.2f} seconds")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_automation()
    sys.exit(0 if success else 1)
