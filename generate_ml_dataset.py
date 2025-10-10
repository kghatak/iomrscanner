#!/usr/bin/env python3
"""
Generate ML Training Dataset from OMR Images

This script adds the ML Dataset Generator stage to the pipeline
and processes OMR images to create training data for the ML model.

Usage:
    python generate_ml_dataset.py <image_path>
    
Example:
    python generate_ml_dataset.py test_input_pdf/OMR_300DPI_pages/page_1.png
"""

import sys
import os
from image_processor import ImageProcessor
from pipeline.ml_dataset_generator_stage import MLDatasetGeneratorStage


def generate_dataset(image_path: str):
    """Generate ML dataset from an OMR image"""
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found: {image_path}")
        return False
    
    print("=" * 80)
    print("🤖 ML Dataset Generator")
    print("=" * 80)
    print(f"Input image: {image_path}")
    print()
    
    # Initialize processor
    print("📦 Initializing image processor...")
    processor = ImageProcessor()
    
    # Add ML dataset generator stage to pipeline
    ml_stage = MLDatasetGeneratorStage(processor)
    processor.pipeline_manager.add_stage(ml_stage, position=5)  # After answer extraction
    
    print(f"✅ ML Dataset Generator added to pipeline")
    print(f"   Pipeline now has {len(processor.pipeline_manager.stages)} stages")
    print()
    
    # Get output folder
    output_folder = os.path.dirname(image_path)
    if not output_folder:
        output_folder = "."
    
    print(f"📂 Output folder: {output_folder}")
    print()
    
    # Run the pipeline
    print("=" * 80)
    print("🚀 Running Pipeline")
    print("=" * 80)
    print()
    
    result = processor.process_image_pipeline(image_path, output_folder)
    
    # Check results
    print()
    print("=" * 80)
    print("📊 Results")
    print("=" * 80)
    
    if result['success']:
        print("✅ Pipeline completed successfully!")
        
        # Get ML dataset info
        stages = result.get('stages', {})
        ml_result = stages.get('ml_dataset_generator', {})
        
        if ml_result.get('success'):
            dataset_dir = ml_result.get('dataset_directory')
            total_patches = ml_result.get('total_patches', 0)
            initial_marked = ml_result.get('initial_marked', 0)
            initial_unmarked = ml_result.get('initial_unmarked', 0)
            
            print()
            print(f"📦 Dataset Generated:")
            print(f"   Directory: {dataset_dir}")
            print(f"   Total patches: {total_patches}")
            print(f"   Initially marked: {initial_marked}")
            print(f"   Initially unmarked: {initial_unmarked}")
            print()
            print(f"🎯 Next Steps:")
            print(f"   1. Review labels:")
            print(f"      python tools/manual_review_tool.py")
            print(f"   2. Train model:")
            print(f"      python ml/train_circle_classifier.py {dataset_dir}")
        else:
            print("⚠️  ML dataset generation stage did not complete successfully")
    else:
        print(f"❌ Pipeline failed at stage: {result.get('error_stage')}")
        print(f"   Error: {result.get('error_message')}")
        return False
    
    print()
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_ml_dataset.py <image_path>")
        print()
        print("Example:")
        print("  python generate_ml_dataset.py test_input_pdf/OMR_300DPI_pages/page_1.png")
        print()
        sys.exit(1)
    
    image_path = sys.argv[1]
    success = generate_dataset(image_path)
    
    sys.exit(0 if success else 1)

